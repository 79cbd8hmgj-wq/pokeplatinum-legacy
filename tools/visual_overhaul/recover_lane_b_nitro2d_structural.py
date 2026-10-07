#!/usr/bin/env python3
"""Structurally recover the remaining Lane B Nitro 2D resources.

This pass is deliberately conservative:
- NCGR resources are parsed and checked for valid Nitro 4bpp geometry/nonblank pixels.
- NCLR resources are parsed and checked for valid Nitro palette payload/nontrivial colors.
- Structurally valid components become valid_render-equivalent evidence only when the
  component itself is self-describing enough to decode faithfully.
- They are NOT promoted to usable here because correct NCGR<->NCLR pairing still has
  to be established for a trustworthy coloured render.

No Platinum resources are modified.
"""
from __future__ import annotations

import argparse
import json
import struct
from collections import Counter
from pathlib import Path


def u16(data: bytes, off: int) -> int:
    return struct.unpack_from("<H", data, off)[0]


def u32(data: bytes, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]


def parse_ncgr(path: Path) -> dict:
    raw = path.read_bytes()
    if len(raw) < 0x30 or raw[:4] != b"RGCN" or raw[0x10:0x14] != b"RAHC":
        raise ValueError("invalid RGCN/RAHC header")
    wt = u16(raw, 0x18)
    ht = u16(raw, 0x1A)
    fmt = u16(raw, 0x1C)
    size = u32(raw, 0x28)
    body = raw[0x30:0x30 + size]
    if len(body) != size:
        raise ValueError("truncated NCGR body")
    if fmt != 3:
        raise ValueError(f"unsupported NCGR pixel format {fmt}")
    if wt in (0, 0xFFFF) or ht in (0, 0xFFFF):
        raise ValueError(f"unspecified NCGR geometry {wt}x{ht}")
    expected = wt * ht * 32
    if expected != len(body):
        raise ValueError(f"NCGR geometry expects {expected} bytes, got {len(body)}")
    used = set()
    nonzero = 0
    for b in body:
        lo, hi = b & 0x0F, b >> 4
        used.add(lo); used.add(hi)
        nonzero += int(lo != 0) + int(hi != 0)
    return {
        "width": wt * 8,
        "height": ht * 8,
        "pixel_format": fmt,
        "payload_bytes": size,
        "used_palette_indices": sorted(used),
        "nonzero_pixels": nonzero,
    }


def bgr555(v: int) -> tuple[int, int, int]:
    return (v & 31, (v >> 5) & 31, (v >> 10) & 31)


