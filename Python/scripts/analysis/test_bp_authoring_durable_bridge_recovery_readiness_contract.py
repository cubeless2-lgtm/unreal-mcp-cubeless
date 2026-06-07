#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_bridge_recovery_readiness_contract.py."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_bridge_recovery_readiness_contract as bridge_recovery  # noqa: E402


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="mcp_bridge_recovery_fixture_") as temp_dir:
        root = Path(temp_dir)
        project_root = root / "CubelessStylized"
        python_dir = root / "unreal-mcp-cubeless" / "Python"
        python_dir.mkdir(parents=True)
        (project_root).mkdir()
        (python_dir / "unreal_mcp_server.py").write_text("# fixture\n", encoding="utf-8")
        mcp_config = {
            "mcpServers": {
                "unrealMCP": {
                    "command": "uv",
                    "args": [
                        "--directory",
                        "../unreal-mcp-cubeless/Python",
                        "run",
                        "--python",
                        "3.11",
                        "unreal_mcp_server.py",
                    ],
                }
            }
        }
        inputs = bridge_recovery.collect_bridge_recovery_inputs(
            project_root,
            mcp_config=mcp_config,
            uv_available=True,
        )
        assert inputs["mcp_config_present"] is True
        assert inputs["server_defined"] is True
        assert inputs["command"] == "uv"
        assert inputs["directory_arg"] == "../unreal-mcp-cubeless/Python"
        assert inputs["python_version"] == "3.11"
        assert inputs["python_dir_exists"] is True
        assert inputs["server_script_exists"] is True
        assert inputs["uv_available"] is True

        contract = bridge_recovery.build_bridge_recovery_readiness_contract(True, inputs)
        assert contract["schema"] == bridge_recovery.BRIDGE_RECOVERY_READINESS_SCHEMA
        assert contract["requested"] is True
        assert contract["local_recovery_inputs_ready"] is True
        assert contract["missing_recovery_inputs"] == []
        assert contract["missing_recovery_input_count"] == 0
        assert contract["bridge_socket_probe_performed"] is False
        assert contract["bridge_reachable"] is False
        assert contract["read_only_canary_retry_allowed_after_recovery"] is False
        assert contract["durable_executor_may_open_after_recovery"] is False
        assert contract["durable_authoring_allowed"] is False
        assert contract["save_delete_rename_allowed"] is False
        assert contract["live_authoring_command_count"] == 0
        assert contract["live_save_or_delete_command_count"] == 0
        assert "section_71_recovery_readiness_does_not_probe_or_open_bridge" in contract["blocked_by"]

        summary = bridge_recovery.summarize_bridge_recovery_readiness_contracts([contract])
        assert summary == {
            "schema": bridge_recovery.BRIDGE_RECOVERY_READINESS_SUMMARY_SCHEMA,
            "status": "passed",
            "durable_requested_bridge_recovery_readiness_count": 1,
            "local_recovery_inputs_ready_count": 1,
            "missing_recovery_input_count": 0,
            "bridge_socket_probe_performed_count": 0,
            "bridge_reachable_count": 0,
            "read_only_canary_retry_allowed_after_recovery_count": 0,
            "durable_executor_may_open_after_recovery_count": 0,
            "durable_authoring_allowed_count": 0,
            "save_delete_rename_allowed_count": 0,
            "live_authoring_command_count": 0,
            "live_save_or_delete_command_count": 0,
        }

    print("BP authoring durable bridge recovery readiness contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
