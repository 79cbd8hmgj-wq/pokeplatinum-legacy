# G4 Runtime QA — melonDS + NDS Disassembly Toolkit

Status: runtime harness added; source/build-only G4 validation is no longer treated as sufficient.

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

`make debug` produces the project debug metadata including
`build/overlay.map`, which `runtime_g4_probe.py` uses to resolve source
symbols to runtime addresses. If a symbol is absent or ambiguous, pass an
explicit override:

```bash
--address AreaLightManager_New=0x02......
```

## Scenario workflow

Place the player immediately before entering/reloading the target area, then run
the matching scenario. Keep the emulator running; the harness owns one GDB
session and chains temporary breakpoints in execution order.

```bash
python tools/visual_overhaul/runtime_g4_probe.py eterna
python tools/visual_overhaul/runtime_g4_probe.py snow
python tools/visual_overhaul/runtime_g4_probe.py distortion
python tools/visual_overhaul/runtime_g4_probe.py spear
python tools/visual_overhaul/runtime_g4_probe.py lakes
python tools/visual_overhaul/runtime_g4_probe.py turnback
python tools/visual_overhaul/runtime_g4_probe.py galactic
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

Every scenario proves at runtime that `AreaLightManager_New()` receives the
expected archive ID, then confirms that the light manager reaches its steady
update path.

Eterna additionally proves:

- `ForestAmbienceRenderer_New()` is selected during field-effect initialization
- `ForestAmbienceRenderer_Task()` executes after map initialization

Spear Pillar, Distortion World, and the Mt. Coronet control additionally prove:

- `FieldMap_ApplySpecialAreaFog()` executes
- that path reaches `FogManager_ApplyParameters()` before continuing

This is stronger than checking only that the modified source exists.

## Static contract gate

Run this in ordinary CI/source validation:

```bash
python tools/visual_overhaul/validate_area_light_contract.py
```

It verifies that:

- `lighting_sets.order` is contiguous and index-stable
- `AREA_LIGHT_SET_COUNT` matches the real archive member count
- every `area_data_*.json` lighting reference is inside that range

## Remaining visual-only check

These runtime tests prove path selection, archive IDs, fog activation, and
forest-renderer execution. They do not judge whether a palette is aesthetically
too saturated, too dark, or otherwise visually undesirable.

A short rendered-frame check in melonDS/Delta remains useful for that final
subjective judgment, but it is no longer the primary G4 correctness gate.
