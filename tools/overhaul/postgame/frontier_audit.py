#!/usr/bin/env python3
"""D6 F3/F4: audit every Battle Frontier Pokemon set against the overhaul data.

Findings (see docs/overhaul/implementation/postgame/FRONTIER_SET_AUDIT.md):
  INVALID   species/move constant with no data, or empty/duplicate move slot  (always a FAIL)
  RETYPE    retyped species whose new type has no damaging representation in ANY of its sets
  LOST_STAB set whose only STAB came from a type the species no longer has (vanilla set had STAB)
  STAT      set whose damaging moves are all on the weaker offensive stat after redistribution
  REMOVED   move that was learnable by the species in vanilla but is no longer learnable
  DUPLICATE two set files of one species with identical moves/item/nature
  MOVECHG   set uses a move whose type or class changed in C1/C2

`audit()` returns the structured findings; `main()` prints a summary.
"""
import collections
import json
import sys

import frontier_lib as L


class Ctx:
    def __init__(self):
        self.sets = L.load_sets()
        self.tm = L.tm_moves()
        self._sp, self._vsp, self._mv, self._vmv = {}, {}, {}, {}

    def sp(self, c):
        if c not in self._sp:
            self._sp[c] = L.species_data(c)
        return self._sp[c]

    def vsp(self, c):
        if c not in self._vsp:
            self._vsp[c] = L.species_data(c, L.VANILLA_SHA)
        return self._vsp[c]

    def mv(self, c):
        if c not in self._mv:
            self._mv[c] = L.move_data(c)
        return self._mv[c]

    def vmv(self, c):
        if c not in self._vmv:
            self._vmv[c] = L.move_data(c, L.VANILLA_SHA)
        return self._vmv[c]


def offence_ratio(stats):
    return stats["attack"] / max(1, stats["special_attack"])


def audit(ctx=None):
    ctx = ctx or Ctx()
    F = collections.defaultdict(list)
    by_species = collections.defaultdict(list)
    for name, s in ctx.sets.items():
        by_species[s["species"]].append(name)

    for name, s in sorted(ctx.sets.items()):
        spc = s["species"]
        if spc == "SPECIES_NONE":  # vanilla padding set used to fill short Brain pools
            F["PLACEHOLDER"].append((name, "SPECIES_NONE padding set"))
            continue
        sp, vsp = ctx.sp(spc), ctx.vsp(spc)
        if sp is None:
            F["INVALID"].append((name, f"species {spc} has no data"))
            continue
        moves = s["moves"]
        if len(moves) != len(set(moves)) or "MOVE_NONE" in moves:
            F["INVALID"].append((name, "duplicate or MOVE_NONE slot"))
        for m in moves:
            if ctx.mv(m) is None:
                F["INVALID"].append((name, f"{m} has no move data"))
        dmg = [m for m in moves if L.damaging(ctx.mv(m))]
        types = set(sp["types"])
        vtypes = set(vsp["types"]) if vsp else types
        stab_now = [m for m in dmg if ctx.mv(m)["type"] in types]
        # lost STAB: vanilla version of the set had STAB on a removed type and now has none
        if types != vtypes and dmg and not stab_now:
            F["LOST_STAB"].append((name, f"types {sorted(types)} (was {sorted(vtypes)}), no damaging STAB"))
        # stat redistribution
        if vsp and sp["base_stats"] != vsp["base_stats"] and dmg:
            phys = sum(1 for m in dmg if ctx.mv(m)["class"] == "CLASS_PHYSICAL")
            spec = sum(1 for m in dmg if ctx.mv(m)["class"] == "CLASS_SPECIAL")
            r, vr = offence_ratio(sp["base_stats"]), offence_ratio(vsp["base_stats"])
            if phys and not spec and r < 0.8 and vr >= 0.8:
                F["STAT"].append((name, f"all-physical set but Atk/SpA now {r:.2f} (was {vr:.2f})"))
            if spec and not phys and r > 1.25 and vr <= 1.25:
                F["STAT"].append((name, f"all-special set but Atk/SpA now {r:.2f} (was {vr:.2f})"))
        # removed (previously learnable, no longer learnable)
        if vsp:
            now, then = L.learnable(sp, ctx.tm), L.learnable(vsp, ctx.tm)
            for m in moves:
                if m in then and m not in now:
                    F["REMOVED"].append((name, f"{m} no longer learnable"))
        for m in moves:
            a, b = ctx.mv(m), ctx.vmv(m)
            if a and b and (a["type"] != b["type"] or a["class"] != b["class"]):
                F["MOVECHG"].append((name, f"{m}: {b['type']}/{b['class']} -> {a['type']}/{a['class']}"))

    # species-level retype representation
    for spc, names in sorted(by_species.items()):
        sp, vsp = ctx.sp(spc), ctx.vsp(spc)
        if not sp or not vsp or set(sp["types"]) == set(vsp["types"]):
            continue
        for t in sorted(set(sp["types"]) - set(vsp["types"])):
            have = [n for n in names for m in ctx.sets[n]["moves"] if L.damaging(ctx.mv(m)) and ctx.mv(m)["type"] == t]
            if not have:
                F["RETYPE"].append((spc, f"new type {t} not represented by any of {len(names)} sets"))

    # exact duplicates
    seen = {}
    for name, s in sorted(ctx.sets.items()):
        key = (s["species"], tuple(sorted(s["moves"])), s["item"], s["nature"])
        if key in seen:
            F["DUPLICATE"].append((name, f"identical to {seen[key]}"))
        else:
            seen[key] = name
    return F, by_species


def main():
    F, by_species = audit()
    for k in ("INVALID", "PLACEHOLDER", "RETYPE", "LOST_STAB", "STAT", "REMOVED", "DUPLICATE", "MOVECHG"):
        print(f"{k}: {len(F[k])}")
        if "-v" in sys.argv:
            for n, msg in F[k]:
                print(f"  {n}: {msg}")
    return len(F["INVALID"])


if __name__ == "__main__":
    sys.exit(main())
