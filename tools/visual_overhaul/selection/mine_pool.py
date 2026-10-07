#!/usr/bin/env python3
"""Systematic mining of the existing DS donor catalog into OPPORTUNITY_POOL.json (+ per-domain passes, needs-evidence queue, summaries).

Deterministic and resumable: pure function of CANDIDATE_GROUPS / curation ledgers / selection ledgers / evidence / explicit findings /
TARGETED_REVIEW.json. Reads no donor repo and modifies no Platinum resource.   usage: mine_pool.py [--domain NAME ...]
"""
from __future__ import annotations

import argparse
import collections
import fnmatch
import math

from common import *  # noqa: F401,F403
import mine_features as MF
import mine_rules as MR
import opportunities as opp

MINING = SEL / "mining"
POOL_JSON = SEL / "OPPORTUNITY_POOL.json"
REVIEW_JSON = MINING / "TARGETED_REVIEW.json"
NE_JSON = MINING / "NEEDS_EVIDENCE_QUEUE.json"
RES_JSON = MINING / "EVIDENCE_RESOLUTIONS.json"
DOMAINS = ["trainer_sprites", "pokemon_sprites", "pokemon_animation", "npc_player_sprites", "field_graphics", "environmental_effects", "battle_effects", "field_effects", "ui_menus_hud",
           "location_area", "textures", "models", "interface_embellishments", "transitions_presentation", "icons", "backgrounds", "misc"]
EVID_PTR = {"hgss": ["docs/visual_overhaul/DONOR_ASSET_CATALOG.json", "docs/visual_overhaul/catalog_extensions/MANIFEST.json"], "pmd_sky": ["docs/visual_overhaul/LANE_CDE_PMD_SKY_RECOVERY.json"],
            "ranger2": ["docs/visual_overhaul/LANE_B_RANGER_EMBEDDED_RECOVERY.json", "docs/visual_overhaul/RANGER_VISUAL_BUNDLE_CLASSIFICATION.json"], "diamond": ["docs/visual_overhaul/DONOR_ASSET_CATALOG.json"]}
SUBSYS_EVID = {"pokemon_battle_sprites", "trainer_battle_sprites", "field_npc_player_sprites", "field_environment_art", "pokemon_icons"}


def signals(g, f) -> list[str]:
    s = []
    if not f["has_native_target"]:
        s.append("no_platinum_equivalent")
    rel = f["native_relation"]
    if rel and rel.startswith("art_diff"):
        s.append("richer_or_revised_variant")
    if rel == "palette_only":
        s.append("palette_treatment_differs")
    if rel in ("identical", "content_match_native"):
        s.append("identical_to_native")
    if g["source_id"] == "diamond":
        s.append("control_source")
    if f["has_nanr"] or f["frames_total"] > 1 or f["cells_total"] > 1:
        s.append("animated_structure")
    if f["cells_total"] >= 12 or f["frames_total"] >= 12:
        s.append("multi_phase_or_many_frames")
    if f["anim_groups"] >= 3:
        s.append("multiple_animation_states")
    if f["has_animated_tiles"]:
        s.append("animated_tiles_companion")
    if f["map_w"]:
        s.append(f"composed_map_{f['quad_layers']}_layers")
    if f["tex_chips"]:
        s.append("texture_payload")
    if f["bg_w"]:
        s.append("composed_background")
    if f["tod"]:
        s.append("time_of_day_variants")
    if f["cell_count"] > 1:
        s.append("multi_cell_sprite_set")
    if f["family_size"] >= 15:
        s.append(f"family_library_{f['family_size']}")
    if f["companion_only"]:
        s.append("companion_only")
    if f["decode_issues"]:
        s.append("unresolved_decode_members")
    if f["needs_evidence"]:
        s.append("ledger_needs_evidence")
    if g["ledger_member_counts"] and f["ledger_role"] in ("alternate",):
        s.append("previously_alternate")
    if f["ledger_role"] == "not_selected" and not f["native_relation"] in ("identical",):
        s.append("previously_not_selected")
    return s


