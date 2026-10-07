#!/usr/bin/env python3
"""Evidence provider: trainer_battle_sprites (HGSS direct donor, Diamond control).

HGSS: decoded render PNGs in catalog_extensions/hgss_trainer_sprites/renders (no donor access needed).
Diamond: trfgra/trbgra PNGs (read-only). Native: res/trainers/classes/<class>/{front,back}.png.
Relations follow the battle-sprite vocabulary (identical / palette_only / art_diff_geometry_{close,review});
frame-count/size differences add risk flag `frame_layout_differs`.
"""
from __future__ import annotations

import argparse
import collections
import re
import subprocess
from pathlib import Path

from PIL import Image

from common import *  # noqa: F401,F403

NATIVE = ROOT / "res" / "trainers" / "classes"
RENDERS = EXT_DIR / "hgss_trainer_sprites" / "renders"
MAX_BOTTOM, MAX_CENTER, MAX_SIZE = 3, 4.0, 10
MINOR_RATIO = jload(RULES_JSON)["thresholds"]["minor_diff_ratio"]


def rgba(im: Image.Image):
    pal = im.getpalette() or []
    px = im.tobytes()
    return [(0, 0, 0, 0) if i == 0 else (pal[3 * i], pal[3 * i + 1], pal[3 * i + 2], 255) for i in px], px


