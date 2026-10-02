#!/usr/bin/env python3
"""Build docs/overhaul/implementation/evolution_manifest.json from the pinned base commit + locked overlay."""
import json
import os
import sys

from evo_lib import (ALL_METHODS, BASE_COMMIT, CHANGE_AUTHORITY, EVOLUTION_STONES, LOCKED_FINAL, LOCKED_KEEP, MANIFEST,
                     NEW_METHODS, ROOT, UNRESOLVED, VANILLA_METHODS, data_path, final_tables, load_base_tables,
                     species_const)

SUPERSEDED = [
    "trade evolution (any)", "trade-with-held-item evolution (Metal Coat, King's Rock, Dragon Scale, Protector, Electirizer, "
    "Magmarizer, Reaper Cloth, Up-Grade, Dubious Disc, Deep Sea Tooth, Deep Sea Scale)",
    "direct use of non-stone items as evolution triggers",
    "level + held Razor Fang / Razor Claw / Metal Coat / King's Rock / Dragon Scale / Protector / Electirizer / Magmarizer / "
    "Reaper Cloth / Up-Grade / Dubious Disc",
    "earliest provisional trade-evolution level suggestions where later Pass A / C3 values differ",
]

NEW_METHOD_SEMANTICS = {
    "EVO_LEVEL_SPATK_GT_ATK": "level >= param AND SpA > Atk (strict)",
    "EVO_LEVEL_SPATK_GE_ATK": "level >= param AND SpA >= Atk (equality included)",
    "EVO_LEVEL_ATK_GT_SPATK": "level >= param AND Atk > SpA (strict)",
    "EVO_LEVEL_SPDEF_GT_DEF": "level >= param AND SpD > Def (strict)",
    "EVO_LEVEL_NIGHT": "level >= param AND IsNight() (no held item required)",
    "EVO_LEVEL_DAY": "level >= param AND NOT IsNight() (no held item required)",
}


def classify(species: str, edge: list, before: list) -> str:
    if species in UNRESOLVED and edge == UNRESOLVED[species]["edge"]:
        return "UNRESOLVED_AUTHORITY"
    if species in LOCKED_FINAL:
        return "LOCKED_KEEP" if edge in before else "LOCKED_CHANGED"
    if species in LOCKED_KEEP:
        return "LOCKED_KEEP"
    return "VANILLA_KEEP"


def build() -> dict:
    base = load_base_tables()
    final = final_tables(base)
    species_entries, edges = [], []
    counts = {"LOCKED_CHANGED": 0, "LOCKED_KEEP": 0, "VANILLA_KEEP": 0, "UNRESOLVED_AUTHORITY": 0, "SUPERSEDED_EARLY_PROPOSAL": 0}
    for sp in sorted(final):
        before, after = base.get(sp, []), final[sp]
        classes = [classify(sp, e, before) for e in after]
        changed = after != before
        entry = {"species": species_const(sp), "dir": sp, "source": data_path(sp), "before": before, "after": after,
                 "changed": changed, "edge_classes": classes}
        if sp in CHANGE_AUTHORITY:
            entry["authority_key"], entry["provenance"] = CHANGE_AUTHORITY[sp]
        if sp in LOCKED_KEEP:
            entry["authority_key"], entry["provenance"] = "LOCKED_KEEP", LOCKED_KEEP[sp]
        if sp in UNRESOLVED:
            entry["authority_key"] = UNRESOLVED[sp]["key"]
            entry["provenance"] = "UNRESOLVED: global no-held-item rule applies but no final method was recovered; left as vanilla"
        species_entries.append(entry)
        for i, (e, c) in enumerate(zip(after, classes)):
            counts[c] += 1
            edges.append({"species": species_const(sp), "index": i, "edge": e, "class": c})
    n_changed_species = sum(1 for s in species_entries if s["changed"])
    return {
        "schema": "evolution_manifest/1",
        "base_commit": BASE_COMMIT,
        "scope": "res/pokemon/*/data.json evolutions + minimal evolution-engine methods",
        "engine_methods": {
            "vanilla_count": len(VANILLA_METHODS),
            "new": [{"id": ALL_METHODS.index(m), "name": m, "semantics": NEW_METHOD_SEMANTICS[m]} for m in NEW_METHODS],
            "first_match_wins": True,
        },
        "evolution_stones": EVOLUTION_STONES,
        "superseded_early_proposals": SUPERSEDED,
        "unresolved_authority": [{"species": species_const(k), "key": v["key"], "edge": v["edge"],
                                  "note": "Held Oval Stone (day) evolution is not a genuine stone use and no replacement was ever recovered; "
                                          "left vanilla and reported. Statically achievable in one save (Lost Tower 2F field item; common held item of wild Happiny/Chansey/Blissey)."}
                                 for k, v in UNRESOLVED.items()],
        "summary": {"evolution_bearing_species": len(species_entries), "total_edges": len(edges),
                    "edge_class_counts": counts, "species_with_changed_tables": n_changed_species,
                    "changed_edges": counts["LOCKED_CHANGED"]},
        "species": species_entries,
        "edges": edges,
    }


def main() -> int:
    m = build()
    path = os.path.join(ROOT, MANIFEST)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=1)
        f.write("\n")
    print(json.dumps(m["summary"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