def target_or_host(g, f):
    dom = f["domain"]
    sysname, refs = MR.HOST.get(dom, MR.HOST["misc"])
    if f["has_native_target"]:
        return {"exists": True, "target_id": g["target_id"], "host_system": sysname, "refs": refs}
    return {"exists": False, "target_id": None, "host_system": sysname, "refs": refs}


def next_evidence(g, f) -> str:
    if f["needs_evidence"] or f["native_relation"] in ("subject_unverified", "unmeasured") and g["source_id"] == "hgss":
        return "compare against the Platinum counterpart / verify subject identity with a render"
    if g["source_id"] == "pmd_sky":
        return "render a small sample with the SkyTemple-based decoder and review"
    if g["source_id"] == "ranger2":
        return "render a sample with render_ranger_pokemon_package.py (pinned pokeranger2) and review"
    return "targeted visual review"


def resolution_for(res: dict | None, g: dict, f: dict) -> dict | None:
    """Evidence resolution for a group: group-level entry merged over the first matching family-level entry (see resolve_evidence.py)."""
    if not res or g["group_id"] not in res["scope_groups"]:
        return None
    gr = res["group_resolutions"].get(g["group_id"])
    fr = next((x for x in res["family_resolutions"] if x["source_id"] == g["source_id"] and x["domain"] == f["domain"] and
               (fnmatch.fnmatchcase(f["family"], x["family"]) or x.get("match_group") == g["group_id"])), None)
    if fr is None and gr is None:
        return None
    out = dict(fr or {})
    if gr:
        for k, v in gr.items():
            out[k] = {**out.get(k, {}), **v} if k == "dims" and isinstance(v, dict) else v
        out["evidence_refs"] = list(dict.fromkeys((fr or {}).get("evidence_refs", []) + gr.get("evidence_refs", [])))
    return out


