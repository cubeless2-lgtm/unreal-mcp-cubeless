"""Runtime tool registry and management helpers for Unreal MCP."""

import ipaddress
import inspect
import logging
import os
import threading
import time
from collections import Counter, deque
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from functools import wraps
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, Set

from mcp.server.fastmcp import Context, FastMCP


logger = logging.getLogger("UnrealMCP")


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int = 0) -> int:
    value = os.environ.get(name)
    if value is None or value.strip() == "":
        return default
    try:
        return int(value)
    except ValueError:
        logger.warning("Invalid integer for %s: %s", name, value)
        return default


def _is_loopback_host(host: str) -> bool:
    normalized = (host or "").strip().lower()
    if normalized in {"localhost", "localhost.localdomain"}:
        return True
    try:
        return ipaddress.ip_address(normalized).is_loopback
    except ValueError:
        return False


class RuntimeTelemetry:
    """Small in-memory telemetry buffer for MCP tool and bridge requests."""

    def __init__(self, max_events: int = 80) -> None:
        self.started_at = time.time()
        self._lock = threading.Lock()
        self._next_id = 1
        self._active: Dict[int, Dict[str, Any]] = {}
        self._recent_events = deque(maxlen=max_events)
        self._total_by_kind: Counter = Counter()
        self._failure_by_kind: Counter = Counter()
        self._total_by_name: Counter = Counter()
        self._failure_by_name: Counter = Counter()
        self._status_counts: Counter = Counter()
        self._guard_events: Counter = Counter()

    def begin(self, kind: str, name: str) -> Dict[str, Any]:
        now = time.perf_counter()
        with self._lock:
            request_id = self._next_id
            self._next_id += 1
            token = {"id": request_id, "kind": kind, "name": name, "started": now}
            self._active[request_id] = token
            self._total_by_kind[kind] += 1
            self._total_by_name[f"{kind}:{name}"] += 1
            return token

    def end(self, token: Dict[str, Any], success: bool, status: str = "ok", error: str = "") -> None:
        finished = time.perf_counter()
        duration_ms = round((finished - float(token.get("started", finished))) * 1000.0, 3)
        kind = str(token.get("kind", "unknown"))
        name = str(token.get("name", "unknown"))
        request_id = int(token.get("id", 0))
        event = {
            "id": request_id,
            "kind": kind,
            "name": name,
            "success": bool(success),
            "status": status,
            "duration_ms": duration_ms,
        }
        if error:
            event["error"] = str(error)[:500]
        with self._lock:
            self._active.pop(request_id, None)
            if not success:
                self._failure_by_kind[kind] += 1
                self._failure_by_name[f"{kind}:{name}"] += 1
            self._status_counts[status] += 1
            self._recent_events.append(event)

    def record_guard_event(self, guard_type: str, name: str, decision: Dict[str, Any]) -> None:
        event = {
            "id": 0,
            "kind": "guard",
            "name": name,
            "success": bool(decision.get("allowed", False)),
            "status": guard_type,
            "duration_ms": 0.0,
            "reason": decision.get("reason", ""),
            "mode": decision.get("mode", ""),
            "would_block": bool(decision.get("would_block", False)),
        }
        with self._lock:
            self._guard_events[guard_type] += 1
            self._recent_events.append(event)

    def report(self, include_recent: bool = True) -> Dict[str, Any]:
        with self._lock:
            active_by_kind = Counter(item["kind"] for item in self._active.values())
            report = {
                "started_at_epoch": self.started_at,
                "uptime_seconds": round(time.time() - self.started_at, 3),
                "active_requests": len(self._active),
                "active_by_kind": dict(active_by_kind),
                "total_by_kind": dict(self._total_by_kind),
                "failure_by_kind": dict(self._failure_by_kind),
                "total_by_name": dict(self._total_by_name),
                "failure_by_name": dict(self._failure_by_name),
                "status_counts": dict(self._status_counts),
                "guard_events": dict(self._guard_events),
            }
            if include_recent:
                report["recent_events"] = list(self._recent_events)
            return report

    def reset_for_tests(self) -> None:
        with self._lock:
            self._active.clear()
            self._recent_events.clear()
            self._total_by_kind.clear()
            self._failure_by_kind.clear()
            self._total_by_name.clear()
            self._failure_by_name.clear()
            self._status_counts.clear()
            self._guard_events.clear()


