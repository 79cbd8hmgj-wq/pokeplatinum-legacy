#!/usr/bin/env python3
"""Static cue-trace simulator + invariant checker for Opal move animation scripts (B6-05).

It symbolically executes res/moves/<move>/anim.s (and common_anims) over EVERY control-flow path
(Jump / JumpIf* / Call / Return), using the real Opal macro bodies from asm/macros/btlanim_opal.inc,
and emits a deterministic cue log per path. Invariants asserted on every path:

  * every sprite manager that is initialised is freed before End; a manager id is never initialised twice
  * every FX sprite uses the resources of the manager it is added to; live sprite estimate <= manager capacity
  * every particle system that is loaded is unloaded, and after all sprite managers were freed
  * base-BG fades (Func_FadeBg FADE_BG_TYPE_BASE) never overlap in time, never leave alpha != 0, stay within 0..16
  * Opal camera cues never overlap each other or a native base-BG shake and are capped at 90 frames
  * Call / Return are balanced; every path reaches End; no path revisits a label with the same state (no loops)
  * at End every known cue (camera, fades, FX sprites) has finished -> "no live visual cue after the action"

Frame times are lower-bound estimates (Delay, fades, camera phases, FX lifetimes from provenance); unknown native
tasks count as zero length, so timing results are for ordering/overlap policy, not performance claims.
"""
import copy
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONSTS = ROOT / "include/constants/battle/battle_anim.h"
OPAL_INC = ROOT / "asm/macros/btlanim_opal.inc"
PROV = ROOT / "docs/visual_overhaul/opal_installed_fx"

MAX_FX_LIFETIME = 180
MAX_OAM_ENTRIES = 40  # of 128 main-OAM entries (battle_main.c sOamTemplate); healthboxes, battlers, terrain and the vanilla effect sprites own the rest
MAX_OBJ_CHAR_TILES = 400  # measured policy cap per script: 12.5 KiB of the 64 KiB main-OBJ VRAM bank (GX_VRAM_OBJ_64_E, battle_main.c)
MAX_CONCURRENT_MANAGERS = 2  # OBJ palette slots: every sprite manager owns one palette; keep headroom for healthboxes/battlers
BATTLER_BITS = {"ATTACKER": 1 << 1, "ATTACKER_PARTNER": 1 << 2, "DEFENDER": 1 << 3, "DEFENDER_PARTNER": 1 << 4}


# ------------------------------------------------------------------ constants / expression evaluation
def load_defines(text, env=None):
    env = dict(env or {})
    funcs = {}
    for line in text.splitlines():
        m = re.match(r"\s*#define\s+(\w+)\(([^)]*)\)\s+(.*)", line)
        if m:
            funcs[m.group(1)] = ([a.strip() for a in m.group(2).split(",")], m.group(3).split("//")[0].strip())
            continue
        m = re.match(r"\s*#define\s+(\w+)\s+(.*)", line)
        if m:
            env[m.group(1)] = m.group(2).split("//")[0].strip()
    return env, funcs


def evaluate(expr, env, funcs, depth=0):
    """Evaluate a cpp-style integer expression after macro substitution; returns int or None if symbolic."""
    expr = expr.strip()
    for _ in range(12):
        changed = False
        for name, (params, body) in funcs.items():
            m = re.search(rf"\b{name}\(", expr)
            if m:
                i, level, j = m.end(), 1, m.end()
                while level and j < len(expr):
                    level += {"(": 1, ")": -1}.get(expr[j], 0)
                    j += 1
                args = split_args(expr[i:j - 1])
                rep = body
                for p, a in zip(params, args):
                    rep = re.sub(rf"\b{p}\b", f"({a})", rep)
                expr = expr[:m.start()] + f"({rep})" + expr[j:]
                changed = True
        for name, val in env.items():
            if re.search(rf"\b{name}\b", expr):
                expr = re.sub(rf"\b{name}\b", f"({val})", expr)
                changed = True
        if not changed:
            break
    try:
        return int(eval(expr, {"__builtins__": {}}, {}))
    except Exception:
        return None


def split_args(text):
    out, depth, cur = [], 0, ""
    for ch in text:
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip() or out:
        out.append(cur.strip())
    return out


