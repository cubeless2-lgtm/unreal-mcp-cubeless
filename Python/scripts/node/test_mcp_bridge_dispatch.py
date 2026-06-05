#!/usr/bin/env python
"""
Smoke test for UnrealMCP bridge command dispatch.

This verifies that simple bridge commands return promptly before running
Blueprint graph authoring smoke tests.
"""

import json
import socket
from typing import Any, Dict


HOST = "127.0.0.1"
PORT = 55557


def send_command(command: str, params: Dict[str, Any], timeout: float = 20.0) -> Dict[str, Any]:
    command_obj = {"type": command, "params": params}
    with socket.create_connection((HOST, PORT), timeout=10.0) as sock:
        sock.sendall(json.dumps(command_obj).encode("utf-8"))
        sock.settimeout(timeout)

        chunks = []
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
            try:
                return json.loads(b"".join(chunks).decode("utf-8"))
            except json.JSONDecodeError:
                continue

    raise RuntimeError(f"No JSON response for command: {command}")


def require_success(command: str, params: Dict[str, Any], timeout: float = 20.0) -> Dict[str, Any]:
    response = send_command(command, params, timeout=timeout)
    if response.get("status") != "success":
        raise RuntimeError(f"{command} failed: {response}")
    return response.get("result", response)


def main() -> None:
    ping = require_success("ping", {})
    if ping.get("message") != "pong":
        raise RuntimeError(f"Unexpected ping response: {ping}")

    python_result = require_success(
        "execute_python",
        {
            "code": "print('mcp bridge dispatch smoke')",
            "mode": "execute",
            "defer_to_ticker": False,
        },
        timeout=30.0,
    )
    if not python_result.get("success"):
        raise RuntimeError(f"execute_python did not report success: {python_result}")

    # Confirm the bridge remains responsive after execute_python.
    second_ping = require_success("ping", {})
    if second_ping.get("message") != "pong":
        raise RuntimeError(f"Unexpected second ping response: {second_ping}")

    print("UnrealMCP bridge dispatch smoke passed")


if __name__ == "__main__":
    main()
