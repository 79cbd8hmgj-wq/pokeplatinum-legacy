"""Shared data loading, hatch-cycle math and the one-save egg-move legality audit
for Breeding 2.0 (docs/overhaul/breeding/BREEDING_SPEC.md)."""
import glob
import json
import math
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
IMPL = os.path.join(ROOT, "docs", "overhaul", "implementation", "breeding")
START_SHA = "e2d73d33a702bc151ae283a1245ebf64575476ed"
SPEC = "docs/overhaul/breeding/BREEDING_SPEC.md"
PLAN = "docs/overhaul/breeding/BREEDING_IMPLEMENTATION_PLAN.md"

NO_INCENSE_BABIES = [
    ("SPECIES_WYNAUT", "SPECIES_WOBBUFFET", "ITEM_LAX_INCENSE"),
    ("SPECIES_AZURILL", "SPECIES_MARILL", "ITEM_SEA_INCENSE"),
    ("SPECIES_MIME_JR", "SPECIES_MR_MIME", "ITEM_ODD_INCENSE"),
    ("SPECIES_BONSLY", "SPECIES_SUDOWOODO", "ITEM_ROCK_INCENSE"),
    ("SPECIES_MUNCHLAX", "SPECIES_SNORLAX", "ITEM_FULL_INCENSE"),
    ("SPECIES_MANTYKE", "SPECIES_MANTINE", "ITEM_WAVE_INCENSE"),
    ("SPECIES_BUDEW", "SPECIES_ROSELIA", "ITEM_ROSE_INCENSE"),
    ("SPECIES_HAPPINY", "SPECIES_CHANSEY", "ITEM_LUCK_INCENSE"),
    ("SPECIES_CHINGLING", "SPECIES_CHIMECHO", "ITEM_PURE_INCENSE"),
]
POWER_ITEMS = {
    "ITEM_POWER_WEIGHT": "STAT_HP",
    "ITEM_POWER_BRACER": "STAT_ATTACK",
    "ITEM_POWER_BELT": "STAT_DEFENSE",
    "ITEM_POWER_LENS": "STAT_SPECIAL_ATTACK",
    "ITEM_POWER_BAND": "STAT_SPECIAL_DEFENSE",
    "ITEM_POWER_ANKLET": "STAT_SPEED",
}
SHOP_ITEMS = {"ITEM_EVERSTONE": 200, **{k: 3000 for k in POWER_ITEMS}}
SHOP_STOCK_ARRAY = "VeilstoneDeptStoreStock_2F_UP"
SHOP_VENDOR_ID = "MART_SPECIALTIES_ID_VEILSTONE_2F_UP"
SHOP_PATH = "include/data/mart_items.h"


def hatch_target(vanilla):
    return max(5, math.ceil(vanilla / 2))


def species_const(dirname):
    return "SPECIES_" + dirname.upper()


def load_species():
    out = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "res/pokemon/*/data.json"))):
        name = os.path.basename(os.path.dirname(f))
        d = json.load(open(f))
        d["_path"] = os.path.relpath(f, ROOT)
        out[species_const(name)] = d
    return out


def is_breedable(d):
    return d["egg_groups"][0] not in ("EGG_GROUP_UNDISCOVERED", "EGG_GROUP_DITTO")


def hatch_scope(species):
    """Species whose hatch_cycles are halved: every breedable species plus every
    legitimate egg result (offspring of a breedable species, i.e. the babies)."""
    scope = {s for s, d in species.items() if is_breedable(d)}
    scope |= {d["offspring"] for d in species.values() if is_breedable(d)}
    scope.discard("SPECIES_NONE")
    return scope


def egg_species_of(species, mother):
    """Egg species a given non-Ditto mother can produce (mirrors
    Egg_DetermineEggSpeciesAndParentSlots)."""
    base = species[mother]["offspring"]
    if base == "SPECIES_NIDORAN_F":
        return {"SPECIES_NIDORAN_F", "SPECIES_NIDORAN_M"}
    if base == "SPECIES_ILLUMISE":
        return {"SPECIES_ILLUMISE", "SPECIES_VOLBEAT"}
    if base == "SPECIES_MANAPHY":
        return {"SPECIES_PHIONE"}
    return {base}


# ---------------------------------------------------------------- legality audit
def tm_moves():
    out = {}
    for f in glob.glob(os.path.join(ROOT, "res/items/data/[th]m[0-9][0-9].json")):
        d = json.load(open(f))
        out[d["name"]] = d["teachesMove"]
    return out


