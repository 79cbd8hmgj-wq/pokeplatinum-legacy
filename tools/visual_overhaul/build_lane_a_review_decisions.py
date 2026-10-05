#!/usr/bin/env python3
"""Build evidence-backed Lane A review decisions.

Only states justified by completed technical inspection are emitted here:
- blank rendered images -> reject, EXCEPT Ranger frames whose cell references tiles
  missing from its own group (renderer limitation, not donor invalidity) ->
  decode_issue / ranger_reconstruction_issue
- actual image decode failures -> decode_issue

No nonblank candidate is promoted to valid_render/usable/alternate automatically.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--integrity", required=True, type=Path)
    p.add_argument("--write-json", required=True, type=Path)
    p.add_argument("--write-md", required=True, type=Path)
    p.add_argument(
        "--ranger-structural",
        type=Path,
        help="RANGER_RENDER_STRUCTURAL_VALIDATION.json; keeps renderer-caused Ranger "
        "blanks from being recorded as donor rejects.",
    )
    args = p.parse_args()
    ranger_groups = (
        json.loads(args.ranger_structural.read_text())["group_ledger"]
        if args.ranger_structural
        else {}
    )
    ranger_id = re.compile(r"^ranger2:pokemon:\d+:\d+:(?P<group>[^:]+):cell_(?P<cell>\d+)$")

    def renderer_caused(asset_id: str) -> bool:
        m = ranger_id.match(asset_id)
        group = ranger_groups.get(m.group("group")) if m else None
        return bool(group) and int(m.group("cell")) in set(group["oob_cells"])

    audit = json.loads(args.integrity.read_text())
    decisions = []

    for row in audit.get("records", []):
        state = row.get("technical_state")
        if state == "blank" and renderer_caused(row["asset_id"]):
            decisions.append({
                "asset_id": row["asset_id"],
                "review_status": "decode_issue",
                "reason_code": "ranger_reconstruction_issue",
                "reason": "Blank render, but the cell references tiles absent from its own "
                "group's character data (they live in another resource). Renderer "
                "limitation; the donor asset is not proven invalid. Not a reject.",
                "evidence": {
                    "technical_state": state,
                    "materialization": row.get("materialization"),
                    "pixel_sha256": row.get("pixel_sha256"),
                },
            })
        elif state == "blank":
            decisions.append({
                "asset_id": row["asset_id"],
                "review_status": "reject",
                "reason_code": "blank_render",
                "reason": "Completed render audit found no visible pixels.",
                "evidence": {
                    "technical_state": state,
                    "materialization": row.get("materialization"),
                    "pixel_sha256": row.get("pixel_sha256"),
                    "width": row.get("width"),
                    "height": row.get("height"),
                },
            })
        elif state == "decode_error":
            decisions.append({
                "asset_id": row["asset_id"],
                "review_status": "decode_issue",
                "reason_code": "image_decode_error",
                "reason": "Materialized source exists, but the completed Lane A image audit could not decode it as an image.",
                "evidence": {
                    "technical_state": state,
                    "materialization": row.get("materialization"),
                    "error": row.get("error"),
                    "file_size": row.get("file_size"),
                },
            })

    decisions.sort(key=lambda d: d["asset_id"])
    counts = Counter(d["review_status"] for d in decisions)
    reason_counts = Counter(d["reason_code"] for d in decisions)

    payload = {
        "schema_version": 1,
        "lane": "A_render_ready",
        "source_integrity_report": str(args.integrity),
        "decision_count": len(decisions),
        "status_counts": dict(sorted(counts.items())),
        "reason_counts": dict(sorted(reason_counts.items())),
        "scope": (
            "Technical evidence decisions only. Nonblank decodable candidates remain "
            "unchanged pending visual review."
        ),
        "decisions": decisions,
    }

    args.write_json.parent.mkdir(parents=True, exist_ok=True)
    args.write_json.write_text(json.dumps(payload, indent=2) + "\n")

    lines = [
        "# Lane A Evidence-Backed Review Decisions",
        "",
        "This decision layer records only statuses justified by completed technical review.",
        "It does not promote nonblank candidates to valid_render, usable, or alternate.",
        "",
        "## Summary",
        "",
        f"- Decisions recorded: **{len(decisions)}**",
        f"- Reject / blank render: **{counts.get('reject', 0)}**",
        f"- Decode issue (image decode failure or Ranger reconstruction limitation): **{counts.get('decode_issue', 0)}**",
        "",
        "## Policy",
        "",
        "- Blank renders are rejected because they contain no visible donor art, unless the",
        "  Ranger cell references tiles missing from its own group (renderer limitation):",
        "  those are decode_issue / ranger_reconstruction_issue, never reject.",
        "- Decode failures are marked decode_issue because an actual decode attempt failed.",
        "- Decodable nonblank assets remain pending visual inspection.",
        "- This file is an override/decision layer; it does not modify Platinum resources.",
    ]
    args.write_md.write_text("\n".join(lines) + "\n")

    print("Decisions:", len(decisions))
    print("Status counts:", dict(counts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
