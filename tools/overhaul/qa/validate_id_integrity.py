#!/usr/bin/env python3
"""D7 §5/§19: every move/species/item constant referenced by trainers, Frontier sets, learnsets, evolutions and the
availability manifests must exist (invalid ID = release blocker)."""
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from qa_lib import ROOT, Checker, jl, lines, species_data  # noqa: E402


def main():
    c = Checker("ID integrity")
    moves, items, species = set(lines("generated/moves.txt")), set(lines("generated/items.txt")), set(lines("generated/species.txt"))
    moves.discard("MAX_MOVES")
    none_ok = {"ITEM_NONE", "MOVE_NONE", None, ""}

    def mv(ref, where):
        if ref not in none_ok:
            c.check(ref in moves, f"{where}: invalid move {ref}")

    def it(ref, where):
        if ref not in none_ok:
            c.check(ref in items, f"{where}: invalid item {ref}")

    def sp(ref, where):
        c.check(ref in species, f"{where}: invalid species {ref}")

    for name, d in species_data().items():
        w = f"pokemon/{name}"
        for _, m in d["learnset"]["by_level"]:
            mv(m, w)
        for m in d["learnset"].get("egg_moves", []) + d["learnset"].get("by_tutor", []):
            mv(m, w)
        for e in d.get("evolutions", []):
            sp(e[-1], w)
            if e[0] == "EVO_LEVEL_KNOW_MOVE":
                mv(e[1], w)
            elif e[0] in ("EVO_USE_ITEM", "EVO_USE_ITEM_MALE", "EVO_USE_ITEM_FEMALE"):
                it(e[1], w)
            elif e[0] == "EVO_LEVEL_SPECIES_IN_PARTY":
                sp(e[1], w)
        for h in d.get("held_items", {}).values():
            it(h, w)
    for p in glob.glob(os.path.join(ROOT, "res/trainers/data/*.json")):
        j, w = jl(os.path.relpath(p, ROOT)), "trainer/" + os.path.basename(p)
        for i in j.get("items", []):
            it(i, w)
        for m in j["party"]:
            sp(m["species"], w)
            it(m.get("item"), w)
            for x in (m.get("moves") or []):
                mv(x, w)
    sets = set()
    for p in glob.glob(os.path.join(ROOT, "res/trainers/frontier/pokemon/*.json")):
        j, w = jl(os.path.relpath(p, ROOT)), "frontier_set/" + os.path.basename(p)
        sets.add(os.path.basename(p)[:-5])
        sp(j["species"], w)
        it(j.get("item"), w)
        for x in j["moves"]:
            mv(x, w)
    for p in glob.glob(os.path.join(ROOT, "res/trainers/frontier/data/*.json")):
        j, w = jl(os.path.relpath(p, ROOT)), "frontier_trainer/" + os.path.basename(p)
        for s in j.get("availableSets", []):
            c.check(s in sets, f"{w}: availableSets references missing set {s}")
    for e in jl("docs/overhaul/implementation/wild_encounters.json")["entries"]:
        sp(e["species"], "wild_encounters.json")
    for ev in jl("docs/overhaul/implementation/events/native_legendary_events.json")["events"]:
        sp(ev["species"], "events")
    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
