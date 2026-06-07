# Niagara Tools

These MCP tools add a conservative Niagara MVP on top of the generic
`execute_python` bridge.

The first version is intentionally read-heavy. It can list assets, inspect
reflected system/emitter/script data, list level components, duplicate systems
to `/Game/_MCP_Temp`, and run a best-effort compile/save validation path. It
does not edit Niagara stack modules or graph internals.

## Tools

- `list_niagara_assets(root_path="/Game", include_scripts=false, include_parameter_collections=false)`
  - Lists Niagara Systems and Emitters under a content path.
  - Optional flags include NiagaraScript/module assets and Niagara parameter collections.
- `inspect_niagara_system(system_path, include_emitters=true, include_scripts=true, include_parameters=true)`
  - Loads a Niagara System by package path, object path, or short asset name.
  - Reports system scripts, exposed parameters, emitter handles, renderer hints, and compile data where Python reflection exposes them.
- `list_niagara_components(selected_only=false)`
  - Lists Niagara components in the current editor level.
- `duplicate_niagara_system_to_temp(system_path, temp_folder="/Game/_MCP_Temp", new_name="")`
  - Duplicates a System into disposable MCP temp content for safe experiments.
- `compile_and_save_niagara_system(system_path, save=false)`
  - Attempts the Python-exposed compile/wait/poll path.
  - `save=true` is accepted only for Niagara Systems under `/Game/_MCP_Temp`.

## Safety Rules

- Treat `/Game/_MCP_Temp` Niagara outputs as disposable validation artifacts.
- `duplicate_niagara_system_to_temp` refuses destinations outside `/Game/_MCP_Temp` and may replace only a colliding temp duplicate under that root.
- `compile_and_save_niagara_system(save=true)` refuses original project assets outside `/Game/_MCP_Temp`.
- Do not apply destructive or graph-level Niagara edits to original project assets in the MVP.
- Use `duplicate_niagara_system_to_temp` before experimenting with parameter or emitter changes.
- Trust `compile_and_save_niagara_system` only after checking whether the response says the compile methods were actually exposed and called.
- For production Niagara graph or module stack editing, add a dedicated C++ command layer after the read-only MVP proves which data is needed.

## Current Limits

Niagara exposes some useful fields through Python reflection, but several editor stack APIs are C++-only. If `inspect_niagara_system` returns sparse emitter, parameter, or compile details, that means the current engine build did not expose those internals through Python.

The next safe expansion step is parameter or renderer property editing on `_MCP_Temp` duplicates only, followed by compile validation and preview capture.