def build_records(data: dict, reviews: dict, res: dict | None = None) -> tuple[list[dict], dict, list[dict]]:
    groups, F = data["groups"], data["features"]
    recs, per_group, ne = [], {}, []
    for g in groups:
        gid = g["group_id"]
        f = F[gid]
        props = MR.proposals(g, f)
        sig = signals(g, f)
        rs = resolution_for(res, g, f)
        closed = bool(rs and rs["verdict"] == "reference_only")
        if closed:
            sig.append("evidence_closed_reference_only")
        elif rs:
            sig.append("evidence_resolved")
        scored = []
        for p in props:
            d = MR.score(g, f, p)
            if rs and not closed and rs.get("techniques") and p["class"] in ("technique_donor", "novel_capability"):
                p = {**p, "techniques": list(rs["techniques"])}
            if rs and not closed:
                d.update({**rs.get("dims", {}).get("*", {}), **rs.get("dims", {}).get(p["class"], {})})
            if p["class"] in ("reference_only", "reject"):
                scored.append((0.0, p, d))
            else:
                scored.append((MR.composite(d), p, d))
        rv = reviews.get(gid)
        ev_floor = 4 if rv and rv["verdict"] == "confirm" else None
        if rs and not closed:
            ev_floor = max(ev_floor or 0, rs.get("evidence_floor", 4))
        scored.sort(key=lambda t: (-t[0], t[1]["class"]))
        made = []
        seen = set()
        for comp, p, d in scored:
            cls = p["class"]
            if cls in ("reference_only", "reject") or closed:
                continue
            if rv and rv["verdict"] == "downgrade" and rv.get("class") in (None, cls):
                continue
            if ev_floor:
                d["evidence"] = max(d["evidence"], ev_floor)
                comp = MR.composite(d)
            key = (cls, p["use_mode"])
            if key in seen or len(made) >= 3:
                continue
            if comp < MR.PROMOTE and cls != "replacement_candidate" and not f["needs_evidence"] and f["family_size"] >= 50 and f["rich_pct"] < 0.5 and not ev_floor:
                continue  # large low-evidence families surface only their richer half as needs-evidence leads
            ne_flag = d["evidence"] <= 2 or f["needs_evidence"] and not ev_floor
            if rs:
                if comp < MR.PROMOTE and cls != "replacement_candidate":
                    sig.append("evidence_closed_below_threshold")
                    continue
                status = "promoted"
                seen.add(key)
                made.append((comp, p, d, status))
                continue
            if comp >= MR.PROMOTE or (cls == "replacement_candidate" and f["ledger_role"] == "preferred") or (comp >= MR.NEEDS_EVIDENCE and d["evidence"] <= 2) or (f["needs_evidence"] and comp >= 2.8):
                status = "needs_evidence" if ne_flag or (comp < MR.PROMOTE and cls != "replacement_candidate") else "promoted"
                seen.add(key)
                made.append((comp, p, d, status))
        if made:
            sec = [m[1]["class"] for m in made[1:]]
            for i, (comp, p, d, status) in enumerate(made):
                oid = f"opp:mined/{gid}/{p['class']}/{p['use_mode']}"
                tg = target_or_host(g, f)
                ev_ptrs = list(EVID_PTR.get(g["source_id"], [])) + ([f"docs/visual_overhaul/selection/evidence/{g['subsystem']}.json"] if g["subsystem"] in SUBSYS_EVID else []) + [f"docs/visual_overhaul/selection/ledgers/{g['subsystem']}.json"]
                if rv:
                    ev_ptrs += rv.get("evidence_refs", [])
                if rs:
                    ev_ptrs += rs.get("evidence_refs", [])
                rec = {
                    "opportunity_id": oid, "origin": "mined", "status": status, "source_id": g["source_id"], "group_id": gid, "member_count": f["n_members"], "member_digest": g["member_digest"],
                    "member_sample": f["member_ids"][:6], "subsystem": g["subsystem"], "domain": f["domain"], "family": f["family"], "classification": p["class"],
                    "secondary_classes": sorted({c for c in [m[1]["class"] for m in made] + [] if c != p["class"]}) if len(made) > 1 else [], "use_mode": p["use_mode"],
                    "platinum_target_exists": tg["exists"], "platinum_target": tg["target_id"], "platinum_host": {"system": tg["host_system"], "refs": tg["refs"]},
                    "useful_property": p["components"] or p["techniques"] or ["whole asset"], "component_categories": p["components"], "technique_tags": p["techniques"],
                    "why_surfaced": sig, "why_it_matters": p["why_surfaced"], "expected_visual_gain": MR.IMPACT_TEXT[d["visual_impact"]], "novelty": d["novelty"], "reuse_potential": d["reuse"],
                    "adaptation": p["adaptation"] or ["re-express through Platinum-native resources", "human visual review before any use"],
                    "format_notes": f"{g['format_family']} / conversion {g['conversion_requirement']} / donor class {g['donor_class']}",
                    "cost": MR.cost_label(d["cost"]), "risk": MR.cost_label(d["risk"]), "confidence": MR.confidence(d["evidence"], p["class"]), "evidence_pointers": ev_ptrs,
                    "donor_pixels_intended": p["pixel_use"] in ("donor_pixels", "recolored_donor"), "pixel_use": p["pixel_use"], "remains_platinum_native": p["class"] != "replacement_candidate",
                    "human_visual_review": "required" if p["pixel_use"] != "none" or d["evidence"] <= 3 else "recommended",
                    "dims": d, "composite": comp, "ledger": {"role": f["ledger_role"], "reason": f["ledger_reason"], "native_relation": f["native_relation"]},
                    "targeted_review": ({"verdict": rv["verdict"], "note": rv["note"], "reviewed_by": rv["reviewed_by"]} if rv else None),
                }
                if rs:
                    rec["evidence_resolution"] = {"verdict": rs["verdict"], "note": rs.get("note"), "measured": rs.get("measured"), "decided_by": rs.get("decided_by")}
                recs.append(rec)
                if status == "needs_evidence":
                    ne.append({"opportunity_id": oid, "group_id": gid, "domain": f["domain"], "family": f["family"], "source_id": g["source_id"], "classification": p["class"], "composite": comp,
                               "evidence_quality": d["evidence"], "next_evidence": next_evidence(g, f)})
        disp = ("promoted" if any(m[3] == "promoted" for m in made) else "needs_evidence" if made else
                "reject" if all(p["class"] == "reject" for p in props) else "reference_only")
        per_group[gid] = {"g": gid, "src": g["source_id"], "dom": f["domain"], "fam": f["family"], "disp": disp, "best": made[0][0] if made else 0.0,
                          "cls": [m[1]["class"] for m in made] or [props[0]["class"]], "sig": sig, "rec": [f"opp:mined/{gid}/{m[1]['class']}/{m[1]['use_mode']}" for m in made]}
    return recs, per_group, ne