def parse_nclr(path: Path) -> dict:
    raw = path.read_bytes()
    if len(raw) < 0x28 or raw[:4] != b"RLCN" or raw[0x10:0x14] != b"TTLP":
        raise ValueError("invalid RLCN/TTLP header")
    # TTLP payload size field is at 0x20 in standard Nitro NCLR.
    payload_size = u32(raw, 0x20)
    # Some tools include a small palette-data offset; the actual color array starts at 0x28.
    body = raw[0x28:]
    if len(body) % 2:
        raise ValueError("odd NCLR palette payload")
    colors = [u16(body, i) for i in range(0, len(body), 2)]
    if not colors:
        raise ValueError("empty NCLR palette")
    unique = len(set(colors))
    nonzero = sum(1 for c in colors if c != 0)
    return {
        "declared_payload_bytes": payload_size,
        "palette_entries": len(colors),
        "unique_colors": unique,
        "nonzero_colors": nonzero,
        "first_colors_bgr555": [bgr555(c) for c in colors[:16]],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True, type=Path)
    ap.add_argument("--diamond-root", required=True, type=Path)
    ap.add_argument("--hgss-root", required=True, type=Path)
    ap.add_argument("--write-json", required=True, type=Path)
    ap.add_argument("--write-md", required=True, type=Path)
    args = ap.parse_args()

    plan = json.loads(args.plan.read_text())
    roots = {"diamond": args.diamond_root, "hgss": args.hgss_root}

    records = []
    for group in plan["groups"]:
        for source_path in group["examples"] if group["asset_count"] == len(group["examples"]) else []:
            pass

    # The plan is grouped for display; recover exact asset IDs from its source JSON is not possible.
    # Reconstruct the 217 targets deterministically from the listed family itself.
    targets = []
    for g in plan["groups"]:
        # group_count is 216; all but one group contain a single asset.
        # examples includes every member when asset_count <= 12, which holds for this plan.
        if g["asset_count"] != len(g["examples"]):
            raise SystemExit("Nitro2D plan group exceeds embedded example coverage")
        for path in g["examples"]:
            targets.append({
                "source_id": g["source_id"],
                "group": g["group"],
                "asset_type": g["asset_type"],
                "suffix": g["suffix"],
                "source_path": path,
            })

    if len(targets) != 217:
        raise SystemExit(f"target reconstruction mismatch: {len(targets)} != 217")

    for t in targets:
        root = roots[t["source_id"]]
        path = root / t["source_path"]
        evidence = {}
        state = "decode_issue"
        code = "nitro_component_parse_failed"
        reason = "Nitro 2D component could not be parsed structurally."
        try:
            if t["suffix"] == ".ncgr":
                evidence = parse_ncgr(path)
                if evidence["nonzero_pixels"] > 0:
                    state = "structurally_valid"
                    code = "ncgr_structurally_valid"
                    reason = (
                        "NCGR is a valid nonblank self-describing 4bpp Nitro character resource. "
                        "Palette pairing is still required before usable promotion."
                    )
            elif t["suffix"] == ".nclr":
                evidence = parse_nclr(path)
                if evidence["nonzero_colors"] > 0 and evidence["unique_colors"] > 1:
                    state = "structurally_valid"
                    code = "nclr_structurally_valid"
                    reason = (
                        "NCLR is a valid nontrivial Nitro palette resource. "
                        "Character-resource pairing is still required before usable promotion."
                    )
            else:
                raise ValueError("unexpected suffix")
        except Exception as exc:
            evidence = {"error": str(exc)}

        records.append({
            **t,
            "technical_state": state,
            "reason_code": code,
            "reason": reason,
            "evidence": evidence,
        })

    counts = Counter(r["technical_state"] for r in records)
    suffix_counts = {}
    for suffix in sorted({r["suffix"] for r in records}):
        suffix_counts[suffix] = dict(sorted(Counter(
            r["technical_state"] for r in records if r["suffix"] == suffix
        ).items()))

    payload = {
        "schema_version": 1,
        "lane": "B_pokemon_facing",
        "route": "nitro_2d_decode",
        "asset_count": len(records),
        "technical_state_counts": dict(sorted(counts.items())),
        "suffix_state_counts": suffix_counts,
        "records": records,
    }
    args.write_json.parent.mkdir(parents=True, exist_ok=True)
    args.write_json.write_text(json.dumps(payload, indent=2) + "\n")

    lines = [
        "# Lane B Nitro 2D Structural Recovery",
        "",
        "Structural decode audit of the 217 remaining Nitro 2D resources.",
        "No Platinum resources are modified and no resource is promoted to usable yet.",
        "",
        f"- Assets checked: **{len(records)}**",
    ]
    for state, count in sorted(counts.items()):
        lines.append(f"- {state}: **{count}**")
    lines += [
        "",
        "## Boundary",
        "",
        "- NCGR and NCLR are validated independently.",
        "- Valid components stay pending until correct character/palette pairing is proven.",
        "- This prevents another false-positive recreation problem like the earlier Ranger renderer issue.",
    ]
    args.write_md.write_text("\n".join(lines) + "\n")
    print("Nitro2D structural recovery:", dict(counts))
    print("By suffix:", suffix_counts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
