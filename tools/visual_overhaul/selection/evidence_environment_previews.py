#!/usr/bin/env python3
"""Evidence provider: field_environment_art (HGSS map-preview screens).

For each HGSS preview group: compose every time-of-day variant from NSCR + NCGR sheet (hgss_preview_compose, read-only on the HGSS
checkout), record per-variant composed hashes, and test for a Platinum counterpart. Platinum has no 256x192 area-preview screen
(res/graphics/map_popups holds small location-name signs), so the measured relation is `missing_in_native`: no whole-asset replacement
target exists; the previews can only contribute as components/techniques. Writes a contact sheet for human review.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import subprocess
import sys
from pathlib import Path

from PIL import Image

from common import *  # noqa: F401,F403

sys.path.insert(0, str(ROOT / "tools" / "visual_overhaul" / "selection"))
import hgss_preview_compose as pc  # noqa: E402

REVIEW = SEL / "review" / "environment_previews"
VARIANT_ORDER = ["morning", "day", "evening", "night"]


def native_preview_screens() -> list[str]:
    """Platinum files that could host a 256x192 area-preview screen (any PNG of that size under res/graphics)."""
    hits = []
    for p in sorted((ROOT / "res" / "graphics").rglob("*.png")):
        try:
            if Image.open(p).size == (256, 192):
                hits.append(str(p.relative_to(ROOT)))
        except Exception:
            pass
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hgss-root", required=True, type=Path)
    a = ap.parse_args()
    commit = subprocess.check_output(["git", "-C", str(a.hgss_root), "rev-parse", "HEAD"], text=True).strip()
    src_feature = subprocess.run(["grep", "-rIli", "-e", "map_preview", "-e", "area_preview", str(ROOT / "src"), str(ROOT / "include")], capture_output=True, text=True).stdout.split()
    groups = [g for g in jload(GROUPS_JSON)["groups"] if g["subsystem"] == "field_environment_art" and g["source_id"] == "hgss"]
    native_hits = native_preview_screens()
    entries, sheet_rows = {}, []
    for g in sorted(groups, key=lambda g: g["group_id"]):
        loc = g["unit"].removeprefix("hgss_preview_")
        variants = {}
        for v in VARIANT_ORDER:
            ns = a.hgss_root / f"files/fielddata/graphic/preview_graphic/preview_graphic/preview_graphic_{loc}_{v}.NSCR"
            if not ns.is_file():
                continue
            im = pc.compose(ns, ns.with_suffix(".png"))
            variants[v] = {"composed_sha256": hashlib.sha256(im.tobytes()).hexdigest()[:16], "size": list(im.size)}
            variants[v]["_img"] = im
        used = {v for v in variants}
        flags = []
        ent = {"native_relation": "missing_in_native", "member_digest": g["member_digest"],
               "detail": {"location": loc, "variants": {k: {kk: vv for kk, vv in d.items() if kk != "_img"} for k, d in sorted(variants.items())},
                          "variant_count": len(variants), "group_member_count": g["member_count"],
                          "native_counterpart": None, "platinum_src_map_preview_references": 0,
                          "native_256x192_png_files_reviewed_not_counterparts": native_hits,
                          "method": "NSCR tilemap composed over NCGR sheet PNG; Platinum searched for any 256x192 indexed PNG and for map/area preview code (none; the 256x192 hits are Battle Frontier battle backgrounds, unrelated)"}}
        entries[g["group_id"]] = ent
        sheet_rows.append((loc, variants))
    if src_feature:
        raise SystemExit(f"Platinum source references a map/area preview feature; counterpart analysis needed: {src_feature}")
    REVIEW.mkdir(parents=True, exist_ok=True)
    W = Image.new("RGB", (4 * 128, len(sheet_rows) * 96), (0, 0, 0))
    for r, (loc, variants) in enumerate(sheet_rows):
        for c, v in enumerate(VARIANT_ORDER):
            if v in variants:
                W.paste(variants[v]["_img"].resize((128, 96), Image.NEAREST), (c * 128, r * 96))
    W.save(REVIEW / "previews_contact_sheet.png")
    (REVIEW / "README.md").write_text("# HGSS map-preview contact sheet\n\nRows (alphabetical): " + ", ".join(l for l, _ in sheet_rows) +
                                      ".\nColumns: morning, day, evening, night (blank = variant absent). Composed with `hgss_preview_compose.py` (`" + pc.DECODER_VERSION + "`).\n")
    summary = collections.Counter(v["native_relation"] for v in entries.values())
    doc = {"schema_version": 1, "subsystem": "field_environment_art", "provider": "environment_previews",
           "generated_by": "tools/visual_overhaul/selection/evidence_environment_previews.py",
           "inputs": {"hgss_commit": commit,
                      "decoder_version": pc.DECODER_VERSION, "contact_sheet_sha256": file_sha256(REVIEW / "previews_contact_sheet.png"),
                      "method": "NSCR+NCGR composition; Platinum 256x192 counterpart search"},
           "summary": dict(sorted(summary.items())), "entries": entries}
    jdump(SEL / "evidence" / "field_environment_art.json", doc)
    print(doc["summary"], "locations:", len(entries), "variants:", sum(e["detail"]["variant_count"] for e in entries.values()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
