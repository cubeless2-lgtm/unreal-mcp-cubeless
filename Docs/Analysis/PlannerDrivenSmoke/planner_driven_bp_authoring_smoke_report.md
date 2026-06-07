# Planner Driven BP Authoring Smoke

- Generated UTC: `2026-06-07T04:22:05.003129+00:00`
- Temp package path: `/Game/_MCP_Temp/PlannerDrivenSmoke`
- Live status: `passed`
- Manifest version: `section_39_bp_authoring_job_contract_v28`
- Safe requests queued: `12`
- Non-safe requests prevented: `7`

## Planner Gate

### Authoring Queue

- `safe_actor_shell` `safe_to_author` `actor_blueprint` parent=`Actor`: Create an Actor Blueprint shell with a Static Mesh Component, exposed health variable, BeginPlay event, and branch.
- `safe_function_call_defaults` `safe_to_author` `actor_blueprint` parent=`Actor`: Create an Actor Blueprint shell with a Static Mesh Component using the Engine cube mesh, float speed variable default 450, BeginPlay branch, and PrintString function call.
- `safe_component_hierarchy` `safe_to_author` `actor_blueprint` parent=`Actor`: Create an Actor Blueprint shell with a Scene Component root named PlannerSmokeRoot and a child Static Mesh Component named PlannerSmokeMesh attached to PlannerSmokeRoot, plus BeginPlay branch.
- `safe_component_property_defaults` `safe_to_author` `actor_blueprint` parent=`Actor`: Create an Actor Blueprint shell with a Static Mesh Component visibility false and BeginPlay branch.
- `safe_function_graph_authoring` `safe_to_author` `actor_blueprint` parent=`Actor`: Create an Actor Blueprint shell with a function graph named ComputePlannerValue, int input InputValue default 3, int output ResultValue default 7, and a return node.
- `safe_function_graph_body_math` `safe_to_author` `actor_blueprint` parent=`Actor`: Create an Actor Blueprint shell with a function graph named ComputePlannerBody, double local variable LocalValue default 5, an add math node using LocalValue plus 2, double output ResultValue, connect the math result to the return node, and compile.
- `safe_function_graph_local_set` `safe_to_author` `actor_blueprint` parent=`Actor`: Create an Actor Blueprint shell with a function graph named ComputePlannerLocalSet, double input InputValue default 3, double local variable AccumulatedValue default 0, add 2 to InputValue, set AccumulatedValue from the math result, then return AccumulatedValue as ResultValue.
- `safe_function_graph_compare_branch` `safe_to_author` `actor_blueprint` parent=`Actor`: Create an Actor Blueprint shell with a function graph named ComputePlannerBranch, double input InputValue default 3, double output ResultValue default 0, double local variable BranchResult default 0, compare InputValue greater than 10, branch on the comparison, set BranchResult to 1 on then and -1 on else, then return BranchResult as ResultValue.
- `safe_typed_variables_defaults` `safe_to_author` `actor_blueprint` parent=`Actor`: Create an Actor Blueprint shell with a Scene Component transform default, bool variable bPlannerEnabled default true, string variable PlannerLabel default Section22, and vector variable PlannerOffset default X=10 Y=20 Z=30.
- `safe_event_sequence_flow` `safe_to_author` `actor_blueprint` parent=`Actor`: Create an Actor Blueprint shell with BeginPlay, a Sequence node with two outputs, and two PrintString calls for the first and second sequence outputs.
- `safe_generated_function_invocation` `safe_to_author` `actor_blueprint` parent=`Actor`: Create an Actor Blueprint shell with BeginPlay, a function graph named ComputePlannerInvocation, double input AddendValue default 2, double local variable LocalValue default 5, an add math node returning ResultValue, then call the generated function from BeginPlay with AddendValue default 2 and store the ResultValue output in double variable LastInvocationResult default 0.
- `safe_event_dispatcher` `safe_to_author` `actor_blueprint` parent=`Actor`: Create a Blueprint Event Dispatcher, call it, bind it to a compatible custom event, assign it, unbind it, and clear it.

### Prevented Requests

- `review_component_property_unsupported` `safe_to_author` authoring_attempted=`False`: Create an Actor Blueprint shell with a Static Mesh Component component property CastShadow false.
- `review_parent_class_unsupported` `safe_to_author` authoring_attempted=`False`: Create a Character Blueprint shell with a Static Mesh Component and BeginPlay branch.
- `review_durable_authoring_save_requested` `safe_to_author` authoring_attempted=`False`: Create and save a durable Actor Blueprint named BP_PlannerDurable in /Game/Blueprints with a Static Mesh Component and BeginPlay branch.
- `review_umg_button` `requires_review` authoring_attempted=`False`: Create a UMG button click event graph for a UserWidget.
- `blocked_async_proxy` `blocked_until_reinforced` authoring_attempted=`False`: Convert a UBlueprintAsyncActionBase async action with callback exec pins, Activate(), Broadcast(), and cancellation cleanup.
- `blocked_gas_replication` `blocked_until_reinforced` authoring_attempted=`False`: Build a Gameplay Ability with AbilityTask prediction and replicated Server RPC state changes.
- `blocked_commonui` `blocked_until_reinforced` authoring_attempted=`False`: Create a CommonUI activatable widget tree with layer activation policy and back handling.

## Live Gate

- Status: `passed`
- Non-safe authoring attempted: `False`
- Durable authoring attempted: `False`
- Durable save/delete attempted: `False`

### Durable Preflight Live Results

