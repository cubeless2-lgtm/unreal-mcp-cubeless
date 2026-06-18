# Unreal MCP Node Tools

This document provides detailed information about the Blueprint node tools available in the Unreal MCP integration.

## Overview

Node tools allow you to manipulate Blueprint graph nodes and connections programmatically, including adding event nodes, function nodes, variables, and creating connections between nodes.

## Graph Authoring

Most node authoring commands accept optional graph selector fields:

- `graph_id` (string, optional) - Graph GUID from `list_blueprint_graphs` or `resolve_blueprint_graph`
- `graph_name` (string, optional) - Graph name
- `graph_type` (string, optional) - `event`, `function`, `macro`, `delegate`, or `any`
- `create_graph_if_missing` (boolean, optional) - For node creation commands, create a missing function graph when `graph_type` is `function`

When no graph selector is supplied, commands keep the legacy behavior and target the Blueprint event graph.

### ensure_anim_graph_input_pose_passthrough

Ensure an Animation Blueprint `AnimGraph` passes the incoming input pose through to the root output. This is intended for safe Post Process AnimBP setup and learning fixtures.

The command creates or reuses an `AnimGraphNode_LinkedInputPose` node and connects its `Pose` output to the root node's `Result` input. If the root result pin is already linked to another node, the command fails unless `replace_existing` is `true`.

**Parameters:**
- `blueprint_name` (string) - Anim Blueprint name or path
- `graph_name` (string, optional) - Defaults to `AnimGraph`
- `graph_id` (string, optional) - Target graph GUID
- `graph_type` (string, optional) - Defaults to `function`, because Unreal reports AnimGraph through the Blueprint function graph list
- `replace_existing` (boolean, optional) - Replace an existing root pose link
- `input_node_position` (array, optional) - `[X, Y]` editor position for a newly created input pose node

**Example:**
```json
{
  "command": "ensure_anim_graph_input_pose_passthrough",
  "params": {
    "blueprint_name": "/Game/_MCP_Sample/AnimStudy/ABP_Bot_PostProcess_Study.ABP_Bot_PostProcess_Study",
    "graph_name": "AnimGraph",
    "graph_type": "function",
    "replace_existing": false
  }
}
```

### ensure_anim_graph_modify_bone_demo

Ensure an Animation Blueprint `AnimGraph` contains a simple component-space Modify Bone demo chain. This is intended for Post Process AnimBP learning fixtures where the incoming pose should pass through a visible, reversible bone offset.

The command creates or reuses this chain:

`LinkedInputPose -> LocalToComponentSpace -> Transform (Modify) Bone -> ComponentToLocalSpace -> Root`

The Modify Bone node is configured to ignore translation and scale, use additive rotation in bone space, and write the requested rotation both to the runtime node settings and the exposed `Rotation` input pin default.

**Parameters:**
- `blueprint_name` (string) - Anim Blueprint name or path
- `graph_name` (string, optional) - Defaults to `AnimGraph`
- `graph_id` (string, optional) - Target graph GUID
- `graph_type` (string, optional) - Defaults to `function`
- `bone_name` (string, optional) - Target skeleton bone; defaults to `head`
- `rotation` (array, optional) - `[Pitch, Yaw, Roll]` additive rotation in degrees; defaults to `[0, 0, 6]`
- `replace_existing` (boolean, optional) - Replace existing pose links needed to install the demo chain

**Example:**
```json
{
  "command": "ensure_anim_graph_modify_bone_demo",
  "params": {
    "blueprint_name": "/Game/_MCP_Sample/AnimStudy/ABP_Bot_PostProcess_Study.ABP_Bot_PostProcess_Study",
    "graph_name": "AnimGraph",
    "graph_type": "function",
    "bone_name": "head",
    "rotation": [0, 0, 4],
    "replace_existing": true
  }
}
```

### ensure_anim_graph_modify_curve_demo

Ensure an Animation Blueprint `AnimGraph` contains a simple Modify Curve demo chain. This is intended for sample-only animation learning fixtures where the incoming pose should pass through forced curve values, especially ControlRig gate experiments.

The command creates or reuses this chain:

`LinkedInputPose -> ModifyCurve -> Root`

By default the command refuses to modify AnimBPs outside `/Game/_MCP_Sample/`. Pass `allow_non_sample=true` only for intentional non-sample edits.

The default curve values are tuned for the StackOBot ControlRig gate study:

- `IK_blend_interact=1.0`
- `IKBlend_l=1.0`

**Parameters:**
- `blueprint_name` (string) - Anim Blueprint name or path
- `graph_name` (string, optional) - Defaults to `AnimGraph`
- `graph_id` (string, optional) - Target graph GUID
- `graph_type` (string, optional) - Defaults to `function`
- `curve_values` (object or array, optional) - Curve values as `{ "CurveName": 1.0 }` or `[{"name":"CurveName","value":1.0}]`
- `alpha` (number, optional) - Modify Curve alpha; defaults to `1.0`
- `apply_mode` (string, optional) - `Add`, `Scale`, `Blend`, `WeightedMovingAverage`, or `RemapCurve`; defaults to `Add`
- `replace_existing` (boolean, optional) - Replace existing pose links needed to install the demo chain
- `allow_non_sample` (boolean, optional) - Allow non-`/Game/_MCP_Sample/` AnimBP edits

**Example:**
```json
{
  "command": "ensure_anim_graph_modify_curve_demo",
  "params": {
    "blueprint_name": "/Game/_MCP_Sample/AnimStudy/ABP_Bot_ControlRig_ForcedCurve_Study.ABP_Bot_ControlRig_ForcedCurve_Study",
    "graph_name": "AnimGraph",
    "graph_type": "function",
    "curve_values": {
      "IK_blend_interact": 1.0,
      "IKBlend_l": 1.0
    },
    "apply_mode": "Add",
    "replace_existing": true
  }
}
```

### set_anim_graph_controlrig_input_defaults

Expose ControlRig AnimGraph input pins and set their default values. This is intended for sample-only animation learning fixtures that need to force ControlRig driver inputs without hand-editing protected AnimGraph internals.

By default the command refuses to modify AnimBPs outside `/Game/_MCP_Sample/`. Pass `allow_non_sample=true` only for intentional non-sample edits.

The default input values are tuned for the StackOBot ControlRig forced-driver study:

- `ShouldDoIKTrace=true`
- `InteractionWorldLocation=[80, -40, 80]`

**C++ API note:** this command exists because ControlRig AnimGraph custom input pins are backed by protected editor-node optional-pin state. Python cannot safely expose and rebuild those pins directly on UE 5.7.

**Parameters:**
- `blueprint_name` (string) - Anim Blueprint name or path
- `graph_name` (string, optional) - Defaults to `AnimGraph`
- `graph_id` (string, optional) - Target graph GUID
- `graph_type` (string, optional) - Defaults to `function`
- `input_defaults` (object or array, optional) - Input defaults as `{ "InputName": value }` or `[{"name":"InputName","value":value}]`
- `node_id` (string, optional) - ControlRig node GUID or object-name filter
- `node_name` (string, optional) - ControlRig node object-name filter
- `title_contains` (string, optional) - ControlRig node title substring filter
- `control_rig_class` (string, optional) - ControlRig generated class path or substring filter
- `disconnect_existing_links` (boolean, optional) - Disconnect existing links on target pins so defaults drive the sample; defaults to `false`
- `allow_non_sample` (boolean, optional) - Allow non-`/Game/_MCP_Sample/` AnimBP edits

**Example:**
```json
{
  "command": "set_anim_graph_controlrig_input_defaults",
  "params": {
    "blueprint_name": "/Game/_MCP_Sample/AnimStudy/ABP_Bot_ControlRig_InputDefaults_Study.ABP_Bot_ControlRig_InputDefaults_Study",
    "graph_name": "AnimGraph",
    "graph_type": "function",
    "control_rig_class": "CR_Bot_Correction",
    "input_defaults": {
      "ShouldDoIKTrace": true,
      "InteractionWorldLocation": [80, -40, 80]
    },
    "disconnect_existing_links": true
  }
}
```

### ensure_controlrig_forced_driver_animbp

Ensure a sample Animation Blueprint has a forced ControlRig driver path. The command inserts or reuses a `ModifyCurve` node directly before the selected ControlRig node, preserves the existing upstream source pose, forces curve values, exposes ControlRig input pins, and can disconnect existing input links so the requested defaults drive the sample.

By default the command refuses to modify AnimBPs outside `/Game/_MCP_Sample/`. Pass `allow_non_sample=true` only for intentional non-sample edits.

The default forced-driver values are tuned for the StackOBot ControlRig study:

- Curves: `IK_blend_interact=1.0`, `IKBlend_l=1.0`
- ControlRig inputs: `ShouldDoIKTrace=true`, `InteractionWorldLocation=[80, -40, 80]`

