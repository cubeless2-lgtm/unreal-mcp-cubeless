# BP Authoring Executor Capability Policy

This policy captures the Section 42-45 executor capability matrix.

## Section 42 - Typed Defaults

Typed defaults are executor-ready only when the manifest contains readback
evidence for the authored data:

- variables must have `assert_variable_default`
- components must have `assert_component_default`
- component properties must have `assert_component_property`

## Section 43 - Graph Layout And Dataflow

Graph execution is executor-ready only when authored graph intent is validated
with structural assertions:

- node placement uses `assert_node_layout`
- spacing uses `assert_layout_spacing`
- execution/data links use `assert_pin_link`

## Section 44 - Function Graph Executor

Function graph manifests are executor-ready only when they include executable
function graph steps, graph resolution evidence, node existence assertions, and
compile validation.

## Section 45 - Dispatcher Lifecycle Executor

Dispatcher lifecycle manifests are executor-ready only when declaration, call,
custom event, bind, assign, unbind, and clear commands are all present and the
delegate pins/links are structurally validated.

## Current Default Matrix

For the default Section 40 request set, the executor must report:

- typed defaults: `5` requested, `5` ready
- graph layout/dataflow: `11` requested, `11` ready
- function graph executor: `5` requested, `5` ready
- dispatcher lifecycle executor: `1` requested, `1` ready

Any missing-evidence count blocks the capability from being treated as
production-ready, even if the live smoke happens to compile.
