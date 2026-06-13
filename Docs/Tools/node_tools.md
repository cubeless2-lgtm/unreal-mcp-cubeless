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

### list_blueprint_graphs

List graphs in a Blueprint and return stable graph IDs.

**Parameters:**
- `blueprint_name` (string) - Blueprint name or path
- `graph_type` (string, optional) - Filter by graph type

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
