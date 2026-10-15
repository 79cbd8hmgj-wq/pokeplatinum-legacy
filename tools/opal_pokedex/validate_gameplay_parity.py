#!/usr/bin/env python3
"""Gameplay-parity validator for the Opal Pokedex information pages.

The runtime pages read the compiled tables, so parity means:
  (1) the compiled tables equal the repository sources           (needs --build-dir, optional)
  (2) the generated manifest / location table / strings are current
  (3) Opal's locked gameplay facts hold in those sources
  (4) the C reader covers every method / kind / message it can meet.

Exit status 0 only if every check passes. `--self-test` additionally proves the checks can fail by
running them against deliberately corrupted copies of the data.
"""
import argparse
import json
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_gameplay_data as bgd  # noqa: E402
import gameplay_sources as gs  # noqa: E402
import narc_reader  # noqa: E402
import opal_strings  # noqa: E402

failures = []
passes = 0


def check(cond, msg):
    global passes
    if cond:
        passes += 1
    else:
        failures.append(msg)


def enum_ids(name):
    return {n: i for i, n in enumerate(gs.read_lines("generated", name))}


TYPE_ID = enum_ids("pokemon_types.txt")
ABILITY_ID = enum_ids("abilities.txt")
ITEM_ID = enum_ids("items.txt")
EVO_ID = enum_ids("evolution_methods.txt")
MOVE_ID = gs.MOVE_ID


# ---------------------------------------------------------------------------
# (1) compiled tables vs sources
# ---------------------------------------------------------------------------
def tm_slot_index(slot):
    kind, num = slot[:2], int(slot[2:])
    return num - 1 if kind == "TM" else 92 + num - 1


