"""Shared helpers for the D7 QA validators (no gameplay logic)."""
from __future__ import annotations

import glob
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def jl(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return json.load(f)


def lines(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip()]


def text(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def species_data():
    out = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "res/pokemon/*/data.json"))):
        out[os.path.basename(os.path.dirname(p))] = jl(os.path.relpath(p, ROOT))
    return out


class Checker:
    def __init__(self, name):
        self.name, self.passed, self.failed = name, 0, []

    def check(self, cond, msg):
        if cond:
            self.passed += 1
        else:
            self.failed.append(msg)
        return cond

    def finish(self):
        for m in self.failed[:40]:
            print("FAIL", m)
        if len(self.failed) > 40:
            print(f"... {len(self.failed) - 40} more")
        print(f"{self.name}: {self.passed} pass, {len(self.failed)} fail")
        return 1 if self.failed else 0