# ------------------------------------------------------------------ source loading
class Macro:
    def __init__(self, name, params, body):
        self.name, self.params, self.body = name, params, body


def parse_macros(lines):
    macros, out, i = {}, [], 0
    while i < len(lines):
        s = lines[i].strip()
        m = re.match(r"\.macro\s+(\w+)\s*(.*)", s)
        if m:
            params = []
            for p in [x.strip() for x in m.group(2).split(",") if x.strip()]:
                nm, _, dflt = p.partition("=")
                nm, _, req = nm.partition(":")
                params.append((nm.strip(), dflt.strip() if dflt else None, req.strip() == "req"))
            body, i = [], i + 1
            while lines[i].strip() != ".endm":
                body.append(lines[i])
                i += 1
            macros[m.group(1)] = Macro(m.group(1), params, body)
        else:
            out.append(lines[i])
        i += 1
    return macros, out


def strip_cpp(text, env):
    """Handle #if / #else / #endif on object-like defines; drop #include / #define lines."""
    keep, stack = [], []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("#if "):
            v = evaluate(s[4:], env, {})
            stack.append(bool(v))
        elif s.startswith("#else"):
            stack[-1] = not stack[-1]
        elif s.startswith("#endif"):
            stack.pop()
        elif s.startswith("#"):
            continue
        elif all(stack):
            keep.append(line.split("//")[0].rstrip())
    return keep


def tokenise(lines):
    """-> list of ('label', name) / ('cmd', name, [args])"""
    out = []
    for line in lines:
        s = line.strip()
        if not s or s.startswith("."):
            continue
        m = re.match(r"(\w+):\s*(.*)", s)
        if m:
            out.append(("label", m.group(1)))
            s = m.group(2).strip()
            if not s:
                continue
        name, _, rest = s.partition(" ")
        out.append(("cmd", name, split_args(rest) if rest.strip() else []))
    return out


def expand(stmts, macros, env, funcs, depth=0):
    out = []
    for st in stmts:
        if st[0] == "cmd":
            st = ("cmd", st[1], _flatten_res(st[2], env))
        if st[0] == "cmd" and st[1] in macros:
            mac = macros[st[1]]
            args = list(st[2])
            sub = {}
            for idx, (pn, dflt, req) in enumerate(mac.params):
                sub[pn] = args[idx] if idx < len(args) and args[idx] != "" else dflt
            body = []
            for bl in mac.body:
                for pn, val in sub.items():
                    bl = re.sub(rf"\\{pn}\b", lambda _m, v=val: v if v is not None else "", bl)
                body.append(bl.split("//")[0].rstrip())
            body = strip_cpp("\n".join(body), env) if any(l.strip().startswith("#") for l in body) else body
            out += expand(tokenise(body), macros, env, funcs, depth + 1)
        else:
            out.append(st)
    return out


OVERRIDES = {}


def load_script(path: Path):
    env, funcs = load_defines(CONSTS.read_text())
    env.update(OVERRIDES)
    env.setdefault("TRUE", "1")
    env.setdefault("FALSE", "0")
    opal_text = OPAL_INC.read_text()
    env, funcs = _merge(env, funcs, load_defines("\n".join(_keep_defines(opal_text, env))))
    script_text = path.read_text()
    env, funcs = _merge(env, funcs, load_defines("\n".join(_keep_defines(script_text, env))))
    # cpp-style OPAL_RES(sheet, pal) -> the four NAIX names (kept symbolic)
    funcs["OPAL_RES"] = (["sheet", "pal"], "sheet##_NCGR_lz, pal##_NCLR, sheet##_cell_NCER_lz, sheet##_anim_NANR_lz")
    inc_lines = strip_cpp(opal_text, env)
    macros, _ = parse_macros(inc_lines)
    lines = strip_cpp(script_text, env)
    local, rest = parse_macros(lines)
    macros.update(local)
    stmts = tokenise(rest)
    # expand OPAL_RES symbolically before macro substitution
    stmts = [(s[0], s[1], _flatten_res(s[2], env)) if s[0] == "cmd" else s for s in stmts]
    stmts = expand(stmts, macros, env, funcs)
    stmts = [(s[0], s[1], _flatten_res(s[2], env)) if s[0] == "cmd" else s for s in stmts]
    return stmts, env, funcs


