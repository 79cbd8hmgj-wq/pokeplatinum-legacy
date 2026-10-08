"""Markdown renderer for CROSS_GEN_IMPLEMENTATION_PLAN.md (called by build_cross_gen_synthesis.py)."""
from __future__ import annotations

import textwrap

WAVES = {
    1: ("Wave 1 - prove the first runtime service", "One engineering slice plus the spikes and art-direction reviews every later wave needs."),
    2: ("Wave 2 - new presentation layers", "Two new Platinum-native layers whose hosts are decided by Wave 1 spikes."),
    3: ("Wave 3 - build on the Wave 2 hosts / authoring tracks", "One item that reuses a Wave 2 host (area preview), plus authoring-bound tracks with no engineering dependency (overworld sheet pilot, Ace Trainer shading)."),
    4: ("Wave 4 - per-asset and per-move work (later)", "Valid but needs a design step or is a second pass over already-graded assets."),
    5: ("Wave 5 - high-cost or unscoped (later)", "Needs a missing pipeline, unscoped evidence, or low-value library work."),
    6: ("Wave 6 - replacement candidates (runtime-QA gated)", "Whole-asset replacement is one outcome among eight; nothing here starts before runtime QA."),
}


def _cell(s: str) -> str:
    return str(s).replace("|", "/").replace("\n", " ")


def _donors(x: dict) -> str:
    out = [f"{d['source_id']}{'' if d['role'] == 'primary' else ' (supporting)'}" for d in x["donors"]]
    out += [f"{c['donor']} (corroborates)" for c in x["corroboration"]]
    return ", ".join(dict.fromkeys(out))