def bbox(px, w, h):
    xs = [i % w for i, p in enumerate(px) if p]
    ys = [i // w for i, p in enumerate(px) if p]
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None


def normalize_dp(im: Image.Image) -> Image.Image:
    """DP trainer PNGs are 160x80 (two frames side by side); Platinum stacks frames vertically with a 1px gap
    and collapses duplicate frames to a single 80x80 image."""
    if im.size != (160, 80):
        return im
    f0, f1 = im.crop((0, 0, 80, 80)), im.crop((80, 0, 160, 80))
    if f0.tobytes() == f1.tobytes():
        out = f0.copy()
        out.putpalette(im.getpalette())
        return out
    out = Image.new("P", (80, 161))
    out.putpalette(im.getpalette())
    out.paste(f0, (0, 0))
    out.paste(f1, (0, 81))
    return out


def split_frames(im: Image.Image, fh: int) -> list[Image.Image]:
    n = (im.height + 1) // (fh + 1) if im.height > fh else 1
    out = []
    for k in range(max(n, 1)):
        f = im.crop((0, k * (fh + 1), im.width, k * (fh + 1) + fh))
        f.putpalette(im.getpalette())
        out.append(f)
    return out


def geometry(d0: Image.Image, n0: Image.Image) -> list[str]:
    db, nb = bbox(d0.tobytes(), d0.width, d0.height), bbox(n0.tobytes(), n0.width, n0.height)
    if not (db and nb):
        return ["empty frame 0"]
    reasons = []
    bd = db[3] - nb[3]
    cx = ((db[0] + db[2]) - (nb[0] + nb[2])) / 2
    cy = ((db[1] + db[3]) - (nb[1] + nb[3])) / 2
    dw, dh = (db[2] - db[0]) - (nb[2] - nb[0]), (db[3] - db[1]) - (nb[3] - nb[1])
    if abs(bd) > MAX_BOTTOM:
        reasons.append(f"bottom shift {bd:+d}px")
    if abs(cx) > MAX_CENTER or abs(cy) > MAX_CENTER:
        reasons.append(f"center shift ({cx:+.1f},{cy:+.1f})px")
    if abs(dw) > MAX_SIZE or abs(dh) > MAX_SIZE:
        reasons.append(f"bbox size delta ({dw:+d},{dh:+d})px")
    return reasons


def diff_ratio(dfs, nfs) -> float:
    diff = union = 0
    for d, n in zip(dfs, nfs):
        A, _ = rgba(d)
        B, _ = rgba(n)
        for x, y in zip(A, B):
            if x[3] or y[3]:
                union += 1
                diff += x != y
    return diff / union if union else 0.0


def compare(donor: Image.Image, native: Image.Image, frame_h: int | None) -> tuple[str, list[str], dict]:
    fh = frame_h or 80
    df, nf = split_frames(donor, fh), split_frames(native, fh)
    detail = {"donor_size": list(donor.size), "native_size": list(native.size), "donor_frames": len(df), "native_frames": len(nf)}
    flags = ["frame_layout_differs"] if len(df) != len(nf) or donor.width != native.width else []
    common = min(len(df), len(nf))
    if donor.width == native.width:
        rel_pal, rel_ident = True, True
        for k in range(common):
            drgb, dpx = rgba(df[k])
            nrgb, npx = rgba(nf[k])
            if drgb != nrgb:
                rel_ident = False
            if dpx != npx:
                rel_pal = False
        if rel_ident and len(df) <= len(nf):
            return "identical", [], detail
        if rel_pal and len(df) <= len(nf):
            return "palette_only", [], detail
        if rel_ident and len(df) > len(nf):
            detail["common_frames_identical"] = True
            return "art_diff_geometry_close", flags, detail  # donor adds frames beyond the native sheet
    ratio = diff_ratio(df[:common], nf[:common]) if donor.width == native.width else 1.0
    detail["diff_ratio"] = round(ratio, 4)
    if ratio < MINOR_RATIO and donor.width == native.width:
        return "art_diff_minor", sorted(set(flags)), detail
    reasons = geometry(df[0], nf[0].crop((0, 0, df[0].width, nf[0].height))) if donor.width == native.width else ["width differs"]
    detail["geometry_reasons"] = reasons
    if reasons:
        flags.append("geometry_review")
        return "art_diff_geometry_review", sorted(set(flags)), detail
    return "art_diff_geometry_close", sorted(set(flags)), detail


def git_head(repo: Path) -> str:
    return subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--diamond-root", required=True, type=Path)
    a = ap.parse_args()
    align = jload(SEL / "alignment" / "trainer_classes.json")
    cat = {x["source_path"]: x for x in jload(EXT_DIR / "hgss_trainer_sprites" / "CATALOG.json")["assets"]}
    groups = [g for g in jload(GROUPS_JSON)["groups"] if g["subsystem"] == "trainer_battle_sprites"]
    entries = {}
    for g in groups:
        view = "back" if "back" in g["unit"] or "trbgra" in g["unit"] else "front"
        idx = g["unit"].split("_")[-1]
        tbl = align[("hgss_" if g["source_id"] == "hgss" else "diamond_") + view]
        pclass = tbl[idx]["platinum_class"]
        native = NATIVE / pclass / f"{view}.png" if pclass else None
        detail = {"view": view, "platinum_class": pclass, "alignment_method": tbl[idx]["method"]}
        flags: list[str] = []
        if native is None or not native.is_file():
            rel = "missing_in_native"
        elif g["source_id"] == "hgss":
            sp = g["sample_paths"][0]
            asset = cat[sp]
            donor = Image.open(ROOT / asset["render_path"])
            fh = asset["source_metadata"]["cell_dims"][0][1]
            rel, flags, d = compare(donor, Image.open(native), fh)
            detail.update(d)
            detail["native_path"] = str(native.relative_to(ROOT))
        else:
            sp = g["sample_paths"][0]
            donor = Image.open(a.diamond_root / sp)
            donor = normalize_dp(donor) if donor.mode == "P" else donor
            if donor.mode != "P":
                rel = "unmeasured"
            else:
                rel, flags, d = compare(donor, Image.open(native), None)
                detail.update(d)
            detail["native_path"] = str(native.relative_to(ROOT))
        e = {"native_relation": rel, "member_digest": g["member_digest"], "detail": detail}
        if flags:
            e["risk_flags"] = sorted(set(flags))
        entries[g["group_id"]] = e
    summary = collections.Counter(f"{k.split('/')[1]}:{v['native_relation']}" for k, v in entries.items())
    doc = {
        "schema_version": 1, "subsystem": "trainer_battle_sprites", "provider": "trainer_sprites",
        "generated_by": "tools/visual_overhaul/selection/evidence_trainer_sprites.py",
        "inputs": {"hgss_commit": next(iter(jload(EXT_DIR / "hgss_trainer_sprites" / "CATALOG.json")["sources"]))["source_commit"],
                   "diamond_commit": git_head(a.diamond_root),
                   "alignment_sha256": file_sha256(SEL / "alignment" / "trainer_classes.json"),
                   "method": "frame-sheet pixel/palette comparison; frame-0 bbox geometry thresholds bottom<=3, center<=4, size<=10"},
        "summary": dict(sorted(summary.items())),
        "entries": entries,
    }
    jdump(SEL / "evidence" / "trainer_battle_sprites.json", doc)
    print(doc["summary"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
