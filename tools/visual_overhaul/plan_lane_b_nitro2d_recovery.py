#!/usr/bin/env python3
"""Summarize remaining Lane B Nitro 2D decode targets after completed recoveries.

Planning/audit only. No curation state mutation and no Platinum writes.
"""
from __future__ import annotations
import argparse, json
from collections import Counter, defaultdict
from pathlib import Path

def fam(path: str) -> str:
    parts=[p for p in str(path or "").replace("\\","/").split("/") if p]
    return "/".join(parts[:5])

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--recovered", required=True, type=Path)
    ap.add_argument("--audit", required=True, type=Path)
    ap.add_argument("--write-json", required=True, type=Path)
    ap.add_argument("--write-md", required=True, type=Path)
    a=ap.parse_args()
    recovered=json.loads(a.recovered.read_text())
    audit=json.loads(a.audit.read_text())
    unresolved={r["asset_id"]:r for r in recovered["records"] if r["review_status"]=="decode_issue"}
    rows=[r for r in audit["records"] if r["asset_id"] in unresolved and r["recovery_route"]=="nitro_2d_decode"]
    if len(rows)!=217:
        raise SystemExit(f"remaining Nitro 2D mismatch: {len(rows)} != 217")
    groups=defaultdict(list)
    for r in rows:
        k=(r.get("source_id"), r.get("group"), r.get("asset_type"), r.get("suffix"), fam(r.get("source_path")))
        groups[k].append(r)
    out=[]
    for k,m in sorted(groups.items(), key=lambda kv: tuple(str(x) for x in kv[0])):
        src,grp,typ,suf,pf=k
        out.append({
            "source_id":src,"group":grp,"asset_type":typ,"suffix":suf,"path_family":pf,
            "asset_count":len(m),"examples":[x["source_path"] for x in m[:12]],
        })
    payload={"schema_version":1,"lane":"B_pokemon_facing","route":"nitro_2d_decode",
             "asset_count":len(rows),"group_count":len(out),
             "source_counts":dict(sorted(Counter(r["source_id"] for r in rows).items())),
             "suffix_counts":dict(sorted(Counter(r["suffix"] for r in rows).items())),
             "groups":out}
    a.write_json.parent.mkdir(parents=True,exist_ok=True)
    a.write_json.write_text(json.dumps(payload,indent=2)+"\n")
    lines=["# Lane B Remaining Nitro 2D Recovery Plan","",
           f"- Assets: **{len(rows)}**",f"- Groups: **{len(out)}**","","## Groups","",
           "| # | Source | Group | Type | Suffix | Path family | Assets |",
           "|---:|---|---|---|---|---|---:|"]
    tick=chr(96)
    for i,g in enumerate(out,1):
        lines.append(f"| {i} | {g['source_id']} | {g['group']} | {g['asset_type']} | {g['suffix']} | {tick}{g['path_family']}{tick} | {g['asset_count']} |")
    a.write_md.write_text("\n".join(lines)+"\n")
    print("Nitro 2D remaining:",len(rows))
    print("Groups:",len(out))
    print("Sources:",payload["source_counts"])
    print("Suffixes:",payload["suffix_counts"])
    return 0
if __name__=="__main__":
    raise SystemExit(main())
