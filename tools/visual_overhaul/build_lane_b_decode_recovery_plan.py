#!/usr/bin/env python3
"""Lane B decode-recovery plan: the original 7,183 decode_issue records by family, with current disposition.

A family = (source, asset_type, group, extension/member kind, path family).  For each family the plan
records its recovery route, the method/tool that recovered it, and how many records are now
usable / reject / still decode_issue.  Deterministic; no Platinum resources are modified.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def member_kind(r: dict) -> str:
    aid = r["asset_id"]
    if ":embedded:" in aid:
        m = aid.rsplit(":", 1)[1]
        return "member_N" if m.startswith("member_") else m.rsplit(".", 1)[-1]
    name = r["source_path"].rsplit("/", 1)[-1]
    return name.rsplit(".", 1)[-1].lower() if "." in name else "(none)"


def path_family(r: dict) -> str:
    p = r["source_path"].split("/")
    if r["source_id"] == "ranger2" and "data" in p:
        i = p.index("data")
        return "/".join(p[i + 1:i + 3])
    return "/".join(p[:3])


METHOD = {
    "source_png_equivalent": "same-stem native PNG already curated usable (resolve_lane_b_source_png_equivalents.py)",
    "nitro_2d_decode": "Diamond icon NCGR sentinel geometry (recover_lane_b_diamond_icons.py); otherpoke NCGR/NCLR pairing from decomp pokemon.c with back-to-front LCG decrypt (recover_lane_b_nitro2d_pairs.py)",
    "pmd_format_decode": "SkyTemple reference decoder (recover_lane_b_pmd_sky.py)",
    "ranger_embedded_decode": "Ranger LZ10->NARC->NCLR/NCBR/NCGR/NCER render incl. 1D OBJ mapping + sentinel NCGR (recover_lane_b_ranger_embedded.py); map chips (recover_lane_b_ranger_maps.py)",
    "container_unpack_then_decode": "same package pipelines as ranger_embedded_decode, applied at package level",
    "format_context_unknown": "evidence-based non-art classification (classify_lane_b_support_files.py)",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", type=Path, required=True)
    ap.add_argument("--current", type=Path, required=True)
    ap.add_argument("--write-json", type=Path, required=True)
    ap.add_argument("--write-md", type=Path, required=True)
    a = ap.parse_args()
    audit = json.loads(a.audit.read_text())["records"]
    cur = {r["asset_id"]: r for r in json.loads(a.current.read_text())["records"]}
    fam = defaultdict(lambda: Counter())
    for r in audit:
        c = cur[r["asset_id"]]
        key = (r["source_id"], r["asset_type"], r["group"], member_kind(r), path_family(r), r["recovery_route"])
        fam[key]["total"] += 1
        fam[key][c["review_status"]] += 1
    rows = []
    for k, c in fam.items():
        rows.append({"source": k[0], "asset_type": k[1], "group": k[2], "member_kind": k[3], "path_family": k[4],
                     "route": k[5], "total": c["total"], "usable": c["usable"], "reject": c["reject"],
                     "decode_issue": c["decode_issue"]})
    rows.sort(key=lambda x: (-x["total"], x["source"], x["path_family"], x["member_kind"]))
    tot = Counter()
    by_source = defaultdict(Counter)
    for r in rows:
        for s in ("total", "usable", "reject", "decode_issue"):
            tot[s] += r[s]
            by_source[r["source"]][s] += r[s]
    routes = defaultdict(Counter)
    for r in rows:
        for s in ("total", "usable", "reject", "decode_issue"):
            routes[r["route"]][s] += r[s]
    payload = {"schema_version": 1, "scope": "Lane B original decode_issue population and current disposition",
               "original_decode_issue": tot["total"], "current": {s: tot[s] for s in ("usable", "reject", "decode_issue")},
               "by_source": {k: dict(v) for k, v in sorted(by_source.items())},
               "by_route": {k: {"method": METHOD.get(k, ""), **dict(v)} for k, v in sorted(routes.items())},
               "families": rows}
    a.write_json.write_text(json.dumps(payload, indent=1) + "\n")
    md = ["# Lane B Decode Recovery Plan", "",
          "Original Lane B `decode_issue` population (7,183) grouped by family with current disposition.",
          "No Platinum resources are modified.", "",
          f"- Original decode_issue: **{tot['total']}**",
          f"- Now usable: **{tot['usable']}**  ·  reject: **{tot['reject']}**  ·  still decode_issue: **{tot['decode_issue']}**", "",
          "## By source", "", "| Source | Original | usable | reject | decode_issue |", "|---|---:|---:|---:|---:|"]
    md += [f"| {k} | {v['total']} | {v['usable']} | {v['reject']} | {v['decode_issue']} |" for k, v in sorted(by_source.items())]
    md += ["", "## By route and method", "", "| Route | Original | usable | reject | decode_issue | Method |", "|---|---:|---:|---:|---:|---|"]
    md += [f"| {k} | {v['total']} | {v['usable']} | {v['reject']} | {v['decode_issue']} | {METHOD.get(k, '')} |" for k, v in sorted(routes.items())]
    md += ["", "## Families still needing work", "", "| Source | Type | Group | Kind | Path family | Remaining |", "|---|---|---|---|---|---:|"]
    md += [f"| {r['source']} | {r['asset_type']} | {r['group']} | {r['member_kind']} | `{r['path_family']}` | {r['decode_issue']} |"
           for r in rows if r["decode_issue"]][:60]
    a.write_md.write_text("\n".join(md) + "\n")
    print(dict(tot))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
