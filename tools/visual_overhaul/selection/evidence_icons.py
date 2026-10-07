#!/usr/bin/env python3
"""Evidence provider: pokemon_icons. Compares donor icon index pixels against Platinum's icon.png files.

Read-only on donor checkouts. HGSS icons are PNG; Diamond icons are raw RGCN (decoded with the
Lane B recovery decoder). Members that do not map to a base species are content-matched against
every Platinum icon.png (form icons), recording the matched folder if any.
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import subprocess
from pathlib import Path

from PIL import Image

from common import *  # noqa: F401,F403
import mapping

PT_ICONS = ROOT / "res" / "pokemon"


def png_indices(path: Path):
    im = Image.open(path)
    if im.mode != "P":
        raise ValueError(f"{path}: not indexed")
    return im.size, im.tobytes()


def load_diamond_decoder():
    spec = importlib.util.spec_from_file_location("rdi", ROOT / "tools/visual_overhaul/recover_lane_b_diamond_icons.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def git_head(repo: Path) -> str:
    return subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hgss-root", required=True, type=Path)
    ap.add_argument("--diamond-root", required=True, type=Path)
    a = ap.parse_args()

    species = species_constants()
    native: dict[int, tuple[str, bytes]] = {}
    by_hash: dict[bytes, list[str]] = {}
    for i, c in enumerate(species):
        p = PT_ICONS / c.removeprefix("SPECIES_").lower() / "icon.png"
        if p.is_file():
            _, px = png_indices(p)
            native[i] = (str(p.relative_to(ROOT)), px)
    for p in sorted(list(PT_ICONS.glob("*/icon.png")) + list(PT_ICONS.glob("*/forms/*/icon.png"))):
        _, px = png_indices(p)
        by_hash.setdefault(px, []).append(str(p.parent.relative_to(PT_ICONS)))

    groups = [g for g in jload(GROUPS_JSON)["groups"] if g["subsystem"] == "pokemon_icons"]
    rdi = load_diamond_decoder()
    entries = {}
    for g in groups:
        sp = g["sample_paths"][0]
        m = re.search(r"(?:narc_|poke_icon_)(\d+)", sp)
        member = int(m.group(1))
        si = member - mapping.ICON_MEMBER_BIAS
        if g["source_id"] == "hgss":
            if sp.lower().endswith(".png"):
                _, px = png_indices(a.hgss_root / sp)
            else:
                entries[g["group_id"]] = {"native_relation": "unmeasured", "member_digest": g["member_digest"], "detail": {"note": "non-png icon member"}}
                continue
        else:
            if sp.lower().endswith(".png"):
                _, px = png_indices(a.diamond_root / sp)
            else:
                w, h, pix = rdi.read_rgcn(a.diamond_root / sp)
                if (w, h) != (32, 64):
                    entries[g["group_id"]] = {"native_relation": "unmeasured", "member_digest": g["member_digest"], "detail": {"note": f"geometry {w}x{h}"}}
                    continue
                px = bytes(pix)
        detail = {"member": member, "species_index": si}
        if si in native and g["unit_kind"] == "species":
            npath, npx = native[si]
            detail["native_path"] = npath
            if npx == px:
                rel = "identical"
            else:
                rel = "different"
                detail["differing_pixels"] = sum(1 for x, y in zip(npx, px) if x != y)
        else:
            hit = by_hash.get(px)
            if hit:
                rel = "content_match_native"
                detail["matched_native_folders"] = sorted(hit)
            else:
                rel = "different"
                detail["note"] = "no Platinum icon has identical index pixels (form/special member)"
        entries[g["group_id"]] = {"native_relation": rel, "member_digest": g["member_digest"], "detail": detail}

    import collections
    doc = {
        "schema_version": 1,
        "subsystem": "pokemon_icons",
        "provider": "icons",
        "generated_by": "tools/visual_overhaul/selection/evidence_icons.py",
        "inputs": {
            "hgss_commit": git_head(a.hgss_root),
            "diamond_commit": git_head(a.diamond_root),
                        "comparison": "Platinum res/pokemon/<species>/icon.png index bytes vs donor index bytes (32x64 indexed)",
        },
        "summary": dict(collections.Counter(f'{k.split("/")[1]}:{v["native_relation"]}' for k, v in entries.items())),
        "entries": entries,
    }
    jdump(SEL / "evidence" / "pokemon_icons.json", doc)
    print(doc["summary"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