**C++ API note:** this command is required because a safe forced-driver sample must rewire protected AnimGraph pose links around a ControlRig node and expose ControlRig custom input pins. Plain Python reflection should not hand-edit that graph state on UE 5.7.

**Parameters:**
- `blueprint_name` (string) - Anim Blueprint name or path
- `graph_name` (string, optional) - Defaults to `AnimGraph`
- `graph_id` (string, optional) - Target graph GUID
- `graph_type` (string, optional) - Defaults to `function`
- `curve_values` (object or array, optional) - Forced curve values as `{ "CurveName": 1.0 }` or `[{"name":"CurveName","value":1.0}]`
- `input_defaults` (object or array, optional) - ControlRig input defaults as `{ "InputName": value }` or `[{"name":"InputName","value":value}]`
- `alpha` (number, optional) - Modify Curve alpha; defaults to `1.0`
- `apply_mode` (string, optional) - `Add`, `Scale`, `Blend`, `WeightedMovingAverage`, or `RemapCurve`; defaults to `Add`
- `node_id` (string, optional) - ControlRig node GUID or object-name filter
- `node_name` (string, optional) - ControlRig node object-name filter
- `title_contains` (string, optional) - ControlRig node title substring filter
- `control_rig_class` (string, optional) - ControlRig generated class path or substring filter
- `replace_existing` (boolean, optional) - Replace pose links needed to insert ModifyCurve before ControlRig; defaults to `true`
- `disconnect_existing_links` (boolean, optional) - Disconnect existing ControlRig input links so defaults drive the sample; defaults to `true`
- `allow_non_sample` (boolean, optional) - Allow non-`/Game/_MCP_Sample/` AnimBP edits

**Example:**
```json
{
  "command": "ensure_controlrig_forced_driver_animbp",
  "params": {
    "blueprint_name": "/Game/_MCP_Sample/AnimStudy/ABP_Bot_ControlRig_ForcedDriver_Study.ABP_Bot_ControlRig_ForcedDriver_Study",
    "graph_name": "AnimGraph",
    "graph_type": "function",
    "control_rig_class": "CR_Bot_Correction",
    "curve_values": {
      "IK_blend_interact": 1.0,
      "IKBlend_l": 1.0
    },
    "input_defaults": {
      "ShouldDoIKTrace": true,
      "InteractionWorldLocation": [80, -40, 80]
    },
    "replace_existing": true,
    "disconnect_existing_links": true
  }
}
```

### ensure_anim_graph_trail_demo

Ensure an Animation Blueprint `AnimGraph` contains a Trail Controller demo chain. This is intended for sample-only animation learning fixtures where the incoming pose should pass through an active component-space `Trail` node without modifying original project assets.

The command creates or reuses this chain:

`LinkedInputPose -> LocalToComponentSpace -> Trail -> ComponentToLocalSpace -> Root`

By default the command refuses to modify AnimBPs outside `/Game/_MCP_Sample/`. Pass `allow_non_sample=true` only for intentional non-sample edits.

**Parameters:**
- `blueprint_name` (string) - Anim Blueprint name or path
- `graph_name` (string, optional) - Defaults to `AnimGraph`
- `graph_id` (string, optional) - Target graph GUID
- `graph_type` (string, optional) - Defaults to `function`
- `trail_bone` (string, optional) - Active trail bone; defaults to `VB VBHead`
- `base_joint` (string, optional) - Base joint for velocity; defaults to `head`
- `chain_length` (number, optional) - Trail chain length; minimum `2`
- `chain_bone_axis` (string, optional) - `X`, `Y`, or `Z`; defaults to `X`
- `alpha` (number, optional) - Trail node alpha; defaults to `1.0`
- `fake_velocity` (array, optional) - `[X, Y, Z]` fake velocity for static preview tests; defaults to `[0, 0, 0]`
- `replace_existing` (boolean, optional) - Replace existing pose links needed to install the demo chain
- `allow_non_sample` (boolean, optional) - Allow non-`/Game/_MCP_Sample/` AnimBP edits
- `invert_chain_bone_axis` (boolean, optional) - Invert the selected chain bone axis
- `reorient_parent_to_child` (boolean, optional) - Reorient parent bones toward children; defaults to `true`
- `actor_space_fake_velocity` (boolean, optional) - Apply fake velocity in actor space instead of world space
- `relaxation_speed_scale` (number, optional) - Trail relaxation scale; defaults to `1.0`
- `limit_stretch` (boolean, optional) - Enable stretch limiting
- `stretch_limit` (number, optional) - Stretch limit when enabled
- `max_delta_time` (number, optional) - Optional timestep clamp

**Example:**
```json
{
  "command": "ensure_anim_graph_trail_demo",
  "params": {
    "blueprint_name": "/Game/_MCP_Sample/AnimStudy/ABP_Bot_Trail_Study.ABP_Bot_Trail_Study",
    "graph_name": "AnimGraph",
    "graph_type": "function",
    "trail_bone": "VB VBHead",
    "base_joint": "head",
    "chain_length": 2,
    "chain_bone_axis": "X",
    "fake_velocity": [0, 0, 0],
    "replace_existing": true
  }
}
```

### list_blueprint_graphs

List graphs in a Blueprint and return stable graph IDs.

**Parameters:**
- `blueprint_name` (string) - Blueprint name or path
- `graph_type` (string, optional) - Filter by graph type

### inspect_anim_graph_node_settings

Read reflected runtime settings from AnimGraph nodes. This is useful for learning or validating nodes such as `RigidBody`, `Trail`, `ControlRig`, `Transform (Modify) Bone`, and other editor nodes that wrap an internal `FAnimNode_*` struct.

The command is read-only. It returns normal node metadata plus a `settings` object containing the wrapped anim-node struct type and UPROPERTY values.

**Parameters:**
- `blueprint_name` (string) - Animation Blueprint name or path
- `graph_name` (string, optional) - Defaults to `AnimGraph`
- `graph_id` (string, optional) - Target graph GUID
- `graph_type` (string, optional) - Defaults to `function`
- `node_id` (string, optional) - Node GUID filter
- `node_type` (string, optional) - Node class or title substring filter, such as `RigidBody`
- `title_contains` (string, optional) - Node title substring filter
- `include_pins` (boolean, optional) - Include pin metadata and links
- `max_depth` (number, optional) - Nested struct/array dump depth, clamped from `1` to `8`

**Example:**
```json
{
  "command": "inspect_anim_graph_node_settings",
  "params": {
    "blueprint_name": "/Game/StackOBot/Characters/Blobling/Anim/ABP_Baddy.ABP_Baddy",
    "graph_name": "AnimGraph",
    "graph_type": "function",
    "node_type": "RigidBody",
    "max_depth": 5
  }
}
```

### inspect_anim_state_machine_transitions

Read Animation Blueprint state-machine transition topology. The command is read-only and does not compile, save, or modify the Blueprint.

The response includes state-machine nodes, optional state summaries, transition source/target states, transition blend/priority settings, the bound transition rule graph, and optional rule graph nodes/pins.

**Parameters:**
- `blueprint_name` (string) - Animation Blueprint name or path
- `state_machine_name` (string, optional) - State machine name/title substring filter
- `include_pins` (boolean, optional) - Include pin metadata and links on returned graph nodes
- `include_rule_graph_nodes` (boolean, optional) - Include nodes inside each transition rule graph
- `include_state_nodes` (boolean, optional) - Include state node summaries for each state machine
- `max_rule_graph_nodes` (number, optional) - Max rule graph nodes per transition, `-1` for unlimited

**Example:**
```json
{
  "command": "inspect_anim_state_machine_transitions",
  "params": {
    "blueprint_name": "/Game/StackOBot/Characters/Bot/ABP_Bot.ABP_Bot",
    "state_machine_name": "AirLocomotion",
    "include_pins": true,
    "include_rule_graph_nodes": true,
    "max_rule_graph_nodes": 64
  }
}
```

### controlrig_direct_gate_probe

Run a transient direct ControlRig gate probe without modifying or saving assets. The command creates a runtime ControlRig instance per case, applies requested UPROPERTY values and hierarchy curve values, executes ControlRig events, samples hierarchy transforms, and reports deltas from the first successful case.

The default case set is tuned for the StackOBot Control Rig learning pass:

- `ShouldDoIKTrace`
- `InteractionWorldLocation`
- `IKBlend_l`
- `IK_blend_interact`
- sampled elements such as `foot_l`, `foot_r`, `IK_foot_L`, and `IK_foot_R`

**Parameters:**
- `control_rig_path` (string, optional) - ControlRig Blueprint asset path
- `control_rig_class` (string, optional) - Generated ControlRig class path; use this instead of `control_rig_path` when probing a native/generated class directly
- `cases` (array, optional) - Case objects. Each case may include `name`, `properties`, shorthand `should_trace`, shorthand `loc` or `interaction_world_location`, and `curves`
- `sample_elements` (array, optional) - Hierarchy element names or objects such as `{"type":"Control","name":"IK_foot_L"}`
- `execute_events` (array, optional) - ControlRig event names; defaults to `Construction`, `Forwards Solve`, and `Post Forwards Solve`
- `should_trace_property` (string, optional) - Property used by shorthand `should_trace`; defaults to `ShouldDoIKTrace`
- `interaction_location_property` (string, optional) - Property used by shorthand `loc`; defaults to `InteractionWorldLocation`

