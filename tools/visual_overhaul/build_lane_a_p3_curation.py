#!/usr/bin/env python3
"""Curate Lane A P3 native HGSS/Diamond PNG representatives.

P3 contains source-native PNG assets that already passed Lane A render-integrity
(nonblank/decodable) checks. Unlike reconstructed Ranger frames, these PNGs do
not require a reconstruction-validity judgment. This pass promotes P3
representatives to usable only when queue metadata supplies a recognized,
plausible Platinum target family.

This is donor curation only. It does not choose a preferred donor, mark exact
duplicates as alternate, or modify Platinum resources.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

ALLOWED_GROUPS = {
    ("diamond", "pokemon_battle"),
    ("diamond", "trainer_graphics"),
    ("hgss", "field"),
    ("hgss", "graphics"),
    ("hgss", "pokemon_battle"),
    ("hgss", "pokemon_icons"),
}

PLAUSIBLE_TAGS = {
    "battle_back", "battle_front", "pokemon", "portrait", "trainer",
    "field", "overworld", "graphics", "ui", "party_icon", "summary_icon",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--queue", required=True, type=Path)
    ap.add_argument("--priority", required=True, type=Path)
    ap.add_argument("--integrity", required=True, type=Path)
    ap.add_argument("--review-set", required=True, type=Path)
    ap.add_argument("--write-json", required=True, type=Path)
    ap.add_argument("--write-md", required=True, type=Path)
    args = ap.parse_args()

    queue = json.loads(args.queue.read_text())
    priority = json.loads(args.priority.read_text())
    integrity = json.loads(args.integrity.read_text())
    review_set = json.loads(args.review_set.read_text())

    q = {r["asset_id"]: r for r in queue["records"]}
    integ = {r["asset_id"]: r for r in integrity["records"]}
    cand = {r["representative_asset_id"]: r for r in review_set["candidates"]}

    p3 = [r for r in priority["records"] if r["priority"] == "P3_native_source_png"]
    decisions = []
    errors = []

    for row in p3:
        aid = row["asset_id"]
        qr = q.get(aid)
        ir = integ.get(aid)
        cr = cand.get(aid)
        if not qr or not ir or not cr:
            errors.append(f"missing evidence for {aid}")
            continue

        tags = sorted(qr.get("target_tags") or [])
        key = (qr.get("source_id"), qr.get("group"))
        plausible = bool(set(tags) & PLAUSIBLE_TAGS)
        native_png = qr.get("asset_type") == "source_png"
        nonblank = ir.get("technical_state") == "verified_nonblank"
        recognized = key in ALLOWED_GROUPS

        if native_png and nonblank and plausible and recognized:
            status = "usable"
            reason_code = "native_png_plausible_platinum_use"
            reason = (
                "Source-native PNG is decodable/nonblank and its donor semantic "
                "group/target tags identify at least one plausible Platinum visual use."
            )
        else:
            status = "reject"
            reason_code = "p3_semantic_or_integrity_mismatch"
            reason = (
                "P3 representative failed the native-PNG, nonblank, recognized-group, "
                "or plausible-target invariant required by this pass."
            )

        decisions.append({
            "asset_id": aid,
            "source_id": qr.get("source_id"),
            "group": qr.get("group"),
            "source_path": qr.get("source_path"),
            "review_status": status,
            "reason_code": reason_code,
            "reason": reason,
            "target_tags": tags,
            "technical_state": ir.get("technical_state"),
            "visual_key": cr.get("visual_key"),
            "duplicate_count": cr.get("duplicate_count"),
            "duplicate_member_asset_ids": cr.get("member_asset_ids"),
            "width": row.get("width"),
            "height": row.get("height"),
            "alpha_bbox": row.get("alpha_bbox"),
        })

    if errors:
        raise SystemExit("\n".join(errors[:20]))

    if len(decisions) != 3165:
        raise SystemExit(f"P3 coverage mismatch: {len(decisions)} != 3165")
    if len({d["asset_id"] for d in decisions}) != len(decisions):
        raise SystemExit("duplicate P3 decision asset_id")

    counts = Counter(d["review_status"] for d in decisions)
    by_group = Counter((d["source_id"], d["group"], d["review_status"]) for d in decisions)

    payload = {
        "schema_version": 1,
        "lane": "A_render_ready",
        "priority": "P3_native_source_png",
        "scope": (
            "Semantic donor curation only. Native PNG + verified nonblank + recognized "
            "semantic target is enough for usable; no preferred/alternate selection and "
            "no Platinum resource writes."
        ),
        "candidate_count": len(decisions),
        "status_counts": dict(sorted(counts.items())),
        "decisions": decisions,
    }
    args.write_json.parent.mkdir(parents=True, exist_ok=True)
    args.write_json.write_text(json.dumps(payload, indent=2) + "\n")

    lines = [
        "# Lane A P3 Native PNG Curation",
        "",
        "Semantic curation of the native HGSS/Diamond PNG representatives.",
        "No Platinum resource is modified and no preferred donor is selected.",
        "",
        "## Summary",
        "",
        f"- P3 representatives curated: **{len(decisions)}**",
        f"- usable: **{counts.get('usable', 0)}**",
        f"- reject: **{counts.get('reject', 0)}**",
        "",
        "## Decision rule",
        "",
        "A P3 representative is usable when all four conditions hold:",
        "",
        "1. it is a source-native PNG;",
        "2. Lane A integrity recorded it as verified nonblank;",
        "3. its source/group is one of the known P3 semantic families; and",
        "4. its target tags identify a plausible Platinum visual use.",
        "",
        "This does not mean the asset is preferred. Exact duplicates and competing",
        "donors remain available until the later preferred/alternate selection pass.",
        "",
        "## By semantic group",
        "",
        "| Source | Group | Status | Candidates |",
        "|---|---|---|---:|",
    ]
    for (source, group, status), count in sorted(by_group.items()):
        lines.append(f"| {source} | {group} | {status} | {count} |")

    args.write_md.write_text("\n".join(lines) + "\n")
    print("P3 decisions:", len(decisions), dict(counts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