def render(o: dict) -> str:
    c = o["counts"]
    R = o["ranked"]
    byid = {x["io_id"]: x for x in R}
    top10 = R[:10]
    L: list[str] = []
    A = L.append

    A("# Cross-generation implementation plan (final synthesis)")
    A("")
    A("Status: **SYNTHESIS PROPOSAL / NOT HUMAN-APPROVED / NO PLATINUM SOURCE OR ASSET MODIFIED**")
    A(f"Baseline: `main` @ `{o['baseline_commit']}` (post PR #76). Machine-readable: `CROSS_GEN_OPPORTUNITY_RANKING.json`. Generator: `tools/visual_overhaul/selection/build_cross_gen_synthesis.py`.")
    A("")
    A("Inputs are read, never rewritten: the DS evidence base (`OPPORTUNITY_POOL.json`, `IMPLEMENTATION_QUEUE.json`, `opportunities/findings.json`, `CROSS_DONOR_IMPLEMENTATION_PLAN.md`) and the frozen GBA/GBC pool (`gba_gbc/`). Donor identity stays attached to every member of every opportunity.")
    A("")
    A("## 1. Answers")
    A("")
    A(f"* **What should actually be implemented?** {c['ranked_implementation_opportunities']} ranked opportunities: {c['ranked_immediate']} immediate candidates and {c['ranked_later']} later/high-cost. {c['gated_excluded_clusters']} further clusters ({c['gated_excluded_ds_queue_items']} DS queue items) are gated out of the ranking. The GBA/GBC donor layer adds **no new ranked opportunity**; it strengthens {c['gba_gbc_strengthened_ranked_opportunities']} existing ones.")
    A("* **Strongest ideas (canonical score):** " + "; ".join(f"{x['title']} ({x['canonical_score']})" for x in R[:4]) + ".")
    A("* **Best first slice:** `IO-PAL-CYCLE` - the battle-terrain palette-cycle service on the water platform (section 10).")
    A("* **Donor findings that informed design but must not be implemented:** all 14 GBA/GBC `reference_only` records and 2 `reject` records (Emerald, FireRed, Crystal, Yellow, plus the PMD Red engine/pixels record) and the DS `reference_only`/`reject` findings (section 9).")
    A("* **Duplicates/subsumed:** 9 decisions (section 8). Headline cases: FireRed map preview -> HGSS area preview; PMD Red status overlay -> PMD Sky status indicators; FireRed palette sequences -> PMD Sky palette cycling; Yellow reaction table -> follower mechanic.")
    A("* **Deferred, non-blocking:** Crystal angels motif, Ruby (both by project decision), plus the DS evidence gaps in section 6.")
    A("")
    A("## 2. Frozen GBA/GBC donor status")
    A("")
    A("| Donor | Pinned commit | Status | Records | Needs evidence |")
    A("|---|---|---|---|---:|")
    pins = {"emerald": "a81cfacb", "firered": "037335f4", "pmd_red": "aefe6a46", "crystal": "3bc8daa4", "yellow": "e89ead15", "ruby": "-"}
    st = {
        "emerald": ("complete", "3 reference_only", 0), "firered": ("complete", "4 reference_only", 0),
        "pmd_red": ("complete", "1 novel_detail, 1 technique_donor (conditional), 1 reference_only", 0),
        "crystal": ("reviewed; **angels motif deferred** (non-blocking)", "3 reference_only, 1 reject, 1 needs_evidence", 1),
        "yellow": ("complete", "3 reference_only, 1 reject", 0), "ruby": ("**skipped by project decision**", "none (not mined)", 0)}
    for d, (s, r, n) in st.items():
        A(f"| {d} | `{pins[d]}` | {s} | {r} | {n} |")
    A("")
    A("Skipped and not blocking: B4.5 (Crystal angels evidence closure) and B5 (Ruby semantic delta). `ne:crystal/angels_motif_vs_platinum` is kept as an explicit deferred item (provisional `reference_only`, excluded from ranking) and is **not resolved** here.")
    A("")
    A("### Pool validation (`validate_gba_gbc_pool.py`, passes)")
    A("")
    A("| Check | Result |")
    A("|---|---|")
    A("| Duplicate finding ids / collisions with DS ids | none |")
    A("| Provenance | every record carries the pinned donor commit, verification facts, and evidence refs that exist in the repo |")
    A("| Taxonomy | all classes canonical; 2 records corrected (below); pixel policy and target policy hold for all 19 |")
    A("| `replacement_candidate` overuse | 0 of 19 GBA/GBC records. In the DS pool 32 of ~3,170 promoted records (about 1%); in this ranking 2 of 16 opportunities, both last and runtime-QA gated |")
    A("| `reference_only`/`reject` isolation | 16 GBA/GBC + 10 DS findings are listed in a separate register and cannot enter `ranked` |")
    A("| Needs evidence | 1 (Crystal angels), deferred; Ruby recorded as a non-blocking skip |")
    A("")
    A("Corrections applied by `freeze_gba_gbc_pool.py` (no donor fact changed): `opp:pmd_red/battler_status_overlays` used target kind `battle_presentation_layer` and had null cost/feasibility, and `opp:pmd_red/battler_status_overlays/multi_status_cycling` used target kind `ui_behaviour`; both are now canonical (`none` + host system for the novel_detail, `system` for the technique donor, cost/risk as low/medium/high with the prose kept in `risk_note`, feasibility 2 to match the DS record they merge into). The two records also gained a `merge` pointer.")
    A("")
    A("## 3. Method")
    A("")
    A("* **Unit.** One implementation opportunity (IO) = one concept on one Platinum host. All 94 DS queue items and all 19 GBA/GBC records are accounted for exactly once: ranked member, corroboration, gated, or reference_only/reject/deferred.")
    A("* **Score.** Canonical 7-weight mean from `OPPORTUNITY_CLASSES.json`: visual impact 7, novelty 6, feasibility 5, reuse 4, cost 3 (inverted), risk 2 (inverted), slice 1; scale 1-5.")
    A("* **Anchor.** If a reviewed explicit DS finding exists for the concept, its scores are the IO's scores; otherwise the strongest mined library (mean of its top-5 records per dimension, no library-size bonus). Mined scores are auto-assigned and flagged as such (`score_basis`, `confidence`).")
    A("* **Corroboration never moves a score.** GBA/GBC evidence raises confidence and evidence breadth only; it cannot inflate a ranking.")
    A("* **Ranking vs. execution.** Rank is the pure canonical score. Execution order adds dependencies, spikes and risk (section 7), so the two differ on purpose.")
    A("* **DS queue scores differ.** `IMPLEMENTATION_QUEUE.json` uses a 10-dimension composite with a library-size bonus; DS queue ranks are kept as `ds_queue_rank` for traceability.")
    A("* **Gating.** A mined library whose pool is covered by an explicit `reference_only` finding is excluded unless a later reviewed decision (cross-donor slice plan S2/S3) chose a narrower technique use; those nuances are on the IO.")
    A("")
    A("## 4. Final ranked implementation opportunities")
    A("")
    A("| # | IO | Class | Score | Donors | Bucket | Wave | Exec. order | Cost / risk |")
    A("|---:|---|---|---:|---|---|---:|---:|---|")
    for x in R:
        A(f"| {x['rank']} | `{x['io_id']}` {_cell(x['title'])} | {x['class']} | {x['canonical_score']} | {_cell(_donors(x))} | {x['bucket']} | {x['wave']} | {x['execution_order']} | {x['cost']} / {x['risk']} |")
    A("")
    A("### Top 10")
    A("")
    for x in top10:
        A(f"{x['rank']}. **`{x['io_id']}`** - {x['title']} - *{x['class']}*, score {x['canonical_score']}, {x['bucket']}, wave {x['wave']}. {x['summary']}")
    A("")
    A("## 5. Implementation-ready shortlist (immediate candidates)")
    A("")
    A("Nature = canonical class (novel capability / novel detail / technique donor / component donor / enhancement candidate / replacement candidate).")
    A("")
    for x in sorted((i for i in R if i["bucket"] == "immediate"), key=lambda i: i["execution_order"]):
        A(f"### {x['execution_order']}. `{x['io_id']}` - {x['title']}")
        A("")
        A(f"* **Nature:** {x['class']} | **Score:** {x['canonical_score']} (rank {x['rank']}, {x['score_basis']}) | **Wave:** {x['wave']}" + (f" | **Slice:** {x['slice_ref']}" if x["slice_ref"] else ""))
        A(f"* **What:** {x['summary']}")
        A("* **Donors (scored):** " + "; ".join(f"{d['source_id']} [{d['generation']}, {d['role']}]: " + ", ".join(f"`{i['id']}`" for i in d["items"][:3]) + (f" +{len(d['items']) - 3} more" if len(d["items"]) > 3 else "") for d in x["donors"]))
        if x["corroboration"]:
            A("* **Corroboration (does not move the score):** " + "; ".join(f"{c['donor']} `{c['id']}` ({c['classification']}, {c['role']})" for c in x["corroboration"]))
        A("* **Likely files/subsystems:** " + ", ".join(f"`{f}`" for f in x["platinum_files"]))
        A("* **Depends on:** " + ("; ".join(x["depends_on"]) if x["depends_on"] else "none") + ("; spikes/gates: " + "; ".join(x["spikes_or_gates"]) if x["spikes_or_gates"] else ""))
        A(f"* **Cost/risk:** {x['cost']} / {x['risk']} | **Pixel use:** {x['pixel_use']}")
        A(f"* **Human review:** {x['human_review']}")
        A(f"* **Rollback:** {x['rollback']}")
        if x["reference_only_overlap_note"]:
            A(f"* **Note:** {x['reference_only_overlap_note']}")
        A("")
    A("### Later / high-cost candidates")
    A("")
    A("| IO | Nature | Score | Why later | Depends on / gate | Likely files |")
    A("|---|---|---:|---|---|---|")
    for x in sorted((i for i in R if i["bucket"] == "later"), key=lambda i: i["execution_order"]):
        why = x["reference_only_overlap_note"] or x["summary"]
        gate = "; ".join(x["depends_on"] + x["spikes_or_gates"]) or "none"
        A(f"| `{x['io_id']}` {_cell(x['title'])} | {x['class']} | {x['canonical_score']} | {_cell(textwrap.shorten(why, 150))} | {_cell(textwrap.shorten(gate, 110))} | {_cell(', '.join(x['platinum_files'][:3]))} |")
    A("")
    A("## 6. Deferred, gated, reference-only and evidence gaps")
    A("")
    A("### Gated out of the ranking (DS mined libraries)")
    A("")
    A("| Cluster | DS queue items | Records | Reason |")
    A("|---|---:|---:|---|")
    for g in o["gated_excluded"]:
        A(f"| `{g['gate_id']}` {_cell(g['title'])} | {len(g['ds_queue_items'])} | {g['ds_records']} | {_cell(g['reason'])} |")
    A("")
    A("### Unresolved but non-blocking evidence gaps")
    A("")
    A("| Id | Donor | Status | Affects | Note |")
    A("|---|---|---|---|---|")
    for g in o["evidence_gaps"]:
        A(f"| `{g['id']}` | {g['donor']} | {g['status']} | {g['affects']} | {_cell(g['note'])} |")
    A("")
    A("None of these blocks an immediate candidate. `defer:platinum/battle_overlay_oam_palette_headroom` becomes the first step of the `IO-STATUS` spike.")
    A("")
    A("## 7. Waves, dependencies and execution order")
    A("")
    for w, (t, d) in WAVES.items():
        items = [x for x in sorted(R, key=lambda i: i["execution_order"]) if x["wave"] == w]
        if not items:
            continue
        A(f"### {t}")
        A("")
        A(d)
        A("")
        for x in items:
            dep = ("; depends on " + "; ".join(x["depends_on"])) if x["depends_on"] else ""
            A(f"{x['execution_order']}. `{x['io_id']}` ({x['class']}, {x['canonical_score']}){dep}")
        A("")
    A("**Parallel tracks that need no engineering (start in Wave 1):** (a) card art-direction review for `IO-CARD`; (b) 2-3 pilot location previews art-direction for `IO-PREVIEW`; (c) four Platinum-side spikes: palette write path (`IO-PAL-CYCLE`), card BG layer (`IO-CARD`), battle OAM/palette headroom (`IO-STATUS`) and the overworld OBJ palette pipeline (`IO-FOL-SHEETS`).")
    A("")
    A("### Dependency graph")
    A("")
    A("```")
    A("IO-PAL-CYCLE   (none; spike: palette write path)")
    A("IO-CARD        (none; spike: BG layer)  ----soft----> IO-PREVIEW")
    A("IO-STATUS      (none; spike: OAM headroom)")
    A("IO-FOL-SHEETS  (spike: OBJ palette pipeline) ----> IO-FOL-MECH")
    A("IO-TRN-COMP    (none; review gate) ----> IO-PKM-COMP")
    A("```")
    A("")
    A("## 8. Duplicates and subsumption")
    A("")
    A("| Id | Kept | Absorbed | Decision |")
    A("|---|---|---|---|")
    for d in o["duplicates_subsumed"]:
        A(f"| {d['id']} | {_cell(d['kept'])} | {_cell('; '.join(d['absorbed']))} | {_cell(d['decision'])} |")
    A("")
    A("## 9. Informed design but not to be implemented (reference_only / reject)")
    A("")
    A("Kept for design understanding with donor identity; never ranked.")
    A("")
    A("| Id | Gen | Donor | Class | Subject | Merge |")
    A("|---|---|---|---|---|---|")
    for r in o["reference_only_register"]:
        m = r["merge"]["into"] if r.get("merge") else ""
        A(f"| `{r['id']}` | {r['generation']} | {r['donor']} | {r['classification']} | {_cell(textwrap.shorten(r['subject'], 110))} | {_cell(m)} |")
    A("")
    A("## 10. Recommended execution order and first slice")
    A("")
    A("| Order | IO | Why here |")
    A("|---:|---|---|")
    why = {
        "IO-PAL-CYCLE": "best first slice: no dependency, one small runtime spike, visible in every battle, produces a reusable service",
        "IO-CARD": "highest-novelty new screen type; art direction runs in Wave 1 so engineering starts with an approved look",
        "IO-STATUS": "new gameplay-facing feedback; starts with the OAM headroom spike",
        "IO-PREVIEW": "top canonical score but needs new art and a clean coexistence with the map-name popup; follows the card host",
        "IO-FOL-SHEETS": "ranks 2nd, but the OBJ palette pipeline is unproven; do a pilot subset after the spike",
        "IO-TRN-COMP": "cheap, risk-free authoring task that proves the component review gate; low impact, so it is filler, not a driver",
        "IO-FX-PRIM": "valid, but per-move targets have not been chosen", "IO-TEX-HGSS": "second pass over already graded assets",
        "IO-FX-SEQ": "G5 already applied the idea", "IO-FOL-MECH": "highest impact, lowest feasibility; needs sheets first",
        "IO-TEX-RANGER": "905 groups unscoped", "IO-NPC-COMP": "small, auto-scored", "IO-MODELS": "no NSBMD authoring pipeline",
        "IO-PKM-COMP": "hundreds of hand-reviewed sprites; needs the review gate first", "IO-PKM-REPL": "runtime QA gate", "IO-TRN-REPL": "runtime QA gate"}
    for x in sorted(R, key=lambda i: i["execution_order"]):
        A(f"| {x['execution_order']} | `{x['io_id']}` | {why.get(x['io_id'], '')} |")
    A("")
    f = byid["IO-PAL-CYCLE"]
    A("### Best first implementation slice: `IO-PAL-CYCLE`")
    A("")
    A(f"* Canonical score {f['canonical_score']} (rank {f['rank']}), the top-scoring item with no dependency, no new art direction and no donor pixels. Evidence: PMD Sky BPA palette animation (`mining/evidence/pmd_mapbg_bpa.json`), with FireRed's Elite Four/Champion palette sequences corroborating the timing shape.")
    A("* Scope: `src/battle/terrain.c` tick + data table, re-indexed water platform (day/evening/night), `generate_battle_terrain.py` extension. Rollback: remove one tick call and revert one PNG/PAL.")
    A("* Gate before merge: animated capture at game speed, subtle-vs-busy and photosensitivity review.")
    A("* **Differs from the earlier proposal.** `CROSS_DONOR_IMPLEMENTATION_PLAN.md` ordered S1 (Ace Trainer shading) first. Under the canonical weights S1 scores {s1} (visual impact 2, novelty 2, rank {r1} of {n}), and the review gate it proves mainly benefits lower-value component work. S1 moves to Wave 3 as a parallel authoring task; S2 leads. S3 (card) and S4 (area preview) keep the earlier relative order.".format(s1=byid["IO-TRN-COMP"]["canonical_score"], r1=byid["IO-TRN-COMP"]["rank"], n=len(R)))
    A("")
    A("## 11. Scope guard")
    A("")
    A("No file under `res/` or `src/` was modified. `PHASE_SCOPE.json` still governs the DS-only register/queue and is unchanged; this layer is separate and read-only over them. DS evidence files (`OPPORTUNITY_POOL.json`, `IMPLEMENTATION_QUEUE.json`, `findings.json`, ledgers) and Ruby are untouched; the Crystal angels item is not resolved. Added/updated: this plan, `CROSS_GEN_OPPORTUNITY_RANKING.json`, the four GBA/GBC artifacts, and the generator/validator scripts under `tools/visual_overhaul/selection/`.")
    A("")
    return "\n".join(L)
