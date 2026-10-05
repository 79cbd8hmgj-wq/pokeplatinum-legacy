#!/usr/bin/env python3
"""Build the Lane A P1 (Ranger species render) visual-review decision ledger.

Visual validation only. Inputs are the generated Lane A artifacts; the visual
findings below were recorded by direct inspection of every P1 contact sheet
(docs/visual_overhaul/review/lane_a/species/*.png). Nothing here imports donor
assets, edits Platinum resources, or picks preferred/usable/alternate donors.

Rules, in precedence order:
  1. COHERENT_SLOTS   -> valid_render (reconstruction visibly appears correct).
  2. alpha-bbox area <= SPARSE_MAX_BBOX_AREA -> needs_review (too little visible
     art on a contact-sheet thumbnail to judge as correct or broken).
  3. everything else on a P1 sheet -> reject (visibly scrambled / horizontally
     sliced / fragmented reconstruction; not a recognisable complete frame).
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VO = ROOT / "docs" / "visual_overhaul"

PRIORITY = VO / "LANE_A_VISUAL_REVIEW_PRIORITY.json"
SHEETS = VO / "LANE_A_REVIEW_SHEETS.json"
REVIEW_SET = VO / "LANE_A_VISUAL_REVIEW_SET.json"
DECISIONS = VO / "LANE_A_REVIEW_DECISIONS.json"
OUT_JSON = VO / "LANE_A_P1_VISUAL_REVIEW.json"
OUT_MD = VO / "LANE_A_P1_VISUAL_REVIEW.md"

P1 = "P1_ranger_species_render"
SPARSE_MAX_BBOX_AREA = 256

# Sheet slots whose renders visibly reconstruct a coherent Pokemon/object frame.
# (sheet_id, first_slot, last_slot, what_was_seen)
COHERENT_SLOTS = [
    ("species:421:p001", 1, 36, "Cherubi body frames render as clean, recognisable sprites"),
    ("species:422:p001", 45, 76, "Shellos (west sea) frames render as clean, recognisable sprites"),
    ("species:465:p001", 29, 80, "Tangrowth frames render as clean, recognisable sprites"),
    ("species:465:p002", 1, 8, "Tangrowth frames render as clean, recognisable sprites"),
    ("species:490:p001", 33, 33, "small round icon-style frame renders cleanly (Manaphy-egg-like)"),
]

REASONS = {
    "valid_render": ("coherent_reconstruction",
                     "Contact-sheet inspection: reconstruction visibly appears correct."),
    "reject": ("scrambled_reconstruction",
               "Contact-sheet inspection: horizontally sliced / scrambled / fragmented "
               "tile reconstruction; not a recognisable complete frame."),
    "needs_review": ("too_sparse_to_judge",
                     "Alpha bbox area <= %d px; too little visible art at contact-sheet "
                     "scale to call correct or broken." % SPARSE_MAX_BBOX_AREA),
}


def load(p):
    with open(p) as f:
        return json.load(f)


def bbox_area(b):
    return (b[2] - b[0]) * (b[3] - b[1])


def main():
    prio = load(PRIORITY)
    sheets = load(SHEETS)
    rset = load(REVIEW_SET)
    decisions = load(DECISIONS)

    p1 = {r["asset_id"]: r for r in prio["records"] if r["priority"] == P1}
    members = {c["representative_asset_id"]: c["member_asset_ids"] for c in rset["candidates"]}
    prior_ids = {d["asset_id"] for d in decisions["decisions"]}

    coherent = {}
    for sid, lo, hi, note in COHERENT_SLOTS:
        for s in range(lo, hi + 1):
            coherent[(sid, s)] = note

    records = []
    seen = set()
    sheet_ids = [s["sheet_id"] for s in sheets["sheets"] if s["kind"] == "species"]
    coherent_hit = set()
    for sh in sheets["sheets"]:
        if sh["kind"] != "species":
            continue
        for e in sh["entries"]:
            aid = e["asset_id"]
            if aid in seen:
                raise SystemExit("asset on more than one sheet slot: " + aid)
            seen.add(aid)
            r = p1[aid]
            key = (sh["sheet_id"], e["slot"])
            if key in coherent:
                status = "valid_render"
                coherent_hit.add(key)
                note = coherent[key]
            elif bbox_area(r["alpha_bbox"]) <= SPARSE_MAX_BBOX_AREA:
                status = "needs_review"
                note = None
            else:
                status = "reject"
                note = None
            code, reason = REASONS[status]
            mem = members[aid]
            records.append({
                "asset_id": aid,
                "species_dex": r["species_dex"],
                "source": r["source_id"],
                "sheet_id": sh["sheet_id"],
                "sheet_slot": e["slot"],
                "visual_key": r["visual_key"],
                "duplicate_count": r["duplicate_count"],
                "duplicate_member_asset_ids": mem,
                "review_status": status,
                "reason_code": code,
                "reason": reason,
                "evidence": {
                    "method": "contact_sheet_visual_inspection",
                    "sheet_path": sh["path"],
                    "alpha_bbox": r["alpha_bbox"],
                    "alpha_bbox_area": bbox_area(r["alpha_bbox"]),
                    "unique_rgba_colors": r["unique_rgba_colors"],
                    **({"observation": note} if note else {}),
                },
            })

    # ---- validation: every P1 candidate accounted for exactly once ----
    errors = []
    if set(p1) != seen or len(records) != len(p1):
        errors.append("P1 candidates not covered exactly once: %d records vs %d P1"
                      % (len(records), len(p1)))
    if coherent_hit != set(coherent):
        errors.append("coherent slot list references slots that do not exist: %s"
                      % sorted(set(coherent) - coherent_hit)[:5])
    if prior_ids & seen:
        errors.append("P1 records overlap preserved blank/decode decisions: %d"
                      % len(prior_ids & seen))
    dup_members = set()
    for rec in records:
        if rec["asset_id"] not in rec["duplicate_member_asset_ids"]:
            errors.append("representative missing from its own duplicate members: " + rec["asset_id"])
        if len(rec["duplicate_member_asset_ids"]) != rec["duplicate_count"]:
            errors.append("duplicate_count mismatch: " + rec["asset_id"])
        dup_members.update(rec["duplicate_member_asset_ids"])
    if dup_members & prior_ids:
        errors.append("duplicate members collide with preserved decisions: %d"
                      % len(dup_members & prior_ids))
    if errors:
        for m in errors:
            print("VALIDATION FAILED:", m, file=sys.stderr)
        sys.exit(1)

    records.sort(key=lambda x: (x["species_dex"], x["sheet_id"], x["sheet_slot"]))
    counts = Counter(r["review_status"] for r in records)
    by_species = defaultdict(Counter)
    for r in records:
        by_species[r["species_dex"]][r["review_status"]] += 1

    out = {
        "schema_version": 1,
        "lane": "A_render_ready",
        "priority": P1,
        "scope": "Visual validation only. No donor import, no usable/alternate selection, "
                 "no Platinum resource changes. Preserves LANE_A_REVIEW_DECISIONS.json unchanged.",
        "inputs": [str(p.relative_to(ROOT)) for p in (PRIORITY, SHEETS, REVIEW_SET, DECISIONS)],
        "sparse_max_bbox_area": SPARSE_MAX_BBOX_AREA,
        "coherent_slots": [{"sheet_id": s, "first_slot": a, "last_slot": b, "observation": n}
                           for s, a, b, n in COHERENT_SLOTS],
        "candidate_count": len(records),
        "sheet_count": len(sheet_ids),
        "species_count": len(by_species),
        "status_counts": dict(sorted(counts.items())),
        "assets_covered_including_duplicates": len(dup_members),
        "records": records,
    }
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=1, sort_keys=False)
        f.write("\n")

    ok = sorted(d for d, c in by_species.items() if c["valid_render"])
    md = []
    md.append("# Lane A P1 Visual Review (Ranger species renders)\n")
    md.append("Visual validation only. No donor assets imported, no Platinum resources "
              "changed, no usable/alternate/preferred-donor selection made.\n")
    md.append("## Summary\n")
    md.append("- P1 candidates reviewed: **%d** (each accounted for exactly once)" % len(records))
    md.append("- Contact sheets inspected: **%d**; species: **%d**" % (len(sheet_ids), len(by_species)))
    md.append("- valid_render: **%d**" % counts["valid_render"])
    md.append("- reject: **%d**" % counts["reject"])
    md.append("- decode_issue: **%d** (none newly assigned; see note)" % counts["decode_issue"])
    md.append("- needs_review (ambiguous, left open): **%d**" % counts["needs_review"])
    md.append("- Assets covered incl. exact-duplicate members: **%d**\n" % len(dup_members))
    md.append("## Findings\n")
    md.append("- The overwhelming majority of Ranger frames reconstruct as horizontally "
              "sliced / scrambled tile soup, consistent with the still-open reconstruction "
              "concern recorded in `DDA1J_RANGER_RENDER_VISUAL_QA.md`. These are `reject`.")
    md.append("- Only these slots visibly reconstruct correctly (`valid_render`):")
    for s, a, b, n in COHERENT_SLOTS:
        md.append("  - `%s` slots %d-%d: %s" % (s, a, b, n))
    md.append("- `valid_render` means the pixels look like a correct reconstruction only. "
              "It does **not** mean usable/alternate for Platinum; no semantic/use review was done.")
    md.append("- Slots with alpha bbox area <= %d px are `needs_review`: too little visible "
              "art to judge at contact-sheet scale. This is a deterministic metadata rule, "
              "not a visual verdict." % SPARSE_MAX_BBOX_AREA)
    md.append("- No `decode_issue` was assigned: no decode failure occurred in this pass, and "
              "the root cause of the scrambling (stride/geometry vs. other) was not isolated "
              "here. Treating the scrambling as a reconstruction defect is a hypothesis for "
              "the renderer owner, not a conclusion of this review.\n")
    md.append("## Limits of this review\n")
    md.append("- Judgement was made on 96px contact-sheet thumbnails; the raw per-frame PNGs "
              "are CI artifacts not present in the repo. The `valid_render` slots are clear at "
              "that scale; borderline cases fall to `needs_review`, not `valid_render`.")
    md.append("- Species sheet slot -> `asset_id` mapping comes from `LANE_A_REVIEW_SHEETS.json`.\n")
    md.append("## Species with any valid_render\n")
    md.append(", ".join("%03d" % d for d in ok) + "\n")
    md.append("## Per-species counts\n")
    md.append("| Dex | valid_render | reject | needs_review |")
    md.append("|---:|---:|---:|---:|")
    for d in sorted(by_species):
        c = by_species[d]
        md.append("| %03d | %d | %d | %d |" % (d, c["valid_render"], c["reject"], c["needs_review"]))
    with open(OUT_MD, "w") as f:
        f.write("\n".join(md) + "\n")
    print(json.dumps(out["status_counts"]), len(records), len(by_species), len(dup_members))


if __name__ == "__main__":
    main()