**Example:**
```json
{
  "command": "controlrig_direct_gate_probe",
  "params": {
    "control_rig_path": "/Game/StackOBot/Characters/Bot/Rig/CR_Bot_Correction.CR_Bot_Correction",
    "sample_elements": ["foot_l", "foot_r", "Control:IK_foot_L", "Control:IK_foot_R"],
    "cases": [
      {
        "name": "baseline",
        "should_trace": false,
        "loc": [0, 0, 0],
        "curves": {"IKBlend_l": 0, "IK_blend_interact": 0}
      },
      {
        "name": "interact_side",
        "should_trace": true,
        "loc": [80, -40, 80],
        "curves": {"IKBlend_l": 1, "IK_blend_interact": 1}
      }
    ]
  }
}
```

### sample_controlrig_pre_post_runtime_pose

Sample ControlRig hierarchy transforms before and after execute events without modifying or saving assets. The default case is tuned for the StackOBot forced-driver study: `ShouldDoIKTrace=true`, `InteractionWorldLocation=[80, -40, 80]`, `IKBlend_l=1.0`, and `IK_blend_interact=1.0`.

**Important scope note:** this command currently samples a transient ControlRig instance directly. It reports `runtime_source=direct_transient_controlrig` and `runtime_graph_prepost=false`; it does not instrument the compiled AnimGraph node stack or capture the actual upstream AnimBP pose inside a running SkeletalMeshComponent.

Use this command when you need a stable same-instance pre/post ControlRig solve measurement before building deeper runtime AnimGraph instrumentation.

**Parameters:**
- `control_rig_path` (string, optional) - ControlRig Blueprint asset path
- `control_rig_class` (string, optional) - Generated ControlRig class path; use this instead of `control_rig_path` when probing a native/generated class directly
- `input_defaults` (object, optional) - ControlRig property defaults; defaults to `ShouldDoIKTrace=true` and `InteractionWorldLocation=[80, -40, 80]`
- `curve_values` (object, optional) - Hierarchy curve values; defaults to `IKBlend_l=1.0` and `IK_blend_interact=1.0`
- `cases` (array, optional) - Case objects. If provided, each case may include `name`, `properties`, shorthand `should_trace`, shorthand `loc` or `interaction_world_location`, and `curves`
- `sample_elements` (array, optional) - Hierarchy element names or objects such as `{"type":"Control","name":"IK_foot_L"}`
- `execute_events` (array, optional) - ControlRig event names to execute between pre/post samples; defaults to `Forwards Solve`
- `should_trace_property` (string, optional) - Property used by shorthand `should_trace`; defaults to `ShouldDoIKTrace`
- `interaction_location_property` (string, optional) - Property used by shorthand `loc`; defaults to `InteractionWorldLocation`

**Returns:**
- `pre_pose` and `post_pose` hierarchy transform samples per case
- `deltas` with translation distance, rotation delta in degrees, and scale delta
- property/curve inputs and echoes
- execute result list and warning/error arrays

**Example:**
```json
{
  "command": "sample_controlrig_pre_post_runtime_pose",
  "params": {
    "control_rig_path": "/Game/StackOBot/Characters/Bot/Rig/CR_Bot_Correction.CR_Bot_Correction",
    "sample_elements": ["foot_l", "foot_r", "Control:IK_foot_L", "Control:IK_foot_R"],
    "input_defaults": {
      "ShouldDoIKTrace": true,
      "InteractionWorldLocation": [80, -40, 80]
    },
    "curve_values": {
      "IKBlend_l": 1.0,
      "IK_blend_interact": 1.0
    }
  }
}
```

### sample_anim_node_pre_post_runtime_pose

Resolve a target AnimGraph node or run a limited active-component tick-delta pose probe.

**Important scope note:** `dry_run=true` is a read-only target resolver. `dry_run=false` supports `mode=active_component_tick_delta` and `mode=isolated_temp_components`. Active tick-delta samples final `SkeletalMeshComponent` pose before and after forced ticks on a matched live component. Isolated temp mode duplicates the AnimBP under `_MCP_Temp`, bypasses the selected node in a source copy, and compares it against a selected-node copy on separate transient components. Neither runtime mode is true same-instance compiled AnimGraph instrumentation. Runtime responses intentionally report `runtime_graph_prepost=false` and `same_instance_prepost=false`.

Use this command before implementing or running deeper AnimGraph node instrumentation so ambiguous node selectors are caught early.

**Parameters:**
- `blueprint_name` or `anim_blueprint` (string) - Animation Blueprint name or path
- `graph_name` (string, optional) - Defaults to `AnimGraph`
- `graph_id` (string, optional) - Exact graph GUID
- `graph_type` (string, optional) - Defaults to `function` for AnimGraph
- `node_id` (string, optional) - Exact target node GUID. Required when filters are ambiguous.
- `node_type` (string, optional) - Node class/title filter, such as `AnimGraphNode_RigidBody`, `AnimGraphNode_Trail`, or `AnimGraphNode_ControlRig`
- `title_contains` (string, optional) - Node title substring filter
- `sample_bones` (array, optional) - Bone list to echo in dry-run or sample in runtime mode. Runtime default is a compact StackOBot/Baddy study set.
- `sample_sockets` (array, optional) - Socket list to echo in dry-run or sample in runtime mode
- `mode` (string, optional) - Runtime mode for `dry_run=false`: `active_component_tick_delta` or `isolated_temp_components`.
- `skeletal_mesh` (string, optional) - SkeletalMesh path required by `isolated_temp_components`
- `temp_root` (string, optional) - Temp asset root for isolated mode. Defaults to `/Game/_MCP_Temp/AnimNodePrePost`.
- `cleanup` (boolean, optional) - Delete transient actors/temp assets after isolated sampling. Defaults to `true`.
- `overwrite_existing_temp_assets` (boolean, optional) - Replace colliding temp assets. Defaults to `true`.
- `run_id` (string, optional) - Stable suffix for generated temp asset/actor names
- `actor_label`, `actor_name`, `actor_path` (string, optional) - Live actor selector for runtime mode
- `component_name` (string, optional) - Live `SkeletalMeshComponent` selector for runtime mode
- `prefer_pie_world` (boolean, optional) - Prefer PIE/SIE/play worlds over editor world. Defaults to `true`.
- `require_pie_world` (boolean, optional) - Refuse editor-world fallback. Defaults to `false`.
- `tick_count` (number, optional) - Forced tick count between pre/post samples, clamped `0..240`. Defaults to `1`.
- `tick_delta_time` (number, optional) - Forced tick delta time, clamped `0..1`. Defaults to `1/30`.
- `settle_tick_count` (number, optional) - Forced ticks before the pre sample, clamped `0..240`. Defaults to `0`.
- `refresh_bone_transforms` (boolean, optional) - Refresh bone transforms after forced ticks. Defaults to `true`.
- `allow_missing_bones` (boolean, optional) - Return partial samples instead of failing on missing bones/sockets. Defaults to `false`.
- `include_pins` (boolean, optional) - Include full selected-node pin data. Defaults to `true`.
- `max_depth` (number, optional) - Reflected settings depth. Defaults to `3`.
- `dry_run` (boolean, optional) - Resolve only when true; run `active_component_tick_delta` when false. Defaults to `true`.

**Returns:**
- `target_node` with node metadata, reflected settings, preferred input/output pose pins, upstream/downstream pose links, `mvp_kind`, and `isolated_sampler_mvp_supported`
- `mode=dry_run_target_resolver` for dry-run
- `mode=active_component_tick_delta` and `comparison_kind=active_component_tick_delta` for runtime tick-delta sampling
- `mode=isolated_temp_components` and `comparison_kind=isolated_temp_components` for temp source-vs-output sampling
- `runtime_graph_prepost=false`
- `same_instance_prepost=false`
- `pre_tick_pose`, `post_tick_pose`, and `deltas` for active tick-delta mode
- `source_pose`, `post_pose`, `deltas`, `prepare_temp_assets`, and `cleanup_results` for isolated temp mode
- `next_implementation_mode=isolated_temp_components` for dry-run
- warning/error details when the selector matches no node or multiple nodes

**Dry-run example:**
```json
{
  "command": "sample_anim_node_pre_post_runtime_pose",
  "params": {
    "blueprint_name": "/Game/StackOBot/Characters/Blobling/Anim/ABP_Baddy.ABP_Baddy",
    "graph_name": "AnimGraph",
    "graph_type": "function",
    "node_type": "AnimGraphNode_RigidBody",
    "sample_bones": ["Head_02", "TailEnd", "R_Stalk_04", "L_Stalk_04"]
  }
}
```