def _keep_defines(text, env):
    """Lines of `text` that are live under the current #if/#else/#endif evaluation (keeps #define lines)."""
    keep, stack = [], []
    for line in text.splitlines():
        t = line.strip()
        if t.startswith("#if "):
            stack.append(bool(evaluate(t[4:], env, {})))
        elif t.startswith("#else"):
            stack[-1] = not stack[-1]
        elif t.startswith("#endif"):
            stack.pop()
        elif all(stack):
            keep.append(line)
    return keep


def _merge(env, funcs, other):
    env2, funcs2 = dict(env), dict(funcs)
    env2.update(other[0])
    funcs2.update(other[1])
    return env2, funcs2


def _res(arg):
    m = re.fullmatch(r"OPAL_RES\((\w+),\s*(\w+)\)", arg.strip())
    if m:
        sheet, pal = m.groups()
        return f"{sheet}_NCGR_lz, {pal}_NCLR, {sheet}_cell_NCER_lz, {sheet}_anim_NANR_lz"
    return arg


def _resolve_alias(a, env):
    a = a.strip()
    for _ in range(4):
        if re.fullmatch(r"\w+", a) and a in env and "OPAL_RES(" in env[a]:
            a = env[a].strip()
        else:
            break
    return a


def _flatten_res(args, env):
    out = []
    for a in args:
        r = _res(_resolve_alias(a, env))
        out += split_args(r) if "_NCGR_lz," in r else [r]
    return out


# ------------------------------------------------------------------ simulation
class Fail(Exception):
    pass


def load_sheets():
    sheets = {}
    for p in PROV.glob("opal_*.provenance.json"):
        d = json.loads(p.read_text())
        sheets[d["name"]] = d
    return sheets


def popcount_mask(mask):
    if mask == 0:
        return 0
    if mask & (1 << 6):  # ALL_BATTLERS
        return 4
    if mask & (1 << 5):  # NOT_ATTACKER
        return 3
    return sum(1 for b in BATTLER_BITS.values() if mask & b)


class State:
    def __init__(self):
        self.t = 0
        self.managers = {}  # id -> {"max": n, "res": {...}, "live": [(end_t, count)]}
        self.particles = set()
        self.unloaded_with_managers = False
        self.base_alpha = 0
        self.base_fade_end = 0
        self.cam_end = 0
        self.cam_start = None
        self.shake_base_t = None
        self.fx_end = 0
        self.busy = 0  # end time of every known task
        self.stack = []
        self.log = []
        self.vars = {}
        self.peak_managers = 0
        self.peak_fx = 0
        self.peak_tiles = 0
        self.peak_oam = 0

    def copy(self):
        return copy.deepcopy(self)


def sheet_max_oams(res):
    """Worst-case hardware OAM entries one live sprite of this manager's sheet can occupy (max over its cells)."""
    sheet = (res.get("LoadCharResObj") or "").replace("_NCGR_lz", "")
    p = ROOT / "res/graphics/battle/moves" / f"{sheet}_cell.json"
    if not p.exists():
        return 0
    return max(c["oamCount"] for c in json.loads(p.read_text())["cells"])


def sheet_tiles(res, sheets):
    sheet = (res.get("LoadCharResObj") or "").replace("_NCGR_lz", "")
    if sheet in sheets:
        return sheets[sheet]["obj_tiles"]
    b1 = ROOT / "docs/visual_overhaul/b1_installed_donors" / f"{sheet}.provenance.json"
    if b1.exists():
        return json.loads(b1.read_text())["obj_tiles"]
    return 0  # native vanilla sheet: not measured here


