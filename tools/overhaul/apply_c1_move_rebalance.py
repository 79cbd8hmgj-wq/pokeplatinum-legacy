#!/usr/bin/env python3
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MOVES = ROOT / "res" / "moves"
MANIFEST = ROOT / "docs/overhaul/implementation/c1_move_changes_manifest.json"
GUARDS = ROOT / "docs/overhaul/implementation/c1_move_before_guards.json"
REPORT = ROOT / "docs/overhaul/implementation/C1_MOVE_IMPLEMENTATION_REPORT.md"

def move_index():
    out = {}
    for path in MOVES.glob("*/data.json"):
        data = json.loads(path.read_text())
        if isinstance(data.get("name"), str):
            out[data["name"]] = path
    return out

def getv(data, key):
    return data["effect"]["type"] if key == "effect_type" else data[key]

def setv(data, key, value):
    if key == "effect_type":
        data["effect"]["type"] = value
    else:
        data[key] = value

manifest = json.loads(MANIFEST.read_text())
edits = manifest["edits"]
expected = manifest["expected_edit_count"]
if len(edits) != expected:
    raise SystemExit(f"manifest count {len(edits)} != {expected}")

index = move_index()
missing = [e["move"] for e in edits if e["move"] not in index]
if missing:
    raise SystemExit("missing move files: " + ", ".join(missing))

guards = {
    "schema_version": 1,
    "basis": "main@67af26fb3f118a1a010359540115ca39a6e7e9d7",
    "manifest": "docs/overhaul/implementation/c1_move_changes_manifest.json",
    "entries": []
}
rows = []

for edit in edits:
    name = edit["move"]
    path = index[name]
    raw = path.read_bytes()
    data = json.loads(raw)
    before = {}
    for key, target in edit["target"].items():
        before[key] = getv(data, key)
        setv(data, key, target)

    if name == "Razor Wind":
        before["description"] = data["description"]
        data["description"] = [
            "Blades of wind hit the\n",
            "foe. It has a high\n",
            "critical-hit ratio."
        ]

    guards["entries"].append({
        "move": name,
        "path": str(path.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "before": before,
        "target": edit["target"],
        "batch": edit.get("batch")
    })
    path.write_text(json.dumps(data, indent=4) + "\n")
    rows.append((name, edit.get("batch", ""), before, edit["target"]))

if len({str(index[e["move"]]) for e in edits}) != expected:
    raise SystemExit("duplicate move targets")

GUARDS.write_text(json.dumps(guards, indent=2) + "\n")

lines = [
    "# C1 Existing-Move Rebalance — Implementation Report",
    "",
    "Status: source-applied; CI/build verification pending.",
    "",
    f"- Manifest entries applied: **{expected}**",
    f"- Move data files changed: **{expected}**",
    "- New moves: **0**",
    "- New battle mechanics: **0**",
    "- Razor Wind is the only effect reassignment; its description is updated.",
    "- Trapping duration/residual mechanics remain unchanged.",
    "",
    "## Applied edits",
    "",
    "| Move | Batch | Before -> target |",
    "|---|---|---|",
]
for name, batch, before, target in rows:
    parts = [f"{k}: {before[k]} -> {v}" for k, v in target.items()]
    if name == "Razor Wind":
        parts.append("description updated")
    lines.append(f"| {name} | {batch} | {'; '.join(parts)} |")
REPORT.write_text("\n".join(lines) + "\n")

print(f"Applied {expected} guarded C1 move edits.")
