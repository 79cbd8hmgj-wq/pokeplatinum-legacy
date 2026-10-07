#!/usr/bin/env python3
"""Baseline curation for review-queue lanes C (effects/animation), D (environment/UI), E (decode/context).

Same principle as Lane B: nothing is rejected because a render is missing.  Non-art
metadata/context is rejected; every plausible visual resource/container stays decode_issue
until technical recovery produces evidence.  No usable promotion happens here.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

LANES = {"C_effects_animation": 1603, "D_environment_ui": 4724, "E_decode_or_context_needed": 2798}

VISUAL_TYPES = {
    "compressed_visual_package", "embedded_visual_resource", "nitro_visual_resource",
    "pmd_effect_or_texture_resource", "pmd_sprite_animation_container", "raw_visual_resource",
    "visual_container", "pmd_background_or_map_resource", "binary_visual_candidate",
    "visual_candidate_file", "source_png",
}
CONTEXT_TYPES = {"source_metadata", "visual_metadata"}
CONTEXT_MARKERS = ("/mapmatrix/", "/maptable/", "/encountdata/", "/eventdata/", "/script/", ".gitignore", ".knarcignore", ".narcignore", ".narcorder")
VISUAL_SUFFIXES = (".ncgr", ".nclr", ".ncer", ".nanr", ".nscr", ".nsbmd", ".nsbtx", ".nsbca", ".nsbta", ".nsbtp", ".nsbma",
                   ".narc", ".wan", ".wte", ".wtu", ".wat", ".wba", ".bpl", ".bma", ".bpc", ".bpa", ".bgp", ".ncbr")


def classify(row: dict) -> tuple[str, str, str]:
    kind = str(row.get("asset_type") or "")
    path = str(row.get("source_path") or "").replace("\\", "/").lower()
    if kind in CONTEXT_TYPES:
        return "reject", "context_not_standalone_visual", "Metadata/context record is not standalone donor artwork."
    if any(m in path for m in CONTEXT_MARKERS):
        return "reject", "context_or_build_list", "Path identifies gameplay/context/build-list metadata rather than visual art."
    if kind in VISUAL_TYPES:
        return "decode_issue", "visual_resource_requires_decode", "Plausible visual resource/container without a trustworthy decoded render yet."
    return "decode_issue", "unknown_resource_requires_format_context", "Resource requires format/context resolution before visual validation."


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--queue", required=True, type=Path)
    ap.add_argument("--write-json", required=True, type=Path)
    ap.add_argument("--write-md", required=True, type=Path)
    a = ap.parse_args()
    rows = [r for r in json.loads(a.queue.read_text())["records"] if r.get("lane") in LANES]
    got = Counter(r["lane"] for r in rows)
    if dict(got) != LANES:
        raise SystemExit(f"lane count mismatch: {dict(got)}")
    out = []
    for r in rows:
        st, code, why = classify(r)
        out.append({"asset_id": r["asset_id"], "lane": r["lane"], "source_id": r["source_id"], "asset_type": r["asset_type"],
                    "group": r.get("group"), "source_path": r["source_path"], "target_tags": r.get("target_tags") or [],
                    "review_status": st, "reason_code": code, "reason": why})
    if len({x["asset_id"] for x in out}) != len(out):
        raise SystemExit("duplicate asset ids")
    out.sort(key=lambda x: x["asset_id"])
    counts = Counter((x["lane"], x["review_status"]) for x in out)
    payload = {"schema_version": 1, "scope": "lanes C/D/E baseline", "asset_count": len(out),
               "lane_status_counts": {f"{l}:{s}": n for (l, s), n in sorted(counts.items())}, "records": out}
    a.write_json.write_text(json.dumps(payload, indent=1) + "\n")
    md = ["# Lanes C/D/E Baseline Curation", "", "Baseline classification before decode recovery. No Platinum resources are modified.", "",
          f"- Assets: **{len(out)}**", "", "| Lane | Status | Assets |", "|---|---|---:|"]
    md += [f"| {l} | {s} | {n} |" for (l, s), n in sorted(counts.items())]
    a.write_md.write_text("\n".join(md) + "\n")
    print(dict(counts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
