"""Encounter state: live files, or base commit + manifests applied in memory."""
from __future__ import annotations

import copy
import json

from base_source import all_base_maps, base_encounter
from common import ENC_DIR, IMPL_DIR, encounter_files, map_name

WATER_METHODS = ("surf", "old_rod", "good_rod", "super_rod")
VERSIONS = ("ruby", "sapphire", "emerald", "firered", "leafgreen")


def load_manifest(name: str) -> dict:
    return json.load(open(IMPL_DIR / name))


def live_state() -> dict[str, dict]:
    return {map_name(p): json.load(open(p)) for p in encounter_files()}


def base_state() -> dict[str, dict]:
    return {n: copy.deepcopy(base_encounter(n)) for n in all_base_maps()}


class GuardError(Exception):
    pass


def _set_array(arr, idx, species, before, what, check):
    cur = arr[idx]
    if check and cur not in (before, species):
        raise GuardError(f"{what}: expected {before} (or already {species}), found {cur}")
    arr[idx] = species


METHOD_GROUPS = {"land": ("land", "land_day", "land_night"), "water": WATER_METHODS}


def apply_wild(state: dict[str, dict], wild: dict, check: bool = True, only_maps=None, only_groups=None) -> int:
    """only_groups: subset of METHOD_GROUPS keys (None = all methods)."""
    n = 0
    allowed = None if only_groups is None else {m for g in only_groups for m in METHOD_GROUPS[g]}
    for e in wild["entries"]:
        if only_maps is not None and e["map"] not in only_maps:
            continue
        if allowed is not None and e["method"] not in allowed:
            continue
        j = state[e["map"]]
        m, s = e["method"], e["slot"]
        what = f'{e["map"]}:{m}[{s}]'
        b = e["before"]
        if m == "land":
            t = j["land_encounters"][s]
            if check and not ((t["species"], t["level"]) in ((b["species"], b["level_min"]), (e["species"], e["level_min"]))):
                raise GuardError(f"{what}: expected {b}, found {t}")
            t["species"], t["level"] = e["species"], e["level_min"]
        elif m in ("land_day", "land_night"):
            key = "day" if m == "land_day" else "night"
            _set_array(j[key], s - 2, e["species"], b["species"], what, check)
        elif m in WATER_METHODS:
            t = j[f"{m}_encounters"][s]
            ok = (t["species"], t["level_min"], t["level_max"]) in (
                (b["species"], b["level_min"], b["level_max"]), (e["species"], e["level_min"], e["level_max"]))
            if check and not ok:
                raise GuardError(f"{what}: expected {b}, found {t}")
            t["species"], t["level_min"], t["level_max"] = e["species"], e["level_min"], e["level_max"]
        else:
            raise GuardError(f"{what}: unknown method")
        n += 1
    return n


def _apply_list(arr, before, after, what, check):
    if len(arr) != len(before) or len(after) != len(arr):
        raise GuardError(f"{what}: length mismatch")
    if check and arr not in (before, after):
        raise GuardError(f"{what}: expected {before} (or already {after}), found {arr}")
    arr[:] = list(after)


def apply_special(state: dict[str, dict], special: dict, check: bool = True, only_maps=None) -> int:
    """Apply special_systems.json; only_maps (a set of map names) restricts which encounter files are touched."""
    n = 0
    sel = (lambda m: True) if only_maps is None else (lambda m: m in only_maps)
    for name, rec in special["dual_slot"]["maps"].items():
        if not sel(name):
            continue
        j = state[name]
        for v in VERSIONS:
            _apply_list(j[v], rec["before"][v], rec["after"], f"{name}:{v}", check)
            n += 1
    for system in ("radar", "swarm"):
        for name, rec in special[system]["maps"].items():
            if not sel(name):
                continue
            _apply_list(state[name][system if system == "radar" else "swarms"], rec["before"], rec["after"],
                        f"{name}:{system}", check)
            n += 1
    if sel("honey_tree"):
        h = state["honey_tree"]
        for tier, rec in special["honey"]["tiers"].items():
            _apply_list(h[tier], rec["before"], rec["after"], f"honey_tree:{tier}", check)
            n += 1
    if sel("trophy_garden"):
        _apply_list(state["trophy_garden"]["daily_encounters"], special["trophy_garden"]["daily"]["before"],
                    special["trophy_garden"]["daily"]["after"], "trophy_garden:daily", check)
        n += 1
    if sel("great_marsh_lookout"):
        for k, rec in special["great_marsh"]["arrays"].items():
            _apply_list(state["great_marsh_lookout"][k], rec["before"], rec["after"], f"great_marsh_lookout:{k}", check)
            n += 1
    return n


def manifest_state(check: bool = True) -> dict[str, dict]:
    st = base_state()
    apply_wild(st, load_manifest("wild_encounters.json"), check)
    apply_special(st, load_manifest("special_systems.json"), check)
    return st
