# BP Authoring Durable Executor Gate Policy

This policy captures the Section 46-48 durable authoring boundary.

## Section 46 - Durable Gate Matrix

Durable Blueprint requests may be classified and inspected, but they must not
be executed by the temporary manifest executor. The executor policy must report
a durable gate for every manifest and prove these counts for the default
request set:

- durable requested manifests: `1`
- read-only live preflight allowed: `1`
- durable executor enabled: `0`
- durable executor executable: `0`
- allowed durable authoring commands: `0`
- save/delete/rename commands allowed: `0`
- preflight pass: `0`

If any durable save, delete, rename, overwrite, or authoring command becomes
allowed before a separate durable executor is explicitly enabled, the temporary
executor policy must block the manifest with `durable_gate_opened`.

## Section 47 - Explicit Durable Enable Contract

The durable executor remains disabled by default. A future durable executor
must prove all of these before any saved asset can be created:

- explicit durable executor enable flag
- target package allowlist
- live read-only asset-exists result promoted into the save gate
- overwrite-or-rename decision
- rollback policy that protects preexisting assets
- compile/save validation for durable-only manifests
- executor-created asset ownership marker

Until those checks pass, durable manifests stay non-executable records.

## Section 48 - Limited Live Preflight

The only live action currently allowed for a durable request is a read-only
`unreal.EditorAssetLibrary.does_asset_exist` check against the target asset.
The live preflight result must prove:

- `read_only=true`
- `authoring_attempted=false`
- `save_or_delete_attempted=false`
- the asset-exists check was performed
- `preflight_pass=false`

The planner-driven live smoke may run this read-only preflight while still
blocking durable authoring. It must fail if the preflight result attempts
authoring, save, delete, rename, or reports an unexpected manifest id.

## Section 51 - Durable Authoring Enable Contract

Section 51 still does not enable durable Blueprint creation or saving. It
separates the preconditions a later durable executor must satisfy before it can
open:

- target package allowlist
- exactly one overwrite-or-rename decision
- rollback readiness that protects preexisting assets
- executor-created asset ownership marker policy

For the default request set, the release boundary must prove:

- durable enable contract requests: `1`
- enable contract satisfied: `0`
- durable executor may open: `0`
- durable authoring allowed: `0`
- forbidden command allowance for `save=true`, `save_asset`, `delete_asset`, and `rename_asset`: `0`
- target allowlist gate passed: `1`
- overwrite/rename decision gate passed: `0`
- rollback readiness gate passed: `0`
- ownership marker gate passed: `0`

The contract is intentionally stricter than the current read-only preflight.
Even if all Section 51 gates are satisfied in a future offline contract, this
section alone still reports `durable_executor_may_open=false`; a later explicit
durable release must separately enable and verify live durable authoring.

## Section 52 - Rollback Ownership Marker Contract

Section 52 defines the ownership marker a future durable executor must record
before rollback/delete can even be considered. The marker must bind the created
asset to:

- marker schema and namespace
- executor id, durable plan id, and run id
- target asset path and created asset path
- proof that the preflight asset-exists result was `false`

The release boundary must prove:

- durable ownership marker requests: `1`
- ownership marker policy ready: `1`
- delete without marker allowed: `0`
- delete preexisting asset allowed: `0`

This section only authorizes a future rollback decision at contract level. It
still reports `delete_allowed_now=false` and does not run live delete, save,
rename, or overwrite commands.

## Section 53 - Durable Executor Dry-Run Plan

Section 53 records a future durable executor plan without allowing any live
command execution. The plan may list report-only steps for:

- read-only target preflight
- conflict policy review
- ownership marker preparation
- compile validation draft
- save gate review
- rollback authorization draft

The release boundary must prove:

- durable dry-run plan requests: `1`
- dry-run plan created: `1`
- dry-run plan valid: `1`
- durable executor may execute: `0`
- live command count: `0`
- forbidden command allowance: `0`

The dry-run `execution_command_plan` must remain empty. A dry-run plan is
evidence for review only, not permission to create, save, delete, rename, or
overwrite assets.

## Section 54 - Durable Save Validation Simulator

Section 54 evaluates durable save prerequisites without running a save. The
simulator checks:

- target package allowlist
- read-only asset-exists result availability
- overwrite-or-rename decision
- ownership marker policy
- rollback readiness
- dry-run plan validity
- enable contract satisfaction
- compile/save validation enablement
- explicit durable executor enable flag

The release boundary must prove:

- durable save simulation requests: `1`
- simulation evaluated: `1`
- future save conditions satisfied: `0`
- `save=true` allowed: `0`
- `save_asset` allowed: `0`
- compile-save command allowed: `0`
- live command count: `0`

The simulator may explain why a future save is blocked, but it must not promote
that explanation into live durable execution.

## Decision

Section 46-48 improves durable safety visibility, Section 51 separates the
future durable enable gates, and Section 52 defines the ownership marker needed
for future rollback. Section 53 adds a no-command dry-run plan. Section 54 adds
a no-command save validation simulator. These sections do not enable durable
Blueprint creation, saving, delete, or rename.