**Active component tick-delta example:**
```json
{
  "command": "sample_anim_node_pre_post_runtime_pose",
  "params": {
    "blueprint_name": "/Game/StackOBot/Characters/Blobling/Anim/ABP_Baddy.ABP_Baddy",
    "graph_name": "AnimGraph",
    "graph_type": "function",
    "node_id": "81E779C34D36CC52F0125F91BF52BAF3",
    "actor_label": "MCP_AnimNodeProbe_Baddy",
    "mode": "active_component_tick_delta",
    "dry_run": false,
    "settle_tick_count": 3,
    "tick_count": 5,
    "tick_delta_time": 0.033333,
    "sample_bones": ["Head_02", "TailEnd", "R_Stalk_04", "L_Stalk_04"]
  }
}
```

**Isolated temp source-vs-output example:**
```json
{
  "command": "sample_anim_node_pre_post_runtime_pose",
  "params": {
    "blueprint_name": "/Game/StackOBot/Characters/Blobling/Anim/ABP_Baddy.ABP_Baddy",
    "graph_name": "AnimGraph",
    "graph_type": "function",
    "node_id": "81E779C34D36CC52F0125F91BF52BAF3",
    "skeletal_mesh": "/Game/StackOBot/Characters/Blobling/SKM_Baddy.SKM_Baddy",
    "mode": "isolated_temp_components",
    "dry_run": false,
    "cleanup": true,
    "settle_tick_count": 3,
    "tick_count": 5,
    "tick_delta_time": 0.033333,
    "sample_bones": ["Head_02", "TailEnd", "R_Stalk_04", "L_Stalk_04"]
  }
}
```

### sample_skeletal_bones_in_sie

Sample bone and socket world/component transforms from a live `SkeletalMeshComponent` without modifying or saving assets.

**Important scope note:** this command is an immediate read-only sampler. It prefers an active PIE/SIE/play world, falls back to the editor world, and reports `sampled_world_type` plus `is_play_session_active`. It does not start SIE, spawn actors, or tick frames by itself. Use Python/editor automation to create or advance the runtime pose first, then call this command to capture the current pose.

**Parameters:**
- `actor_label` (string, optional) - Actor label filter, case-insensitive exact match
- `actor_name` (string, optional) - Actor object name filter, case-insensitive exact match
- `actor_path` (string, optional) - Actor path filter, exact or path suffix match
- `component_name` (string, optional) - SkeletalMeshComponent object name. If omitted, the first skeletal component on the matched actor is sampled.
- `bones` (array, optional) - Bone names to sample. Defaults to `root`, `pelvis`, `spine_03`, `head`, `foot_l`, and `foot_r`.
- `sockets` (array, optional) - Socket names to sample
- `prefer_pie_world` (boolean, optional) - Prefer active PIE/SIE/play world before editor world. Defaults to `true`.
- `require_pie_world` (boolean, optional) - Fail instead of falling back to the editor world when no PIE/SIE/play world matches. Defaults to `false`.

**Returns:**
- `actor` and `component` metadata for the sampled target
- `sampled_world_type`, `sampled_world_name`, and `is_play_session_active`
- `bone_samples` and `socket_samples` with `world` and `component` transforms
- warning/error arrays for missing bones, ambiguous matches, or missing sockets

**Example:**
```json
{
  "command": "sample_skeletal_bones_in_sie",
  "params": {
    "actor_label": "MCP_BlendSpace_SIE_Bot",
    "component_name": "SkeletalMeshComponent0",
    "bones": ["root", "pelvis", "spine_03", "head", "foot_l", "foot_r"],
    "sockets": ["head"],
    "prefer_pie_world": true
  }
}
```

### inspect_anim_instance_runtime_state

Inspect runtime `AnimInstance` state from a matched live `SkeletalMeshComponent` without modifying or saving assets.

**Important scope note:** this command is an immediate read-only inspector. It prefers an active PIE/SIE/play world, falls back to the editor world, and reports `sampled_world_type` plus `is_play_session_active`. It does not start SIE, spawn actors, or tick frames by itself. Use Python/editor automation to create or advance the runtime state first, then call this command to read the current AnimInstance state.

**Parameters:**
- `actor_label` (string, optional) - Actor label filter, case-insensitive exact match
- `actor_name` (string, optional) - Actor object name filter, case-insensitive exact match
- `actor_path` (string, optional) - Actor path filter, exact or path suffix match
- `component_name` (string, optional) - SkeletalMeshComponent object name. If omitted, the first skeletal component on the matched actor is inspected.
- `state_machine_name` (string, optional) - State-machine name substring filter
- `include_states` (boolean, optional) - Include per-state metadata. Per-state weights and relevant animation timing are intentionally omitted in the safe MVP. Defaults to `true`.
- `include_montages` (boolean, optional) - Include the current active montage summary. Defaults to `true`.
- `include_curves` (boolean, optional) - Include curve values. Defaults to `false`.
- `curve_names` (array, optional) - Specific curve names to sample when `include_curves=true`
- `max_state_machines` (number, optional) - Maximum state machines to include. Defaults to `32`.
- `max_state_machine_instances_to_probe` (number, optional) - Maximum runtime AnimNode indexes to probe for state-machine instances. Defaults to `256`.
- `max_states_per_machine` (number, optional) - Maximum states per state machine. Defaults to `64`.
- `max_curves` (number, optional) - Maximum curves to include. Defaults to `128`.
- `prefer_pie_world` (boolean, optional) - Prefer active PIE/SIE/play world before editor world. Defaults to `true`.
- `require_pie_world` (boolean, optional) - Fail instead of falling back to the editor world when no PIE/SIE/play world matches. Defaults to `false`.

**Returns:**
- `actor`, `component`, and `anim_instance` metadata
- `sampled_world_type`, `sampled_world_name`, and `is_play_session_active`
- `state_machines` with current state name/index, elapsed time, runtime/class machine indexes, and optional per-state metadata
- optional `active_montage`
- optional `curves`
- warning/error arrays for ambiguous matches, missing state machines, or missing curves

The state-machine reader uses live `FAnimNode_StateMachine` instances and maps them back to baked class data with `StateMachineIndexInClass`. This avoids unsafe `UAnimInstance` helper calls whose machine indexes do not always match baked state-machine array indexes.

**Example:**
```json
{
  "command": "inspect_anim_instance_runtime_state",
  "params": {
    "actor_label": "MCP_AnimState_Smoke",
    "state_machine_name": "Locomotion",
    "include_states": true,
    "include_curves": true,
    "curve_names": ["GroundSpeed", "IK_blend_interact"],
    "prefer_pie_world": true
  }
}
```

### set_anim_instance_runtime_property_for_probe

Set properties on the matched live `AnimInstance` object for runtime probing.

**Important scope note:** this command modifies only the current runtime `AnimInstance`; it does not modify or save the Animation Blueprint asset. The response reports `read_only=false`, `runtime_only=true`, `asset_modified=false`, and `saves_assets=false`.

Supported value types follow the shared runtime property writer: booleans, numbers, strings/names, `Vector`, `Rotator`, and `Transform`.

**Parameters:**
- `actor_label` (string, optional) - Actor label filter, case-insensitive exact match
- `actor_name` (string, optional) - Actor object name filter, case-insensitive exact match
- `actor_path` (string, optional) - Actor path filter, exact or path suffix match
- `component_name` (string, optional) - SkeletalMeshComponent object name
- `properties` (object or array, optional) - Property assignments, either `{ "GroundSpeed": 250.0 }` or `[{"name":"GroundSpeed","value":250.0}]`
- `property_name` + `value` (optional) - Single-property assignment alternative
- `tick_after_set` (boolean, optional) - Force component animation ticks after assignment. Defaults to `false`.
- `tick_count` (number, optional) - Forced `USkeletalMeshComponent::TickAnimation` count when `tick_after_set=true`. Defaults to `1`.
- `tick_delta_time` (number, optional) - Delta time per forced tick. Defaults to `1/30`.
- `refresh_bone_transforms` (boolean, optional) - Refresh bone transforms during/after forced ticks when `tick_after_set=true` and `tick_count > 0`. Defaults to `true`.
- `include_snapshot_after` (boolean, optional) - Include state-machine/montage/curve snapshot after assignment. Defaults to `true`.
- `include_previous_values` (boolean, optional) - Include previous property values in the assignment result. Defaults to `true`.
- Snapshot filters from `inspect_anim_instance_runtime_state`, such as `state_machine_name`, `include_states`, `include_curves`, and `curve_names`.
- Target/world selection options from `inspect_anim_instance_runtime_state`, such as `prefer_pie_world` and `require_pie_world`.

**Example:**
```json
{
  "command": "set_anim_instance_runtime_property_for_probe",
  "params": {
    "actor_label": "MCP_AnimState_Smoke",
    "properties": {
      "GroundSpeed": 250.0
    },
    "tick_after_set": true,
    "tick_count": 2,
    "prefer_pie_world": true
  }
}
```

