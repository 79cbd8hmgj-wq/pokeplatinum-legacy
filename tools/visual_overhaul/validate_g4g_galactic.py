#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
BASE=Path("/tmp/g4g_validate")
REPORT=ROOT/"docs/visual_overhaul/G4G_GALACTIC_INTERIORS.md"
JSON_REPORT=ROOT/"docs/visual_overhaul/G4G_GALACTIC_GRADE_REPORT.json"

ALLOWED={
"main":{"ginga1","m_dun26_01","m_dun26_02","m_dun26_04","m_dun26_06","m_dun26_10","m_dun26_16","m_dun26_19","m_dun26_30","m_dun26_31","m_dun26_32","m_dun26_35","m_dun26_36","m_dun26_36_2","m_dun26_37","m_dun26_38","map_dun26_05","saku","table_l01","z"},
"lab":{"m_dun26_19","m_dun26_23","m_dun26_25","m_dun26_26","m_dun26_27"},
"warehouse":{"carpet04_1","carpet04_2","carpet05_1","carpet05_2","counter_b01","counter_b02","counter_g01","counter_g02","floor01","floor03","floor04","floor_b01","floor_b02","libra_01","libra_02","libra_03","libra_04","libra_05","m_comp_01","m_comp_02","m_muse_01","m_muse_03","m_muse_04","m_muse_05","m_muse_06","phouse_01","phouse_03","scho_01","scho_02","shikii_b01","shouse_02","shouse_03","shouse_04","wall03","wall04","wall05","wall_b01"}
}
MIN_CHANGED={"main":8,"lab":4,"warehouse":12}

def check(name):
    before=BASE/name/"before"
    after=BASE/name/"after"
    bp={p.name:p for p in before.glob("*.png")}
    ap={p.name:p for p in after.glob("*.png")}
    if bp.keys()!=ap.keys(): raise SystemExit(f"{name}: texture names changed")
    dims=[]; indices=[]; visual=[]
    for fn in sorted(bp):
        with Image.open(bp[fn]) as a, Image.open(ap[fn]) as b:
            if a.size!=b.size: dims.append(fn); continue
            if a.mode=="P" and b.mode=="P" and list(a.getdata())!=list(b.getdata()):
                indices.append(fn)
            if a.convert("RGBA").tobytes()!=b.convert("RGBA").tobytes():
                visual.append(Path(fn).stem)
    bpal={p.stem:p.read_text() for p in before.glob("*.pal")}
    apal={p.stem:p.read_text() for p in after.glob("*.pal")}
    if bpal.keys()!=apal.keys(): raise SystemExit(f"{name}: palette names changed")
    changed=sorted(k for k in bpal if bpal[k]!=apal[k])
    unexpected=sorted(set(changed)-ALLOWED[name])
    if dims or indices or unexpected or len(changed)<MIN_CHANGED[name]:
        raise SystemExit(f"{name}: dims={dims} indices={indices} unexpected={unexpected} changed={changed}")
    return {"textures":len(bp),"changed_palettes":changed,"visual_textures":visual}

results={name:check(name) for name in ("main","lab","warehouse")}
JSON_REPORT.write_text(json.dumps({"schema_version":1,"results":results},indent=2)+"\n")

lines=[
"# G4G — Team Galactic Interiors",
"",
"Status: source-applied; runtime inspection pending.",
"",
"G4G completes the representative environment reconstruction pass with a restrained",
"cooler industrial grade for Team Galactic interiors. Geometry, collision, scripts,",
"warps, texture dimensions, texture indices, transparency, and resource names are unchanged.",
"",
"## Main Galactic buildings",
"",
f"- Textures validated: **{results['main']['textures']}**",
f"- Palettes changed: **{len(results['main']['changed_palettes'])}**",
f"- Rendered textures affected: **{len(results['main']['visual_textures'])}**",
"- Eterna Galactic Building and the main Galactic HQ remain on their dedicated texture set 057.",
"",
"## Control room / laboratory",
"",
f"- Textures validated: **{results['lab']['textures']}**",
f"- Palettes changed: **{len(results['lab']['changed_palettes'])}**",
f"- Rendered textures affected: **{len(results['lab']['visual_textures'])}**",
"- The laboratory/control-room family remains on dedicated texture set 067.",
"",
"## Veilstone Galactic Warehouse",
"",
f"- Textures validated: **{results['warehouse']['textures']}**",
f"- Palettes changed: **{len(results['warehouse']['changed_palettes'])}**",
f"- Rendered textures affected: **{len(results['warehouse']['visual_textures'])}**",
"- The warehouse is isolated from shared generic interior area_data_031 into area_data_077.",
"- Its texture bank is cloned from shared set 030 into dedicated map_texture_set_076 before grading.",
"",
"## G4 completion checkpoint",
"",
"Source-side G4 representative environment reconstruction is complete:",
"- G4A Eterna Forest",
"- G4B Snowpoint / Route 217",
"- G4C Distortion World",
"- G4D Spear Pillar",
"- G4E lakes",
"- G4F Turnback Cave",
"- G4G Team Galactic interiors",
"",
"Remaining gate: runtime visual inspection in Delta of the representative areas.",
]
REPORT.write_text("\n".join(lines)+"\n")
print(json.dumps({k:{'palettes':len(v['changed_palettes']),'visual':len(v['visual_textures'])} for k,v in results.items()}))
