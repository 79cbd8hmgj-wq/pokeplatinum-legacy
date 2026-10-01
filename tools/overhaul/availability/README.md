# Availability implementation tooling

Implements `docs/overhaul/AVAILABILITY_ARCHITECTURE.md` as guarded, machine-verifiable data.
Pinned base commit: `cb420c0d` (`common.BASE_COMMIT`).

## Pipeline

```
availability_families.json   build_families.py          (matrix rows x live evolution components)
placement plan               plan_e0_e1.py plan_m1_p0.py plan_water.py  (authoring aid; levels/guards read from the base commit)
wild_encounters.json         build_wild_manifest.py
special_systems.json         build_special_manifest.py  (dual-slot / Radar / swarm / Honey / Garden / Marsh + fixed fallbacks)
encounter_zones.json         build_zones.py
validate_availability.py     --state manifest   (pre-apply proof)   |  --state live (post-apply proof)
apply_wild_encounters.py     --bands E0,E1 --groups land,water,special [--dry-run]   (before-value guards, fail closed, idempotent)
semantic_diff.py             live JSON vs manifest target (+ scope audit)
verify_built_encounters.py   --build <meson build dir>   (decodes the compiled encounter binaries)
test_validators.py           mutation tests proving the validators fail when they should
```

Regenerate everything: `for s in build_families build_wild_manifest build_special_manifest build_zones; do python3 tools/overhaul/availability/$s.py; done`

Dev note: set `AVAIL_IMPL_DIR` to point the tools at a different manifest directory (used by `test_validators.py`).
The manifests are the canonical data; the `plan_*.py` files are the authoring source they are generated from.