### sample_anim_state_machine_runtime_response

Apply runtime `AnimInstance` property cases, force a narrow component animation tick, and sample state-machine response.

**Important scope note:** this is a controlled runtime probe. It does not start SIE/PIE, spawn actors, or save assets. By default each successful property change is restored after the case so repeated cases can start from the current pre-probe value.

**Parameters:**
- `actor_label`, `actor_name`, `actor_path`, `component_name` - Same target filters as `inspect_anim_instance_runtime_state`
- `cases` (array, optional) - Case objects. Each case may include `name`, `properties`, `tick_count`, `tick_delta_time`, and `restore_after_case`.
- `properties` (object, optional) - Single-case property assignments when `cases` is omitted
- `name` (string, optional) - Single-case name when `cases` is omitted
- `tick_count` (number, optional) - Default forced tick count per case. Defaults to `1`.
- `tick_delta_time` (number, optional) - Default delta time per forced tick. Defaults to `1/30`.
- `refresh_bone_transforms` (boolean, optional) - Refresh bone transforms during/after forced ticks when `tick_count > 0`. Defaults to `true`.
- `restore_after_case` (boolean, optional) - Restore successful property changes after each case. Defaults to `true`.
- `include_baseline` (boolean, optional) - Capture state before applying cases. Defaults to `true`.
- Snapshot filters from `inspect_anim_instance_runtime_state`, such as `state_machine_name`, `include_states`, `include_curves`, `curve_names`, and state-machine limits.
- Target/world selection options from `inspect_anim_instance_runtime_state`, such as `prefer_pie_world` and `require_pie_world`.

**Returns:**
- Target actor/component/AnimInstance metadata
- Optional `baseline`
- `cases` array, each with applied property echo, tick result, state-machine snapshot, restore result, warnings, and errors
- `asset_modified=false` and `saves_assets=false`

**Example:**
```json
{
  "command": "sample_anim_state_machine_runtime_response",
  "params": {
    "actor_label": "MCP_AnimState_Smoke",
    "cases": [
      {
        "name": "speed_0",
        "properties": {"GroundSpeed": 0.0},
        "tick_count": 2
      },
      {
        "name": "speed_500",
        "properties": {"GroundSpeed": 500.0},
        "tick_count": 4
      }
    ],
    "restore_after_case": true,
    "prefer_pie_world": true
  }
}
```

### set_anim_graph_rigidbody_settings

Set a narrow group of `RigidBody` AnimGraph node settings. This is intended for sample Animation Blueprint experiments, especially under `/Game/_MCP_Sample/`.

By default the command refuses to modify Animation Blueprints outside `/Game/_MCP_Sample/`. Pass `allow_non_sample=true` only for deliberate non-sample edits.

Supported settings:

- `alpha`
- `external_force`
- `simulation_space`: `ComponentSpace`, `WorldSpace`, or `BaseBoneSpace`
- `enable_world_geometry`

The command updates both runtime node fields and exposed input pin defaults for `Alpha` and `ExternalForce`.

**Parameters:**
- `blueprint_name` (string) - Animation Blueprint name or path
- `graph_name` (string, optional) - Defaults to `AnimGraph`
- `graph_id` (string, optional) - Target graph GUID
- `graph_type` (string, optional) - Defaults to `function`
- `node_id` (string, optional) - RigidBody node GUID filter
- `alpha` (number, optional) - RigidBody alpha
- `external_force` (array, optional) - `[X, Y, Z]` external force
- `simulation_space` (string, optional) - `ComponentSpace`, `WorldSpace`, or `BaseBoneSpace`
- `enable_world_geometry` (boolean, optional) - Enable world geometry collision
- `allow_non_sample` (boolean, optional) - Allow editing non-sample assets

**Example:**
```json
{
  "command": "set_anim_graph_rigidbody_settings",
  "params": {
    "blueprint_name": "/Game/_MCP_Sample/AnimStudy/ABP_Baddy_RigidBody_Study_ForceZ",
    "graph_name": "AnimGraph",
    "graph_type": "function",
    "alpha": 1.0,
    "external_force": [0, 0, 350],
    "simulation_space": "ComponentSpace"
  }
}
```

### resolve_blueprint_graph

Resolve or create a Blueprint graph.

**Parameters:**
- `blueprint_name` (string) - Blueprint name or path
- `graph_name` (string, optional) - Graph name
- `graph_id` (string, optional) - Graph GUID
- `graph_type` (string, optional) - Graph type
- `create_if_missing` (boolean, optional) - Create a missing function graph

**Example:**
```json
{
  "command": "resolve_blueprint_graph",
  "params": {
    "blueprint_name": "MyActor",
    "graph_name": "ConvertedFunction",
    "graph_type": "function",
    "create_if_missing": true
  }
}
```

### add_blueprint_branch_node

Add a Branch node to the selected graph.

### add_blueprint_sequence_node

Add a Sequence node to the selected graph.

**Parameters:**
- `output_count` (integer, optional) - Number of exec output pins, minimum 2

### add_blueprint_return_node

Add or resolve a Return node in a function graph.

### add_blueprint_dynamic_cast_node

Add a Dynamic Cast node to the selected graph.

**Parameters:**
- `target_class` (string) - UObject class name or path
- `pure` (boolean, optional) - Create a pure cast node

### Loop & Collection Authoring

#### add_blueprint_loop_node

Add a supported standard Blueprint loop macro node.

**Parameters:**
- `loop_type` (string, optional) - `for_loop`; this is the only stable loop type currently supported
- `first_index` (integer, optional) - Default value for the For Loop `FirstIndex` pin
- `last_index` (integer, optional) - Default value for the For Loop `LastIndex` pin

The command creates a `UK2Node_MacroInstance` backed by Unreal's standard `ForLoop` macro and returns full pin metadata for `execute`, `FirstIndex`, `LastIndex`, `LoopBody`, `Index`, and `Completed` where exposed by the engine version.

`ForEachLoop`, `ForEachLoopWithBreak`, and `WhileLoop` are intentionally unsupported in this stable pass. `ForEachLoop` depends on array wildcard inference, and `WhileLoop` needs explicit guard policy before it is safe for automatic C++ conversion.

#### add_blueprint_array_function_node

Add a typed Blueprint array function node.

**Parameters:**
- `operation` (string) - `length`, `get`, `set`, or `add`
- `element_type` (string) - Element type descriptor, for example `int`, `bool`, `double`, `vector`, `object`, `class`, or `enum`
- `type_object` (string, optional) - Class path/name for object or class element types
- `enum_type` (string, optional) - Enum object path for enum element types
- `param_defaults` (object, optional) - Defaults for non-array input pins such as `Index`, `Item`, `NewItem`, or `bSizeToFit`

This command uses `UK2Node_CallArrayFunction` and explicitly pins the array element type before returning node metadata. The `TargetArray` pin must be connected from a typed array variable or array-producing node; defaults for `TargetArray` are rejected.

Generic `KismetArrayLibrary` passthrough remains blocked by `add_blueprint_call_function_node` unless a later section implements a wider wildcard policy.

#### add_blueprint_make_array_node

Add a typed Blueprint `Make Array` node for collection literals.

**Parameters:**
- `element_type` (string) - Element type descriptor, for example `int`, `bool`, `double`, `string`, `name`, `text`, `vector`, `object`, `class`, or `enum`
- `input_count` (integer, optional) - Number of element input pins to create, from 0 to 128. If omitted, defaults to the number of `values` entries when `values` is provided, otherwise 1
- `values` (array, optional) - Element defaults applied to `[0]`, `[1]`, and later pins through K2 schema validation
- `type_object` (string, optional) - Class path/name for object or class element types
- `enum_type` (string, optional) - Enum object path for enum element types

The command creates `UK2Node_MakeArray`, explicitly types the output `Array` pin as an array and each input pin as a single element value, then applies defaults through the same validation path as `set_blueprint_pin_default`.

Stable scope is intentionally limited to 1D arrays. Nested arrays, maps, sets, wildcard inference, and direct use of `Make Array` output as the by-reference target for mutating array functions are deferred.

### Expression Node Authoring

These commands add pure Kismet expression nodes that are useful when translating C++ expressions into Blueprint graphs. They support the same graph selector fields listed above.

#### add_blueprint_compare_node

Add a typed comparison node.

**Parameters:**
- `operation` (string) - `less`, `greater`, `less_equal`, `greater_equal`, `equal`, `not_equal`, or aliases such as `<`, `>`, `<=`, `>=`, `==`, `!=`
- `value_type` (string, optional) - `int`, `int64`, `double`, `bool`, `object`, `class`, or `name`; default `double`

Relational operations are supported for numeric types. Equality and inequality are also supported for `bool`, `object`, `class`, and `name`.

#### add_blueprint_boolean_node

Add a boolean operator node.

