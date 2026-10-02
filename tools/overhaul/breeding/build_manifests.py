#!/usr/bin/env python3
"""Generate the Breeding 2.0 manifests from the start commit and (optionally) apply
the guarded data edits (hatch cycles, breeder shop stock).

  build_manifests.py            write manifests (before-values read from START_SHA)
  build_manifests.py --apply    also apply edits; every edit asserts its before-value
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
import breeding_lib as L  # noqa: E402

AUTH = "BREEDING_SPEC.md"


def git_show(path):
    return subprocess.check_output(["git", "show", f"{L.START_SHA}:{path}"], cwd=L.ROOT).decode()


def write(name, obj):
    with open(os.path.join(L.IMPL, name), "w") as f:
        json.dump(obj, f, indent=2)
        f.write("\n")


def hatch_manifest():
    entries, floor = [], []
    for sp in sorted(L.hatch_scope(L.load_species())):
        path = f"res/pokemon/{sp[8:].lower()}/data.json"
        m = re.search(r'"hatch_cycles": (\d+),', git_show(path))
        before = int(m.group(1))
        if L.hatch_target(before) == before:
            floor.append(sp)
            continue
        entries.append({
            "species": sp,
            "source_path": path,
            "field": "hatch_cycles",
            "before": before,
            "target": L.hatch_target(before),
            "rationale": "target = max(5, ceil(vanilla / 2))",
            "locked_authority": f"{L.SPEC}#11",
        })
    return {
        "schema": "breeding_hatch_cycle_changes/1",
        "start_sha": L.START_SHA,
        "formula": "max(5, ceil(vanilla_hatch_cycles / 2))",
        "scope": "breedable species (egg group not Undiscovered/Ditto) plus every legitimate egg result (babies); Undiscovered-only species that never hatch are untouched",
        "flame_body_magma_armor": "unchanged: Party_GetEggCyclesToSubtract still subtracts 2 per cycle event",
        "unchanged_at_floor": floor,
        "entries": entries,
    }


def shop_manifest():
    src = git_show(L.SHOP_PATH)
    m = re.search(r"const u16 %s\[\] = \{(.*?)\};" % L.SHOP_STOCK_ARRAY, src, re.S)
    before = re.findall(r"\b(ITEM_\w+)", m.group(1))
    prices = {}
    for it in L.SHOP_ITEMS:
        js = git_show(f"res/items/data/{it[5:].lower()}.json")
        prices[it] = int(re.search(r'"price": (\d+)', js).group(1))
    return {
        "schema": "breeding_breeder_shop_changes/1",
        "start_sha": L.START_SHA,
        "vendor_id": L.SHOP_VENDOR_ID,
        "vendor": "Veilstone Department Store 2F (battle-item counter)",
        "source_path": L.SHOP_PATH,
        "stock_array": L.SHOP_STOCK_ARRAY,
        "before": before,
        "target": before + list(L.SHOP_ITEMS),
        "added": [{"item": it, "price": p, "price_source": f"res/items/data/{it[5:].lower()}.json", "price_before": prices[it]} for it, p in L.SHOP_ITEMS.items()],
        "rationale": "Veilstone Department Store is reachable at the 4th-badge window, not postgame/Frontier-gated, and is already a renewable vendor; prices are the existing item prices (spec #12), so no item JSON edits",
        "locked_authority": f"{L.SPEC}#12",
        "ditto": "no gift added; Ditto is a deterministic M1 wild placement (availability_families.json family 'ditto', wild_encounters.json)",
    }


def rules_manifest():
    return {
        "schema": "breeding_rules/1",
        "start_sha": L.START_SHA,
        "locked_authority": [L.SPEC, L.PLAN],
        "source": ["src/overlay005/daycare.c", "include/overlay005/breeding_rules.h", "include/constants/daycare.h"],
        "rules": [
            {"id": "everstone", "before": "50% inheritance, only from the female/Ditto parent", "target": "0 stones: random; 1: that parent 100%; 2: random holder 100%; no gender restriction", "symbol": "BreedingRules_PickNatureParent", "authority": f"{L.SPEC}#3"},
            {"id": "iv_count", "before": "NUM_INHERITED_IVS = 3 (selection could repeat a stat: RemoveIVIndexFromList removed loop index, not the picked stat)", "target": "NUM_INHERITED_IVS = 4, distinct stats", "symbol": "BreedingRules_SelectInheritedIVs", "authority": f"{L.SPEC}#4"},
            {"id": "power_items", "before": "none", "target": L.POWER_ITEMS, "note": "one guarantee; both holders -> random holder; Destiny Knot not implemented", "authority": f"{L.SPEC}#4"},
            {"id": "ability_slot", "before": "personality bit 0 random", "target": "80% species parent's slot / 20% other slot, only when the egg species has two distinct normal abilities", "representation": "ability slot is personality bit 0 (BoxPokemon_CalcAbility); the egg personality is re-rolled under the existing nature/ability constraints, no new state", "symbol": "BreedingRules_PickAbilitySlot", "species_parent": "non-Ditto parent (mother in a normal pair)", "authority": f"{L.SPEC}#5"},
            {"id": "egg_moves", "before": "father only", "target": "listed egg moves from either parent, father first, deduplicated; father TM/HM, shared level-up and Volt Tackle unchanged", "symbol": "BreedingRules_GatherEggMoves", "authority": f"{L.SPEC}#6"},
            {"id": "no_incense_babies", "before": "sIncenseBabyTable converted the baby to its adult unless a parent held the incense", "target": "table and Daycare_AlterEggSpeciesWithIncenseItem removed; offspring field (pms.narc) yields the baby", "babies": [{"baby": b, "adult": a, "former_incense": i} for b, a, i in L.NO_INCENSE_BABIES], "authority": f"{L.SPEC}#9"},
            {"id": "egg_check_interval", "before": "egg roll when day-care step counter & 0xff == 0xff (every 256 steps)", "target": "& 0x7f == 0x7f (every 128 steps); compatibility 0/20/50/70 unchanged", "symbol": "DAYCARE_EGG_CHECK_INTERVAL", "authority": f"{L.SPEC}#10"},
            {"id": "special_date_bonus", "before": "Daycare_GetEggCycleLength: 255 steps per hatch cycle, 230 on 12 special dates", "target": "unchanged", "normalization": "The 255/230 constant is the hatch-cycle length, not the egg-roll cadence (that is the day-care step counter above). Halving it would stack with the halved hatch_cycles table and make eggs hatch in ~1/4 of vanilla, contradicting spec #11 ('roughly half'). It is therefore left alone; the special-date micro-bonus only shortens hatching and cannot make the egg interval slower than ordinary overhaul breeding.", "authority": f"{L.PLAN}#9"},
            {"id": "hatch_cycles", "before": "species hatch_cycles", "target": "see hatch_cycle_changes.json", "authority": f"{L.SPEC}#11"},
            {"id": "flame_body_magma_armor", "before": "subtract 2 cycles per cycle event", "target": "unchanged", "symbol": "BreedingRules_EggCyclesToSubtract", "authority": f"{L.SPEC}#11"},
            {"id": "masuda", "before": "up to 4 ARNG personality rerolls when parent languages differ", "target": "same reroll count; rerolls keep the inherited Everstone nature and the chosen ability slot", "authority": f"{L.SPEC}#16"},
            {"id": "ball", "before": "Poké Ball", "target": "unchanged", "authority": f"{L.SPEC}#15"},
        ],
        "baseline_guards": {
            "daycare_c_blob": subprocess.check_output(["git", "rev-parse", f"{L.START_SHA}:src/overlay005/daycare.c"], cwd=L.ROOT).decode().strip(),
            "daycare_h_blob": subprocess.check_output(["git", "rev-parse", f"{L.START_SHA}:include/constants/daycare.h"], cwd=L.ROOT).decode().strip(),
            "vanilla_patterns": {
                "everstone_50_percent": "if (LCRNG_Next() >= (0xffff / 2)) {\n            return -1;",
                "female_ditto_only": "search for female gender",
                "inherited_ivs_3": "#define NUM_INHERITED_IVS 3",
                "father_only_egg_moves": "// Egg moves from the father",
                "incense_table": "sIncenseBabyTable",
                "interval_256": "& 0xff) == 0xff",
                "hatch_cycle_255": "return 255;",
                "flame_body_2": "return 2;",
                "masuda_loop": "for (i = 0; i < 4; i++) {\n                personality = ARNG_Next(personality);",
            },
        },
    }


def egg_group_manifest():
    return {"schema": "breeding_egg_group_changes/1", "start_sha": L.START_SHA, "locked_authority": f"{L.SPEC}#8", "note": "Legality audit found no egg-group edit that is required without a design decision; vanilla Platinum egg groups retained.", "entries": []}


AUTH_RULING = "owner ruling on PR #18: preserve family egg moves orphaned by no-incense breeding; remove entries with no legal one-save donor chain"
MIGRATE = [
    ("SPECIES_MARILL", "SPECIES_AZURILL", ["MOVE_LIGHT_SCREEN", "MOVE_PRESENT", "MOVE_AMNESIA", "MOVE_FUTURE_SIGHT", "MOVE_BELLY_DRUM", "MOVE_PERISH_SONG", "MOVE_SUPERSONIC", "MOVE_AQUA_JET"]),
    ("SPECIES_SNORLAX", "SPECIES_MUNCHLAX", ["MOVE_FISSURE"]),
]
REMOVE = [
    ("SPECIES_CLEFFA", "MOVE_BELLY_DRUM"),
    ("SPECIES_IGGLYBUFF", "MOVE_PERISH_SONG"),
    ("SPECIES_GEODUDE", "MOVE_MEGA_PUNCH"),
    ("SPECIES_MANKEY", "MOVE_MEDITATE"),
    ("SPECIES_SHELLDER", "MOVE_TAKE_DOWN"),
]


def egg_moves_at_start(sp):
    return list(json.loads(git_show(f"res/pokemon/{sp[8:].lower()}/data.json"))["learnset"].get("egg_moves", []))


def egg_move_manifest():
    edits = {}
    for adult, baby, moves in MIGRATE:
        before = egg_moves_at_start(baby)
        assert not set(moves) & set(before)
        assert set(moves) <= set(egg_moves_at_start(adult))
        edits[baby] = {"species": baby, "source_path": f"res/pokemon/{baby[8:].lower()}/data.json", "before": before, "target": before + moves,
                       "rationale": f"preserve existing {adult[8:].title()}-family egg moves orphaned because no-incense breeding now hatches {baby[8:].title()}; moves taken from the former {adult[8:].title()} list",
                       "locked_authority": [AUTH_RULING, f"{L.SPEC}#9"]}
    for sp, mv in REMOVE:
        e = edits.setdefault(sp, {"species": sp, "source_path": f"res/pokemon/{sp[8:].lower()}/data.json", "before": egg_moves_at_start(sp), "rationale": "", "locked_authority": [AUTH_RULING, f"{L.SPEC}#7"]})
        e["target"] = [m for m in e["target"] if m != mv] if "target" in e else [m for m in e["before"] if m != mv]
        e["rationale"] = f"remove {mv}: no legal one-save donor chain under the final egg groups/learnsets; no unrelated data changed to create one"
    entries = [edits[k] for k in sorted(edits)]
    return {
        "schema": "breeding_egg_move_changes/1",
        "start_sha": L.START_SHA,
        "locked_authority": [f"{L.SPEC}#7", AUTH_RULING],
        "note": "Targeted repair only; adult-keyed lists are left as dead data (those species can no longer hatch).",
        "entries": entries,
        "migrated_moves": [{"from": a, "to": b, "moves": m} for a, b, m in MIGRATE],
        "removed_moves": [{"egg_species": s, "move": m} for s, m in REMOVE],
        "unreachable_pending_design": [],
    }


def apply_egg_moves(man):
    for e in man["entries"]:
        p = os.path.join(L.ROOT, e["source_path"])
        s = open(p).read()
        m = re.search(r'("egg_moves": \[)(.*?)(\n\s*\])', s, re.S)
        cur = re.findall(r'"(MOVE_\w+)"', m.group(2))
        if cur == e["target"]:
            continue
        assert cur == e["before"], f"{e['species']}: egg_moves {cur} != guard"
        indent = re.search(r"\n(\s*)\"MOVE_", m.group(2)).group(1)
        body = ",".join(f'\n{indent}"{x}"' for x in e["target"])
        s = s[: m.start(2)] + body + s[m.end(2):]
        open(p, "w").write(s)


def apply_hatch(man):
    for e in man["entries"]:
        p = os.path.join(L.ROOT, e["source_path"])
        s = open(p).read()
        m = re.search(r'"hatch_cycles": (\d+),', s)
        cur = int(m.group(1))
        if cur == e["target"]:
            continue
        assert cur == e["before"], f"{e['species']}: hatch_cycles {cur} != guard {e['before']}"
        s = s[: m.start()] + f'"hatch_cycles": {e["target"]},' + s[m.end():]
        open(p, "w").write(s)


def apply_shop(man):
    p = os.path.join(L.ROOT, man["source_path"])
    s = open(p).read()
    m = re.search(r"(const u16 %s\[\] = \{)(.*?)(\};)" % man["stock_array"], s, re.S)
    items = re.findall(r"(ITEM_\w+|SHOP_ITEM_END)", m.group(2))
    cur = [i for i in items if i != "SHOP_ITEM_END"]
    if cur == man["target"]:
        return
    assert cur == man["before"], f"{man['stock_array']} stock {cur} != guard"
    body = "\n" + "".join(f"    {i},\n" for i in man["target"]) + "    SHOP_ITEM_END\n"
    s = s[: m.start(2)] + body + s[m.end(2):]
    open(p, "w").write(s)


def main():
    os.makedirs(L.IMPL, exist_ok=True)
    hatch, shop, emm = hatch_manifest(), shop_manifest(), egg_move_manifest()
    for name, obj in [("breeding_rules.json", rules_manifest()), ("egg_group_changes.json", egg_group_manifest()), ("egg_move_changes.json", emm), ("hatch_cycle_changes.json", hatch), ("breeder_shop_changes.json", shop)]:
        write(name, obj)
    if "--apply" in sys.argv:
        apply_hatch(hatch)
        apply_egg_moves(emm)
        apply_shop(shop)
        print(f"applied {len(hatch['entries'])} hatch-cycle edits and the {shop['stock_array']} stock edit")


if __name__ == "__main__":
    main()
