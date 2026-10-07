#!/usr/bin/env python3
"""Trainer class target alignment: donor trainer class/backpic -> canonical Platinum target.

Targets are Platinum trainer class folders (res/trainers/classes/<dir>): `tc_<dir>` (front) and `tcb_<dir>` (back).
Donor classes without a confident Platinum counterpart get `tc_<source>_<name>` (never forced).
Methods are recorded per entry. Read-only on donor checkouts (constants headers + file lists only).
"""
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

from common import *  # noqa: F401,F403

PT_CLASSES = ROOT / "res" / "trainers" / "classes"

# Name differences between donors and Platinum folder names (confident equivalences only).
SUFFIX = [("_m", "_male"), ("_f", "_female")]
COMMON_ALIAS = {
    "pkmn_breeder": None,  # handled by prefix rule
    "belle__pa": "belle_and_pa", "interviewers": "interviewers",
    "galactic": "galactic_grunt_male", "galactic_f": "galactic_grunt_female",
    "pkmn_trainer_m": "player_male", "pkmn_trainer_f": "player_female",
    "pkmn_trainer_barry": "rival",
    "pkmn_trainer_lucas": "dp_player_male", "pkmn_trainer_dawn": "dp_player_female",
    "pkmn_trainer_cheryl": "trainer_cheryl", "pkmn_trainer_riley": "trainer_riley",
    "pkmn_trainer_buck": "trainer_buck", "pkmn_trainer_mira": "trainer_mira", "pkmn_trainer_marley": "trainer_marley",
    "elite_four_lucien": "elite_four_lucian", "champion": "champion_cynthia",
    "pokefan": "pokefan_female", "pokefan_f": "pokefan_female",
}
HGSS_ONLY_ALIAS = {
    "pkmn_trainer_lucas_dp": "dp_player_male", "pkmn_trainer_dawn_dp": "dp_player_female",
    "pkmn_trainer_lucas_pt": "player_male", "pkmn_trainer_dawn_pt": "player_female",
    "champion": None, "rival": None,  # HGSS champion/rival are different characters than Platinum's
    "pokefan": "pokefan_female",
}
HGSS_BACK_ALIAS = {
    "lucas_dp": "dp_player_male", "dawn_dp": "dp_player_female", "barry_dp": "dp_rival",
    "lucas_pt": "player_male", "dawn_pt": "player_female", "barry_pt": "rival",
    "cheryl": "trainer_cheryl", "riley": "trainer_riley", "buck": "trainer_buck", "mira": "trainer_mira", "marley": "trainer_marley",
}


def norm(name: str, table: dict, dirs: set[str]) -> tuple[str | None, str]:
    n = name.lower()
    if n in table:
        return table[n], "alias"
    if n in dirs:
        return n, "exact_name"
    for a, b in SUFFIX:
        if n.endswith(a):
            for cand in (n[: -len(a)] + b, re.sub(r"^pkmn_", "", n[: -len(a)]) + b):
                if cand in dirs:
                    return cand, "suffix_name"
    if n.startswith("pkmn_"):
        m = re.sub(r"^pkmn_", "", n)
        if m in dirs:
            return m, "prefix_name"
    return None, "none"


def git_head(repo: Path) -> str:
    return subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hgss-root", required=True, type=Path)
    ap.add_argument("--diamond-root", required=True, type=Path)
    a = ap.parse_args()
    dirs = {p.name for p in PT_CLASSES.iterdir() if p.is_dir() and (p / "front.png").is_file()}
    back_dirs = {p.name for p in PT_CLASSES.iterdir() if p.is_dir() and (p / "back.png").is_file()}
    pt_consts = [l.strip().removeprefix("TRAINER_CLASS_").lower() for l in (ROOT / "generated/trainer_classes.txt").read_text().splitlines() if l.strip()]

    hg_txt = (a.hgss_root / "include/constants/trainer_class.h").read_text()
    hg_front = {int(i): n.lower() for n, i in re.findall(r"define TRAINERCLASS_(\w+)\s+(\d+)", hg_txt)}
    hg_back = {int(i): n.lower() for n, i in re.findall(r"define TRAINER_BACKPIC_(\w+)\s+(\d+)", hg_txt)}
    dp_txt = (a.diamond_root / "include/constants/trainer_classes.h").read_text()
    dp_front = {int(i): n.lower() for n, i in re.findall(r"define TRAINER_CLASS_(\w+)\s+(\d+)", dp_txt)}

    out = {"schema_version": 1,
           "inputs": {"hgss_commit": git_head(a.hgss_root), "diamond_commit": git_head(a.diamond_root),
                      "platinum_front_classes": len(dirs), "platinum_back_classes": len(back_dirs)},
           "hgss_front": {}, "hgss_back": {}, "diamond_front": {}, "diamond_back": {}}
    for i, n in sorted(hg_front.items()):
        t, m = norm(n, {**COMMON_ALIAS, **HGSS_ONLY_ALIAS}, dirs)
        out["hgss_front"][f"{i:03d}"] = {"name": n, "target": f"tc_{t}" if t else f"tc_hgss_{n}", "platinum_class": t, "method": m}
    for i, n in sorted(hg_back.items()):
        t = HGSS_BACK_ALIAS.get(n)
        ok = t in back_dirs if t else False
        out["hgss_back"][f"{i:03d}"] = {"name": n, "target": f"tcb_{t}" if ok else f"tcb_hgss_{n}", "platinum_class": t if ok else None,
                                        "method": "backpic_constant_alias" if ok else "none"}
    for i, n in sorted(dp_front.items()):
        t, m = norm(n, COMMON_ALIAS, dirs)
        idx_name = pt_consts[i] if i < len(pt_consts) else None
        if t is None and idx_name == n:
            t, m = n, "exact_name"
        out["diamond_front"][f"{i:03d}"] = {"name": n, "target": f"tc_{t}" if t else f"tc_dp_{n}", "platinum_class": t, "method": m,
                                           "platinum_index_agrees": idx_name == t}
    # Diamond back sprites: narc_0000..0014 even -> backpic i//2; names from content are resolved by evidence, not here.
    from PIL import Image
    pt_back = {}
    for d in sorted(back_dirs):
        im = Image.open(PT_CLASSES / d / "back.png")
        pt_back.setdefault(im.tobytes(), []).append(d)
    for p in sorted((a.diamond_root / "files/poketool/trgra/trbgra").glob("narc_*.png")):
        n = int(re.search(r"(\d+)", p.stem).group(1)) // 2
        hit = pt_back.get(Image.open(p).tobytes())
        t = hit[0] if hit and len(hit) == 1 else None
        out["diamond_back"][f"{n:03d}"] = {"name": f"dp_trbgra_{n:03d}", "target": f"tcb_{t}" if t else f"tcb_dp_{n:03d}",
                                           "platinum_class": t, "method": "index_content_match" if t else "none"}
    jdump(SEL / "alignment" / "trainer_classes.json", out)
    for k in ("hgss_front", "hgss_back", "diamond_front", "diamond_back"):
        v = out[k]
        print(k, len(v), "aligned", sum(1 for e in v.values() if e["platinum_class"]),
              {m: sum(1 for e in v.values() if e["method"] == m) for m in sorted({e["method"] for e in v.values()})})
    bad = [k for k, e in out["diamond_front"].items() if e["platinum_class"] and not e["platinum_index_agrees"]]
    print("diamond name-vs-platinum-index disagreements:", bad)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