**Parameters:**
- `operation` (string) - `not`, `and`, `nand`, `or`, `xor`, `nor`, `equal`, `not_equal`, or aliases such as `!`, `&&`, `||`, `==`, `!=`

#### add_blueprint_select_node

Add a typed Select node.

**Parameters:**
- `value_type` (string, optional) - `string`, `text`, `name`, `int`, `double`, `vector`, `rotator`, `color`, `transform`, `object`, or `class`; default `int`

#### add_blueprint_literal_node

Add a typed literal node.

**Parameters:**
- `literal_type` (string) - `int`, `int64`, `float`, `double`, `bool`, `name`, `byte`, `string`, or `text`
- `value` (any, optional) - Default literal value to apply to the node's `Value` pin

#### add_blueprint_enum_literal_node

Add a typed enum literal node.

**Parameters:**
- `enum_type` (string) - Enum object path. Prefer fully qualified native paths such as `/Script/Engine.ECollisionEnabled`
- `value` (string or integer, optional) - Enum entry name, scoped enum entry name, or integer enum value. When omitted, the first visible enum value is used

The node uses Unreal's enum pin representation: `PC_Byte` with the loaded `UEnum` as the subcategory object. Hidden and spacer enum entries are rejected as defaults.

#### add_blueprint_is_valid_node

Add an `Is Valid` expression node.

**Parameters:**
- `value_type` (string, optional) - `object` or `class`; default `object`

### Typed Control & Struct Authoring

These commands cover typed helpers that are safer to author directly than generic K2 wildcard nodes.

#### add_blueprint_make_struct_node

Add a native Make helper node.

**Parameters:**
- `struct_type` (string) - `vector`, `rotator`, or `transform`

This uses native `UKismetMathLibrary` functions such as `MakeVector`, `MakeRotator`, and `MakeTransform`.

#### add_blueprint_break_struct_node

Add a native Break helper node.

**Parameters:**
- `struct_type` (string) - `vector`, `rotator`, or `transform`

This uses native `UKismetMathLibrary` functions such as `BreakVector`, `BreakRotator`, and `BreakTransform`.

Generic make/break struct authoring is intentionally deferred until struct type loading and `CanBeMade`/`CanBeBroken` validation are implemented.

#### add_blueprint_switch_int_node

Add a `Switch on Int` node with contiguous case pins.

**Parameters:**
- `start_index` (integer, optional) - First case value, default `0`
- `case_count` (integer, optional) - Number of contiguous case pins, default `2`, maximum `128`
- `case_values` (array of integer, optional) - Ascending contiguous case values. When supplied, this overrides `start_index` and `case_count`
- `has_default_pin` (boolean, optional) - Include a `Default` exec pin, default `true`

Sparse switch cases are rejected by this command. Convert sparse cases with compare/branch fallback until sparse switch authoring is explicitly supported.

### Enum & Advanced Control Flow Authoring

#### add_blueprint_switch_enum_node

Add a `Switch on Enum` node.

**Parameters:**
- `enum_type` (string) - Enum object path. Prefer fully qualified native paths such as `/Script/Engine.ECollisionEnabled`
- `has_default_pin` (boolean, optional) - Include a `Default` exec pin, default `false`

The command creates case exec pins for the enum entries Unreal exposes on `UK2Node_SwitchEnum`. Arbitrary enum case subsets are intentionally unsupported.

Type descriptors for variables, function parameters, and local variables now support:

- `enum` or `byte_enum` with `type_object`, `enum_type`, or `enum_path`
- `is_array=true` for enum arrays, without array default serialization

Sparse int fallback authoring remains intentionally left for later graph-authoring passes. Sparse switch fallback should be built as compare/branch chains rather than by mutating `UK2Node_SwitchInteger` into unsupported sparse cases. Loop authoring currently supports the stable `ForLoop` macro path; ForEach and While variants remain deferred.

### Graph Validation Flow

After creating or modifying a Blueprint graph, call `compile_and_validate_blueprint`. Treat `validation_pass=false` or `compile_error_count > 0` as a failed authoring step.

Before running graph authoring smoke tests after C++ changes, fully close Unreal Editor and Live Coding, run a normal Development Editor UBT build, then reopen the editor. If Live Coding is still active, UBT will reject the build and MCP runtime smoke results can be stale or blocked by an older in-editor module.

Recommended smoke order after bridge or Blueprint authoring C++ changes:

1. `python Python/scripts/node/test_mcp_bridge_dispatch.py`
2. `python Python/scripts/node/test_bp_graph_authoring_validation.py`
3. `python Python/scripts/node/test_bp_control_flow_expression_authoring.py`
4. `python Python/scripts/node/test_bp_typed_control_struct_authoring.py`
5. `python Python/scripts/node/test_bp_enum_advanced_control_authoring.py`
6. `python Python/scripts/node/test_bp_object_call_semantics_authoring.py`
7. `python Python/scripts/node/test_bp_loop_collection_authoring.py`
8. `python Python/scripts/node/test_bp_collection_literal_authoring.py`
9. `python Python/scripts/node/test_bp_data_function_authoring.py`

## Data & Function Authoring

Section 2 commands add Blueprint data declarations that are needed when converting C++ members and function signatures into Blueprint assets.

Supported type descriptors:

- `bool`, `int`, `int64`, `float`, `double`, `string`, `name`, `text`
- `vector`, `rotator`, `transform`
- `object` or `class` with `type_object`, for example `Actor` or `/Script/Engine.Actor`
- `enum` or `byte_enum` with `type_object`, `enum_type`, or `enum_path`, for example `/Script/Engine.ECollisionEnabled`
- `is_array=true` for array variables or pins

In UE 5.7, `float` and `double` are authored as `PC_Real` pins with `PC_Float` or `PC_Double` subcategories.

Default values are serialized through the K2 schema where possible. Vector defaults accept `[x, y, z]` or `{ "x": 1, "y": 2, "z": 3 }`; rotator defaults accept `[pitch, yaw, roll]` or matching object keys; transform defaults accept `location` or `translation`, `rotation`, and `scale` or `scale3d`.

### add_blueprint_function_parameter

Add an input or output pin to a Blueprint function graph.

**Parameters:**
- `blueprint_name` (string) - Blueprint name or path
- `parameter_name` (string) - Parameter pin name
- `parameter_type` (string) - Type descriptor
- `direction` (string, optional) - `input` or `output`, default `input`
- `default_value` (any, optional) - Default value for the user-defined pin
- `type_object` (string, optional) - Class path/name for `object` or `class`
- `is_array` (boolean, optional) - Create an array pin
- graph selector fields - Function graph target, usually `graph_name`/`graph_id` plus `graph_type="function"`

### add_blueprint_local_variable

Add a function-scoped local variable declaration.

**Parameters:**
- `blueprint_name` (string) - Blueprint name or path
- `variable_name` (string) - Local variable name
- `variable_type` (string) - Type descriptor
- `default_value` (any, optional) - Local variable default value
- `category` (string, optional) - Variable category
- `tooltip` (string, optional) - Variable tooltip metadata
- `type_object` (string, optional) - Class path/name for `object` or `class`
- `is_array` (boolean, optional) - Create an array local variable
- graph selector fields - Must resolve to a function graph

After declaring a local variable, `add_blueprint_variable_get_node` and `add_blueprint_variable_set_node` can target that same function graph and resolve the local variable by name when no member variable with that name exists.

### add_blueprint_variable_get_node

Add a variable getter node to a Blueprint graph.

**Parameters:**
- `blueprint_name` (string) - Blueprint name or path
- `variable_name` (string) - Variable or component member name
- `node_position` (array or string, optional) - `[X, Y]` position in the graph. String forms such as `"120, 240"` are accepted by the Unreal bridge.
- `target_class` (string, optional) - Class path/name for an external object member variable, for example a component Blueprint generated class. When omitted, the command resolves member or local variables on `blueprint_name`.
- graph selector fields - Optional target graph selector

**External member example:**
```json
{
  "command": "add_blueprint_variable_get_node",
  "params": {
    "blueprint_name": "/Game/Field/BP_Field",
    "variable_name": "Radius",
    "target_class": "/Game/Field/BPC_InteractionSource.BPC_InteractionSource_C",
    "node_position": [600, 240]
  }
}
```

## Node Tools

### add_blueprint_event_node

Add an event node to a Blueprint's event graph.

**Parameters:**
- `blueprint_name` (string) - Name of the target Blueprint
- `event_type` (string) - Type of event (BeginPlay, Tick, etc.)
- `node_position` (array, optional) - [X, Y] position in the graph (default: [0, 0])

**Returns:**
- Response containing the node ID and success status

**Example:**
```json
{
  "command": "add_blueprint_event_node",
  "params": {
    "blueprint_name": "MyActor",
    "event_type": "BeginPlay",
    "node_position": [100, 100]
  }
}
```

### add_blueprint_input_action_node

Add an input action event node to a Blueprint's event graph.

