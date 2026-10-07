#!/usr/bin/env python3
"""Build the final per-asset Lane A curation ledger.

Evidence sources:
- P1 Ranger reconstruction review: valid_render/decode_issue at unique visual rep level.
- P3 native PNG curation: usable/reject at unique visual rep level.
- Lane A technical decisions: blank/decode failures outside the nonblank review set.

Policy:
- A structurally valid Ranger Pokémon frame has an obvious plausible Platinum use
  as Pokémon animation/sprite donor material, so P1 valid_render -> usable.
- P1 decode_issue remains decode_issue.
- P3 decisions are preserved.
- Exact-pixel duplicate members inherit the representative's curation state.
- Technical blank/decode decisions are preserved verbatim.
- Nothing here selects a preferred donor, marks a competing valid donor alternate,
  or modifies Platinum resources.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--queue", required=True, type=Path)
    ap.add_argument("--p1", required=True, type=Path)
    ap.add_argument("--p3", required=True, type=Path)
    ap.add_argument("--technical-decisions", required=True, type=Path)
    ap.add_argument("--write-json", required=True, type=Path)
    ap.add_argument("--write-md", required=True, type=Path)
    args = ap.parse_args()

    queue = json.loads(args.queue.read_text())
    p1 = json.loads(args.p1.read_text())
    p3 = json.loads(args.p3.read_text())
    tech = json.loads(args.technical_decisions.read_text())

    lane_a_ids = {
        r["asset_id"] for r in queue["records"]
        if r.get("lane") == "A_render_ready"
    }
    q = {r["asset_id"]: r for r in queue["records"]}

    out = {}
    provenance = {}

    def assign(aid: str, status: str, reason_code: str, reason: str, source: str) -> None:
        if aid in out:
            raise SystemExit(f"duplicate Lane A final decision: {aid}")
        out[aid] = {
            "asset_id": aid,
            "source_id": q.get(aid, {}).get("source_id"),
            "asset_type": q.get(aid, {}).get("asset_type"),
            "species_dex": q.get(aid, {}).get("species_dex"),
            "group": q.get(aid, {}).get("group"),
            "source_path": q.get(aid, {}).get("source_path"),
            "render_path": q.get(aid, {}).get("render_path"),
            "target_tags": q.get(aid, {}).get("target_tags") or [],
            "review_status": status,
            "reason_code": reason_code,
            "reason": reason,
            "decision_source": source,
        }
        provenance[aid] = source

    # P1: Ranger frames. Promote reconstruction-valid frames to usable because the
    # asset class itself supplies a plausible Platinum Pokémon-animation use.
    for rec in p1["records"]:
        p1_status = rec["review_status"]
        if p1_status == "valid_render":
            status = "usable"
            code = "ranger_valid_frame_plausible_animation_use"
            reason = (
                "Ranger frame is structurally validated and is Pokémon sprite/animation "
                "material, giving it at least one plausible Platinum visual use."
            )
        elif p1_status == "decode_issue":
            status = "decode_issue"
            code = rec.get("reason_code") or "ranger_reconstruction_issue"
            reason = rec.get("reason") or "Ranger frame reconstruction remains unresolved."
        else:
            raise SystemExit(f"unexpected P1 status {p1_status}: {rec['asset_id']}")

        for aid in rec["duplicate_member_asset_ids"]:
            assign(aid, status, code, reason, "LANE_A_P1_VISUAL_REVIEW")

    # P3: native PNG semantic decisions, propagated to exact-pixel duplicates.
    for rec in p3["decisions"]:
        status = rec["review_status"]
        if status not in {"usable", "reject"}:
            raise SystemExit(f"unexpected P3 status {status}: {rec['asset_id']}")
        for aid in rec["duplicate_member_asset_ids"]:
            assign(
                aid,
                status,
                rec.get("reason_code") or "p3_native_png_curation",
                rec.get("reason") or "Native PNG semantic curation.",
                "LANE_A_P3_CURATION",
            )

    # Remaining Lane A technical decisions: blank renders and decode failures.
    for rec in tech["decisions"]:
        status = rec["review_status"]
        if status not in {"reject", "decode_issue"}:
            raise SystemExit(f"unexpected technical status {status}: {rec['asset_id']}")
        assign(
            rec["asset_id"],
            status,
            rec.get("reason_code") or "lane_a_technical_decision",
            rec.get("reason") or "Lane A evidence-backed technical decision.",
            "LANE_A_REVIEW_DECISIONS",
        )

    decided = set(out)
    missing = sorted(lane_a_ids - decided)
    extra = sorted(decided - lane_a_ids)
    if missing or extra:
        raise SystemExit(
            f"Lane A coverage mismatch missing={len(missing)} extra={len(extra)} "
            f"first_missing={missing[:1]} first_extra={extra[:1]}"
        )
    if len(decided) != 40559:
        raise SystemExit(f"Lane A decision count mismatch: {len(decided)} != 40559")

    records = [out[aid] for aid in sorted(out)]
    counts = Counter(r["review_status"] for r in records)
    source_counts = {}
    for source in sorted({r["source_id"] for r in records}):
        source_counts[source] = dict(sorted(Counter(
            r["review_status"] for r in records if r["source_id"] == source
        ).items()))

    payload = {
        "schema_version": 1,
        "lane": "A_render_ready",
        "scope": (
            "Complete Lane A donor curation. Every Lane A asset receives a final current "
            "curation state. No preferred/alternate selection and no Platinum resource writes."
        ),
        "asset_count": len(records),
        "status_counts": dict(sorted(counts.items())),
        "source_status_counts": source_counts,
        "records": records,
    }

    args.write_json.parent.mkdir(parents=True, exist_ok=True)
    args.write_json.write_text(json.dumps(payload, indent=2) + "\n")

    lines = [
        "# Lane A Final Curation",
        "",
        "Complete per-asset curation ledger for Lane A. No Platinum resources are modified.",
        "",
        "## Summary",
        "",
        f"- Lane A assets curated: **{len(records)}**",
    ]
    for status, count in sorted(counts.items()):
        lines.append(f"- {status}: **{count}**")

    lines += [
        "",
        "## By source",
        "",
        "| Source | usable | alternate | reject | decode_issue |",
        "|---|---:|---:|---:|---:|",
    ]
    for source, c in source_counts.items():
        lines.append(
            f"| {source} | {c.get('usable', 0)} | {c.get('alternate', 0)} | "
            f"{c.get('reject', 0)} | {c.get('decode_issue', 0)} |"
        )

    lines += [
        "",
        "## Policy",
        "",
        "- P1 structurally valid Ranger Pokémon frames are usable donor candidates because",
        "  the asset class itself supplies a plausible animation/sprite use.",
        "- P1 reconstruction failures remain decode_issue.",
        "- P3 native PNG semantic decisions are preserved.",
        "- Exact-pixel duplicate members inherit the representative decision.",
        "- Technical blanks/decode failures preserve their evidence-backed decisions.",
        "- usable means plausible donor use, not preferred selection.",
        "- Preferred/alternate ranking across competing usable donors is deferred until",
        "  the full donor database is curated.",
    ]
    args.write_md.write_text("\n".join(lines) + "\n")

    print("Lane A final:", len(records), dict(counts))
    print("By source:", source_counts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
