#!/usr/bin/env python3
"""Build the Lane A P1 (Ranger species render) visual-review decision ledger.

Validation only. Inputs are the generated Lane A artifacts plus the Ranger
structural-validation ledger emitted by diagnose_ranger_structure.py --corpus.
Nothing here imports donor assets, edits Platinum resources, or picks
preferred/usable/alternate donors.

Rules, in precedence order:
  1. Every duplicate member's NCER cell has all of its OAM tile references inside
     the character data of its own group (RANGER_RENDER_STRUCTURAL_VALIDATION.json)
     -> valid_render.  The reader/mapping behind that is validated pixel-exact
     against paired NCGR/NCBR resources (see RANGER_RENDERER_ROOT_CAUSE.md).
  2. Some member cell references tiles that do not exist in its group's character
     data (they live in another resource) -> decode_issue, reason
     ranger_reconstruction_issue.  Renderer-side limitation; the donor asset is
     NOT proven invalid, so nothing here is `reject`.
valid_render means reconstruction validity only, never usable/alternate.
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VO = ROOT / "docs" / "visual_overhaul"

STRUCT = VO / "RANGER_RENDER_STRUCTURAL_VALIDATION.json"
PRIORITY = VO / "LANE_A_VISUAL_REVIEW_PRIORITY.json"
SHEETS = VO / "LANE_A_REVIEW_SHEETS.json"
REVIEW_SET = VO / "LANE_A_VISUAL_REVIEW_SET.json"
DECISIONS = VO / "LANE_A_REVIEW_DECISIONS.json"
OUT_JSON = VO / "LANE_A_P1_VISUAL_REVIEW.json"
OUT_MD = VO / "LANE_A_P1_VISUAL_REVIEW.md"

P1 = "P1_ranger_species_render"
RANGER_ID_RE = re.compile(
    r"^ranger2:pokemon:(?P<species>\d{3}):(?P<variant>\d{2}):(?P<group>[^:]+):cell_(?P<cell>\d+)$"
)

REASONS = {
    "valid_render": ("structurally_verified_reconstruction",
                     "All OAM tile references of every duplicate member resolve inside the "
                     "group's own character data under the validated Ranger mapping "
                     "(scanline NCBR raster width inferred, palette row applied)."),
    "decode_issue": ("ranger_reconstruction_issue",
                     "At least one OAM object of a duplicate member references tiles that "
                     "are absent from its group's character data (they live in another "
                     "resource), so this frame cannot be fully reconstructed from the group "
                     "alone. The donor asset has NOT been proven invalid; not a reject."),
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

    struct = load(STRUCT)["group_ledger"]
    p1 = {r["asset_id"]: r for r in prio["records"] if r["priority"] == P1}
    members = {c["representative_asset_id"]: c["member_asset_ids"] for c in rset["candidates"]}
    prior_ids = {d["asset_id"] for d in decisions["decisions"]}

    def member_ok(asset_id):
        m = RANGER_ID_RE.match(asset_id)
        if not m:
            raise SystemExit("unparseable ranger asset id: " + asset_id)
        g = struct[m.group("group")]
        return int(m.group("cell")) not in set(g["oob_cells"]), g

    records = []
    seen = set()
    sheet_ids = [s["sheet_id"] for s in sheets["sheets"] if s["kind"] == "species"]
    for sh in sheets["sheets"]:
        if sh["kind"] != "species":
            continue
        for e in sh["entries"]:
            aid = e["asset_id"]
            if aid in seen:
                raise SystemExit("asset on more than one sheet slot: " + aid)
            seen.add(aid)
            r = p1[aid]
            mem = members[aid]
            checks = [member_ok(m) for m in mem]
            ok = all(c[0] for c in checks)
            status = "valid_render" if ok else "decode_issue"
            code, reason = REASONS[status]
            _, g = member_ok(aid)
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
                    "method": "structural_validation",
                    "sheet_path": sh["path"],
                    "char_source": g["src"],
                    "raster_width_tiles": g["raster_w"],
                    "members_with_missing_tiles": sum(1 for c in checks if not c[0]),
                    "alpha_bbox": r["alpha_bbox"],
                    "alpha_bbox_area": bbox_area(r["alpha_bbox"]),
                    "unique_rgba_colors": r["unique_rgba_colors"],
                },
            })

    # ---- validation: every P1 candidate accounted for exactly once ----
    errors = []
    if set(p1) != seen or len(records) != len(p1):
        errors.append("P1 candidates not covered exactly once: %d records vs %d P1"
                      % (len(records), len(p1)))
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
        "scope": "Reconstruction validation only. No donor import, no usable/alternate selection, "
                 "no Platinum resource changes. Preserves LANE_A_REVIEW_DECISIONS.json unchanged.",
        "inputs": [str(p.relative_to(ROOT)) for p in (STRUCT, PRIORITY, SHEETS, REVIEW_SET, DECISIONS)],
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
    md.append("- decode_issue (unresolved Ranger reconstruction issue): **%d**" % counts["decode_issue"])
    md.append("- needs_review (ambiguous, left open): **%d**" % counts["needs_review"])
    md.append("- reject: **%d** (no donor asset independently proven invalid in this pass)" % counts["reject"])
    md.append("- Assets covered incl. exact-duplicate members: **%d**\n" % len(dup_members))
    md.append("## Findings\n")
    md.append("- Root cause of the earlier scrambled output was in the Ranger renderer, not the "
              "donor assets (see `RANGER_RENDERER_ROOT_CAUSE.md`). After the fix, status is "
              "derived deterministically from structural validation rather than by-eye slot "
              "ranges.")
    md.append("- `valid_render`: every duplicate member's cell resolves all OAM tile references "
              "inside its own group's character data. Reconstruction validity only; **not** "
              "usable/alternate for Platinum, and no semantic/use review was done.")
    md.append("- `decode_issue` (`ranger_reconstruction_issue`): some member cell references "
              "tiles absent from its own group (they live in another resource). Renderer-side "
              "limitation; the donor asset is not proven invalid. Nothing in this pass is "
              "`reject`.")
    md.append("- `needs_review`: none; the old sparse-bbox rule only existed because of "
              "contact-sheet judging limits and is superseded by the structural rule.\n")
    md.append("## Species with any valid_render\n")
    md.append(", ".join("%03d" % d for d in ok) + "\n")
    md.append("## Per-species counts\n")
    md.append("| Dex | valid_render | decode_issue | needs_review |")
    md.append("|---:|---:|---:|---:|")
    for d in sorted(by_species):
        c = by_species[d]
        md.append("| %03d | %d | %d | %d |" % (d, c["valid_render"], c["decode_issue"], c["needs_review"]))
    with open(OUT_MD, "w") as f:
        f.write("\n".join(md) + "\n")
    print(json.dumps(out["status_counts"]), len(records), len(by_species), len(dup_members))


if __name__ == "__main__":
    main()
