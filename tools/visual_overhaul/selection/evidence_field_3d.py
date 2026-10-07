#!/usr/bin/env python3
"""Evidence provider `field_3d` (donor-free): per-group native relation for the hgss_field_3d extension.

Reads only the committed extension catalog and CANDIDATE_GROUPS.json (run build_candidate_groups.py first) and writes
evidence/{field_building_models,field_texture_sets,overworld_pokemon_sheets}.json. Relations are measured in the inventory
(inventory_hgss_field_3d.py) against Platinum's own prop models, texture sets and overworld Pokemon sheets.
"""
from __future__ import annotations

import collections

from common import *  # noqa: F401,F403

EXT = EXT_DIR / "hgss_field_3d" / "CATALOG.json"
SUBS = ("field_building_models", "field_texture_sets", "overworld_pokemon_sheets")


def main() -> int:
    cat = jload(EXT)
    A = {a["asset_id"]: a for a in cat["assets"]}
    gdoc = jload(GROUPS_JSON)
    members: dict[str, list[str]] = collections.defaultdict(list)
    # membership via mapping (same derivation as the groups)
    import mapping
    recs = load_recovered_records()
    for aid in A:
        r = recs[aid]
        if r["review_status"] != "usable":
            continue
        c = mapping.classify(r)
        members[f"{c['subsystem']}/{r['source_id']}/{c['unit']}"].append(aid)
    out = {s: {} for s in SUBS}
    for g in gdoc["groups"]:
        if g["subsystem"] not in SUBS:
            continue
        ids = sorted(members[g["group_id"]])
        assert len(ids) == g["member_count"], g["group_id"]
        ms = [A[i]["source_metadata"] for i in ids]
        if g["subsystem"] == "field_building_models":
            m = ms[0]
            rel, detail = m["native_relation"], m["relation_detail"]
        elif g["subsystem"] == "field_texture_sets":
            n = len(ms)
            ident = sum(m["texture_use"] == "identical_to_platinum" for m in ms)
            rel = "identical" if ident >= 0.9 * n else "missing_in_native"
            detail = {"textures": n, "identical_to_platinum": ident, "near_match": sum(bool(m["platinum_near_match"]) for m in ms), "basis": "exact RGBA hash against Platinum prop/map texture sets and prop-model textures"}
        else:
            m = ms[0]
            rel = m["platinum_relation"] or "missing_in_native"
            detail = {"platinum_equivalents": m["platinum_equivalents"], "platinum_frame_counts": m["platinum_frame_counts"], "hgss_frames": m["frames"], "frame_matches": m["platinum_frame_matches"]}
        out[g["subsystem"]][g["group_id"]] = {"native_relation": rel, "member_digest": g["member_digest"], "detail": detail}
    for s in SUBS:
        summ = collections.Counter(v["native_relation"] for v in out[s].values())
        jdump(SEL / "evidence" / f"{s}.json", {"schema_version": 1, "subsystem": s, "provider": "field_3d", "generated_by": "tools/visual_overhaul/selection/evidence_field_3d.py",
                                               "inputs": {"hgss_commit": cat["sources"][0]["source_commit"], "catalog_sha256": file_sha256(EXT), "groups_sha256": file_sha256(GROUPS_JSON)},
                                               "summary": dict(sorted(summ.items())), "entries": out[s]})
        print(s, dict(summ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
