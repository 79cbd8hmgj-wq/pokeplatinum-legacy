#!/usr/bin/env python3
"""Decode the *compiled* encounter binaries from a meson build dir and compare them with the expected state.

  verify_built_encounters.py --build /var/tmp/pp_r1 [--bands all]

This proves the build output contains exactly the manifest data (it is NOT a runtime test).
"""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

from common import BANDS, SPECIES
from state import apply_special, apply_wild, base_state, load_manifest
from zone_index import zone_index


def sp(n):
    return SPECIES[n]


def decode_map(b: bytes) -> dict:
    o = 0

    def u32():
        nonlocal o
        v = struct.unpack_from("<I", b, o)[0]
        o += 4
        return v
    d = {"land_rate": u32(), "land": [], "swarms": [], "day": [], "night": [], "radar": []}
    for _ in range(12):
        lvl, s = u32(), u32()
        d["land"].append((sp(s), lvl))
    for k, n in (("swarms", 2), ("day", 2), ("night", 2), ("radar", 4)):
        d[k] = [sp(u32()) for _ in range(n)]
    d["forms"] = [u32() for _ in range(6)]
    for v in ("ruby", "sapphire", "emerald", "firered", "leafgreen"):
        d[v] = [sp(u32()), sp(u32())]

    def water():
        nonlocal o
        out = []
        for _ in range(5):
            mx, mn = b[o], b[o + 1]
            o += 4
            out.append((sp(u32()), mn, mx))
        return out
    d["surf_rate"] = u32()
    d["surf"] = water()
    o += 44
    for rod in ("old_rod", "good_rod", "super_rod"):
        d[f"{rod}_rate"] = u32()
        d[rod] = water()
    return d


def expected_view(j: dict) -> dict:
    d = {"land_rate": j["land_rate"], "land": [(e["species"], e["level"]) for e in j["land_encounters"]],
         "swarms": j["swarms"], "day": j["day"], "night": j["night"], "radar": j["radar"],
         "surf_rate": j["surf_rate"],
         "surf": [(e["species"], e["level_min"], e["level_max"]) for e in j["surf_encounters"]]}
    for v in ("ruby", "sapphire", "emerald", "firered", "leafgreen"):
        d[v] = j[v]
    for rod in ("old_rod", "good_rod", "super_rod"):
        d[f"{rod}_rate"] = j[f"{rod}_rate"]
        d[rod] = [(e["species"], e["level_min"], e["level_max"]) for e in j[f"{rod}_encounters"]]
    return d


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", required=True)
    ap.add_argument("--groups", default="land,water,special", help="subset of land,water,special")
    ap.add_argument("--bands", default="all")
    args = ap.parse_args()
    bands = set(BANDS) if args.bands == "all" else set(args.bands.split(","))
    wild, special = load_manifest("wild_encounters.json"), load_manifest("special_systems.json")
    selected = {n for n, z in zone_index(wild).items() if z["band"] in bands}
    exp = base_state()
    groups = set(args.groups.split(","))
    wg = sorted(groups & {"land", "water"})
    if wg:
        apply_wild(exp, wild, check=True, only_maps=selected, only_groups=wg)
    if "special" in groups:
        apply_special(exp, special, check=True, only_maps=selected)
    root = Path(args.build) / "res" / "field" / "encounters"
    bad = checked = 0
    for name, j in exp.items():
        f = root / "pl_enc_data.narc.p" / f"encounters_{name}"
        if not f.exists():
            continue                       # honey tree / marsh lookout live in encdata_ex
        got, want = decode_map(f.read_bytes()), expected_view(j)
        checked += 1
        for k in want:
            if got.get(k) != want[k]:
                bad += 1
                print(f"MISMATCH {name}.{k}: built {got.get(k)} expected {want[k]}")
                break
    ex = root / "encdata_ex.narc.p"
    def species_file(p, n):
        data = (ex / p).read_bytes()
        return [sp(struct.unpack_from("<I", data, 4 * i)[0]) for i in range(n)]
    checks = [("encounters_honey_tree_common.bin", exp["honey_tree"]["common"]),
              ("encounters_honey_tree_uncommon.bin", exp["honey_tree"]["uncommon"]),
              ("encounters_honey_tree_rare.bin", exp["honey_tree"]["rare"]),
              ("encounters_trophy_garden_dailies.bin", exp["trophy_garden"]["daily_encounters"]),
              ("encounters_great_marsh_lookout_natdex.bin", exp["great_marsh_lookout"]["after_national_dex"]),
              ("encounters_great_marsh_lookout_local.bin", exp["great_marsh_lookout"]["before_national_dex"])]
    for fname, want in checks:
        checked += 1
        got = species_file(fname, len(want))
        if got != want:
            bad += 1
            print(f"MISMATCH {fname}: built {got[:6]}... expected {want[:6]}...")
    print(f"checked {checked} compiled encounter tables against the manifest-expected state: {bad} mismatch(es)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