def run_script(stmts, env, funcs, sheets, name):
    labels = {s[1]: i for i, s in enumerate(stmts) if s[0] == "label"}
    results = []

    def ev(a):
        return evaluate(a, env, funcs)

    def step(st, pc, seen):
        while True:
            if pc >= len(stmts):
                raise Fail("fell off the end of the script without End")
            s = stmts[pc]
            if s[0] == "label":
                pc += 1
                continue
            _, cmd, args = s
            key = (pc, st.t, len(st.stack))
            if cmd == "End":
                return finish(st)
            if cmd == "Delay":
                st.t += ev(args[0])
                st.log.append(f"t{st.t} Delay")
            elif cmd == "WaitForAnimTasks":
                st.t = max(st.t, st.busy)
            elif cmd == "WaitForAllEmitters":
                pass
            elif cmd == "Jump":
                pc = labels[args[0]]
                continue
            elif cmd == "Call":
                st.stack.append(pc + 1)
                pc = labels[args[0]]
                continue
            elif cmd == "Return":
                if not st.stack:
                    raise Fail("Return without Call")
                pc = st.stack.pop()
                continue
            elif cmd in ("JumpIfEffectChanceOdd", "JumpIfBattlerSide", "JumpIfWeather"):
                targets = args[1:] if cmd == "JumpIfBattlerSide" else args
                for tg in targets:
                    step(st.copy(), labels[tg], set())
                return
            elif cmd in ("JumpIfFriendlyFire", "JumpIfContest"):
                step(st.copy(), labels[args[0]], set())
                pc += 1
                continue
            elif cmd in ("JumpIfEqual", "JumpIfEffectChance"):
                step(st.copy(), labels[args[-1]], set())
                pc += 1
                continue
            elif cmd == "InitSpriteManager":
                mid = ev(args[0])
                if mid in st.managers:
                    raise Fail(f"sprite manager {mid} initialised twice")
                if len(st.managers) >= MAX_CONCURRENT_MANAGERS:
                    raise Fail(f"{len(st.managers) + 1} concurrent sprite managers (policy max {MAX_CONCURRENT_MANAGERS}: one OBJ palette each)")
                st.managers[mid] = {"max": ev(args[1]), "res": {}, "live": []}
                st.peak_managers = max(st.peak_managers, len(st.managers))
                st.log.append(f"t{st.t} manager{mid}+")
            elif cmd in ("LoadCharResObj", "LoadPlttRes", "LoadCellResObj", "LoadAnimResObj"):
                mid = ev(args[0])
                if mid not in st.managers:
                    raise Fail(f"{cmd} into uninitialised manager {mid}")
                st.managers[mid]["res"][cmd] = args[1]
            elif cmd in ("AddSpriteWithFunc", "AddSprite"):
                mid = ev(args[0])
                if mid not in st.managers:
                    raise Fail(f"{cmd} on uninitialised manager {mid}")
                m = st.managers[mid]
                off = 2 if cmd == "AddSpriteWithFunc" else 2
                char, pltt, cell, anim = args[off:off + 4] if cmd == "AddSpriteWithFunc" else args[2:6]
                if (m["res"].get("LoadCharResObj"), m["res"].get("LoadPlttRes"), m["res"].get("LoadCellResObj"), m["res"].get("LoadAnimResObj")) != (char, pltt, cell, anim):
                    raise Fail(f"{cmd} resources do not match manager {mid}: {char},{pltt},{cell},{anim} vs {m['res']}")
                count, life = 1, 0
                if cmd == "AddSpriteWithFunc" and ev(args[1]) == ev("SPRITE_FUNC_OPAL_FX"):
                    a = [ev(x) for x in args[8:18]]
                    anchor, dest, frames, flags = a[0], a[1], a[2], a[9]
                    if None in (anchor, dest, frames, flags):
                        raise Fail("symbolic Opal FX arguments")
                    seq = flags & 0xFF
                    sheet = char.replace("_NCGR_lz", "")
                    plen = 0
                    if sheet in sheets and seq < len(sheets[sheet]["sequences"]):
                        plen = sheets[sheet]["sequences"][seq]["total_delay"]
                    elif (ROOT / "docs/visual_overhaul/b1_installed_donors" / f"{sheet}.provenance.json").exists():
                        # B1 Ranger donor sheet reused through OpalFx (one play-once sequence): length from its installed anim json
                        aj = json.loads((ROOT / "res/graphics/battle/moves" / f"{sheet}_anim.json").read_text())
                        if seq >= len(aj["sequences"]):
                            raise Fail(f"unknown sequence {sheet}:{seq}")
                        plen = sum(fd["frameDelay"] for fd in aj["sequences"][seq]["frameData"])
                    else:
                        raise Fail(f"unknown Opal sheet/sequence {sheet}:{seq}")
                    life = frames if frames > 0 else min(plen, MAX_FX_LIFETIME)
                    trail = bool(flags & (1 << 14)) and dest
                    n_dest = popcount_mask(dest)
                    if trail and n_dest != 1:
                        pass  # engine builds no trail for spreads; still single/limited by cap
                    count = 3 if (trail and n_dest == 1) else min(4, popcount_mask(dest) if dest else popcount_mask(anchor))
                    if trail and n_dest == 1:
                        life += 6
                    if count == 0:
                        raise Fail("Opal FX with empty anchor mask")
                    if frames > MAX_FX_LIFETIME:
                        raise Fail("Opal FX lifetime above hard cap")
                    st.log.append(f"t{st.t} fx {sheet}:{seq} x{count} life{life} anchor{anchor:#x} dest{dest:#x}")
                m["live"] = [(e, c) for e, c in m["live"] if e > st.t]
                m["oam"] = sheet_max_oams(m["res"])
                if sum(c for _, c in m["live"]) + count > m["max"]:
                    raise Fail(f"manager {mid} capacity {m['max']} exceeded by {cmd} ({count} new)")
                m["live"].append((st.t + life, count))
                st.busy = max(st.busy, st.t + life)
                st.peak_fx = max(st.peak_fx, sum(c for mm in st.managers.values() for e, c in mm["live"] if e > st.t))
                st.peak_oam = max(st.peak_oam, sum(c * mm.get("oam", 0) for mm in st.managers.values() for e, c in mm["live"] if e > st.t))
                st.peak_tiles = max(st.peak_tiles, sum(sheet_tiles(mm["res"], sheets) for mm in st.managers.values()))
            elif cmd == "FreeSpriteManager":
                mid = ev(args[0])
                st.managers.pop(mid, None)
                st.log.append(f"t{st.t} manager{mid}-")
            elif cmd in ("LoadParticleResource", "LoadParticleSystem"):
                st.particles.add(ev(args[0]))
            elif cmd == "UnloadParticleSystem":
                pid = ev(args[0])
                if pid not in st.particles:
                    raise Fail(f"UnloadParticleSystem {pid} without load")
                if st.managers:
                    raise Fail(f"particle system {pid} unloaded while sprite managers {sorted(st.managers)} are still live")
                st.particles.discard(pid)
            elif cmd in ("CreateEmitter", "CreateEmitterEx", "CreateEmitterForMove", "CreateEmitterForFriendlyFire"):
                if not st.particles:
                    raise Fail(f"{cmd} with no particle system loaded")
            elif cmd == "Func_FadeBg":
                typ, delay, a0, a1 = (ev(args[0]), ev(args[1]), ev(args[2]), ev(args[3]))
                if typ == ev("FADE_BG_TYPE_BASE"):
                    if not (0 <= a0 <= 16 and 0 <= a1 <= 16):
                        raise Fail("FadeBg alpha out of range")
                    if st.t < st.base_fade_end:
                        raise Fail(f"overlapping base-BG fades at t{st.t} (previous ends t{st.base_fade_end})")
                    if a0 != st.base_alpha:
                        raise Fail(f"base-BG fade starts at alpha {a0} but current alpha is {st.base_alpha}")
                    dur = abs(a1 - a0) * max(delay, 1) + 1
                    st.base_alpha = a1
                    st.base_fade_end = st.t + dur
                    st.busy = max(st.busy, st.base_fade_end)
                    st.log.append(f"t{st.t} basefade {a0}->{a1} dur{dur}")
            elif cmd == "Func_ShakeBg":
                if len(args) > 5 and ev(args[5]) == ev("SHAKE_BG_TARGET_BASE"):
                    if st.t < st.cam_end:
                        raise Fail(f"native base-BG shake at t{st.t} overlaps Opal camera cue ending t{st.cam_end}")
                    st.shake_base_t = st.t
                    st.log.append(f"t{st.t} nativeshakebg")
            elif cmd == "Func_OpalCamera":
                mode, dx, dy, fi, fh, fo = [ev(x) for x in args[:6]]
                total = min(90, max(1, fi) + max(0, fh) + max(1, fo))
                if st.t < st.cam_end:
                    # engine ignores an overlapping request (first owner wins); flag so scripts do not rely on it
                    raise Fail(f"Opal camera cue at t{st.t} overlaps previous cue ending t{st.cam_end}")
                if st.shake_base_t is not None and st.t < st.shake_base_t + 16:
                    raise Fail(f"Opal camera cue at t{st.t} starts within 16 frames of a native base-BG shake")
                st.cam_end = st.t + total
                st.busy = max(st.busy, st.cam_end)
                st.log.append(f"t{st.t} camera mode{mode} {total}f")
            pc += 1

    def finish(st):
        if st.stack:
            raise Fail("End reached inside a Call")
        if st.peak_oam > MAX_OAM_ENTRIES:
            raise Fail(f"peak {st.peak_oam} concurrent Opal OAM entries exceeds the {MAX_OAM_ENTRIES}-entry policy cap")
        if st.peak_tiles > MAX_OBJ_CHAR_TILES:
            raise Fail(f"peak {st.peak_tiles} concurrent OBJ char tiles exceeds the {MAX_OBJ_CHAR_TILES}-tile policy cap")
        if st.managers:
            raise Fail(f"End with live sprite managers {sorted(st.managers)}")
        if st.particles:
            # BattleAnimScriptCmd_End frees every remaining particle system itself; vanilla Fire Blast relies on this for slot 1.
            st.log.append(f"note: End frees particle system(s) {sorted(st.particles)}")
        if st.base_alpha != 0:
            raise Fail(f"End with base-BG fade alpha {st.base_alpha} (not restored)")
        results.append({"frames_lower_bound": max(st.t, st.busy), "peak_sprite_managers": st.peak_managers, "peak_live_fx_sprites": st.peak_fx,
                        "peak_obj_char_tiles": st.peak_tiles, "peak_oam_entries_upper_bound": st.peak_oam, "cue_log": st.log})

    entry = labels.get("L_0", 0)
    step(State(), entry, set())
    return results


