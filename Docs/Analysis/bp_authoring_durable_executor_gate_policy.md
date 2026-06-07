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

## Decision

Section 46-48 improves durable safety visibility only. It does not enable
durable Blueprint creation or saving.