- `review_durable_authoring_save_requested` status=`passed` target=`/Game/Blueprints/BP_PlannerDurable` asset_exists=`False` read_only=`True` authoring_attempted=`False` save_or_delete_attempted=`False`

### Safe Executions

- `safe_actor_shell` `passed` asset=`/Game/_MCP_Temp/PlannerDrivenSmoke/MCP_PlannerSmoke_safe_actor_shell_9b9510a6` compile_errors=`0` nodes=`4` function_nodes=`0` steps=`11` structural_assertions=`7` layout_assertions=`2` layout_spacing_assertions=`1` dataflow_verified=`False` cleanup_deleted=`True`
- `safe_function_call_defaults` `passed` asset=`/Game/_MCP_Temp/PlannerDrivenSmoke/MCP_PlannerSmoke_safe_function_call_defaults_9b9510a6` compile_errors=`0` nodes=`5` function_nodes=`0` steps=`14` structural_assertions=`14` layout_assertions=`3` layout_spacing_assertions=`3` dataflow_verified=`False` cleanup_deleted=`True`
- `safe_component_hierarchy` `passed` asset=`/Game/_MCP_Temp/PlannerDrivenSmoke/MCP_PlannerSmoke_safe_component_hierarchy_9b9510a6` compile_errors=`0` nodes=`4` function_nodes=`0` steps=`12` structural_assertions=`7` layout_assertions=`2` layout_spacing_assertions=`1` dataflow_verified=`False` cleanup_deleted=`True`
- `safe_component_property_defaults` `passed` asset=`/Game/_MCP_Temp/PlannerDrivenSmoke/MCP_PlannerSmoke_safe_component_property_defaults_9b9510a6` compile_errors=`0` nodes=`4` function_nodes=`0` steps=`11` structural_assertions=`7` layout_assertions=`2` layout_spacing_assertions=`1` dataflow_verified=`False` cleanup_deleted=`True`
- `safe_function_graph_authoring` `passed` asset=`/Game/_MCP_Temp/PlannerDrivenSmoke/MCP_PlannerSmoke_safe_function_graph_authoring_9b9510a6` compile_errors=`0` nodes=`3` function_nodes=`2` steps=`8` structural_assertions=`6` layout_assertions=`1` layout_spacing_assertions=`0` dataflow_verified=`False` cleanup_deleted=`True`
- `safe_function_graph_body_math` `passed` asset=`/Game/_MCP_Temp/PlannerDrivenSmoke/MCP_PlannerSmoke_safe_function_graph_body_math_9b9510a6` compile_errors=`0` nodes=`3` function_nodes=`4` steps=`12` structural_assertions=`14` layout_assertions=`3` layout_spacing_assertions=`3` dataflow_verified=`True` cleanup_deleted=`True`
- `safe_function_graph_local_set` `passed` asset=`/Game/_MCP_Temp/PlannerDrivenSmoke/MCP_PlannerSmoke_safe_function_graph_local_set_9b9510a6` compile_errors=`0` nodes=`3` function_nodes=`4` steps=`16` structural_assertions=`14` layout_assertions=`2` layout_spacing_assertions=`1` dataflow_verified=`True` cleanup_deleted=`True`
- `safe_function_graph_compare_branch` `passed` asset=`/Game/_MCP_Temp/PlannerDrivenSmoke/MCP_PlannerSmoke_safe_function_graph_compare_branch_9b9510a6` compile_errors=`0` nodes=`3` function_nodes=`7` steps=`24` structural_assertions=`34` layout_assertions=`5` layout_spacing_assertions=`10` dataflow_verified=`True` cleanup_deleted=`True`
- `safe_typed_variables_defaults` `passed` asset=`/Game/_MCP_Temp/PlannerDrivenSmoke/MCP_PlannerSmoke_safe_typed_variables_defaults_9b9510a6` compile_errors=`0` nodes=`3` function_nodes=`0` steps=`10` structural_assertions=`0` layout_assertions=`0` layout_spacing_assertions=`0` dataflow_verified=`False` cleanup_deleted=`True`
- `safe_event_sequence_flow` `passed` asset=`/Game/_MCP_Temp/PlannerDrivenSmoke/MCP_PlannerSmoke_safe_event_sequence_flow_9b9510a6` compile_errors=`0` nodes=`6` function_nodes=`0` steps=`10` structural_assertions=`22` layout_assertions=`4` layout_spacing_assertions=`6` dataflow_verified=`False` cleanup_deleted=`True`
- `safe_generated_function_invocation` `passed` asset=`/Game/_MCP_Temp/PlannerDrivenSmoke/MCP_PlannerSmoke_safe_generated_function_invocation_9b9510a6` compile_errors=`0` nodes=`7` function_nodes=`4` steps=`28` structural_assertions=`44` layout_assertions=`8` layout_spacing_assertions=`13` dataflow_verified=`True` cleanup_deleted=`True`
- `safe_event_dispatcher` `passed` asset=`/Game/_MCP_Temp/PlannerDrivenSmoke/MCP_PlannerSmoke_safe_event_dispatcher_9b9510a6` compile_errors=`0` nodes=`10` function_nodes=`0` steps=`15` structural_assertions=`32` layout_assertions=`6` layout_spacing_assertions=`15` dataflow_verified=`True` cleanup_deleted=`True`

### Generated Leftovers

- none


## Decision

Run this smoke before letting automated BP requests call live UnrealMCP authoring. A non-safe planner status or non-executable job manifest must remain a dry-run record and must not create assets.
