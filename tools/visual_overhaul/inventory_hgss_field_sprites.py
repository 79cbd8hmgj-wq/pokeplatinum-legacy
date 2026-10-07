#!/usr/bin/env python3
"""Targeted HGSS catalog extension: NPC/player overworld sprite sheets (files/data/mmodel/mmodel/*.NSBTX).

Scope (documented, deterministic): an NSBTX is a human field-sprite candidate when
  * its sprite base name matches a Platinum res/graphics/field_sprites npc/ or player/ entry, OR
  * it has a single palette and only 32x32 textures in a human frame count (12/16/24/32).
Everything else in the family (Pokemon follower sheets, objects, 64x64 sheets, models/json) is NOT cataloged here;
exclusion counts are recorded in CATALOG.json under `scope_excluded`.
Read-only on HGSS. No renders are stored (reproducible from source); render hashes are recorded.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nsbtx_palettes as nsb  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/visual_overhaul/catalog_extensions/hgss_field_sprites"
SRC_DIR = "files/data/mmodel/mmodel"
HUMAN_FRAMES = {12, 16, 24, 32}


def platinum_names() -> dict[str, list[str]]:
    txt = (ROOT / "res/graphics/field_sprites/meson.build").read_text()
    out: dict[str, list[str]] = {}
    for f, b in re.findall(r"\{\s*'file':\s*'([^']+)',\s*'basename':\s*'([^']+)'", txt):
        out.setdefault(b, []).append(f)
    return out


def decode_sheet(data: bytes):
    """Return (frames_sorted, palette_names, palettes) with frames = [(name, w, h, idx)] ordered by numeric suffix."""
    tex = list(nsb.decode_textures(data))
    all_names = nsb.read_textures(data)
    skipped = [n for n in all_names if n not in {t[0] for t in tex}]
    tex.sort(key=lambda t: (t[0].rsplit(".", 1)[0], int(t[0].rsplit(".", 1)[1]) if "." in t[0] and t[0].rsplit(".", 1)[1].isdigit() else 0))
    return tex, skipped, nsb.read_palettes(data)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hgss-root", required=True, type=Path)
    a = ap.parse_args()
    hgss = a.hgss_root.resolve()
    commit = subprocess.check_output(["git", "-C", str(hgss), "rev-parse", "HEAD"], text=True).strip()
    plat = platinum_names()
    cat, cur = [], []
    excluded = {}
    files = sorted((hgss / SRC_DIR).glob("*.NSBTX"))
    for p in files:
        data = p.read_bytes()
        rel = f"{SRC_DIR}/{p.name}"
        issues = []
        try:
            tex, skipped, pals = decode_sheet(data)
        except Exception as e:
            tex, skipped, pals = [], [], {}
            issues.append(f"decode error: {e}")
        bases = sorted({t[0].rsplit(".", 1)[0] for t in tex})
        dims = sorted({(t[1], t[2]) for t in tex})
        aligned = [f for b in bases for f in plat.get(b, []) if f.split("/")[0] in ("npc", "player")]
        human = (not issues) and (bool(aligned) or (len(pals) == 1 and dims == [(32, 32)] and len(tex) in HUMAN_FRAMES))
        if not human:
            key = "decode_failed" if issues else ("pokemon_follower_2pal" if len(pals) == 2 else "object_or_other")
            excluded[key] = excluded.get(key, 0) + 1
            continue
        if skipped:
            issues.append(f"{len(skipped)} textures with unsupported format")
        if len(bases) != 1:
            issues.append(f"multiple base names {bases}")
        pal_name, pal = sorted(pals.items())[0]
        idx = [i for t in tex for i in t[4]]
        opaque = sum(1 for i in idx if i)
        if not opaque:
            issues.append("blank render")
        if idx and max(idx) >= len(pal):
            issues.append("palette index beyond palette")
        digest = hashlib.sha256(bytes(idx) + b"".join(c.to_bytes(2, "little") for c in pal)).hexdigest()[:16]
        aid = f"hgss:source:{rel.replace('/', ':')}"
        meta = {"source_commit": commit, "base_names": bases, "texture_count": len(tex), "texture_dims": [list(d) for d in dims],
                "texture_format": 3, "palette_names": sorted(pals), "palette_colors": len(pal), "render_sha256": digest,
                "sprite_constant": ("SPRITE_" + bases[0].upper()) if len(bases) == 1 else None,
                "platinum_candidates": aligned}
        ok = not issues
        cat.append({"asset_id": aid, "source_id": "hgss", "asset_type": "nsbtx_sprite_sheet", "species_dex": None, "form": None,
                    "variant": bases[0] if len(bases) == 1 else None, "group": "field_sprites", "frame": len(tex), "source_path": rel,
                    "render_path": None, "native_width": dims[0][0] if dims else None, "native_height": dims[0][1] * len(tex) if dims else None,
                    "bbox_width": None, "bbox_height": None, "opaque_pixels": opaque or None,
                    "geometry_class": f"{len(tex)}_frames_{dims[0][0]}x{dims[0][1]}" if dims else None,
                    "review_status": "unreviewed", "target_tags": ["overworld", "npc", "player", "field_sprite"],
                    "quality_notes": "HGSS overworld human sprite sheet (NSBTX frame textures); targeted catalog extension.",
                    "source_metadata": meta})
        cur.append({"asset_id": aid, "source_id": "hgss", "asset_type": "nsbtx_sprite_sheet", "group": "field_sprites", "source_path": rel,
                    "render_path": None, "species_dex": None, "target_tags": ["overworld", "npc", "player", "field_sprite"],
                    "lane": "X_hgss_field_sprites", "review_status": "usable" if ok else "reject",
                    "reason_code": "hgss_field_sprite_sheet_valid_render" if ok else "hgss_field_sprite_sheet_invalid",
                    "reason": ("NSBTX frame textures decode with the sheet palette; stacked sheet is nonblank and indices are covered by the palette."
                               if ok else "; ".join(issues)),
                    "decision_source": "HGSS_FIELD_SPRITES_INVENTORY",
                    "recovery_evidence": {"frames": len(tex), "dims": [list(d) for d in dims], "opaque_pixels": opaque, "issues": issues}})
    cat.sort(key=lambda r: r["asset_id"])
    cur.sort(key=lambda r: r["asset_id"])
    counts = {}
    for r in cur:
        counts[r["review_status"]] = counts.get(r["review_status"], 0) + 1
    catalog = {"schema_version": 1, "extension_id": "hgss_field_sprites",
               "sources": [{"source_id": "hgss", "source_game": "Pokemon HeartGold/SoulSilver", "source_repo": "79cbd8hmgj-wq/pokeheartgold",
                            "source_commit": commit, "notes": f"Targeted extension: human overworld sprite sheets from {SRC_DIR}/*.NSBTX."}],
               "scope_excluded": dict(sorted(excluded.items())), "nsbtx_files_scanned": len(files), "assets": cat}
    curation = {"schema_version": 1, "lane": "X_hgss_field_sprites", "scope": "hgss human overworld sprite catalog extension",
                "asset_count": len(cur), "status_counts": counts, "records": cur}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "CATALOG.json").write_text(json.dumps(catalog, indent=1, sort_keys=True) + "\n")
    (OUT / "CURATION.json").write_text(json.dumps(curation, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"assets": len(cat), "status": counts, "excluded": excluded, "scanned": len(files)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
