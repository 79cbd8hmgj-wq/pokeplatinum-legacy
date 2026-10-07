"""Mining pass 4: human-readable artifacts from the derived pool (all deterministic; no raw catalog dumps)."""
from __future__ import annotations

import collections

from common import *  # noqa: F401,F403
import mine_rules as MR

MINING = SEL / "mining"
CLASS_ORDER = ["novel_capability", "novel_detail", "technique_donor", "enhancement_candidate", "component_donor", "replacement_candidate", "reference_only", "reject"]
BLIND_SPOTS = [
    ("HGSS follower Pokemon sheets (572 NSBTX in files/data/mmodel)", "evidence closure decoded all 572 (8 frames each, normal+shiny); recorded as explicit findings opp:hgss/follower_sheet_library (sheets) and opp:hgss/follower_pokemon (system, deferred); still 0 catalog groups"),
    ("HGSS 3D field models/textures/building models", "evidence closure decoded bm_field (340) / bm_room (222) models and 106 map texture sets (explicit findings opp:hgss/field_building_model_library, opp:hgss/map_texture_set_library); still no catalog groups: a targeted catalog extension is recommended (see DS_EVIDENCE_CLOSURE.md)"),
    ("PMD Sky manpu_* / effect.bin / status-icon art", "uncataloged and still undecoded (status-icon art container not identified); PMD MAP_BG BPA/BPL animation and a WAN sample were decoded in the closure pass"),
    ("Diamond trainer/field/model assets beyond sprites", "Diamond is control only; no field/model catalog"),
    ("Ranger 2 poke/ battle frames semantic pose approval", "w/a/s/t sets rendered (295/596/296/272); poses are field-scale (~40px), not the 160x80 battle contract; walk/s/t sets closed as reference, attack sets kept as a technique library"),
    ("HGSS UI (zukan_gra/plist_gra/camera) visual comparison with Platinum", "targeted renders composed (partial NSCR/NCGR pairing); reference_only confirmed (opp:hgss/ui_dex_party_reference)"),
]


def pct(n, d):
    return f"{100 * n / d:.1f}%" if d else "-"


