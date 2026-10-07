#!/usr/bin/env python3
"""Runtime-validation targets + before/after comparison images for the trainer front pilot (reads repo state only)."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PILOT = ROOT / "docs/visual_overhaul/pilots/trainer_front_pilot_v1"


def rgba(p: Path) -> Image.Image:
    return Image.open(p).convert("RGBA")


def main() -> None:
    man = json.loads((PILOT / "PILOT_MANIFEST.json").read_text())
    consts = [l.strip() for l in (ROOT / "generated/trainers.txt").read_text().splitlines()]
    data_dir = ROOT / "res/trainers/data"
    by_class: dict[str, list] = {}
    for f in sorted(data_dir.glob("*.json")):
        d = json.loads(f.read_text())
        const = "TRAINER_" + f.stem.upper()
        by_class.setdefault(d["class"], []).append({"constant": const, "id": consts.index(const) if const in consts else None,
                                                    "name": d["name"], "double_battle": d["double_battle"], "party_size": len(d["party"])})
    (PILOT / "compare").mkdir(exist_ok=True)
    targets = []
    for e in man["entries"]:
        c = e["class"]
        before = rgba(PILOT / "originals" / c / "front.png")
        after = rgba(ROOT / f"res/trainers/classes/{c}/front.png")
        sheet = Image.new("RGBA", (80 * 3 * 2 + 12, 80 * 3), (70, 70, 90, 255))
        for k, im in enumerate((before, after)):
            t = Image.new("RGBA", im.size, (70, 70, 90, 255))
            t.alpha_composite(im)
            sheet.paste(t.resize((240, 240), Image.NEAREST), (k * 252, 0))
        sheet.convert("RGB").save(PILOT / "compare" / f"{c}.png", optimize=True)
        ts = sorted((t for t in by_class.get("TRAINER_CLASS_" + c.upper(), []) if t["id"] is not None), key=lambda t: t["id"])
        singles = [t for t in ts if not t["double_battle"] and "DUMMY" not in t["constant"]]
        targets.append({"class": c, "hgss_class": e["hgss_class_constant"], "comparison_image": f"compare/{c}.png (left: Platinum original, right: HGSS)",
                        "trainers_using_class": len(ts), "suggested_test_trainers": (singles or ts)[:3],
                        "front_sprite_contexts": ["battle intro (enemy front sprite slide-in)", "battle idle", "battle end / trainer defeated fade"],
                        "files": {f: {"before": v["before_sha256"][:12], "after": v["after_sha256"][:12]} for f, v in e["files"].items()}})
    doc = {"schema_version": 1, "pilot": man["pilot"], "targets": targets}
    (PILOT / "RUNTIME_TARGETS.json").write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
    L = ["# Runtime validation targets", "", "Each class: trainers that use it (first single battles by trainer ID) and a before/after image (`compare/<class>.png`, Platinum left / HGSS right).", "",
         "| Class | Trainers using it | Suggested test trainers (ID) |", "|---|---:|---|"]
    for t in targets:
        L.append(f"| {t['class']} | {t['trainers_using_class']} | " + ", ".join(f"{x['constant'].removeprefix('TRAINER_')} ({x['id']})" for x in t["suggested_test_trainers"]) + " |")
    (PILOT / "RUNTIME_TARGETS.md").write_text("\n".join(L) + "\n")
    print(len(targets), "targets")


if __name__ == "__main__":
    main()
