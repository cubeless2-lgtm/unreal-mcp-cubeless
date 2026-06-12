# Niagara Tools

These tools are local UnrealMCP C++ extensions for Niagara inspection and limited authoring.

Use Python/editor scripting for asset duplication, preview capture, and broad orchestration. Use these C++ tools only for Niagara APIs that are unsafe, protected, or impractical through Unreal Python.

## Tools

- `analyze_niagara_system(system_path, include_renderers=true, include_user_parameters=true, include_stack=true, include_graph=true, include_module_inputs=true, include_compile_status=true, include_pins=false, include_links=false, include_scratch_pads=true, include_resolved_stack_inputs=false, max_function_calls=200, max_nodes_per_graph=300, max_links_per_graph=0, max_modules=200, max_candidates_per_module=24, max_resolved_inputs_per_module=8, max_top_candidates=80)`
  - Aggregates the existing read-only renderer, User parameter, stack, graph, module input, and compile-health inspections into one response.
  - Does not save, request compile, or mutate source assets.
  - Returns `summary`, `section_status`, `limitations`, and the included section payloads.
- `inspect_niagara_renderers(system_path)`
  - Reads enabled renderer classes, material fields, material slots, and used materials.
- `set_niagara_renderer_material(system_path, material_path, emitter_index=None, emitter_name="", renderer_index=None, material_slot_index=0, allow_source_edit=false, save=true)`
  - Sets a renderer material reference.
  - Refuses source assets by default; pass `allow_source_edit=true` only after review.
- `inspect_niagara_user_parameters(system_path)`
  - Reads exposed `User.*` parameters, types, values, and whether MCP can set them.
- `set_niagara_user_parameter(system_path, parameter_name, value, allow_source_edit=false, save=true)`
  - Sets supported exposed User parameter values.
  - Supports common scalar, vector, color, and object-like values handled by the C++ bridge.
- `inspect_niagara_stack(system_path, include_pins=false, max_function_calls=200)`
  - Reads system, emitter, and Scratch Pad function-call stack metadata.
- `inspect_niagara_graph(system_path, include_pins=true, include_links=true, include_scratch_pads=true, max_nodes_per_graph=600, max_links_per_graph=2000)`
  - Reads full Niagara graph node, pin, and link topology for system scripts, emitter graphs, and Scratch Pad scripts.
  - This is read-only and intended as the structured basis for future safe graph authoring.
- `inspect_niagara_scratch_pad_interface(system_path, include_graph_summary=true, include_parent_scratch_pads=true, max_scripts=200, max_function_calls=80)`
  - Reads Scratch Pad ownership, usage, supported usage contexts, inputs, outputs, control hints, and optional compact graph summaries.
  - This is read-only and intended as the authoring-interface basis for future Scratch Pad duplication and graph wiring.
- `duplicate_or_attach_emitter_from_source(target_system_path, source_emitter_path="", source_system_path="", source_emitter_index=None, source_emitter_name="", new_emitter_name="", enabled=None, allow_source_edit=false, save=true, request_compile=true)`
  - Adds a source Niagara Emitter asset or a source Niagara System emitter handle into a target generated temp Niagara System.
  - Refuses target systems outside `/Game/_MCP_Temp/NiagaraGenerated/` by default.
  - Source assets are read-only; only the target system is modified, compiled, and optionally saved.
- `create_or_duplicate_scratch_pad_module(target_system_path, source_script_path="", source_system_path="", source_owner_kind="system", source_script_index=None, source_scratch_pad_name="", source_emitter_index=None, source_emitter_name="", target_owner_kind="system", target_emitter_index=None, target_emitter_name="", new_script_name="", allow_source_edit=false, save=true, request_compile=true)`
  - Duplicates an existing Scratch Pad script into a target generated temp Niagara System or emitter.
  - Refuses target systems outside `/Game/_MCP_Temp/NiagaraGenerated/` by default.
  - This pass only duplicates the Scratch Pad script. Use `add_scratch_pad_module_to_stack` to insert a target-local module into a stack after duplication.
