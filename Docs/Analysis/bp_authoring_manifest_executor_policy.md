# BP Authoring Manifest Executor Policy

This policy defines the Section 40 execution layer between a structured
Blueprint authoring manifest and live UnrealMCP commands.

## Required Flow

1. A user request must first pass through the planner and Section 12-39 job
   manifest contract.
2. The live runner must build a Section 40 executor policy for every manifest.
3. Only manifests with `can_execute=true` may reach temporary live authoring.
4. The executor is temporary-scope only: output must stay under
   `/Game/_MCP_Temp`.
5. Durable authoring, save, overwrite, rename, and delete behavior remains
   disabled.
6. The executor report must expose its version, command plan, blocked reasons,
   section results, structural validation results, and failure diagnostics.
7. Failure diagnostics must use the Section 41 category/replay-safety schema
   before a failed run is considered reviewable.
8. Section 42-45 capability coverage must report whether typed defaults, graph
   layout/dataflow, function graph execution, and dispatcher lifecycle execution
   have the required validation evidence.
9. Section 46-48 durable gate coverage must prove durable requests are limited
   to read-only live preflight and expose zero save/delete/rename/authoring
   command allowance.

## Execution Boundary

The Section 40 executor may run only planner-safe, executable, Actor-parent
temporary manifests. It must block:

- non-safe manifests
- non-executable manifests
- durable authoring requests
- parent classes outside the current allowlist
- temporary package paths outside `/Game/_MCP_Temp`
- unknown live commands
- save/delete/rename commands
- any compile request with `save=true`
- any durable gate that unexpectedly enables saved asset authoring, save,
  delete, rename, overwrite, or replacement behavior

## Validation

- Offline tests must prove the executor policy count: 12 executable temporary
  manifests and 7 blocked manifests for the default request set.
- Offline tests must prove the durable gate count: 1 durable requested manifest,
  1 read-only live preflight allowed manifest, and 0 durable executor/save/delete
  command allowance.
- The planner-driven live smoke must report the executor version and executor
  executable count.
- The planner-driven live smoke may perform only the read-only durable
  asset-exists preflight and must report that no durable authoring or
  save/delete command was attempted.
- The live smoke still owns the Unreal bridge adapter, cleanup, and temp asset
  inspection, but section orchestration must go through
  `bp_authoring_manifest_executor.py`.
- Generated assets must be deleted unless explicitly kept for debugging.

## Decision

Section 40 does not enable durable asset authoring. It only makes temporary safe
manifest execution explicit, inspectable, and reusable before later durable
gates are considered.
