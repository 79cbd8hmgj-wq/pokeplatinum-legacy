#!/usr/bin/env python3
"""C3 learnset timing cross-check for every changed evolution level (read-only; never edits learnsets)."""
import json
import os
import sys

from evo_lib import LOCKED_FINAL, ROOT, data_path, load_base_tables

C3_CITED = {  # evolved species dir -> (evolution level locked by C3 sync notes)
    "alakazam": 36, "machamp": 36, "golem": 36, "gengar": 36, "steelix": 35, "scizor": 38, "electivire": 42,
    "kingdra": 42, "porygon2": 30, "porygon_z": 45, "poliwrath": 35,
}


def moves(d):
    with open(os.path.join(ROOT, data_path(d)), encoding="utf-8") as f:
        return json.load(f)["learnset"]["by_level"]


def rows():
    out = []
    for sp, edges in sorted(LOCKED_FINAL.items()):
        for e in edges:
            if e[0] in ("EVO_USE_ITEM",):
                continue
            lvl, tgt = e[1], e[-1][len("SPECIES_"):].lower()
            pre = [(l, m) for l, m in moves(sp) if l > 1]
            post = [(l, m) for l, m in moves(tgt) if l > 1]
            lost = [(l, m) for l, m in pre if l > lvl]        # pre-evo moves the evolved line abandons
            evo_first = min((l for l, _ in post), default=None)
            skipped = [(l, m) for l, m in post if l <= lvl]    # evolved-form moves at/below the evolution level
            out.append({"from": sp, "to": tgt, "level": lvl, "pre_moves_after_evo_level": lost, "evolved_first_move_level": evo_first,
                        "evolved_moves_at_or_below_evo_level": skipped})
    return out


def main() -> int:
    conflicts = []
    for r in rows():
        print(f"{r['from']:>10} -> {r['to']:<11} Lv{r['level']:>2}  pre-evo moves > Lv: {[l for l,_ in r['pre_moves_after_evo_level']]}  "
              f"evolved lv<=Lv: {[l for l,_ in r['evolved_moves_at_or_below_evo_level']]}  first evolved move Lv{r['evolved_first_move_level']}")
        # Conflict rule: C3-cited evolved forms must not start their learnset before the cited evolution level's neighbourhood
        # such that the synchronized move would sit at or below the evolution level (skipped on evolution).
        cited = C3_CITED.get(r["to"])
        if cited is not None and cited != r["level"]:
            conflicts.append(f"{r['to']}: manifest level {r['level']} != C3-cited {cited}")
    print(f"C3-cited levels checked: {len(C3_CITED)}; conflicts: {len(conflicts)}")
    for c in conflicts:
        print("CONFLICT:", c)
    return 1 if conflicts else 0


if __name__ == "__main__":
    sys.exit(main())
