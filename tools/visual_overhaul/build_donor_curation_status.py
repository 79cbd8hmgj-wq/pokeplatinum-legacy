#!/usr/bin/env python3
"""Cross-lane donor curation status: proves every catalog asset has exactly one curation record.

Inputs: Lane A final, Lane B recovered, Lane C/D/E recovered curation ledgers + the donor catalog ids.
Output: per-lane/per-source status counts and the coverage invariants (no drops, no duplicates,
no unreviewed).  No Platinum resources are modified and no preferred donor is selected.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", type=Path, required=True)
    ap.add_argument("--ledger", action="append", required=True, help="label=path")
    ap.add_argument("--write-json", type=Path, required=True)
    ap.add_argument("--write-md", type=Path, required=True)
    a = ap.parse_args()
    cat_ids = [x["asset_id"] for x in json.loads(a.catalog.read_text())["assets"]]
    seen: dict[str, str] = {}
    per_label: dict[str, Counter] = {}
    per_source: dict[str, Counter] = {}
    dup = []
    for spec in a.ledger:
        label, path = spec.split("=", 1)
        recs = json.loads(Path(path).read_text())["records"]
        per_label[label] = Counter(r["review_status"] for r in recs)
        for r in recs:
            if r["asset_id"] in seen:
                dup.append(r["asset_id"])
            seen[r["asset_id"]] = label
            per_source.setdefault(r["source_id"], Counter())[r["review_status"]] += 1
    missing = sorted(set(cat_ids) - set(seen))
    extra = sorted(set(seen) - set(cat_ids))
    total = Counter()
    for c in per_label.values():
        total.update(c)
    inv = {"catalog_assets": len(cat_ids), "curated_assets": len(seen), "missing": len(missing), "extra": len(extra),
           "duplicates": len(dup), "unreviewed": total.get("unreviewed", 0),
           "complete": not missing and not extra and not dup and not total.get("unreviewed", 0)}
    payload = {"schema_version": 1, "invariants": inv, "status_totals": dict(sorted(total.items())),
               "ledger_status_counts": {k: dict(sorted(v.items())) for k, v in per_label.items()},
               "source_status_counts": {k: dict(sorted(v.items())) for k, v in sorted(per_source.items())},
               "missing_sample": missing[:20], "extra_sample": extra[:20], "duplicate_sample": dup[:20]}
    a.write_json.write_text(json.dumps(payload, indent=1) + "\n")
    md = ["# Donor Curation Status", "", "Cross-lane coverage proof. No Platinum resources are modified; no preferred donor is selected.", "",
          "## Invariants", ""] + [f"- {k}: **{v}**" for k, v in inv.items()]
    md += ["", "## Status totals", ""] + [f"- {k}: **{v}**" for k, v in sorted(total.items())]
    md += ["", "## By ledger", "", "| Ledger | " + " | ".join(sorted(total)) + " |", "|---|" + "---:|" * len(total)]
    for k, v in per_label.items():
        md.append(f"| {k} | " + " | ".join(str(v.get(s, 0)) for s in sorted(total)) + " |")
    md += ["", "## By source", "", "| Source | " + " | ".join(sorted(total)) + " |", "|---|" + "---:|" * len(total)]
    for k, v in sorted(per_source.items()):
        md.append(f"| {k} | " + " | ".join(str(v.get(s, 0)) for s in sorted(total)) + " |")
    a.write_md.write_text("\n".join(md) + "\n")
    print(inv, dict(total))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