**Parameters:**
- `blueprint_name` (string) - Name of the target Blueprint
- `action_name` (string) - Name of the input action to respond to
- `node_position` (array, optional) - [X, Y] position in the graph (default: [0, 0])

**Returns:**
- Response containing the node ID and success status

**Example:**
```json
{
  "command": "add_blueprint_input_action_node",
  "params": {
    "blueprint_name": "MyActor",
    "action_name": "Jump",
    "node_position": [200, 200]
  }
}
```

### add_blueprint_function_node

Add a function call node to a Blueprint's event graph.

**Parameters:**
- `blueprint_name` (string) - Name of the target Blueprint
- `target` (string) - Target object for the function (component name or self)
- `function_name` (string) - Name of the function to call
- `params` (object, optional) - Parameters to set on the function node
- `node_position` (array, optional) - [X, Y] position in the graph (default: [0, 0])

**Returns:**
- Response containing the node ID and success status

**Example:**
```json
{
  "command": "add_blueprint_function_node",
  "params": {
    "blueprint_name": "MyActor",
    "target": "Mesh",
    "function_name": "SetRelativeLocation",
    "params": {
      "NewLocation": [0, 0, 100]
    },
    "node_position": [300, 300]
  }
}
```

### add_blueprint_call_function_node

Add a validated Blueprint function call node. Prefer this command when converting C++ calls into Blueprint graphs.

**Parameters:**
- `blueprint_name` (string) - Name or path of the target Blueprint
- `function_class` (string) - Owner class path/name. Prefer fully qualified native paths such as `/Script/Engine.Actor`
- `function_name` (string) - UFunction name to call
- `param_defaults` (object, optional) - Input pin defaults validated through the K2 schema
- `node_position` (array, optional) - [X, Y] position in the graph
- `allow_latent` (boolean, optional) - Allow latent functions, default `false`
- `allow_editor_only` (boolean, optional) - Allow editor-only functions, default `false`
- `allow_wildcard` (boolean, optional) - Allow wildcard/custom thunk functions, default `false`
- `allow_deprecated` (boolean, optional) - Allow deprecated functions, default `false`
- `allow_internal` (boolean, optional) - Allow Blueprint-internal functions, default `false`

This command rejects non-Blueprint callable/pure functions, latent functions, editor-only functions, deprecated functions, internal-use functions, and wildcard/custom thunk functions by default. It returns full node and pin metadata, so callers can connect explicit object/self/component target pins with `connect_blueprint_nodes`.

Function parameter defaults are applied with the same K2 schema validation path used by `set_blueprint_pin_default`; invalid defaults fail before compile validation and remove the newly created call node.

Current stable scope:
- Static Blueprint function library calls, including class/object defaults where K2 accepts them
- Self/object/component member calls through an explicit target pin connection after node creation
- Pure and impure non-latent calls

Deferred:
- Automatic `UK2Node_CallFunctionOnMember` component call expansion
- `UK2Node_CallArrayFunction` and wildcard container inference
- Latent function graph-policy authoring

### connect_blueprint_nodes

Connect two nodes in a Blueprint's event graph.

**Parameters:**
- `blueprint_name` (string) - Name of the target Blueprint
- `source_node_id` (string) - ID of the source node
- `source_pin` (string) - Name of the output pin on the source node
- `target_node_id` (string) - ID of the target node
- `target_pin` (string) - Name of the input pin on the target node

**Returns:**
- Response indicating success or failure

**Example:**
```json
{
  "command": "connect_blueprint_nodes",
  "params": {
    "blueprint_name": "MyActor",
    "source_node_id": "node_1",
    "source_pin": "exec",
    "target_node_id": "node_2",
    "target_pin": "exec"
  }
}
```

### delete_blueprint_node

Delete one Blueprint graph node by GUID with explicit safety guards.

**Parameters:**
- `blueprint_name` (string) - Name or asset path of the target Blueprint
- `node_id` (string) - Node GUID to delete
- `graph_name` / `graph_id` / `graph_type` (optional) - Target graph selector
- `expected_node_name` (string, optional) - Exact node object name guard
- `expected_node_class` (string, optional) - Node class guard, for example `K2Node_VariableSet`
- `expected_title_contains` (string, optional) - Node title substring guard
- `allow_non_exec_linked_delete` (boolean, optional) - Allow deletion when data pins are linked
- `allow_exec_linked_delete` (boolean, optional) - Allow deletion when execution pins are linked
- `allow_any_linked_delete` (boolean, optional) - Bypass link-type guards

By default the command refuses any linked node. Structural Event/Entry/Return nodes are always refused; this command is for ordinary graph cleanup nodes only. For cleanup of an unexecuted data-linked node, pass `allow_non_exec_linked_delete=true` and keep an `expected_node_class` or title guard.

### add_blueprint_variable

Add a variable to a Blueprint.

**Parameters:**
- `blueprint_name` (string) - Name of the target Blueprint
- `variable_name` (string) - Name of the variable
- `variable_type` (string) - Type of the variable (Boolean, Integer, Float, Vector, etc.)
- `default_value` (any, optional) - Default value for the variable
- `is_exposed` (boolean, optional) - Whether to expose the variable to the editor (default: false)
- `category` (string, optional) - Variable category
- `tooltip` (string, optional) - Variable tooltip metadata
- `friendly_name` (string, optional) - Editor display name
- `type_object` (string, optional) - Class path/name for `object` or `class`
- `is_array` (boolean, optional) - Create an array variable
- `metadata` (object, optional) - String/number/bool metadata values

**Returns:**
- Response indicating success or failure

**Example:**
```json
{
  "command": "add_blueprint_variable",
  "params": {
    "blueprint_name": "MyActor",
    "variable_name": "Health",
    "variable_type": "Float",
    "default_value": 100.0,
    "is_exposed": true
  }
}
```

### set_blueprint_variable_metadata

Set metadata or editor exposure flags on an existing Blueprint member variable.

**Parameters:**
- `blueprint_name` (string) - Blueprint name or path
- `variable_name` (string) - Existing Blueprint member variable name
- `metadata` (object, optional) - String/number/bool metadata values
- `is_editable` (boolean, optional) - Alias for making the variable editable on instances
- `instance_editable` (boolean, optional) - Explicit Instance Editable flag. `true` sets `CPF_Edit` and clears `CPF_DisableEditOnInstance`
- `expose_on_spawn` (boolean, optional) - Set or clear Expose on Spawn metadata and property flag

At least one of `metadata`, `is_editable`, `instance_editable`, or `expose_on_spawn` must be provided. This command is useful when a Blueprint variable already exists but needs to become editable on placed actors or component templates.

**Example:**
```json
{
  "command": "set_blueprint_variable_metadata",
  "params": {
    "blueprint_name": "/Game/Field/BP_Field",
    "variable_name": "FollowTarget",
    "instance_editable": true
  }
}
```

### add_blueprint_event_dispatcher

Add an Event Dispatcher declaration to a Blueprint. This creates the multicast delegate variable and its delegate signature graph. Use `add_blueprint_event_dispatcher_call_node` to broadcast the dispatcher, `add_blueprint_event_dispatcher_bind_node` with `add_blueprint_custom_event_node` to bind it, and the unbind, clear, or assign node tools to manage its lifecycle.

**Parameters:**
- `blueprint_name` (string) - Name of the target Blueprint
- `dispatcher_name` (string) - Name of the Event Dispatcher
- `inputs` (array, optional) - Signature inputs; each item accepts `name` or `parameter_name`, plus `type` or `parameter_type`
- `category` (string, optional) - Event Dispatcher category
- `tooltip` (string, optional) - Tooltip metadata
- `friendly_name` (string, optional) - Editor display name

**Returns:**
- Response containing the dispatcher name, multicast delegate pin type, signature graph metadata, and created inputs

**Example:**
```json
{
  "command": "add_blueprint_event_dispatcher",
  "params": {
    "blueprint_name": "MyActor",
    "dispatcher_name": "OnScoreChanged",
    "inputs": [
      {"name": "Score", "type": "int"}
    ],
    "category": "Gameplay"
  }
}
```

### add_blueprint_event_dispatcher_call_node

Add a call node for an existing Blueprint Event Dispatcher. This broadcasts the dispatcher in an event or function graph. Use `set_blueprint_pin_default` or `connect_blueprint_nodes` to provide signature inputs.

**Parameters:**
- `blueprint_name` (string) - Name of the target Blueprint
- `dispatcher_name` (string) - Name of the Event Dispatcher to call
- `node_position` (array, optional) - [X, Y] position in the graph
- `graph_name` (string, optional) - Target graph name
- `graph_id` (string, optional) - Target graph id
- `graph_type` (string, optional) - Target graph type such as `event` or `function`
- `create_graph_if_missing` (boolean, optional) - Create the target graph when supported

**Returns:**
- Response containing the node id, pins, dispatcher name, signature function, and graph metadata

