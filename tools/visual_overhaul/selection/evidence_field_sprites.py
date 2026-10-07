#!/usr/bin/env python3
"""Evidence provider: field_npc_player_sprites (HGSS direct donor).

Decodes each cataloged HGSS NSBTX (read-only), stacks frame textures (numeric suffix order, no gap) and compares
with Platinum res/graphics/field_sprites/<npc|player>/<stem>.png using the shared sprite comparison
(identical / palette_only / art_diff_minor / art_diff_geometry_*; BGR555-space colour comparison).
"""
from __future__ import annotations

import argparse
import collections
import sys
from pathlib import Path

from PIL import Image

from common import *  # noqa: F401,F403
import evidence_trainer_sprites as cmp

sys.path.insert(0, str(ROOT / "tools" / "visual_overhaul"))
import inventory_hgss_field_sprites as inv  # noqa: E402

NATIVE = ROOT / "res" / "graphics" / "field_sprites"


def sheet_image(data: bytes) -> Image.Image:
    tex, _skipped, pals = inv.decode_sheet(data)
    _name, pal = sorted(pals.items())[0]
    w = tex[0][1]
    px = [i for t in tex for i in t[4]]
    im = Image.new("P", (w, tex[0][2] * len(tex)))
    im.putdata(px)
    flat = []
    for c in pal[:256]:
        r, g, b = c & 31, (c >> 5) & 31, (c >> 10) & 31
        flat += [(r << 3) | (r >> 2), (g << 3) | (g >> 2), (b << 3) | (b >> 2)]
    im.putpalette(flat + [0] * (768 - len(flat)))
    return im


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hgss-root", required=True, type=Path)
    a = ap.parse_args()
    align = jload(SEL / "alignment" / "field_sprites.json")["hgss"]
    groups = [g for g in jload(GROUPS_JSON)["groups"] if g["subsystem"] == "field_npc_player_sprites" and g["source_id"] == "hgss"]
    entries = {}
    for g in groups:
        sp = g["sample_paths"][0]
        e = align[sp]
        detail = {"base": e["base"], "platinum_file": e["platinum_file"], "alignment_method": e["method"]}
        flags: list[str] = []
        if not e["platinum_file"] or not (NATIVE / e["platinum_file"]).is_file():
            rel = "missing_in_native"
        else:
            donor = sheet_image((a.hgss_root / sp).read_bytes())
            native = Image.open(NATIVE / e["platinum_file"])
            rel, flags, d = cmp.compare(donor, native, 32, gap=0)
            detail.update(d)
            if rel not in ("identical", "palette_only", "art_diff_minor"):
                # Slot-name alignment is not subject identity (e.g. Platinum slot `oldman1` = Prof. Rowan, HGSS = another NPC).
                n = min(len(cmp.split_frames(donor, 32, 0)), len(cmp.split_frames(native, 32, 0)))
                detail["mask_iou"] = round(cmp.mask_iou(cmp.split_frames(donor, 32, 0)[:n], cmp.split_frames(native, 32, 0)[:n]), 3)
                detail["underlying_relation"] = rel
                rel, flags = "subject_unverified", []
        ent = {"native_relation": rel, "member_digest": g["member_digest"], "detail": detail}
        if flags:
            ent["risk_flags"] = sorted(set(flags))
        entries[g["group_id"]] = ent
    summary = collections.Counter(v["native_relation"] for v in entries.values())
    cat = jload(EXT_DIR / "hgss_field_sprites" / "CATALOG.json")
    doc = {"schema_version": 1, "subsystem": "field_npc_player_sprites", "provider": "field_sprites",
           "generated_by": "tools/visual_overhaul/selection/evidence_field_sprites.py",
           "inputs": {"hgss_commit": cat["sources"][0]["source_commit"],
                      "alignment_sha256": file_sha256(SEL / "alignment" / "field_sprites.json"),
                      "method": "stacked NSBTX frame textures vs Platinum PNG; frame height 32, no gap; BGR555 colour compare"},
           "summary": dict(sorted(summary.items())), "entries": entries}
    jdump(SEL / "evidence" / "field_npc_player_sprites.json", doc)
    print(doc["summary"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