def explicit_records() -> list[dict]:
    out = []
    for f in opp.load_findings()["findings"]:
        if not opp.active(f):
            continue
        sc = f.get("scores")
        d = None
        comp = None
        if sc:
            ev = {"catalog_evidence": 4, "donor_checkout_verification": 3, "repo_document": 3}.get(f["evidence"]["basis"], 2)
            d = {"visual_impact": sc["visual_impact"], "novelty": sc["novelty"], "feasibility": sc["feasibility"], "reuse": sc["reuse"], "library": sc["reuse"], "evidence": ev, "cost": sc["cost"],
                 "risk": sc["risk"], "dependency": 1 if f["asset_use"] == "techniques" else 3 if f["asset_use"] != "whole_assets" else 4, "slice": sc["slice"]}
            comp = MR.composite(d)
        tg = f["target"]
        out.append({"opportunity_id": f["finding_id"], "origin": "explicit", "status": "promoted" if sc else "reviewed", "source_id": f["donor"]["source_id"], "group_id": None,
                    "group_ids": f["donor"].get("group_ids", []), "subsystem": tg.get("subsystem") or tg.get("host_system"), "domain": None, "classification": f["classification"],
                    "secondary_classes": [], "use_mode": {"whole_assets": "whole_asset", "components": "component", "techniques": "technique", "mixed": "mixed"}.get(f.get("asset_use"), "reference"),
                    "platinum_target_exists": tg["kind"] != "none", "platinum_target": tg.get("target_id") or tg.get("system"), "platinum_host": {"system": tg.get("host_system") or tg.get("system"), "refs": tg.get("refs", [])},
                    "useful_property": f["useful"], "component_categories": f.get("tags", []), "technique_tags": [], "why_it_matters": f["why"], "expected_visual_gain": MR.IMPACT_TEXT[sc["visual_impact"]] if sc else None,
                    "novelty": sc["novelty"] if sc else None, "reuse_potential": sc["reuse"] if sc else None, "adaptation": f["adaptation"], "cost": f["cost"], "risk": f["risk"], "confidence": f["confidence"],
                    "evidence_pointers": f["evidence"].get("refs", []), "donor_pixels_intended": f["pixel_use"] in ("donor_pixels", "recolored_donor"), "pixel_use": f["pixel_use"],
                    "remains_platinum_native": f["classification"] != "replacement_candidate", "human_visual_review": "required", "dims": d, "composite": comp,
                    "format_notes": "see finding", "title": f.get("subject", "")})
    return out


def libraries(recs: list[dict]) -> list[dict]:
    by = collections.defaultdict(list)
    for r in recs:
        if r["origin"] == "mined" and not r.get("subsumed_by"):
            by[(r["source_id"], r["domain"], r["family"], r["classification"], r["use_mode"])].append(r)
    libs = []
    for (src, dom, fam, cls, um), rs in by.items():
        pr = [r for r in rs if r["status"] == "promoted"] or rs
        top = sorted((r["composite"] for r in pr), reverse=True)[:5]
        n = len(pr)
        comps, techs = collections.Counter(), collections.Counter()
        for r in rs:
            comps.update(r["component_categories"]); techs.update(r["technique_tags"])
        libs.append({"library_id": f"lib:{src}/{dom}/{fam}/{cls}/{um}", "source_id": src, "domain": dom, "family": fam, "classification": cls, "use_mode": um, "records": n,
                     "promoted": sum(r["status"] == "promoted" for r in rs), "needs_evidence": sum(r["status"] == "needs_evidence" for r in rs),
                     "members": sum(r["member_count"] for r in rs), "score": round(min(5.0, sum(top) / len(top) + 0.06 * math.log2(n)), 3), "top_composite": top[0],
                     "components": dict(comps.most_common()), "techniques": dict(techs.most_common()), "host": rs[0]["platinum_host"], "top_records": [r["opportunity_id"] for r in sorted(rs, key=lambda r: -r["composite"])[:5]],
                     "group_ids": sorted(r["group_id"] for r in rs)})
    libs.sort(key=lambda l: (-l["score"], l["library_id"]))
    return libs


