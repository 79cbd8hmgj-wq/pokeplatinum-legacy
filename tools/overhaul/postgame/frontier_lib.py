"""Shared loaders for the D6 Frontier set audit and the postgame validator.

Baseline for "vanilla" species/move data is VANILLA_SHA (the last commit before the overhaul's
first source change).  Everything else is read from the working tree.
"""
import glob
import json
import os
import re
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
START_SHA = "98f9cbdf43f9a8ef4c04c3f80e7ee0b6d9482638"
VANILLA_SHA = "1c1fb925"
SETS_DIR = "res/trainers/frontier/pokemon"
TRAINERS_DIR = "res/trainers/frontier/data"
IMPL_DIR = os.path.join(ROOT, "docs/overhaul/implementation/postgame")


def p(*parts):
    return os.path.join(ROOT, *parts)


def read(path):
    with open(p(path)) as f:
        return f.read()


def load_json(path):
    with open(p(path)) as f:
        return json.load(f)


def git_show(sha, path):
    return subprocess.check_output(["git", "show", f"{sha}:{path}"], cwd=ROOT, stderr=subprocess.DEVNULL).decode()


def slug(const, prefix):
    return const[len(prefix):].lower()


def load_constants(path):
    return [l.strip() for l in read(path).splitlines() if l.strip()]


def species_data(const, sha=None):
    path = f"res/pokemon/{slug(const, 'SPECIES_')}/data.json"
    if sha:
        try:
            return json.loads(git_show(sha, path))
        except subprocess.CalledProcessError:
            return None
    if not os.path.exists(p(path)):
        return None
    return load_json(path)


def move_data(const, sha=None):
    path = f"res/moves/{slug(const, 'MOVE_')}/data.json"
    if sha:
        try:
            return json.loads(git_show(sha, path))
        except subprocess.CalledProcessError:
            return None
    if not os.path.exists(p(path)):
        return None
    return load_json(path)


def tm_moves():
    out = {}
    for f in glob.glob(p("res/items/data/[th]m[0-9][0-9].json")):
        d = json.load(open(f))
        out[os.path.basename(f)[:-5].upper()] = d["teachesMove"]
    return out


def learnable(sp, tm_map):
    """Moves the species can learn by level/TM/HM/tutor in a species record."""
    ls = sp["learnset"]
    moves = {m for _, m in ls.get("by_level", [])}
    moves |= {tm_map[t] for t in ls.get("by_tm", []) if t in tm_map}
    moves |= set(ls.get("by_tutor", []))
    return moves


def load_sets():
    sets = {}
    for f in sorted(glob.glob(p(SETS_DIR, "*.json"))):
        name = os.path.basename(f)[:-5]
        sets[name] = json.load(open(f))
    return sets


def damaging(md):
    return md is not None and md.get("class") != "CLASS_STATUS" and md.get("power", 0) > 0


def eff_type(const, md, species_types):
    return md.get("type")
