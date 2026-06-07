# BP Authoring Planner Policy

This policy defines how UnrealMCP should classify a user request before
authoring Blueprint assets or graph nodes.

## Status Priority

1. `blocked_until_reinforced`
2. `requires_review`
3. `safe_to_author`

If one request contains both safe and blocked work, the blocked status wins. The
safe part may be split into a smaller request only after the blocked part is
removed or explicitly deferred.

## Safe Now

- Blueprint shell or simple Actor/Component Blueprint creation.
- Existing component composition and exposed property/default setup.
- Ordinary reflected function calls and simple graph flow.
- Blueprint Event Dispatcher declaration, call, bind, assign, unbind, and clear
  lifecycle nodes.
- Enhanced Input graph glue against existing input assets.

## Requires Review

- Latent function calls and continuation ordering.
- UMG widget-specific event binding.
- Broad "convert this C++" requests that have not been split into safe graph
  glue versus native behavior.

## Blocked Until Reinforced

- Native or arbitrary delegate lifecycle authoring.
- Generic delegate requests that are not explicitly Blueprint Event Dispatcher
  lifecycle work.
- Async action proxy callback exec pins and cancellation/cleanup topology.
- Gameplay Ability System internals, AbilityTasks, and prediction flow.
- Replication, RPC, ReplicationGraph, authority policy, and networking state.
- CommonUI tree/layer/activation policy.
- Animation Blueprint graphs and state machines.
- Custom K2 nodes and editor graph expansion behavior.
- GameFeature or Experience architecture.
- Slate/editor-only C++ behavior.

## Validation Rule

Every safe authoring plan must include compile validation and graph re-read
steps. Unknown requests default to `requires_review`, not `safe_to_author`.