def write_reports(res: dict, doc: dict) -> dict:
    recs = doc["records"]
    mined = [r for r in recs if r["origin"] == "mined"]
    live = [r for r in mined if not r.get("subsumed_by")]
    expl = [r for r in recs if r["origin"] == "explicit"]
    pg = list(res["per_group"].values())
    n_groups = len(pg)
    disp = collections.Counter(x["disp"] for x in pg)
    surfaced = {r["group_id"] for r in mined}
    cls_rec = collections.Counter(r["classification"] for r in live) + collections.Counter(r["classification"] for r in expl if r["classification"] in CLASS_ORDER[:6])
    cls_all = {c: cls_rec.get(c, 0) for c in CLASS_ORDER[:6]}
    cls_all["reference_only"] = disp["reference_only"] + sum(r["classification"] == "reference_only" for r in expl)
    cls_all["reject"] = disp["reject"] + sum(r["classification"] == "reject" for r in expl)
    by_dom = collections.defaultdict(lambda: collections.Counter())
    for x in pg:
        by_dom[x["dom"]]["groups"] += 1
        by_dom[x["dom"]][x["disp"]] += 1
    for r in live:
        by_dom[r["domain"]]["records"] += 1
    um = collections.Counter(r["use_mode"] for r in live + [e for e in expl if e["status"] == "promoted"])
    um_status = {s: collections.Counter(r["use_mode"] for r in live if r["status"] == s) for s in ("promoted", "needs_evidence")}
    comp_lib: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    tech_lib: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for l in doc["libraries"]:
        for c, n in l["components"].items():
            comp_lib[c][l["library_id"]] += n
        for t, n in l["techniques"].items():
            tech_lib[t][l["library_id"]] += n
    ranked = sorted([r for r in recs if r.get("composite")], key=lambda r: (-r["composite"], r["opportunity_id"]))
    top = [r for r in ranked if not r.get("subsumed_by")]
    stats = {"groups_processed": n_groups, "groups_surfaced": len(surfaced), "dispositions": dict(disp), "class_counts": cls_all, "mined_records": len(mined), "mined_unsubsumed": len(live),
             "explicit_records": len(expl), "use_mode": dict(um), "needs_evidence_records": sum(r["status"] == "needs_evidence" for r in live), "libraries": len(doc["libraries"])}
    (MINING / "ranked").mkdir(parents=True, exist_ok=True)
    jdump(MINING / "POOL_STATS.json", stats)
    for dom, c in sorted(by_dom.items()):
        rs = [r for r in ranked if r.get("domain") == dom and not r.get("subsumed_by")][:25]
        L = [f"# Ranked: {dom}", "", f"groups {c['groups']}; promoted {c['promoted']}; needs_evidence {c['needs_evidence']}; reference_only {c['reference_only']}; reject {c['reject']}; records {c['records']}", "",
             "| # | Opportunity | Class | Use | Status | Score |", "|---:|---|---|---|---|---:|"]
        for i, r in enumerate(rs, 1):
            L.append(f"| {i} | {r['opportunity_id'].split('/', 2)[-1][:70]} | {r['classification']} | {r['use_mode']} | {r['status']} | {r['composite']} |")
        (MINING / "ranked" / f"{dom}.md").write_text("\n".join(L) + "\n")

    P = ["# Opportunity pool summary (DS-only)", "", "Generated by `mine_pool.py`. Pool: `OPPORTUNITY_POOL.json`. Deferred GBA/GBC findings are not part of it.", "",
         f"- candidate groups processed: **{n_groups}**; surfaced (promoted or needs-evidence record): **{len(surfaced)}** ({pct(len(surfaced), n_groups)}); group dispositions: " + ", ".join(f"{k} {v}" for k, v in sorted(disp.items())),
         f"- mined opportunity records: {len(mined)} ({len(live)} not subsumed by an explicit finding); explicit findings: {len(expl)}; libraries: {len(doc['libraries'])}", "",
         "## Counts by taxonomy class", "", "| Class | Opportunities | Basis |", "|---|---:|---|"]
    for c in CLASS_ORDER:
        P.append(f"| {c} | {cls_all[c]} | {'records (mined+explicit)' if c in CLASS_ORDER[:6] else 'group dispositions + explicit'} |")
    st = collections.defaultdict(collections.Counter)
    for r in live:
        st[r["classification"]][r["status"]] += 1
    P += ["", "Mined records by status: " + "; ".join(f"{c} {st[c]['promoted']} promoted / {st[c]['needs_evidence']} needs-evidence" for c in CLASS_ORDER[:6] if st[c]) + ". Explicit findings are all promoted.",
          "", "## By mining domain (subsystem pass)", "", "| Domain | Groups | Promoted | Needs evidence | Reference | Reject | Records |", "|---|---:|---:|---:|---:|---:|---:|"]
    for dom in MINING_DOMAINS:
        c = by_dom.get(dom, collections.Counter())
        P.append(f"| {dom} | {c['groups']} | {c['promoted']} | {c['needs_evidence']} | {c['reference_only']} | {c['reject']} | {c['records']} |")
    P += ["", "## Use mode (what the opportunity reuses)", "", "| Use | Promoted | Needs evidence |", "|---|---:|---:|"]
    for m in ("whole_asset", "component", "technique", "composite_input"):
        P.append(f"| {m} | {um_status['promoted'].get(m, 0)} | {um_status['needs_evidence'].get(m, 0)} |")
    P.append("")
    P.append("Explicit findings add: " + ", ".join(f"{k} {v}" for k, v in sorted(collections.Counter(e['use_mode'] for e in expl if e['status'] == 'promoted').items())) + " (mixed = whole assets plus technique).")
    P += ["", "## Top 25 opportunities (score = weighted mean of 10 dimensions, 1-5)", "", "| # | Opportunity | Class | Use | Source | Status | Score |", "|---:|---|---|---|---|---|---:|"]
    for i, r in enumerate(top[:25], 1):
        P.append(f"| {i} | {(r.get('title') or r['opportunity_id'].split('/', 2)[-1])[:80]} | {r['classification']} | {r['use_mode']} | {r['source_id']} | {r['status']} | {r['composite']} |")
    P += ["", "## Strongest libraries (families of recurring opportunities)", "", "| Library | Class | Records | Members | Score | Top components / techniques |", "|---|---|---:|---:|---:|---|"]
    for l in doc["libraries"][:20]:
        tt = ", ".join(list(l["components"])[:3] + list(l["techniques"])[:3])
        P.append(f"| {l['library_id'][4:]} | {l['classification']} | {l['records']} | {l['members']} | {l['score']} | {tt} |")
    P += ["", "## Recurring component categories", "", "| Component | Records | Leading libraries |", "|---|---:|---|"]
    for c, cn in sorted(comp_lib.items(), key=lambda kv: -sum(kv[1].values())):
        P.append(f"| {c} | {sum(cn.values())} | {', '.join(k[4:] for k, _ in cn.most_common(2))} |")
    P += ["", "## Recurring techniques", "", "| Technique | Records | Leading libraries |", "|---|---:|---|"]
    for t, tn in sorted(tech_lib.items(), key=lambda kv: -sum(kv[1].values())):
        P.append(f"| {t} | {sum(tn.values())} | {', '.join(k[4:] for k, _ in tn.most_common(2))} |")
    (SEL / "OPPORTUNITY_POOL_SUMMARY.md").write_text("\n".join(P) + "\n")

    S = ["# DS opportunity mining summary", "", "Phase `ds_only` (Platinum baseline; Diamond control; HGSS, PMD Sky, Ranger 2 donors). No donor repo was rescanned or recataloged; no Platinum asset or code was touched; deferred GBA/GBC findings are excluded.", "",
         "## Method", "",
         "1. **Features** (`mine_features.py`): every candidate group is joined to its members (catalog + recovered curation), ledger decision, evidence relation and target resolution; structural signals are parsed from curation details (frames/animation groups, cells, composed map layers, texture chips, composed backgrounds, animated-tile companions, cell counts, time-of-day variants, family size).",
         "2. **Proposals** (`mine_rules.py`): each group is asked the eight taxonomy questions; rules emit zero or more proposals per group (novel capability/detail, technique, component, enhancement, replacement, reference, reject). A group may therefore yield several records (different contribution types) and loses nothing by failing a replacement comparison.",
         "3. **Scoring**: ten dimensions (visual impact, novelty, feasibility, reuse, library value, evidence quality, cost, risk, format dependency, vertical-slice value; cost/risk/dependency inverted) with weights 7/6/5/4/3/3/3/2/2/2; impact is adjusted by richness percentile inside a family. Whole-asset replacement gets novelty 1 and low library value by construction, so it cannot outrank component/technique/novel work on whole-asset superiority alone.",
         f"4. **Disposition**: composite >= {MR.PROMOTE} -> promoted; >= {MR.NEEDS_EVIDENCE} with evidence quality <= 2 (or ledger needs_evidence) -> needs_evidence; otherwise reference_only, or reject (identical/companion-only/no content). Diamond is control: reference_only only.",
         "5. **Libraries**: promoted records cluster by (source, domain, family, class); library score rewards size.", "",
         "Per-domain passes: `mining/passes/<domain>.json` (every group with disposition, signals, record ids); ranked views: `mining/ranked/<domain>.md`; unresolved: `mining/NEEDS_EVIDENCE_QUEUE.json`.", "",
         "## Result", "", f"- groups processed {n_groups}; surfaced {len(surfaced)}; dispositions " + ", ".join(f"{k} {v}" for k, v in sorted(disp.items())),
         "- class counts: " + ", ".join(f"{c} {cls_all[c]}" for c in CLASS_ORDER), "", "## Catalog blind spots", ""]
    S += [f"- **{a}** — {b}" for a, b in BLIND_SPOTS]
    rvw = jload(MINING / "TARGETED_REVIEW.json") if (MINING / "TARGETED_REVIEW.json").is_file() else {"reviews": [], "family_reviews": []}
    S += ["", "## Targeted review of ambiguous high-value groups", "",
          f"{len(rvw['reviews'])} group reviews (confirm) and {len(rvw['family_reviews'])} family reviews from committed or targeted renders (`mining/TARGETED_REVIEW.json`, images under `mining/review/` and `opportunities/evidence/`). Findings: HGSS-only trainer classes are clean multi-frame sets; Ranger walk frames form genuine cycles; Ranger effect/interface primitives are shaded multi-frame Nitro cells; Ranger composed maps are 2D tile art (motif/prop library, low feasibility); Ranger menu/event/ending bundles have no available renderer and stay needs-evidence.",
          "", "## Evidence closure", "", "`mining/EVIDENCE_RESOLUTIONS.json` (built by `resolve_evidence.py` from the committed decoder evidence under `mining/evidence/`) resolved the frozen baseline needs-evidence queue (`mining/EVIDENCE_CLOSURE_SCOPE.json`, 643 records): records were promoted with measured evidence or the group was closed to reference_only. See `DS_EVIDENCE_CLOSURE.md`.", "", "## Top-level recommendation", "", "Pick vertical slices from the ranked queue (`IMPLEMENTATION_QUEUE.md`); the HGSS 3D field resources need a targeted catalog extension before any import."]
    (SEL / "DS_OPPORTUNITY_MINING_SUMMARY.md").write_text("\n".join(S) + "\n")
    return stats


MINING_DOMAINS = ["trainer_sprites", "pokemon_sprites", "pokemon_animation", "npc_player_sprites", "field_graphics", "environmental_effects", "battle_effects", "field_effects", "ui_menus_hud",
                  "location_area", "textures", "models", "overworld_pokemon", "interface_embellishments", "transitions_presentation", "icons", "backgrounds", "misc"]
