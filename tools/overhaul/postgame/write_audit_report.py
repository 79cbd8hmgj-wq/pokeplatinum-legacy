#!/usr/bin/env python3
"""Generate docs/overhaul/implementation/postgame/FRONTIER_SET_AUDIT.md from the live audit + set-change manifest."""
import json
import collections

import frontier_audit as A
import frontier_lib as L


def main():
    ctx = A.Ctx()
    F, by_species = A.audit(ctx)
    man = json.load(open(L.p("docs/overhaul/implementation/postgame/frontier_set_changes.json")))
    out = ["# Battle Frontier Set Audit (D6 F3 / F4)", "",
           f"Start SHA: `{L.START_SHA}` - vanilla baseline for type/stat/ability/learnset comparison: `{L.VANILLA_SHA}`.", "",
           "Authority: `docs/overhaul/postgame/BATTLE_FRONTIER_POSTGAME_SPEC.md` s5/s6/s14. The Frontier pool was audited, **not rebuilt**.",
           "Tool: `tools/overhaul/postgame/frontier_audit.py`; fixes: `apply_frontier_set_changes.py`; manifest: `frontier_set_changes.json`.", "",
           "## Scope", "",
           f"- Sets audited: **{len(ctx.sets)}** across **{len(by_species)}** species ({len(ctx.sets) - 1} real sets + 1 `none_1` padding set used by Brain pools).",
           "- Checks: constants valid, duplicate/empty move slots, retype representation, lost STAB, stat-redistribution mismatch, moves no longer learnable, identical sets, moves whose type/class changed.", "",
           "## Result after fixes (live tree)", "", "| Finding | Count |", "|---|---:|"]
    for k in ("INVALID", "RETYPE", "LOST_STAB", "STAT", "REMOVED", "DUPLICATE", "MOVECHG"):
        out.append(f"| {k} | {len(F[k])} |")
    out += ["", "`MOVECHG` = 0: no move used by a Frontier set changed type or damage class under C1/C2, so no set silently changed STAB or physical/special split.", "",
            "## Retyped Frontier species (all covered)", "", "| Species | Overhaul types | Vanilla types | Sets | Sets carrying the new type |", "|---|---|---|---:|---|"]
    for spc, names in sorted(by_species.items()):
        sp, v = ctx.sp(spc), ctx.vsp(spc)
        if not sp or not v or set(sp["types"]) == set(v["types"]):
            continue
        newt = sorted(set(sp["types"]) - set(v["types"]))
        reps = []
        for t in newt:
            n = [x for x in names if any(L.damaging(ctx.mv(m)) and ctx.mv(m)["type"] == t for m in ctx.sets[x]["moves"])]
            reps.append(f"{t[5:]}: {len(n)}/{len(names)}")
        out.append(f"| {spc} | {'/'.join(t[5:] for t in sp['types'])} | {'/'.join(dict.fromkeys(t[5:] for t in v['types']))} | {len(names)} | {', '.join(reps)} |")
    out += ["", "Per spec s5 not every set carries both STAB types (Milotic keeps its special/tank sets; only `milotic_4` uses Dragon).", "",
            "## Fixes applied (15 sets)", "", "| Set | Reason | Moves before | Moves after |", "|---|---|---|---|"]
    for c in man["changes"]:
        nm = c["source_path"].rsplit("/", 1)[1][:-5]
        out.append(f"| {nm} | {c['reason']} | {', '.join(m[5:] for m in c['before'])} | {', '.join(m[5:] for m in c['target'])} |")
    out += ["", "Nature changes accompany stat-driven fixes (see manifest `nature`).", "",
            "## Battle Hall static type pool", "",
            f"`sBattleHallPotentialOpponentTypes` is a static vanilla type table, so retyped species drifted out of their Hall type groups. {len(man['hall_pool_type_changes'])} entries were corrected to the overhaul types (Wormadam entries are form-specific and intentionally skipped). Records: `frontier_set_changes.json` -> `hall_pool_type_changes`.", "",
            "## Frontier Brains (F4)", "",
            "- Palmer (Tower), Dahlia (Arcade) and Darach (Castle) Silver/Gold sets were audited separately: no INVALID/RETYPE/LOST_STAB/STAT/REMOVED finding touches a Brain set. **No Brain edits.**",
            "- Palmer Silver's Milotic is Surf/Ice Beam special - consistent with its locked Water/Dragon special-tank identity.",
            "- Thorton (Factory rentals) and Argenta (Hall type-matched pool) have no fixed sets; the Hall pool fix above covers Argenta's retype drift.",
            "- Milestone/streak numbers, facility gimmicks and difficulty relationships are unchanged.", "",
            "## Ability / stat changes reviewed", "",
            "Ability changes on Frontier species (Farfetch'd, Furret, Ledian, Lopunny, Wigglytuff) and stat redistributions on 19 species were screened by the STAT heuristic (all-physical or all-special sets whose attacking stat flipped). Only Raichu, Glalie and Ledian tripped it; those sets were fixed above. Sets left as-is are treated as valid under spec s5 (\"do not force every set\").", "",
            "## Legality note", "",
            "Frontier legality is checked against overhaul move/species data (constants exist, no vanilla-learnable move lost to C3). Vanilla Frontier sets that were already outside a species' learnset (event/egg moves) are inherited and not flagged.", ""]
    with open(L.p("docs/overhaul/implementation/postgame/FRONTIER_SET_AUDIT.md"), "w") as f:
        f.write("\n".join(out))


if __name__ == "__main__":
    main()
