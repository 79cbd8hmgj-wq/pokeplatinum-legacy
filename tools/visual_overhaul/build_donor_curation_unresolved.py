#!/usr/bin/env python3
"""List every record still decode_issue across all lanes, grouped by family, with the recorded technical evidence."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def family(x: dict) -> str:
    p, s = x["source_path"], x["source_id"]
    if s == "ranger2" and x["asset_type"] == "pokemon_sprite_frame":
        return "ranger Pokemon cells: OAM tile data absent from the package or ambiguous between sibling resources"
    ext = p.rsplit(".", 1)[-1].lower()
    if s == "pmd_sky":
        return f"pmd_sky .{ext}"
    if s == "hgss":
        return "hgss GF bitmap font (.bin)" if "/font/" in p else f"hgss .{ext}"
    if s == "ranger2":
        return "ranger2 " + (p.split("data/")[-1].split("/")[0] if "data/" in p else p)
    return f"{s} .{ext}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", action="append", required=True)
    ap.add_argument("--write-json", type=Path, required=True)
    ap.add_argument("--write-md", type=Path, required=True)
    a = ap.parse_args()
    fam: dict[str, list] = defaultdict(list)
    for path in a.ledger:
        for x in json.loads(Path(path).read_text())["records"]:
            if x["review_status"] == "decode_issue":
                fam[family(x)].append({"asset_id": x["asset_id"], "source_path": x["source_path"], "reason_code": x.get("reason_code"),
                                       "reason": x.get("reason")})
    total = sum(len(v) for v in fam.values())
    a.write_json.write_text(json.dumps({"schema_version": 1, "unresolved_count": total,
                                        "families": {k: {"count": len(v), "records": v} for k, v in sorted(fam.items(), key=lambda t: -len(t[1]))}}, indent=1) + "\n")
    md = ["# Donor Curation — Unresolved Records", "", "Records still `decode_issue` after all recovery passes (nothing here is rejected merely for failing to decode).", "",
          f"- Total: **{total}**", "", "| Family | Records |", "|---|---:|"] + [f"| {k} | {len(v)} |" for k, v in sorted(fam.items(), key=lambda t: -len(t[1]))]
    a.write_md.write_text("\n".join(md) + "\n")
    print(total)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
