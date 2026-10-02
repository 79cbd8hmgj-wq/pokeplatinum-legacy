#!/usr/bin/env python3
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
BEFORE = ROOT / "docs/visual_overhaul/review/g4a_eterna_before"
AFTER = ROOT / "docs/visual_overhaul/review/g4a_eterna_dump/map"
REPORT = ROOT / "docs/visual_overhaul/G4A_ETERNA_TEXTURE_RECOLOR_REPORT.md"

TARGETS = {
    "ckado", "enccriff", "fenter", "grass", "hage", "lgreen", "lgreenp",
    "nectgrass", "nhana", "nsandp", "rhana", "sandset", "shana", "tshadow",
}

before_pngs = {p.name: p for p in BEFORE.glob("*.png")}
after_pngs = {p.name: p for p in AFTER.glob("*.png")}
if before_pngs.keys() != after_pngs.keys():
    raise SystemExit("texture filename set changed")

index_failures = []
dimension_failures = []
changed_visuals = []
for name in sorted(before_pngs):
    with Image.open(before_pngs[name]) as a, Image.open(after_pngs[name]) as b:
        if a.size != b.size:
            dimension_failures.append(name)
            continue
        if a.mode == "P" and b.mode == "P":
            if list(a.getdata()) != list(b.getdata()):
                index_failures.append(name)
        if a.convert("RGBA").tobytes() != b.convert("RGBA").tobytes():
            changed_visuals.append(Path(name).stem)

before_pals = {p.stem: p.read_text() for p in BEFORE.glob("*.pal")}
after_pals = {p.stem: p.read_text() for p in AFTER.glob("*.pal")}
if before_pals.keys() != after_pals.keys():
    raise SystemExit("palette filename set changed")

changed_pals = sorted(k for k in before_pals if before_pals[k] != after_pals[k])
unexpected = sorted(set(changed_pals) - TARGETS)
if dimension_failures or index_failures or unexpected:
    raise SystemExit(
        f"validation failed dimensions={dimension_failures} indices={index_failures} unexpected_palettes={unexpected}"
    )
if len(changed_pals) < 8:
    raise SystemExit(f"only {len(changed_pals)} target palettes changed")

lines = [
    "# G4A Eterna Forest Texture Recolor Report",
    "",
    "Status: source-applied; runtime inspection pending.",
    "",
    "The dedicated Eterna Forest texture bank was palette-graded without changing texture geometry or texel indices.",
    "",
    f"- Texture files validated: **{len(before_pngs)}**",
    f"- Dimensions changed: **{len(dimension_failures)}**",
    f"- Indexed texel maps changed: **{len(index_failures)}**",
    f"- Palettes changed: **{len(changed_pals)}**",
    f"- Rendered texture images affected: **{len(changed_visuals)}**",
    "",
    "## Changed palettes",
    "",
]
lines += [f"- {name}" for name in changed_pals]
lines += [
    "",
    "## Intent",
    "",
    "Only green-dominant colors in selected ground/underbrush palettes were adjusted.",
    "The grade reduces the original fluorescent saturation/brightness while retaining Platinum's shapes, texture indices, transparency, map geometry, collision, and animation contracts.",
    "",
    "Tree canopy/trunk palettes, water, rock, bridge, building, and unrelated beach/sea palettes were deliberately left unchanged in this batch.",
]
REPORT.write_text("\n".join(lines) + "\n")
print(f"Validated {len(before_pngs)} textures; {len(changed_pals)} palettes changed.")
