#!/usr/bin/env python
"""Smoke tests for bp_authoring_quality_gate.py."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_quality_gate as gate  # noqa: E402


def write_tool_fixture(root: Path) -> None:
    tools = root / "Python" / "tools"
    tools.mkdir(parents=True)
    (tools / "blueprint_tools.py").write_text(
        """
def register_blueprint_tools(mcp):
    def create_blueprint():
        pass
    def add_component_to_blueprint():
        pass
    def list_blueprint_components():
        pass

    def get_component_property():
        pass
    def compile_and_validate_blueprint():
        pass
    def compile_and_save_blueprint():
        pass
""".strip()
        + "\n",
        encoding="utf-8",
    )
    (tools / "node_tools.py").write_text(
        """
def register_node_tools(mcp):
    def add_blueprint_variable():
        pass
    def add_blueprint_event_dispatcher():
        pass
    def add_blueprint_event_dispatcher_call_node():
        pass
    def add_blueprint_custom_event_node():
        pass
    def add_blueprint_event_dispatcher_bind_node():
        pass
    def add_blueprint_event_dispatcher_unbind_node():
        pass
    def add_blueprint_event_dispatcher_clear_node():
        pass
    def add_blueprint_event_dispatcher_assign_node():
        pass
    def add_blueprint_variable_get_node():
        pass
    def add_blueprint_event_node():
        pass
    def add_blueprint_sequence_node():
        pass
    def add_blueprint_branch_node():
        pass
    def connect_blueprint_nodes():
        pass
    def set_blueprint_pin_default():
        pass
    def resolve_blueprint_graph():
        pass
    def add_blueprint_function_parameter():
        pass
    def list_blueprint_graphs():
        pass
    def list_blueprint_nodes():
        pass
    def resolve_blueprint():
        pass
""".strip()
        + "\n",
        encoding="utf-8",
    )
    (tools / "python_tools.py").write_text(
        """
def register_python_tools(mcp):
    def execute_python():
        pass
""".strip()
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="mcp_bp_quality_gate_fixture_") as temp_dir:
        temp_root = Path(temp_dir)
        mcp_root = temp_root / "MCP"
        output_dir = temp_root / "out"
        write_tool_fixture(mcp_root)

        report = gate.build_report(mcp_root, None, output_dir, None)
        json_path, md_path = gate.write_report(report, output_dir)

        assert json_path.exists()
        assert md_path.exists()
        assert report["capability_manifest"]["all_required_ready"] is True
        assert report["verdict"]["status"] == "capability_manifest_ready_live_gate_not_run"
        assert report["live_gate"]["status"] == "not_requested"
        assert "generic delegate lifecycle authoring for non-Event-Dispatcher targets" in report["capability_manifest"]["deferred_authoring_gaps"]
        assert "generic delegate assign/unbind/clear graph authoring" not in report["capability_manifest"]["deferred_authoring_gaps"]
        assert "Blueprint Event Dispatcher unbind/clear topology" not in report["capability_manifest"]["deferred_authoring_gaps"]
        assert "generic delegate bind/assign/unbind graph authoring" not in report["capability_manifest"]["deferred_authoring_gaps"]
        assert "Blueprint Event Dispatcher declaration and bind topology" not in report["capability_manifest"]["deferred_authoring_gaps"]
        assert "Blueprint Event Dispatcher call and bind topology" not in report["capability_manifest"]["deferred_authoring_gaps"]
        assert "Blueprint Event Dispatcher bind/unbind topology" not in report["capability_manifest"]["deferred_authoring_gaps"]
        assert not (mcp_root / "bp_authoring_quality_gate_report.json").exists()

    print("BP authoring quality gate smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