def load_resolutions() -> dict | None:
    return jload(RES_JSON) if RES_JSON.is_file() else None


def load_reviews() -> dict:
    return {r["group_id"]: r for r in jload(REVIEW_JSON)["reviews"]} if REVIEW_JSON.is_file() else {}


def derive() -> dict:
    data = MF.build()
    recs, per_group, ne = build_records(data, load_reviews(), load_resolutions())
    ex = explicit_records()
    ex_groups = {gid: e["opportunity_id"] for e in ex for gid in e.get("group_ids", [])}
    ex_cls = {(gid, e["classification"]): e["opportunity_id"] for e in ex for gid in e.get("group_ids", [])}
    for r in recs:
        eid = ex_cls.get((r["group_id"], r["classification"]))
        if eid:
            r["subsumed_by"] = eid
        elif r["group_id"] in ex_groups:
            r["related_explicit"] = ex_groups[r["group_id"]]
    recs.sort(key=lambda r: (-r["composite"], r["opportunity_id"]))
    allrecs = ex + recs
    libs = libraries(recs)
    ne.sort(key=lambda r: (-r["composite"], r["opportunity_id"]))
    return {"data": data, "records": allrecs, "per_group": per_group, "libraries": libs, "needs_evidence": ne}


def pool_doc(res: dict) -> dict:
    data = res["data"]
    inputs = {"groups_sha256": file_sha256(GROUPS_JSON), "ledgers": {p.stem: file_sha256(p) for p in sorted((SEL / "ledgers").glob("*.json"))}, "classes_sha256": file_sha256(opp.CLASSES_JSON),
              "scope_sha256": file_sha256(opp.SCOPE_JSON), "findings_sha256": file_sha256(opp.FINDINGS_JSON), "targeted_review_sha256": file_sha256(REVIEW_JSON) if REVIEW_JSON.is_file() else None, "evidence_resolutions_sha256": file_sha256(RES_JSON) if RES_JSON.is_file() else None,
              "rules": {"promote": MR.PROMOTE, "needs_evidence": MR.NEEDS_EVIDENCE, "weights": MR.WEIGHTS}}
    return {"schema_version": 1, "phase": "ds_only", "inputs": inputs, "groups_processed": len(data["groups"]), "records": res["records"], "libraries": res["libraries"]}


def dump_lines(path, doc: dict, list_key: str) -> None:
    """Large list files: one record per line (stable diffs, still valid JSON)."""
    import json
    head = {k: v for k, v in doc.items() if k != list_key}
    lines = [json.dumps(r, sort_keys=True, separators=(",", ":")) for r in doc[list_key]]
    body = json.dumps(head, sort_keys=True, separators=(",", ":"))[:-1] + f',"{list_key}":[\n' + ",\n".join(lines) + "\n]}\n"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(body)


def main() -> int:
    from mine_report import write_reports
    ap = argparse.ArgumentParser()
    ap.parse_args()
    res = derive()
    doc = pool_doc(res)
    dump_lines(POOL_JSON, doc, "records")
    MINING.mkdir(exist_ok=True)
    (MINING / "passes").mkdir(exist_ok=True)
    byd = collections.defaultdict(list)
    for pg in res["per_group"].values():
        byd[pg["dom"]].append(pg)
    for d, gs in byd.items():
        gs.sort(key=lambda x: (-x["best"], x["g"]))
        jdump(MINING / "passes" / f"{d}.json", {"domain": d, "groups": len(gs), "dispositions": dict(collections.Counter(x["disp"] for x in gs)), "ranked": gs})
    jdump(NE_JSON, {"schema_version": 1, "count": len(res["needs_evidence"]), "items": res["needs_evidence"]})
    write_reports(res, doc)
    print(f"groups processed {doc['groups_processed']}; records {len(doc['records'])}; libraries {len(doc['libraries'])}; needs_evidence {len(res['needs_evidence'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