**Example:**
```json
{
  "command": "add_blueprint_event_dispatcher_call_node",
  "params": {
    "blueprint_name": "MyActor",
    "dispatcher_name": "OnScoreChanged",
    "node_position": [600, 0],
    "graph_type": "event"
  }
}
```

### add_blueprint_custom_event_node

Add a custom event node to a Blueprint event graph. When `signature_source_dispatcher_name` is provided, the custom event copies the Event Dispatcher signature and exposes an `OutputDelegate` pin that can be connected into a bind node's `Delegate` pin.

**Parameters:**
- `blueprint_name` (string) - Name of the target Blueprint
- `custom_event_name` (string) - Name of the custom event
- `node_position` (array, optional) - [X, Y] position in the graph
- `signature_source_dispatcher_name` (string, optional) - Event Dispatcher whose signature should be copied
- `call_in_editor` (boolean, optional) - Set the custom event's Call In Editor flag. Existing custom events are reused, and this flag is updated only when provided.
- `graph_name` (string, optional) - Target graph name
- `graph_id` (string, optional) - Target graph id
- `graph_type` (string, optional) - Must resolve to an event graph for custom event nodes
- `create_graph_if_missing` (boolean, optional) - Create the target graph when supported

**Returns:**
- Response containing the node id, pins, custom event name, signature function, and graph metadata

**Example:**
```json
{
  "command": "add_blueprint_custom_event_node",
  "params": {
    "blueprint_name": "MyActor",
    "custom_event_name": "HandleScoreChanged",
    "signature_source_dispatcher_name": "OnScoreChanged",
    "call_in_editor": true,
    "node_position": [600, 300],
    "graph_type": "event"
  }
}
```

### add_blueprint_event_dispatcher_bind_node

Add a bind node for an existing Blueprint Event Dispatcher. Connect a compatible custom event's `OutputDelegate` pin to this node's `Delegate` pin with `connect_blueprint_nodes`.

**Parameters:**
- `blueprint_name` (string) - Name of the target Blueprint
- `dispatcher_name` (string) - Name of the Event Dispatcher to bind
- `node_position` (array, optional) - [X, Y] position in the graph
- `graph_name` (string, optional) - Target graph name
- `graph_id` (string, optional) - Target graph id
- `graph_type` (string, optional) - Target graph type such as `event` or `function`
- `create_graph_if_missing` (boolean, optional) - Create the target graph when supported

**Returns:**
- Response containing the node id, pins, dispatcher name, signature function, and graph metadata

**Example:**
```json
{
  "command": "add_blueprint_event_dispatcher_bind_node",
  "params": {
    "blueprint_name": "MyActor",
    "dispatcher_name": "OnScoreChanged",
    "node_position": [360, 0],
    "graph_type": "event"
  }
}
```

### add_blueprint_event_dispatcher_unbind_node

Add an unbind node for an existing Blueprint Event Dispatcher. Connect the same compatible custom event `OutputDelegate` pin used for binding to this node's `Delegate` pin.

**Parameters:**
- `blueprint_name` (string) - Name of the target Blueprint
- `dispatcher_name` (string) - Name of the Event Dispatcher to unbind
- `node_position` (array, optional) - [X, Y] position in the graph
- `graph_name` (string, optional) - Target graph name
- `graph_id` (string, optional) - Target graph id
- `graph_type` (string, optional) - Target graph type such as `event` or `function`
- `create_graph_if_missing` (boolean, optional) - Create the target graph when supported

**Returns:**
- Response containing the node id, pins, dispatcher name, signature function, and graph metadata

**Example:**
```json
{
  "command": "add_blueprint_event_dispatcher_unbind_node",
  "params": {
    "blueprint_name": "MyActor",
    "dispatcher_name": "OnScoreChanged",
    "node_position": [820, 0],
    "graph_type": "event"
  }
}
```

### add_blueprint_event_dispatcher_clear_node

Add a clear node for an existing Blueprint Event Dispatcher. This removes all events bound to the dispatcher for the target context and does not need a `Delegate` pin connection.

**Parameters:**
- `blueprint_name` (string) - Name of the target Blueprint
- `dispatcher_name` (string) - Name of the Event Dispatcher to clear
- `node_position` (array, optional) - [X, Y] position in the graph
- `graph_name` (string, optional) - Target graph name
- `graph_id` (string, optional) - Target graph id
- `graph_type` (string, optional) - Target graph type such as `event` or `function`
- `create_graph_if_missing` (boolean, optional) - Create the target graph when supported

**Returns:**
- Response containing the node id, pins, dispatcher name, signature function, and graph metadata

**Example:**
```json
{
  "command": "add_blueprint_event_dispatcher_clear_node",
  "params": {
    "blueprint_name": "MyActor",
    "dispatcher_name": "OnScoreChanged",
    "node_position": [1060, 0],
    "graph_type": "event"
  }
}
```

### add_blueprint_event_dispatcher_assign_node

Add an assign node for an existing Blueprint Event Dispatcher. Assign nodes require an event graph and automatically create a signature-compatible custom event wired into the node's `Delegate` pin.

**Parameters:**
- `blueprint_name` (string) - Name of the target Blueprint
- `dispatcher_name` (string) - Name of the Event Dispatcher to assign
- `node_position` (array, optional) - [X, Y] position in the graph
- `graph_name` (string, optional) - Target graph name
- `graph_id` (string, optional) - Target graph id
- `graph_type` (string, optional) - Must resolve to an event graph
- `create_graph_if_missing` (boolean, optional) - Create the target graph when supported

**Returns:**
- Response containing the node id, pins, dispatcher name, signature function, and graph metadata

**Example:**
```json
{
  "command": "add_blueprint_event_dispatcher_assign_node",
  "params": {
    "blueprint_name": "MyActor",
    "dispatcher_name": "OnScoreChanged",
    "node_position": [360, 220],
    "graph_type": "event"
  }
}
```

### create_input_mapping

Create an input mapping for the project.

**Parameters:**
- `action_name` (string) - Name of the input action
- `key` (string) - Key to bind (SpaceBar, LeftMouseButton, etc.)
- `input_type` (string, optional) - Type of input mapping (Action or Axis, default: "Action")

**Returns:**
- Response indicating success or failure

**Example:**
```json
{
  "command": "create_input_mapping",
  "params": {
    "action_name": "Jump",
    "key": "SpaceBar",
    "input_type": "Action"
  }
}
```

### add_blueprint_get_self_component_reference

Add a node that gets a reference to a component owned by the current Blueprint.

**Parameters:**
- `blueprint_name` (string) - Name of the target Blueprint
- `component_name` (string) - Name of the component to get a reference to
- `node_position` (array, optional) - [X, Y] position in the graph (default: [0, 0])

**Returns:**
- Response containing the node ID and success status

**Example:**
```json
{
  "command": "add_blueprint_get_self_component_reference",
  "params": {
    "blueprint_name": "MyActor",
    "component_name": "Mesh",
    "node_position": [400, 400]
  }
}
```

### add_blueprint_self_reference

Add a 'Get Self' node to a Blueprint's event graph.

**Parameters:**
- `blueprint_name` (string) - Name of the target Blueprint
- `node_position` (array, optional) - [X, Y] position in the graph (default: [0, 0])

**Returns:**
- Response containing the node ID and success status

**Example:**
```json
{
  "command": "add_blueprint_self_reference",
  "params": {
    "blueprint_name": "MyActor",
    "node_position": [500, 500]
  }
}
```

### find_blueprint_nodes

Find nodes in a Blueprint's event graph.

**Parameters:**
- `blueprint_name` (string) - Name of the target Blueprint
- `node_type` (string, optional) - Type of node to find (Event, Function, Variable, etc.)
- `event_type` (string, optional) - Specific event type to find (BeginPlay, Tick, etc.)

**Returns:**
- Response containing array of found node IDs and success status

**Example:**
```json
{
  "command": "find_blueprint_nodes",
  "params": {
    "blueprint_name": "MyActor",
    "node_type": "Event",
    "event_type": "BeginPlay"
  }
}
```

## Error Handling

All command responses include a "success" field indicating whether the operation succeeded, and an optional "message" field with details in case of failure.

```json
{
  "success": false,
  "message": "Blueprint 'MyActor' not found in the project",
  "command": "add_blueprint_event_node"
}
```

## Type Reference

### Node Types

Common node types for the `find_blueprint_nodes` command:

- `Event` - Event nodes (BeginPlay, Tick, etc.)
- `Function` - Function call nodes
- `Variable` - Variable nodes
- `Component` - Component reference nodes
- `Self` - Self reference nodes

### Variable Types

Common variable types for the `add_blueprint_variable` command:

- `Boolean` - True/false values
- `Integer` - Whole numbers
- `Float` - Decimal numbers
- `Vector` - 3D vector values
- `String` - Text values
- `Object Reference` - References to other objects
- `Actor Reference` - References to actors
- `Component Reference` - References to components