class RuntimeGuard:
    """Conservative runtime guards for future transports and current bridge use."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._rate_events: Dict[str, deque] = {}

    def config(self) -> Dict[str, Any]:
        mode = os.environ.get("UNREAL_MCP_GUARD_MODE", "hard").strip().lower()
        if mode not in {"off", "soft", "hard"}:
            mode = "hard"
        rate_limit = max(0, _env_int("UNREAL_MCP_RATE_LIMIT_PER_MINUTE", 0))
        return {
            "mode": mode,
            "allow_non_loopback": _env_bool("UNREAL_MCP_ALLOW_NON_LOOPBACK", False),
            "require_token_for_non_loopback": _env_bool("UNREAL_MCP_REQUIRE_TOKEN_FOR_NON_LOOPBACK", True),
            "capability_token_configured": bool(os.environ.get("UNREAL_MCP_CAPABILITY_TOKEN", "")),
            "rate_limit_per_minute": rate_limit,
        }

    def check_bridge_target(self, host: str, port: int) -> Dict[str, Any]:
        config = self.config()
        is_loopback = _is_loopback_host(host)
        if config["mode"] == "off" or is_loopback:
            return {
                "allowed": True,
                "would_block": False,
                "mode": config["mode"],
                "host": host,
                "port": port,
                "loopback": is_loopback,
                "reason": "loopback bridge target" if is_loopback else "guard mode off",
            }

        token_ok = bool(config["capability_token_configured"]) or not bool(config["require_token_for_non_loopback"])
        explicitly_allowed = bool(config["allow_non_loopback"]) and token_ok
        would_block = not explicitly_allowed
        allowed = explicitly_allowed or config["mode"] == "soft"
        reason = "non-loopback bridge target allowed by explicit configuration"
        if would_block:
            reason = "non-loopback bridge target requires explicit allow and configured capability token"
        return {
            "allowed": allowed,
            "would_block": would_block,
            "mode": config["mode"],
            "host": host,
            "port": port,
            "loopback": False,
            "reason": reason,
        }

    def check_rate_limit(self, kind: str, name: str, protected: bool = False) -> Dict[str, Any]:
        config = self.config()
        limit = int(config["rate_limit_per_minute"])
        if protected or config["mode"] == "off" or limit <= 0:
            return {"allowed": True, "would_block": False, "mode": config["mode"], "reason": "rate limit disabled"}

        now = time.monotonic()
        key = f"{kind}:{name}"
        with self._lock:
            events = self._rate_events.setdefault(key, deque())
            while events and now - events[0] >= 60.0:
                events.popleft()
            would_block = len(events) >= limit
            if not would_block or config["mode"] == "soft":
                events.append(now)

        allowed = not would_block or config["mode"] == "soft"
        reason = f"rate limit exceeded for {key}: {limit}/minute" if would_block else "within rate limit"
        return {
            "allowed": allowed,
            "would_block": would_block,
            "mode": config["mode"],
            "reason": reason,
            "limit_per_minute": limit,
            "key": key,
        }

    def reset_for_tests(self) -> None:
        with self._lock:
            self._rate_events.clear()


request_telemetry = RuntimeTelemetry()
runtime_guard = RuntimeGuard()
_health_provider: Optional[Callable[..., Dict[str, Any]]] = None


def set_health_provider(provider: Callable[..., Dict[str, Any]]) -> None:
    global _health_provider
    _health_provider = provider


def _provider_health(ping_unreal: bool = False) -> Dict[str, Any]:
    if _health_provider is None:
        return {
            "success": True,
            "unreal_bridge": {
                "status": "unknown",
                "message": "No Unreal bridge health provider has been registered",
            },
        }
    try:
        return _health_provider(ping_unreal=ping_unreal)
    except Exception as exc:
        logger.warning("Runtime health provider failed: %s", exc)
        return {
            "success": False,
            "unreal_bridge": {
                "status": "error",
                "message": str(exc),
            },
        }


@dataclass(frozen=True)
class ToolRecord:
    name: str
    category: str
    module: str
    line: int
    description: str
    protected: bool = False


class MCPToolRegistry:
    """Track FastMCP tools and apply explicit runtime enable/disable policy."""

    def __init__(self) -> None:
        self._tools: Dict[str, ToolRecord] = {}
        self._disabled_tools: Set[str] = set()
        self._disabled_categories: Set[str] = set()
        self._protected_tools: Set[str] = set()

    @contextmanager
    def capture_tools(
        self,
        mcp: FastMCP,
        category: str,
        protected_tools: Iterable[str] = (),
    ) -> Iterator[None]:
        original_tool = mcp.tool
        protected_names = set(protected_tools)

        def managed_tool(name: Optional[str] = None, description: Optional[str] = None):
            original_decorator = original_tool(name=name, description=description)

            def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
                tool_name = name or func.__name__
                wrapped = self._wrap_tool(tool_name, category, func)
                original_decorator(wrapped)
                self.register_tool(
                    tool_name,
                    category,
                    func,
                    description=description,
                    protected=tool_name in protected_names,
                )
                return wrapped

            return decorator

        mcp.tool = managed_tool  # type: ignore[method-assign]
        try:
            yield
        finally:
            mcp.tool = original_tool  # type: ignore[method-assign]

    def register_tool(
        self,
        name: str,
        category: str,
        func: Callable[..., Any],
        description: Optional[str] = None,
        protected: bool = False,
    ) -> None:
        doc = inspect.getdoc(func) or ""
        record = ToolRecord(
            name=name,
            category=category,
            module=getattr(func, "__module__", ""),
            line=getattr(getattr(func, "__code__", None), "co_firstlineno", 0),
            description=description or doc.splitlines()[0] if doc else description or "",
            protected=protected,
        )
        if name in self._tools:
            logger.warning("Replacing existing MCP tool registry record for %s", name)
        self._tools[name] = record
        if protected:
            self._protected_tools.add(name)
            self._disabled_tools.discard(name)

    def _wrap_tool(self, name: str, category: str, func: Callable[..., Any]) -> Callable[..., Any]:
        tool_category = category
        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                return await self._run_async_tool(name, tool_category, func, *args, **kwargs)

            async_wrapper.__signature__ = inspect.signature(func)  # type: ignore[attr-defined]
            return async_wrapper

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return self._run_sync_tool(name, tool_category, func, *args, **kwargs)

        wrapper.__signature__ = inspect.signature(func)  # type: ignore[attr-defined]
        return wrapper

    def _preflight_tool(self, name: str, tool_category: str) -> Optional[Dict[str, Any]]:
        protected = name in self._protected_tools
        rate_decision = runtime_guard.check_rate_limit("tool", name, protected=protected)
        if rate_decision.get("would_block"):
            request_telemetry.record_guard_event("rate_limit", name, rate_decision)
        if not rate_decision.get("allowed", True):
            return {
                "success": False,
                "status": "rate_limited",
                "error": rate_decision.get("reason", "rate limit exceeded"),
                "tool": name,
                "category": tool_category,
                "guard": rate_decision,
            }

        disabled_reason = self.disabled_reason(name, tool_category)
        if disabled_reason:
            return self.disabled_response(name, tool_category, disabled_reason)
        return None

    def _result_success(self, result: Any) -> bool:
        if isinstance(result, dict):
            if result.get("success") is False:
                return False
            if result.get("status") in {"error", "disabled", "rate_limited", "blocked"}:
                return False
        return True

    def _result_status(self, result: Any) -> str:
        if isinstance(result, dict):
            status = result.get("status")
            if isinstance(status, str) and status:
                return status
            if result.get("success") is False:
                return "error"
        return "ok"

    def _result_error(self, result: Any) -> str:
        if isinstance(result, dict):
            error = result.get("error") or result.get("message")
            if isinstance(error, str):
                return error
        return ""

    def _run_sync_tool(self, name: str, tool_category: str, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        token = request_telemetry.begin("tool", name)
        try:
            preflight = self._preflight_tool(name, tool_category)
            if preflight is not None:
                request_telemetry.end(token, False, status=self._result_status(preflight), error=self._result_error(preflight))
                return preflight
            result = func(*args, **kwargs)
            request_telemetry.end(token, self._result_success(result), status=self._result_status(result), error=self._result_error(result))
            return result
        except Exception as exc:
            request_telemetry.end(token, False, status="exception", error=str(exc))
            raise

    async def _run_async_tool(self, name: str, tool_category: str, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        token = request_telemetry.begin("tool", name)
        try:
            preflight = self._preflight_tool(name, tool_category)
            if preflight is not None:
                request_telemetry.end(token, False, status=self._result_status(preflight), error=self._result_error(preflight))
                return preflight
            result = await func(*args, **kwargs)
            request_telemetry.end(token, self._result_success(result), status=self._result_status(result), error=self._result_error(result))
            return result
        except Exception as exc:
            request_telemetry.end(token, False, status="exception", error=str(exc))
            raise

    def disabled_reason(self, name: str, category: str) -> str:
        if name in self._protected_tools:
            return ""
        if name in self._disabled_tools:
            return f"tool '{name}' is disabled"
        if category in self._disabled_categories:
            return f"category '{category}' is disabled"
        return ""

    def disabled_response(self, name: str, category: str, reason: str) -> Dict[str, Any]:
        return {
            "success": False,
            "status": "disabled",
            "error": reason,
            "tool": name,
            "category": category,
        }

    def set_tool_enabled(self, name: str, enabled: bool) -> Dict[str, Any]:
        if name not in self._tools:
            return {"success": False, "error": f"Unknown tool: {name}"}
        if name in self._protected_tools and not enabled:
            return {"success": False, "error": f"Protected tool cannot be disabled: {name}"}
        if enabled:
            self._disabled_tools.discard(name)
        else:
            self._disabled_tools.add(name)
        return {"success": True, "tool": name, "enabled": self.is_tool_enabled(name)}

    def set_category_enabled(self, category: str, enabled: bool) -> Dict[str, Any]:
        categories = {record.category for record in self._tools.values()}
        if category not in categories:
            return {"success": False, "error": f"Unknown category: {category}"}
        if enabled:
            self._disabled_categories.discard(category)
        else:
            self._disabled_categories.add(category)
        return {"success": True, "category": category, "enabled": category not in self._disabled_categories}

    def reset(self) -> Dict[str, Any]:
        self._disabled_tools.clear()
        self._disabled_categories.clear()
        return {"success": True, "message": "All runtime tool policy overrides were cleared"}

    def is_tool_enabled(self, name: str) -> bool:
        record = self._tools.get(name)
        if not record:
            return False
        return self.disabled_reason(record.name, record.category) == ""

    def report(self, include_tools: bool = True) -> Dict[str, Any]:
        category_summary: Dict[str, Dict[str, Any]] = {}
        for record in sorted(self._tools.values(), key=lambda value: (value.category, value.name)):
            summary = category_summary.setdefault(
                record.category,
                {
                    "total": 0,
                    "enabled": 0,
                    "disabled": 0,
                    "disabled_by_category": record.category in self._disabled_categories,
                },
            )
            summary["total"] += 1
            if self.is_tool_enabled(record.name):
                summary["enabled"] += 1
            else:
                summary["disabled"] += 1

        tools: List[Dict[str, Any]] = []
        if include_tools:
            for record in sorted(self._tools.values(), key=lambda value: (value.category, value.name)):
                item = asdict(record)
                item["enabled"] = self.is_tool_enabled(record.name)
                item["disabled_reason"] = self.disabled_reason(record.name, record.category)
                tools.append(item)

        return {
            "success": True,
            "total_tools": len(self._tools),
            "enabled_tools": sum(1 for name in self._tools if self.is_tool_enabled(name)),
            "disabled_tools": sorted(self._disabled_tools),
            "disabled_categories": sorted(self._disabled_categories),
            "protected_tools": sorted(self._protected_tools),
            "categories": category_summary,
            "tools": tools,
        }

    def health_report(self, include_tools: bool = False, include_recent: bool = True, ping_unreal: bool = False) -> Dict[str, Any]:
        health = _provider_health(ping_unreal=ping_unreal)
        health.update(
            {
                "success": bool(health.get("success", True)),
                "registry": self.report(include_tools=include_tools),
                "telemetry": request_telemetry.report(include_recent=include_recent),
                "guard": runtime_guard.config(),
            }
        )
        return health

    def manage(
        self,
        action: str = "status",
        tool_name: str = "",
        category: str = "",
        enabled: Optional[bool] = None,
        include_tools: bool = True,
        include_recent: bool = True,
        ping_unreal: bool = False,
    ) -> Dict[str, Any]:
        normalized_action = action.lower().strip()

        if normalized_action in {"status", "list", "list_tools"}:
            return self.report(include_tools=include_tools)
        if normalized_action in {"health", "heartbeat"}:
            if normalized_action == "heartbeat":
                ping_unreal = True
            return self.health_report(include_tools=include_tools, include_recent=include_recent, ping_unreal=ping_unreal)
        if normalized_action == "reset":
            result = self.reset()
            result["registry"] = self.report(include_tools=include_tools)
            return result
        if normalized_action in {"enable_tool", "disable_tool", "set_tool"}:
            if not tool_name:
                return {"success": False, "error": "tool_name is required"}
            if normalized_action == "set_tool" and enabled is None:
                return {"success": False, "error": "enabled is required for set_tool"}
            desired = enabled if normalized_action == "set_tool" else normalized_action == "enable_tool"
            result = self.set_tool_enabled(tool_name, bool(desired))
            result["registry"] = self.report(include_tools=include_tools)
            return result
        if normalized_action in {"enable_category", "disable_category", "set_category"}:
            if not category:
                return {"success": False, "error": "category is required"}
            if normalized_action == "set_category" and enabled is None:
                return {"success": False, "error": "enabled is required for set_category"}
            desired = enabled if normalized_action == "set_category" else normalized_action == "enable_category"
            result = self.set_category_enabled(category, bool(desired))
            result["registry"] = self.report(include_tools=include_tools)
            return result

        return {
            "success": False,
            "error": f"Unknown action: {action}",
            "supported_actions": [
                "status",
                "list",
                "list_tools",
                "health",
                "heartbeat",
                "enable_tool",
                "disable_tool",
                "set_tool",
                "enable_category",
                "disable_category",
                "set_category",
                "reset",
            ],
        }


tool_registry = MCPToolRegistry()


def register_management_tools(mcp: FastMCP, registry: MCPToolRegistry = tool_registry) -> None:
    """Register protected runtime management tools."""

    with registry.capture_tools(mcp, category="management", protected_tools=("manage_tools",)):

        @mcp.tool()
        def manage_tools(
            ctx: Context,
            action: str = "status",
            tool_name: str = "",
            category: str = "",
            enabled: Optional[bool] = None,
            include_tools: bool = True,
            include_recent: bool = True,
            ping_unreal: bool = False,
        ) -> Dict[str, Any]:
            """
            Inspect or adjust runtime MCP tool policy.

            Defaults to a read-only status report. Enable/disable actions are
            in-memory only and reset when the MCP server restarts.
            """

            return registry.manage(
                action=action,
                tool_name=tool_name,
                category=category,
                enabled=enabled,
                include_tools=include_tools,
                include_recent=include_recent,
                ping_unreal=ping_unreal,
            )

    logger.info("Management tools registered successfully")