- `add_scratch_pad_module_to_stack(target_system_path, scratch_pad_script_path="", scratch_pad_owner_kind="system", scratch_pad_script_index=None, scratch_pad_name="", scratch_pad_emitter_index=None, scratch_pad_emitter_name="", target_usage="ParticleUpdateScript", target_usage_id="", target_emitter_index=None, target_emitter_name="", target_index=None, suggested_name="", allow_source_edit=false, save=true, request_compile=true, skip_if_duplicate=true)`
  - Inserts an existing target-local Scratch Pad module into a Niagara stack through `FNiagaraStackGraphUtilities::AddScriptModuleToStack`.
  - Refuses target systems outside `/Game/_MCP_Temp/NiagaraGenerated/` by default.
  - Requires `UNiagaraScript` usage `Module` and validates that the Scratch Pad advertises support for the requested target usage before adding the function-call node.
  - Skips duplicate insertion by default when the same Scratch Pad script already exists in the requested output stack, including `target_usage_id` when provided, returning `skipped_duplicate=true` and the existing module node metadata without saving or requesting compile.
  - Does not perform arbitrary internal Scratch Pad graph mutation or pin/link rewiring beyond the stack utility insertion.
- `inspect_niagara_compile_status(system_path, request_compile=false, force=false, allow_source_compile=false, wait_for_completion=false, timeout_seconds=10.0, poll_interval_seconds=0.1)`
  - Reads per-script Niagara compile statuses, warning/error counts, and outstanding compile request state.
  - `request_compile=true` is blocked for source assets unless `allow_source_compile=true` is explicitly passed.
  - `wait_for_completion=true` polls outstanding compile requests up to `timeout_seconds` and reports `wait_timed_out`.
- `inspect_niagara_module_inputs(system_path, include_linked_sources=true, include_resolved_stack_inputs=false, max_modules=200, max_candidates_per_module=24, max_resolved_inputs_per_module=8, max_top_candidates=80)`
  - Reads module input candidates for generation planning.
- `create_niagara_module_input_override(system_path, input_name, value, emitter_index=None, emitter_name="", module_index=None, module_name="", module_node_guid="", overwrite_existing=false, allow_source_edit=false, save=true)`
  - Creates a missing RapidIteration module input override on an existing module input.
  - Refuses source assets by default and refuses to overwrite an existing override unless `overwrite_existing=true` is passed.
- `set_niagara_module_inputs_batch(system_path, edits, operation="set_existing", overwrite_existing=false, continue_on_error=false, allow_source_edit=false, save=true)`
  - Applies multiple RapidIteration module input edits in one command and saves once after successful edits.
  - `operation` may be `set_existing`, `create_override`, or `upsert`; each edit object may override the operation and selectors.
- `set_niagara_module_input_value(system_path, input_name, value, emitter_index=None, emitter_name="", module_index=None, module_name="", module_node_guid="", allow_source_edit=false, save=true)`
  - Sets an existing RapidIteration module input override.
  - Does not create new RapidIteration overrides when no existing parameter data is present.

## Safety Rules

- Default write scope is generated/temp Niagara work under `/Game/_MCP_Temp/NiagaraGenerated/`.
- Keep source Niagara systems read-only unless the caller explicitly passes `allow_source_edit=true`.
- Prefer duplicating a source system first, then editing the duplicate.
- Treat arbitrary Scratch Pad internal graph wiring and emitter merging as future work. `inspect_niagara_graph` and `inspect_niagara_scratch_pad_interface` observe graph/interface topology; stack insertion is limited to target-local Scratch Pad modules through `add_scratch_pad_module_to_stack`.
- Emitter attach/duplicate writes are target-temp-system only by default through `duplicate_or_attach_emitter_from_source`.
- Scratch Pad duplication and stack insertion writes are target-temp-system only by default through `create_or_duplicate_scratch_pad_module` and `add_scratch_pad_module_to_stack`.
- New RapidIteration override creation is available through `create_niagara_module_input_override`, guarded to generated/temp Niagara systems by default.
- Compile-status inspection is read-only by default. Compile requests are allowed by default only under `/Game/_MCP_Temp/NiagaraGenerated/`.

## Maintenance

The C++ implementation lives in:

- `MCPGameProject/Plugins/UnrealMCP/Source/UnrealMCP/Public/Commands/UnrealMCPNiagaraCommands.h`
- `MCPGameProject/Plugins/UnrealMCP/Source/UnrealMCP/Private/Commands/UnrealMCPNiagaraCommands.cpp`

The Python registration lives in:

- `Python/tools/niagara_tools.py`
- `Python/unreal_mcp_server.py`
