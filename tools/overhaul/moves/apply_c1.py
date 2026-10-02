#!/usr/bin/env python3
"""Guarded application of the locked C1 82-edit manifest.

  apply_c1.py --write-guards   (re)generate c1_move_guards.json from the pinned base commit
  apply_c1.py --apply          apply edits plus Razor Wind script/animation resources
Per edit: MATCHES_BEFORE -> apply; ALREADY_AFTER -> record; anything else -> fail closed.
Razor Wind's description/script/animation are guarded independently so partial application is repaired safely.
Only textual in-place edits are made, so unrelated formatting is untouched.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

from c1_lib import *

KEEP_RE = re.compile(r"^KEEP: (.*)\.$", re.M)


def keep_names() -> list[str]:
    txt = open(os.path.join(ROOT, "docs/overhaul/moves/C1_EXISTING_MOVE_REBALANCE_RECOVERY.md")).read()
    names = []
    for m in KEEP_RE.finditer(txt):
        names += [n.strip() for n in m.group(1).split(",")]
    names.append("Magma Storm")
    return names


def write_guards() -> None:
    man = load_json(MANIFEST)
    assert man["expected_edit_count"] == len(man["edits"]) == 82, "manifest count != 82"
    base = base_moves()
    edits = []
    for e in man["edits"]:
        rel, d = unique(base, e["move"])
        before = read_fields(d)
        keys = {"effect_type": "effect_type"}
        tgt = e["target"]
        assert all(k in FIELDS or k == "effect_type" for k in tgt), e
        edits.append({"move": e["move"], "path": rel, "batch": e["batch"],
                      "before": {k: before[k] for k in tgt}, "after": dict(tgt),
                      "kind": "effect_reassignment+script" if "effect_type" in tgt else "data_only"})
        assert edits[-1]["before"] != edits[-1]["after"], f"no-op edit {e['move']}"
    lower = {n.lower(): n for n in base}
    names = keep_names()
    edited = {e["move"] for e in edits}
    keep, unresolved = {}, []
    lower = {n.lower().replace("’", "'"): n for n in base}
    for n in names:
        key = lower.get(n.lower())
        if key is None or n in edited:
            unresolved.append(n)
            continue
        keep[key] = read_fields(unique(base, key)[1])
    out = {"base_commit": BASE_COMMIT, "edit_count": len(edits), "edits": edits,
           "keep_invariants": keep, "keep_unresolved_names": unresolved,
           "later_pass_overrides": [],
           "created_moves": {"first_id": 468, "last_id": 489, "max_moves": 490}}
    with open(os.path.join(ROOT, GUARDS), "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    print(f"guards written: {len(edits)} edits, {len(keep)} KEEP invariants, unresolved KEEP names: {unresolved}")


def sub_field(text: str, key: str, old, new) -> str:
    pat = re.compile(rf'^(    "{key}": ){old}(,?)def apply() -> None:
    g = load_json(GUARDS)
    counts = {"newly_applied": 0, "already_implemented": 0, "later_pass_reconciled": 0, "unresolved": 0}
    report = []
    live = live_moves()
    for e in g["edits"]:
        rel, d = unique(live, e["move"])
        assert rel == e["path"], (rel, e["path"])
        cur = read_fields(d)
        cur_t = {k: cur[k] for k in e["after"]}
        if cur_t == e["before"]:
            path = os.path.join(ROOT, rel)
            text = open(path).read()
            for k, new in e["after"].items():
                old = e["before"][k]
                if k == "effect_type":
                    old_s, new_s = f'"{old}"', f'"{new}"'
                    pat = re.compile(rf'^(        "type": ){re.escape(old_s)}(,?)$', re.M)
                    if len(pat.findall(text)) != 1:
                        raise SystemExit(f"FAIL: effect locate {e['move']}")
                    text = pat.sub(rf"\g<1>{new_s}\g<2>", text, count=1)
                else:
                    text = sub_field(text, k, old, new)
            with open(path, "w") as f:
                f.write(text)
            counts["newly_applied"] += 1
            report.append((e["move"], "NEWLY_APPLIED"))
        elif cur_t == e["after"]:
            counts["already_implemented"] += 1
            report.append((e["move"], "ALREADY_AFTER"))
        else:
            counts["unresolved"] += 1
            report.append((e["move"], f"UNRESOLVED live={cur_t} before={e['before']} after={e['after']}"))
    razor = reconcile_razor_wind_extras()
    for part, state in razor.items():
        print("Razor Wind", part, state)
    for r in report:
        print(*r)
    print(counts, "total", sum(counts.values()))
    if counts["unresolved"] or sum(counts.values()) != 82:
        sys.exit(1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-guards", action="store_true")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    if a.write_guards:
        write_guards()
    if a.apply:
        apply()
, re.M)
    if len(pat.findall(text)) != 1:
        raise SystemExit(f"FAIL: could not uniquely locate {key}={old}")
    return pat.sub(rf"\g<1>{new}\g<2>", text, count=1)


def _razor_resource_after(rel: str) -> tuple[str, str]:
    """Return exact pinned-base and canonical C1 text for a Razor Wind resource."""
    before = git("show", f"{BASE_COMMIT}:{rel}")
    if rel.endswith("script.s"):
        needle = (
            "    // {0} whipped up a whirlwind!\n"
            "    BufferMessage BattleStrings_Text_PokemonWhippedUpAWhirlwind_Ally, TAG_NICKNAME, BTLSCR_ATTACKER\n"
        )
        if before.count(needle) != 1:
            raise SystemExit("FAIL: Razor Wind script base anchor missing")
        return before, before.replace(needle, "", 1)
    if rel.endswith("anim.s"):
        marker = "\nL_2:\n"
        if before.count(marker) != 1:
            raise SystemExit("FAIL: Razor Wind animation strike branch missing")
        header = before.split("\nL_0:\n", 1)[0]
        strike = before.split(marker, 1)[1]
        return before, header + "\nL_0:\n" + strike
    raise SystemExit(f"FAIL: unsupported Razor Wind resource {rel}")


def _apply_guarded_resource(rel: str) -> str:
    before, after = _razor_resource_after(rel)
    path = os.path.join(ROOT, rel)
    current = open(path).read()
    if current == before:
        with open(path, "w") as f:
            f.write(after)
        return "NEWLY_APPLIED"
    if current == after:
        return "ALREADY_AFTER"
    raise SystemExit(f"FAIL: {rel} is neither pinned-base nor canonical C1 state")


def reconcile_razor_wind_extras() -> dict[str, str]:
    """Apply/verify Razor Wind description, battle script and animation independently."""
    status: dict[str, str] = {}
    rel = "res/moves/razor_wind/data.json"
    path = os.path.join(ROOT, rel)
    text = open(path).read()
    live = json.loads(text)
    base = json.loads(git("show", f"{BASE_COMMIT}:{rel}"))
    if live["description"] == base["description"]:
        old_desc = ",\n".join("        " + json.dumps(x) for x in base["description"])
        new_desc = ",\n".join("        " + json.dumps(x) for x in RAZOR_WIND_DESC)
        if old_desc not in text:
            raise SystemExit("FAIL: Razor Wind description base-state anchor missing")
        with open(path, "w") as f:
            f.write(text.replace(old_desc, new_desc, 1))
        status["description"] = "NEWLY_APPLIED"
    elif live["description"] == RAZOR_WIND_DESC:
        status["description"] = "ALREADY_AFTER"
    else:
        raise SystemExit("FAIL: Razor Wind description is neither pinned-base nor canonical C1 state")

    status["script"] = _apply_guarded_resource("res/moves/razor_wind/script.s")
    status["animation"] = _apply_guarded_resource("res/moves/razor_wind/anim.s")
    return status


def apply() -> None:
    g = load_json(GUARDS)
    counts = {"newly_applied": 0, "already_implemented": 0, "later_pass_reconciled": 0, "unresolved": 0}
    report = []
    live = live_moves()
    for e in g["edits"]:
        rel, d = unique(live, e["move"])
        assert rel == e["path"], (rel, e["path"])
        cur = read_fields(d)
        cur_t = {k: cur[k] for k in e["after"]}
        if cur_t == e["before"]:
            path = os.path.join(ROOT, rel)
            text = open(path).read()
            for k, new in e["after"].items():
                old = e["before"][k]
                if k == "effect_type":
                    old_s, new_s = f'"{old}"', f'"{new}"'
                    pat = re.compile(rf'^(        "type": ){re.escape(old_s)}(,?)$', re.M)
                    if len(pat.findall(text)) != 1:
                        raise SystemExit(f"FAIL: effect locate {e['move']}")
                    text = pat.sub(rf"\g<1>{new_s}\g<2>", text, count=1)
                else:
                    text = sub_field(text, k, old, new)
            if e["move"] == "Razor Wind":
                dd = json.loads(text)
                if dd["description"][0].startswith("A two-turn attack."):
                    old_desc = ",\n".join('        ' + json.dumps(x) for x in dd["description"])
                    new_desc = ",\n".join('        ' + json.dumps(x) for x in RAZOR_WIND_DESC)
                    if old_desc not in text:
                        raise SystemExit("FAIL: Razor Wind description locate")
                    text = text.replace(old_desc, new_desc, 1)
            with open(path, "w") as f:
                f.write(text)
            counts["newly_applied"] += 1
            report.append((e["move"], "NEWLY_APPLIED"))
        elif cur_t == e["after"]:
            counts["already_implemented"] += 1
            report.append((e["move"], "ALREADY_AFTER"))
        else:
            counts["unresolved"] += 1
            report.append((e["move"], f"UNRESOLVED live={cur_t} before={e['before']} after={e['after']}"))
    for r in report:
        print(*r)
    print(counts, "total", sum(counts.values()))
    if counts["unresolved"] or sum(counts.values()) != 82:
        sys.exit(1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-guards", action="store_true")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    if a.write_guards:
        write_guards()
    if a.apply:
        apply()
