"""Shared helpers for the C1 existing-move rebalance tooling."""
from __future__ import annotations

import glob
import json
import os
import re
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
BASE_COMMIT = "9034963728913416f2968b56f7dab8ac61b19c07"  # main at C1 implementation start
MANIFEST = "docs/overhaul/implementation/c1_move_changes_manifest.json"
GUARDS = "docs/overhaul/implementation/c1_move_guards.json"
FIELDS = ("power", "accuracy", "pp")
RAZOR_WIND_DESC = ["Blades of wind slash\n", "the foe. It has a\n", "high critical-hit\n", "ratio."]


def git(*args: str) -> str:
    return subprocess.check_output(("git",) + args, cwd=ROOT, text=True)


def load_json(rel: str):
    with open(os.path.join(ROOT, rel)) as f:
        return json.load(f)


def move_dirs():
    return sorted(os.path.relpath(p, ROOT) for p in glob.glob(os.path.join(ROOT, "res/moves/*/data.json")))


def live_moves() -> dict:
    out = {}
    for rel in move_dirs():
        d = load_json(rel)
        out.setdefault(d["name"], []).append((rel, d))
    return out


def base_moves() -> dict:
    out = {}
    for rel in git("ls-tree", "-r", "--name-only", BASE_COMMIT, "res/moves").split():
        if rel.endswith("/data.json"):
            d = json.loads(git("show", f"{BASE_COMMIT}:{rel}"))
            out.setdefault(d["name"], []).append((rel, d))
    return out


def unique(table: dict, name: str):
    hits = table.get(name, [])
    if len(hits) != 1:
        raise SystemExit(f"FAIL: move {name!r} resolved to {len(hits)} records")
    return hits[0]


def read_fields(d: dict) -> dict:
    return {"power": d["power"], "accuracy": d["accuracy"], "pp": d["pp"], "effect_type": d["effect"]["type"]}


def normalize_target(t: dict) -> dict:
    return dict(t)
