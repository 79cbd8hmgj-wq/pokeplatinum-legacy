# G4 Runtime QA — melonDS + NDS Disassembly Toolkit

Status: objective G4 source/build/static validation complete. The headless live-emulator autowarp harness is retained as experimental, non-blocking QA; rendered emulator review remains the final subjective visual check.

## Why this exists

The G4 source pass introduced dedicated lighting archive members through
`lighting_set_014`, isolated area-data records, forest renderer work, and
special fog paths. A normal Rev 0 / Rev 1 build proves that those resources
compile, but it cannot prove that the runtime archive IDs and branch paths are
valid when a map actually loads.

The first runtime-oriented audit immediately caught one such integration gap:
`AreaLightManager_New()` asserted `archiveID < AREA_LIGHT_SET_COUNT`, while the
source enum still described only IDs 0-9 even though the archive and area data
now use IDs 0-14. Spear Pillar's dedicated G4 lighting set also needed to retain
the special-fog branch formerly associated with the original Spear Pillar set.

The runtime harness and static contract validator are intended to prevent this
class of error from surviving another source-only checkpoint.

## Required external tooling

Use the current NDS Disassembly Toolkit as an installed dependency; do not copy
its runtime implementation into this repository.

```bash
python3.11 -m venv .venv-runtime
source .venv-runtime/bin/activate
python -m pip install -e /path/to/NDS-Disassembly-Toolkit-main
```

melonDS must already be running with:

- ARM9 GDB stub enabled
- port 3333 (or pass `--port`)
- JIT disabled
- the debug Platinum build loaded

The toolkit intentionally attaches to an existing GDB stub; it does not launch
melonDS or load the ROM.

## Build the debug target

```bash
make configure ROM_REVISION=1
make debug ROM_REVISION=1
```

`make debug` produces `debug.nef` plus the overlay/source mapping. Export
the actual runtime symbol addresses from the NEF before running a probe:

```bash
arm-none-eabi-nm -n build/debug.nef > build/runtime_symbols.map
```

`runtime_g4_probe.py` consumes that nm-style symbol map. `overlay.map` is
only the source-file-to-overlay index used by the debugger and does not contain
function addresses. If a symbol is absent or ambiguous, pass an
explicit override:

```bash
--address AreaLightManager_New=0x02......
```

## Scenario workflow

For normal autowarp scenarios, boot the debug ROM to any field state and run
the matching scenario. The harness owns one GDB session, writes the requested
debug warp into persistent ARM9 telemetry, resumes execution in bounded slices,
and validates the resulting visual state from memory.

```bash
python tools/visual_overhaul/runtime_g4_probe.py eterna --request-warp
python tools/visual_overhaul/runtime_g4_probe.py snow --request-warp
python tools/visual_overhaul/runtime_g4_probe.py spear --request-warp
python tools/visual_overhaul/runtime_g4_probe.py lakes --request-warp
python tools/visual_overhaul/runtime_g4_probe.py turnback --request-warp
python tools/visual_overhaul/runtime_g4_probe.py galactic --request-warp

# Distortion World currently remains checkpoint-driven because its field
# lifecycle is specialized; attach from a prepared Distortion World state.
python tools/visual_overhaul/runtime_g4_probe.py distortion
```

Expected area-light IDs:

| Scenario | Runtime lighting ID | Source family |
|---|---:|---|
| Eterna Forest | 10 | dedicated Eterna G4 grade |
| Snowpoint / Route 217 | 11 | dedicated snow G4 grade |
| Distortion World | 9 | Distortion World |
| Spear Pillar | 12 | dedicated Spear Pillar G4 grade |
| Sinnoh lakes | 13 | dedicated lake G4 grade |
| Turnback Cave | 14 | dedicated Turnback Cave grade |
| Team Galactic interiors | 6 | Galactic |

There is also a `coronet-control` scenario for lighting ID 7.

## What is verified

Autowarp scenarios use a debug-build-only telemetry block stored in ARM9 core
memory rather than relying on breakpoints inside overlay 5. This avoids
treating overlay-linked symbol addresses as permanently resident code.

For each autowarp scenario the harness writes a request to
`gG4RuntimeQAControl`, resumes the emulator in bounded slices, and requires:

- the requested map to finish field visual initialization
- the expected area-light archive ID to be observed
- the area-light initialization event bit to be set

Eterna additionally requires telemetry proving:

- the dedicated forest ambience renderer was constructed
- its recurring task executed after initialization

Spear Pillar and the Mt. Coronet control additionally require telemetry proving:

- the special-area fog branch executed
- the fog manager received the complete fog application

Distortion World remains checkpoint-driven for now because its field lifecycle
is specialized. Legacy symbol-breakpoint probing remains available for that
manual/checkpoint path, but it is no longer the primary autowarp mechanism.

This is stronger than checking only that the modified source exists or that the
ROM builds.

## Static contract gate

Run this in ordinary CI/source validation:

```bash
python tools/visual_overhaul/validate_area_light_contract.py
```

It verifies that:

- `lighting_sets.order` is contiguous and index-stable
- `AREA_LIGHT_SET_COUNT` matches the real archive member count
- every `area_data_*.json` lighting reference is inside that range

## CI policy

The Rev 0 / Rev 1 debug-symbol gate and static area-light contract are blocking correctness checks.

The DeSmuME autowarp job is intentionally **non-blocking**. It is useful development instrumentation, but clean-boot field automation has proved less deterministic than the game code it is intended to validate. A failure in that experimental job must not hold later visual passes while the normal builds, symbol resolution, and static contracts are green.

The harness remains in-tree so it can be hardened independently and used to catch additional runtime issues when it succeeds.

## Remaining visual-only check

These runtime tests prove path selection, archive IDs, fog activation, and
forest-renderer execution. They do not judge whether a palette is aesthetically
too saturated, too dark, or otherwise visually undesirable.

A short rendered-frame check in melonDS/Delta remains useful for that final
subjective judgment, but it is no longer the primary G4 correctness gate.