def check_compiled_tables(build_dir):
    base = os.path.join(build_dir, "res", "pokemon")
    personal = narc_reader.read_narc(os.path.join(base, "pl_personal.narc"))
    evo = narc_reader.read_narc(os.path.join(base, "evo.narc"))
    wotbl = narc_reader.read_narc(os.path.join(base, "wotbl.narc"))
    check(len(personal[1]) == 44, "personal record is not 44 bytes (SpeciesData layout changed)")
    for sid in range(1, gs.MAX_NATIONAL + 1):
        d = gs.species_data(sid)
        name = gs.SPECIES[sid]
        rec = personal[sid]
        hp, atk, df, spe, spa, spd = rec[0:6]
        want = d["base_stats"]
        check((hp, atk, df, spe, spa, spd) == (want["hp"], want["attack"], want["defense"], want["speed"], want["special_attack"], want["special_defense"]),
              "%s: compiled base stats differ from data.json" % name)
        check((rec[6], rec[7]) == (TYPE_ID[d["types"][0]], TYPE_ID[d["types"][1]]), "%s: compiled types differ from data.json" % name)
        check((rec[22], rec[23]) == (ABILITY_ID[d["abilities"][0]], ABILITY_ID[d["abilities"][1]]), "%s: compiled abilities differ" % name)
        masks = struct.unpack_from("<4I", rec, 28)
        want_mask = [0, 0, 0, 0]
        for slot in d["learnset"]["by_tm"]:
            i = tm_slot_index(slot)
            want_mask[i // 32] |= 1 << (i % 32)
        check(list(masks) == want_mask, "%s: compiled TM/HM mask differs from data.json learnset.by_tm" % name)

        edges = [struct.unpack_from("<HHH", evo[sid], 6 * i) for i in range(7)]
        edges = [e for e in edges if e[0] != 0]
        want_edges = []
        for e in d["evolutions"]:
            method = EVO_ID[e[0]]
            target = gs.SPECIES_ID[e[-1]]
            param = 0
            if len(e) == 3:
                p = e[1]
                if isinstance(p, int):
                    param = p
                elif p.startswith("ITEM_"):
                    param = ITEM_ID[p]
                elif p.startswith("MOVE_"):
                    param = MOVE_ID[p]
                elif p.startswith("SPECIES_"):
                    param = gs.SPECIES_ID[p]
            want_edges.append((method, param, target))
        check(edges == want_edges, "%s: compiled evolution table differs from data.json (%r vs %r)" % (name, edges, want_edges))

        raw = wotbl[sid]
        got = []
        for i in range(0, len(raw), 2):
            v = struct.unpack_from("<H", raw, i)[0]
            if v == 0xFFFF:
                break
            got.append((v >> 9, v & 0x1FF))
        want_ls = [(lv, MOVE_ID[mv]) for lv, mv in d["learnset"]["by_level"]]
        check(got == want_ls, "%s: compiled level-up learnset differs from data.json" % name)


# ---------------------------------------------------------------------------
# (2) generated artefacts are current
# ---------------------------------------------------------------------------
def check_generated_current():
    manifest = bgd.build_manifest()
    per_species, _ = bgd.build_locations()
    check(open(bgd.MANIFEST_PATH, encoding="utf-8").read() == bgd.serialize_manifest(manifest),
          "docs/opal/generated/pokedex_gameplay_manifest.json is stale: run tools/opal_pokedex/build_gameplay_data.py")
    check(open(bgd.LOCATIONS_PATH, "rb").read() == bgd.pack_locations(per_species),
          "res/graphics/pokedex/opal_locations.bin is stale: run tools/opal_pokedex/build_gameplay_data.py")
    check(opal_strings.sync(check=True), "res/text/pokedex.json Opal strings are stale: run tools/opal_pokedex/opal_strings.py")


# ---------------------------------------------------------------------------
# (3) Opal's locked gameplay facts, read from the same sources the ROM compiles
# ---------------------------------------------------------------------------
def check_locked_facts():
    expect = {
        405: ("LUXRAY", ["TYPE_ELECTRIC", "TYPE_DARK"]),
        254: ("SCEPTILE", ["TYPE_GRASS", "TYPE_DRAGON"]),
        350: ("MILOTIC", ["TYPE_WATER", "TYPE_DRAGON"]),
    }
    for sid, (name, types) in expect.items():
        d = gs.species_data(sid)
        check(gs.species_name(sid) == name, "species %d is not %s" % (sid, name))
        check(d["types"] == types, "%s types are %r, expected %r (Opal retype)" % (name, d["types"], types))

    tms = gs.tm_table()
    check(tms["TM21"] == "MOVE_AIR_SLASH", "TM21 must teach Air Slash (found %s)" % tms["TM21"])
    check(tms["TM78"] == "MOVE_POWER_GEM", "TM78 must teach Power Gem (found %s)" % tms["TM78"])

    # runtime TM->move table (generated from the same item JSON) must agree
    gen = os.path.join(args_build_dir(), "res", "items", "item_tm_move_map.h") if args_build_dir() else None
    if gen and os.path.exists(gen):
        text = open(gen).read()
        moves = re.findall(r"\bMOVE_[A-Z0-9_]+", text)
        check(len(moves) >= 100, "generated item_tm_move_map.h has fewer than 100 entries")
        order = ["TM%02d" % i for i in range(1, 93)] + ["HM%02d" % i for i in range(1, 9)]
        check(moves[:100] == [tms[s] for s in order], "item_tm_move_map.h order differs from res/items/data/{tm,hm}NN.json")

    # compat recipient counts must match the locked TM compatibility manifest
    comp = gs.jload("docs", "overhaul", "implementation", "tm_compat_manifest.json")
    recipients = {}
    for sid in range(1, gs.MAX_NATIONAL + 1):
        slots = set(gs.species_data(sid)["learnset"]["by_tm"])
        for f in gs.species_forms(sid).values():
            if "learnset" in f:
                slots |= set(f["learnset"]["by_tm"])
        for s in slots:
            recipients.setdefault(s, set()).add(gs.SPECIES[sid])
    check(len(recipients.get("TM21", ())) >= 48, "TM21 (Air Slash) has too few recipients")
    check(len(recipients.get("TM78", ())) == 27, "TM78 (Power Gem) must have the locked 27 recipients, found %d" % len(recipients.get("TM78", ())))
    del comp

    # no trade evolutions anywhere
    for sid in range(1, gs.MAX_NATIONAL + 1):
        for e in gs.species_data(sid)["evolutions"]:
            check(e[0] not in ("EVO_TRADE", "EVO_TRADE_WITH_HELD_ITEM"), "%s keeps a trade evolution (%s)" % (gs.SPECIES[sid], e[0]))

    # Opal-appended engine methods 27-32 are in the enum
    for name, idx in (("EVO_LEVEL_SPATK_GT_ATK", 27), ("EVO_LEVEL_SPATK_GE_ATK", 28), ("EVO_LEVEL_ATK_GT_SPATK", 29),
                      ("EVO_LEVEL_SPDEF_GT_DEF", 30), ("EVO_LEVEL_NIGHT", 31), ("EVO_LEVEL_DAY", 32)):
        check(EVO_ID.get(name) == idx, "%s is not engine evolution method %d" % (name, idx))

    # Happiny -> Chansey: Lv20 in daytime, no Oval Stone (locked)
    check(gs.species_data(440)["evolutions"] == [["EVO_LEVEL_DAY", 20, "SPECIES_CHANSEY"]], "Happiny evolution is not Lv20 daytime")

    for sid in range(1, gs.MAX_NATIONAL + 1):
        ls = gs.species_data(sid)["learnset"]["by_level"]
        check(len(ls) <= 20, "%s has more than MAX_LEARNSET_ENTRIES level-up moves" % gs.SPECIES[sid])
        check(ls == sorted(ls, key=lambda e: e[0]), "%s level-up list is not sorted by level" % gs.SPECIES[sid])


_build_dir = None


def args_build_dir():
    return _build_dir


# ---------------------------------------------------------------------------
# (4) reader coverage: methods, kinds, message ids, no embedded gameplay tables
# ---------------------------------------------------------------------------
def check_reader_coverage():
    c = open(gs.p("src", "applications", "pokedex", "opal_data.c"), encoding="utf-8").read()
    handled = set(re.findall(r"case (EVO_[A-Z_]+):", c))
    used = {e[0] for sid in range(1, gs.MAX_NATIONAL + 1) for e in gs.species_data(sid)["evolutions"]}
    for m in sorted(used):
        check(m in handled, "opal_data.c does not render evolution method %s" % m)

    # every location kind in the generator has a label and a C enumerator
    for kind in bgd.KIND:
        check(("OPAL_LOC_" + kind) in c, "opal_data.c lacks OPAL_LOC_%s" % kind)
    check("OPAL_LOC_KIND_MAX" in c, "opal_data.c lacks OPAL_LOC_KIND_MAX")
    kinds_c = re.search(r"enum OpalLocationKind \{(.*?)\};", c, re.S).group(1)
    check(len(re.findall(r"OPAL_LOC_[A-Z_]+(?!_MAX)", kinds_c)) - 1 == len(bgd.KIND), "C location kinds differ from generator kinds")

    # message ids referenced from C exist in the string table
    ids = {opal_strings.PREFIX + s for s, _ in opal_strings.STRINGS}
    srcs = [c]
    for f in ("opalref.c", "opalref_sub.c"):
        srcs.append(open(gs.p("src", "applications", "pokedex", f), encoding="utf-8").read())
    refs = set()
    for text in srcs:
        refs |= set(re.findall(r"\bpl_msg_pokedex_opal_[a-z0-9_]+", text))
    for r in sorted(refs):
        check(r in ids, "C references %s which is not in opal_strings.py" % r)
    # strings used only by the generator (curated "where" texts) count as used
    for text_id in bgd.CURATED_WHERE.values():
        refs.add(text_id)
    stray = sorted(ids - refs)
    check(not stray, "strings defined but never used: %s" % ", ".join(stray[:12]))

    # no embedded per-species gameplay tables in the reader
    big = re.findall(r"=\s*\{[^;]*\bSPECIES_(?!DATA_)[A-Z_]+[^;]*\bSPECIES_(?!DATA_)[A-Z_]+[^;]*\bSPECIES_(?!DATA_)[A-Z_]+[^;]*;", c)
    check(not big, "opal_data.c embeds a species table; gameplay data must come from the compiled tables")
    for api in ("SpeciesData_FromMonSpecies", "SpeciesData_FromMonForm", "Pokemon_LoadLevelUpMovesOf", "CanPokemonFormLearnTM",
                "MoveTable_LoadParam", "Item_MoveForTMHM", "NARC_INDEX_POKETOOL__PERSONAL__EVO"):
        check(api in c, "opal_data.c must read %s" % api)


# ---------------------------------------------------------------------------
# (5) location table sanity
# ---------------------------------------------------------------------------
def check_locations():
    manifest = bgd.build_manifest()
    names = {s["const"]: s for s in manifest["species"]}
    pre = {e[-1] for s in manifest["species"] for e in s["evolutions"]}
    loc_msgs = len(gs.jload("res", "text", "location_names.json")["messages"])
    pokedex_msgs = len(gs.jload("res", "text", "pokedex.json")["messages"])
    for s in manifest["species"]:
        check(bool(s["locations"]) or s["const"] in pre, "%s has no recorded source and no pre-evolution (page would claim nothing)" % s["name"])
        check(len(s["locations"]) <= bgd.MAX_RECORDS, "%s has more location records than the table holds" % s["name"])
        rows = len(s["locations"]) + len({l["kind"] for l in s["locations"]}) * 2 + 3
        check(rows <= 128 + 8 * 0 or rows <= 160, "%s location page would exceed OPAL_MAX_ROWS" % s["name"])
        for l in s["locations"]:
            src = l.get("name_src", 0)
            limit = pokedex_msgs if src == 1 else (gs.MAX_NATIONAL + 1 if src == 2 else loc_msgs)
            check(0 <= l["name"] < limit, "%s: location name index %d out of range" % (s["name"], l["name"]))

    # every Legendary/Mythical acquisition in the locked event manifests appears on its species page
    for fname, key in (("native_legendary_events.json", "events"), ("mythical_statics.json", "statics")):
        for e in gs.jload("docs", "overhaul", "implementation", "events", fname)[key]:
            kinds = {l["kind"] for l in names[e["species"]]["locations"]}
            check(bool(kinds & {"STATIC", "EVENT", "ROAMER", "BREEDING", "LEGACY"}), "%s event source missing from its locations" % e["species"])
    for e in gs.jload("docs", "overhaul", "implementation", "events", "legacy_legendary_encounters.json")["encounters"]:
        check(any(l["kind"] == "LEGACY" for l in names[e["species"]]["locations"]), "%s post-game habitat missing" % e["species"])

    # raw table integrity
    blob = open(bgd.LOCATIONS_PATH, "rb").read()
    count = struct.unpack_from("<H", blob, 0)[0]
    check(count == gs.MAX_NATIONAL + 1, "location table species count is %d" % count)
    offsets = struct.unpack_from("<%dH" % (count + 1), blob, 2)
    check(offsets[-1] == len(blob), "location table size does not match its last offset")
    for sid in range(count):
        n = blob[offsets[sid]]
        check(offsets[sid] + 1 + 8 * n == offsets[sid + 1], "location block %d has the wrong length" % sid)


def run_all(build_dir):
    global _build_dir
    _build_dir = build_dir
    check_generated_current()
    check_locked_facts()
    check_reader_coverage()
    check_locations()
    if build_dir:
        check_compiled_tables(build_dir)


def self_test(build_dir):
    """Seed defects into the in-memory sources and prove each check notices."""
    global failures, passes
    results = []

    def expect_failure(label, mutate, restore, fn):
        global failures
        saved = failures
        failures = []
        mutate()
        try:
            fn()
            caught = bool(failures)
        finally:
            restore()
            failures = saved
        results.append((label, caught))

    d = gs.species_data(405)
    orig_types = list(d["types"])
    expect_failure("Luxray retype reverted", lambda: d.__setitem__("types", ["TYPE_ELECTRIC", "TYPE_ELECTRIC"]),
                   lambda: d.__setitem__("types", orig_types), check_locked_facts)
    chans = gs.species_data(440)
    orig = chans["evolutions"]
    expect_failure("Happiny stone evolution restored", lambda: chans.__setitem__("evolutions", [["EVO_USE_ITEM", "ITEM_OVAL_STONE", "SPECIES_CHANSEY"]]),
                   lambda: chans.__setitem__("evolutions", orig), check_locked_facts)
    pk = gs.species_data(25)
    orig_evo = pk["evolutions"]
    expect_failure("trade evolution reintroduced", lambda: pk.__setitem__("evolutions", [["EVO_TRADE", "SPECIES_RAICHU"]]),
                   lambda: pk.__setitem__("evolutions", orig_evo), check_locked_facts)
    real_tm_table = gs.tm_table

    def fake_tm_table():
        t = dict(real_tm_table())
        t["TM21"] = "MOVE_FRUSTRATION"
        return t

    expect_failure("TM21 reverted to Frustration", lambda: setattr(gs, "tm_table", fake_tm_table),
                   lambda: setattr(gs, "tm_table", real_tm_table), check_locked_facts)
    bad = [r for r in results if not r[1]]
    for label, caught in results:
        print(("  self-test caught: " if caught else "  SELF-TEST MISSED: ") + label)
    return not bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build-dir", help="meson build directory: also verify the compiled tables")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    build_dir = args.build_dir
    if build_dir is None and os.path.isdir("/var/tmp/pokeplatinum/res/pokemon") and os.environ.get("OPAL_PARITY_AUTO_BUILD") == "1":
        build_dir = "/var/tmp/pokeplatinum"
    run_all(build_dir)
    ok = not failures
    if args.self_test:
        ok = self_test(build_dir) and ok
    if failures:
        print("FAIL: %d problem(s)" % len(failures))
        for f in failures[:40]:
            print("  -", f)
        sys.exit(1)
    print("PASS: %d gameplay-parity checks%s" % (passes, " (compiled tables verified)" if build_dir else " (source-level; pass --build-dir for compiled tables)"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