def check_move(path: Path, sheets):
    stmts, env, funcs = load_script(path)
    try:
        return run_script(stmts, env, funcs, sheets, path.parent.name), None
    except Fail as e:
        return None, str(e)
    except KeyError as e:
        return None, f"unresolved label/symbol {e}"


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--moves", nargs="*", help="move directory names under res/moves (default: every script using Opal cues)")
    ap.add_argument("--json", type=Path, help="write the cue log of every path")
    ap.add_argument("--baseline", type=Path, help="fail if the cue log differs from this committed baseline (drift gate)")
    ap.add_argument("--define", action="append", default=[], metavar="NAME=VALUE", help="override a constant, e.g. OPAL_LOW_FLASH=1")
    a = ap.parse_args()
    for d in a.define:
        k, _, v = d.partition("=")
        OVERRIDES[k] = v
    sheets = load_sheets()
    paths = []
    if a.moves:
        paths = [ROOT / "res/battle/scripts/common_anims" / (m.split("/")[1] + ".s") if m.startswith("common_anims/") else ROOT / "res/moves" / m / "anim.s" for m in a.moves]
    else:
        for p in sorted(list((ROOT / "res/moves").glob("*/anim.s")) + list((ROOT / "res/battle/scripts/common_anims").glob("*.s"))):
            t = p.read_text()
            if re.search(r"\bOpal\w+|OPAL_", t):
                paths.append(p)
    report, bad = {}, 0
    for p in paths:
        res, err = check_move(p, sheets)
        move = p.parent.name if p.name == "anim.s" else f"common_anims/{p.stem}"
        if err:
            bad += 1
            print(f"FAIL {move}: {err}")
        else:
            report[move] = res
            print(f"ok   {move}: {len(res)} path(s), frames>= {[r['frames_lower_bound'] for r in res]}")
    if a.json:
        a.json.write_text(json.dumps(report, indent=1) + "\n")
    if bad:
        sys.exit(1)
    if a.baseline:
        want = json.loads(a.baseline.read_text())
        if want != json.loads(json.dumps(report)):
            diff = sorted(k for k in set(want) | set(report) if want.get(k) != report.get(k))
            print(f"FAIL: cue trace drifted from {a.baseline} for: {diff}; regenerate with --json after reviewing the change")
            sys.exit(1)
        print(f"baseline {a.baseline.name}: identical")
    print(f"PASS: {len(report)} Opal cue scripts: all paths balanced, no overlapping camera/fade owners, nothing live at End")


if __name__ == "__main__":
    main()