def ancestors(species):
    parents = {}
    for s, d in species.items():
        for evo in d.get("evolutions", []):
            parents.setdefault(evo[-1], set()).add(s)
    memo = {}

    def anc(s):
        if s in memo:
            return memo[s]
        memo[s] = set()
        r = set()
        for p in parents.get(s, ()):
            r.add(p)
            r |= anc(p)
        memo[s] = r
        return r

    return {s: anc(s) for s in species}


def obtainable_species(species):
    fams = json.load(open(os.path.join(ROOT, "docs/overhaul/implementation/availability_families.json")))["families"]
    ok = set()
    for f in fams:
        if f["classification"] == "NONLEGENDARY":
            ok |= set(f["components"])
    return {s for s in ok if s in species}


def can_be_mother(d):
    return d["gender_ratio"] not in ("GENDER_RATIO_MALE_ONLY", "GENDER_RATIO_NO_GENDER")


def can_be_father(d):
    return d["gender_ratio"] not in ("GENDER_RATIO_FEMALE_ONLY", "GENDER_RATIO_NO_GENDER")


def audit_egg_moves(species):
    """For each (egg species, listed egg move) find a legal same-save chain.

    A chain needs: obtainable parents A (the species parent) and Q that can legally
    breed (shared egg group, opposite genders, or one Ditto), egg species resulting,
    and at least one parent that can know the move (learn it, or hold it from its own
    egg-move heritage).  Fixpoint over heritage.  Returns {(species, move): witness|None}.
    """
    tms = tm_moves()
    anc = ancestors(species)
    obtain = obtainable_species(species)

    learn = {}
    for s, d in species.items():
        ls = d["learnset"]
        moves = {m for _, m in ls["by_level"]}
        moves |= {tms[t] for t in ls.get("by_tm", []) if t in tms}
        moves |= set(ls.get("by_tutor", []))
        learn[s] = moves
    learn_line = {s: set(learn[s]).union(*[learn[a] for a in anc[s]]) if anc[s] else set(learn[s]) for s in species}

    breeders = [s for s in obtain if is_breedable(species[s])]
    ditto_ok = "SPECIES_DITTO" in obtain
    groups = {s: set(species[s]["egg_groups"]) for s in breeders}

    egg_lists = {}
    for s, d in species.items():
        em = d["learnset"].get("egg_moves", [])
        if em:
            egg_lists[s] = list(em)
    targets = [(s, m) for s in egg_lists for m in egg_lists[s]]

    reach = {t: None for t in targets}
    mothers_of = {}
    for a in breeders:
        for e in egg_species_of(species, a):
            mothers_of.setdefault(e, []).append(a)

    def knows(s, m, reach_now):
        if m in learn_line[s]:
            return "learn"
        for b in {s} | anc[s]:
            if (b, m) in reach_now and reach_now[(b, m)]:
                return "egg:" + b
        return None

    changed = True
    while changed:
        changed = False
        for (e, m) in targets:
            if reach[(e, m)]:
                continue
            witness = None
            for a in mothers_of.get(e, []):
                if not (can_be_mother(species[a]) or ditto_ok):
                    continue
                k = knows(a, m, reach)
                if k and ditto_ok:
                    witness = (a, "SPECIES_DITTO", k)
                    break
                for q in breeders:
                    if not (groups[a] & groups[q]):
                        continue
                    if not (can_be_mother(species[a]) and can_be_father(species[q])):
                        continue
                    k = knows(a, m, reach) or knows(q, m, reach)
                    if k:
                        witness = (a, q, k)
                        break
                if witness:
                    break
            if witness:
                reach[(e, m)] = witness
                changed = True
    dead = sorted(s for s in egg_lists if s not in set(offspring_species(species)))
    return reach, dead


def offspring_species(species):
    out = set()
    for s, d in species.items():
        if is_breedable(d):
            out |= egg_species_of(species, s)
    return out


def orphan_report(species, dead):
    """For adult-keyed egg lists that can no longer hatch: the moves that exist nowhere
    else (not on the baby's list, not learnable by the adult's evolution line)."""
    tms = tm_moves()
    anc = ancestors(species)
    baby_of = {a: b for b, a, _ in NO_INCENSE_BABIES}
    out = {}
    for a in dead:
        line = {a} | anc[a]
        learn = set()
        for s in line:
            ls = species[s]["learnset"]
            learn |= {m for _, m in ls["by_level"]} | {tms[t] for t in ls.get("by_tm", []) if t in tms} | set(ls.get("by_tutor", []))
        keep = set(species[baby_of[a]]["learnset"].get("egg_moves", []))
        out[a] = [m for m in species[a]["learnset"]["egg_moves"] if m not in keep and m not in learn]
    return out


def split_unreachable(species):
    reach, dead = audit_egg_moves(species)
    live = sorted(k for k, v in reach.items() if not v and k[0] not in set(dead))
    return reach, dead, live, orphan_report(species, dead)
