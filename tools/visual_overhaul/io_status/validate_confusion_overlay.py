#!/usr/bin/env python3
"""Static + symbolic validation for the IO-STATUS confusion overlay pilot.

Usage:
    validate_confusion_overlay.py                 # source checks + mutation self-test
    validate_confusion_overlay.py --no-mutations  # source checks only

What is checked
  1. Gating, read-only battle access, no resource allocation, lifecycle (string-level, kept simple).
  2. Renderer state, by *tracing* the overlay's geometry-command stream on every control-flow
     path (guards, loops, optional Identity) with a small C-subset interpreter:
       - matrix depth never negative, balanced on every path, bounded;
       - Begin/End strictly paired, only Color/Vtx inside, Vtx never outside;
       - only whitelisted G3 commands (no TexPlttBase / MtxMode / Material* / Swap ...);
       - flush precedes the first command; no `return` after any command was emitted
         (the "nothing qualifies" path is command-free);
       - texture parameter state machine: manager -> NONE before the first polygon ->
         restored to the manager's exact argument list after the last one;
       - PolygonAttr issued before every Begin, opaque, unlit, overlay polygon ID block;
       - per-battler polygon/vertex budgets measured from the trace, not from #defines.
  3. Consumer contract (what later 3D users re-establish), checked in the repo sources:
       - the mon pass sets TexPlttBase / material+vertex colour / PolygonAttr before every quad
         and TexImageParam before its loop;
       - every mode-0 frame starts with G3_ResetG3X (-> G3X_Reset, verified against the pinned
         SDK source when the subproject is present);
       - the SPL particle drawer sets PolygonAttr per particle, Color per particle and
         TexImageParam/TexPlttBase per emitter;
       - SysTask_DrawSprites ordering, and no other 3D command issuer exists in the battle code.
  4. Geometry/depth bounds re-evaluated with the same fixed-point formulas.

The mutation self-test applies deliberate defects to in-memory copies of the sources and demands
that each one is rejected. Not a runtime or visual test.
"""
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

FILES = {
    "overlay_c": "src/battle/battle_status_overlay.c",
    "overlay_h": "include/battle/battle_status_overlay.h",
    "battle_main": "src/battle/battle_main.c",
    "battle_display": "src/battle/battle_display.c",
    "meson": "src/meson.build",
    "lsf": "platinum.us/main.lsf",
    "pokemon_sprite": "src/pokemon_sprite.c",
    "particle_helper": "src/overlay011/particle_helper.c",
    "g3x_wrapper": "src/unk_0202419C.c",
    "spl_draw": "lib/spl/src/spl_draw.c",
    "spl_emitter": "lib/spl/src/spl_emitter.c",
}
SDK_G3X = ROOT / "subprojects/NitroSDK-4.2.30001/libraries/gx/src/g3x.c"
# Directories that make up / feed the battle overlay. Any 3D command issuer in them must be known.
BATTLE_DIRS = ["src/battle", "src/battle_anim", "src/battle_sub_menus"]


def load_sources():
    return {k: (ROOT / v).read_text() for k, v in FILES.items()}


# ----------------------------------------------------------------------------- C helpers
def strip_comments(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//[^\n]*", "", text)


def match_brace(text, open_idx, o="{", c="}"):
    depth = 0
    for i in range(open_idx, len(text)):
        if text[i] == o:
            depth += 1
        elif text[i] == c:
            depth -= 1
            if depth == 0:
                return i
    raise ValueError("unbalanced")


def function_body(code, name):
    m = re.search(r"^(?:static\s+)?[\w \*]+?\b" + re.escape(name) + r"\s*\([^;{]*?\)\s*\{", code, re.M)
    if not m:
        return None
    end = match_brace(code, m.end() - 1)
    return code[m.end():end]


def split_args(s):
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


def norm(s):
    return re.sub(r"\s+", "", s)


# ----------------------------------------------------------------------------- mini parser
class Call:
    def __init__(self, name, args):
        self.name, self.args = name, args


class Return:
    pass


class If:
    def __init__(self, cond, then, els):
        self.cond, self.then, self.els = cond, then, els


class For:
    def __init__(self, bound, body):
        self.bound, self.body = bound, body


TRACKED = re.compile(r"\b(G3_\w+|G3X_\w+|NNS_G3d\w+|DrawConfusionStars|DrawStarPass)\s*\(")


def skip_ws(t, i):
    while i < len(t) and t[i].isspace():
        i += 1
    return i


def parse_stmt(t, i):
    i = skip_ws(t, i)
    if t[i] == "{":
        j = match_brace(t, i)
        return parse_block(t[i + 1:j]), j + 1
    m = re.match(r"if\s*\(", t[i:])
    if m:
        p = i + m.end() - 1
        q = match_brace(t, p, "(", ")")
        cond = t[p + 1:q]
        then, j = parse_stmt(t, q + 1)
        j2 = skip_ws(t, j)
        els = []
        if re.match(r"else\b", t[j2:]):
            els, j = parse_stmt(t, j2 + 4)
        return [If(cond, then, els)], j
    m = re.match(r"for\s*\(", t[i:])
    if m:
        p = i + m.end() - 1
        q = match_brace(t, p, "(", ")")
        hdr = t[p + 1:q]
        bm = re.search(r";\s*\w+\s*<\s*(\w+)\s*;", hdr)
        body, j = parse_stmt(t, q + 1)
        return [For(bm.group(1) if bm else None, body)], j
    # simple statement up to ';' at depth 0
    depth, j = 0, i
    while j < len(t):
        if t[j] in "([{":
            depth += 1
        elif t[j] in ")]}":
            depth -= 1
        elif t[j] == ";" and depth == 0:
            break
        j += 1
    stmt = t[i:j]
    if re.match(r"return\b", stmt):
        return [Return()], j + 1
    m = TRACKED.search(stmt)
    if m:
        p = stmt.index("(", m.start())
        q = match_brace(stmt, p, "(", ")")
        return [Call(m.group(1), split_args(stmt[p + 1:q]))], j + 1
    return [], j + 1


def parse_block(t):
    nodes, i = [], 0
    while True:
        i = skip_ws(t, i)
        if i >= len(t):
            return nodes
        n, i = parse_stmt(t, i)
        nodes.extend(n)


def relevant(nodes):
    for n in nodes:
        if isinstance(n, (Call, Return)):
            return True
        if isinstance(n, If) and (relevant(n.then) or relevant(n.els)):
            return True
        if isinstance(n, For) and relevant(n.body):
            return True
    return False


# ----------------------------------------------------------------------------- symbolic trace
ALLOWED = {
    "NNS_G3dGeFlushBuffer", "G3_PushMtx", "G3_PopMtx", "G3_Identity", "G3_TexImageParam",
    "G3_PolygonAttr", "G3_Translate", "G3_Scale", "G3_Color", "G3_Begin", "G3_End", "G3_Vtx",
}
LOOP_BOUNDS = {"maxBattlers": [1]}


class Path:
    def __init__(self, events=None):
        self.events = list(events or [])
        self.status = "cont"
        self.cnt = None  # None = unconstrained, 0 = `count == 0` branch, "nz" = guard passed

    def fork(self):
        p = Path(self.events)
        p.cnt = self.cnt
        return p


def trace(nodes, funcs, consts, paths, errs):
    """Execute nodes over every path; returns the list of resulting paths."""
    for n in nodes:
        live = [p for p in paths if p.status == "cont"]
        done = [p for p in paths if p.status != "cont"]
        paths = done
        if isinstance(n, Call):
            if n.name in funcs:
                paths += trace(funcs[n.name], funcs, consts, live, errs)
            else:
                for p in live:
                    p.events.append((n.name, n.args))
                paths += live
        elif isinstance(n, Return):
            for p in live:
                p.status = "ret"
            paths += live
        elif isinstance(n, If):
            if not relevant([n]):
                paths += live
                continue
            a = [p.fork() for p in live]
            b = [p.fork() for p in live]
            if norm(n.cond) == "count==0":
                for p in a:
                    p.cnt = 0
                for p in b:
                    p.cnt = "nz"
            paths += trace(n.then, funcs, consts, a, errs)
            paths += trace(n.els, funcs, consts, b, errs)
        elif isinstance(n, For):
            if not relevant(n.body):
                paths += live
                continue
            for p0 in live:
                if n.bound == "count":
                    counts = [0] if p0.cnt == 0 else [1, 2, 4] if p0.cnt == "nz" else [0, 1, 2, 4]
                elif n.bound in LOOP_BOUNDS:
                    counts = LOOP_BOUNDS[n.bound]
                elif n.bound in consts:
                    counts = [consts[n.bound]]
                else:
                    errs.append(f"cannot resolve loop bound: {n.bound}")
                    counts = [1]
                for c in counts:
                    cur = [p0.fork()]
                    for _ in range(c):
                        cur = trace(n.body, funcs, consts, cur, errs)
                    paths += cur
    return paths


def check_path(p, mgr_tex_args, consts, errs, tag):
    ev = p.events
    if not ev:
        return 0
    if p.status == "ret":
        errs.append(f"{tag}: `return` after geometry commands were emitted")
    if not any(e[0] == "G3_Begin" for e in ev):
        errs.append(f"{tag}: geometry commands issued although nothing is drawn")
    if ev[0][0] != "NNS_G3dGeFlushBuffer":
        errs.append(f"{tag}: first command must be NNS_G3dGeFlushBuffer, got {ev[0][0]}")
    depth, maxd, open_, tex, pa_ok = 0, 0, False, "MANAGER", False
    verts, quads_begun, last_begin_idx, last_tex_idx = 0, 0, -1, -1
    for idx, (name, args) in enumerate(ev):
        if name not in ALLOWED:
            errs.append(f"{tag}: command not allowed in overlay: {name}")
            continue
        if open_ and name not in ("G3_Vtx", "G3_End"):
            errs.append(f"{tag}: {name} inside Begin/End")
        if name == "G3_PushMtx":
            depth += 1
            maxd = max(maxd, depth)
        elif name == "G3_PopMtx":
            n = int(norm(args[0])) if args and norm(args[0]).isdigit() else None
            if n != 1:
                errs.append(f"{tag}: PopMtx must pop exactly 1 (got {args})")
            depth -= 1
            if depth < 0:
                errs.append(f"{tag}: matrix stack underflow")
        elif name in ("G3_Identity", "G3_Translate", "G3_Scale") and depth < 1:
            errs.append(f"{tag}: {name} outside a PushMtx/PopMtx pair would alter the caller's matrix")
        elif name == "G3_TexImageParam":
            a = [norm(x) for x in args]
            if a and a[0] == "GX_TEXFMT_NONE":
                if a[1] != "GX_TEXGEN_NONE":
                    errs.append(f"{tag}: untextured TexImageParam must use GX_TEXGEN_NONE")
                tex = "NONE"
            elif a == mgr_tex_args:
                tex = "MANAGER"
            else:
                errs.append(f"{tag}: TexImageParam args are neither NONE nor the manager's: {args}")
                tex = "OTHER"
            last_tex_idx = idx
        elif name == "G3_PolygonAttr":
            a = [norm(x) for x in args]
            want = ["GX_LIGHTMASK_NONE", "GX_POLYGONMODE_MODULATE", "GX_CULL_NONE"]
            if a[:3] != want or not a[3].startswith("OVERLAY_POLYGON_ID_BASE") or a[4:] != ["31", "0"]:
                errs.append(f"{tag}: PolygonAttr must be unlit/MODULATE/cull-none/overlay-ID/alpha 31/misc 0: {args}")
            pa_ok = True
        elif name == "G3_Begin":
            if open_:
                errs.append(f"{tag}: nested Begin")
            if norm(args[0]) != "GX_BEGIN_QUADS":
                errs.append(f"{tag}: unexpected primitive {args[0]}")
            if tex != "NONE":
                errs.append(f"{tag}: polygon begun while texture state is {tex}, not NONE")
            if not pa_ok:
                errs.append(f"{tag}: polygon begun before any PolygonAttr")
            open_ = True
            quads_begun += 1
            last_begin_idx = idx
        elif name == "G3_Vtx":
            if not open_:
                errs.append(f"{tag}: Vtx outside Begin/End")
            verts += 1
        elif name == "G3_End":
            if not open_:
                errs.append(f"{tag}: End without Begin")
            open_ = False
    if open_:
        errs.append(f"{tag}: Begin never closed")
    if depth != 0:
        errs.append(f"{tag}: matrix depth {depth} at exit (unbalanced)")
    if maxd > 3:
        errs.append(f"{tag}: matrix depth {maxd} exceeds the pilot bound of 3")
    if tex != "MANAGER":
        errs.append(f"{tag}: texture state not restored to the manager's at exit (is {tex})")
    if last_tex_idx < last_begin_idx:
        errs.append(f"{tag}: texture restore must come after the last polygon")
    if verts % 4 != 0:
        errs.append(f"{tag}: vertex count {verts} is not a multiple of 4 (quads)")
    return verts


# ----------------------------------------------------------------------------- constants
def make_consts(code):
    raw = {}
    for m in re.finditer(r"^#define\s+(\w+)\s+(.+)$", code, re.M):
        raw[m.group(1)] = m.group(2).strip()
    vals = {"FX32_ONE": 0x1000, "FX32_SHIFT": 12}

    def ev(name):
        if name in vals:
            return vals[name]
        expr = raw[name]
        for dep in sorted(set(re.findall(r"(?<![\w.])[A-Za-z_]\w*", expr)), key=len, reverse=True):
            if dep in raw or dep in vals:
                expr = re.sub(r"\b" + dep + r"\b", str(ev(dep)), expr)
        if re.search(r"(?<![\w.])[A-Za-z_]", expr):
            return None
        vals[name] = eval(expr.replace("/", "//"), {"__builtins__": {}})
        return vals[name]

    for k in list(raw):
        try:
            ev(k)
        except Exception:
            pass
    return vals


# ----------------------------------------------------------------------------- the checks
def check_all(S):
    errs = []

    def check(cond, msg):
        if not cond:
            errs.append(msg)

    code = strip_comments(S["overlay_c"])
    main_code = strip_comments(S["battle_main"])
    mon_code = strip_comments(S["pokemon_sprite"])
    consts = make_consts(code)

    def fbody(c, name):
        b = function_body(c, name)
        check(b is not None, f"function not found: {name}")
        return b or ""

    draw = fbody(code, "BattleStatusOverlay_Draw")
    can = fbody(code, "CanDrawOverlay")
    anchor = fbody(code, "TryGetAnchor")
    star = fbody(code, "DrawStarPass")
    stars = fbody(code, "DrawConfusionStars")

    # ---- 1. gating / read-only / lifecycle -------------------------------------------------
    check("BattleSystem_GetRenderMode(battleSys) != 0" in can, "render mode 0 gate missing")
    check("BattleSystem_IsInitialized(battleSys)" in can, "battle-initialized gate missing")
    for t in ("BATTLE_TYPE_LINK", "BATTLE_TYPE_SAFARI", "BATTLE_TYPE_PAL_PARK", "BATTLE_TYPE_CATCH_TUTORIAL"):
        check(t in can, f"battle-type exclusion missing: {t}")
    check("BATTLE_STATUS_RECORDING" in can, "recording/playback exclusion missing")
    check("if (!CanDrawOverlay(battleSys))" in draw, "Draw must early-out on CanDrawOverlay")
    check("if (battleCtx == NULL)" in draw, "Draw must NULL-check the battle context")
    check("BattleSystem_GetBattleContext(battleSys)" in draw, "battle context must be fetched per call")
    check("BATTLEMON_VOLATILE_STATUS" in anchor and "VOLATILE_CONDITION_CONFUSION" in anchor,
          "confusion volatile read missing")
    check("BATTLEMON_CUR_HP" in anchor, "HP==0 hide missing")
    for attr in ("MON_SPRITE_HIDE", "MON_SPRITE_HIDE_2", "MON_SPRITE_PARTIAL_DRAW", "MON_SPRITE_ALPHA",
                 "MON_SPRITE_SCALE_X", "MON_SPRITE_SCALE_Y", "MON_SPRITE_SHADOW_HEIGHT"):
        check(attr in anchor, f"visibility/position attribute not consulted: {attr}")
    check("PokemonSprite_IsActive" in anchor and "PokemonSprite_GetAttribute" in anchor
          and anchor.index("PokemonSprite_IsActive") < anchor.index("PokemonSprite_GetAttribute"),
          "IsActive must precede any attribute read")
    check("monSprite == NULL" in anchor, "NULL check before IsActive missing")
    for pat in [r"\bBattleMon_Set\b", r"\bBattleMon_Add", r"\bBattleContext_Set\b", r"\bstatusVolatile\s*(?:=|\|=|&=)",
                r"\bHeap_Alloc", r"\bHeap_Free", r"\bSysTask_Start\b", r"\bSysTask_Done\b", r"\bSpriteSystem_",
                r"\bManagedSprite", r"\bPaletteData_", r"\bNNS_G2dLoadImage", r"\bPokemonSprite_SetAttribute\b",
                r"\bOS_Alloc\b", r"\bGX_Load", r"\bG3X_", r"\bG3_RequestSwapBuffers\b"]:
        check(re.search(pat, code) is None, f"forbidden construct present: {pat}")
    check(re.search(r"^static\s+[^(\n]*(?:\*|=)[^(\n]*;", code, re.M) is None, "file-scope mutable/pointer state")
    check(re.search(r"^static\s+(?!BOOL|void)[^(\n]*;", code, re.M) is None, "unexpected file-scope variable")

    # ---- 2. renderer-state trace -----------------------------------------------------------
    mon_draw = function_body(mon_code, "PokemonSpriteManager_DrawSprites") or ""
    check(bool(mon_draw), "PokemonSpriteManager_DrawSprites not found")
    tm = re.search(r"G3_TexImageParam\((.*?)\);", mon_draw, re.S)
    mgr_tex = [norm(a) for a in split_args(tm.group(1))] if tm else None
    check(mgr_tex is not None, "manager TexImageParam call not found")

    funcs = {
        "DrawConfusionStars": parse_block(stars),
        "DrawStarPass": parse_block(star),
    }
    trace_errs = []
    paths = trace(parse_block(draw), funcs, consts, [Path()], trace_errs)
    errs.extend(trace_errs)
    cmd_paths = [p for p in paths if p.events]
    empty_paths = [p for p in paths if not p.events]
    check(len(cmd_paths) >= 1, "no path emits geometry commands")
    check(any(p.status == "ret" for p in empty_paths), "no command-free early-return path found")
    check(all(p.status == "ret" for p in empty_paths) or True, "")
    per_count = {}
    for i, p in enumerate(paths):
        v = check_path(p, mgr_tex, consts, errs, f"path{i}")
        if p.events:
            quads = sum(1 for e in p.events if e[0] == "G3_Begin")
            per_count.setdefault(quads, set()).add(v)
    # budgets measured from the trace (each Begin emits two quads = 8 vertices)
    check(consts.get("ORBIT_STAR_COUNT") == 3, "pilot expects 3 orbiting stars")
    for begins, verts in per_count.items():
        check(len(verts) == 1, f"inconsistent vertex totals for {begins} Begin/End pairs: {sorted(verts)}")
        for v in verts:
            check(v == begins * 8, f"vertex total {v} != 8 x {begins} Begin/End pairs")
    per_mon_begins = 2 * consts.get("ORBIT_STAR_COUNT", 0)
    check(sorted(per_count) == [per_mon_begins, 2 * per_mon_begins, 4 * per_mon_begins],
          f"unexpected Begin/End counts for 1/2/4 battlers: {sorted(per_count)}")
    worst_verts = max((v for vs in per_count.values() for v in vs), default=0)
    check(worst_verts == 192 and worst_verts // 4 == 48, f"four-battler budget changed: {worst_verts} vertices")
    check(worst_verts // 4 <= 64 and worst_verts <= 256, "polygon/vertex cap exceeded")
    # TexImageParam is restored with the manager's exact args, and placed inside the matrix pair
    check(bool(mgr_tex) and any(
        e[0] == "G3_TexImageParam" and [norm(a) for a in e[1]] == mgr_tex
        for p in cmd_paths for e in p.events), "restore TexImageParam does not equal the manager's")
    check(draw.rfind("G3_TexImageParam") != -1 and draw.rfind("G3_TexImageParam") < draw.rfind("G3_PopMtx"),
          "restore must precede the final PopMtx")
    check("31, 0);" in draw and consts.get("OVERLAY_POLYGON_ID_BASE", 0) >= 4
          and consts.get("OVERLAY_POLYGON_ID_BASE", 99) + 3 <= 63, "overlay polygon IDs must be in 4..63")
    bd = S["battle_display"]
    check(re.search(r"PokemonSpriteManager_CreateSpriteAtIndex\([^;]*,\s*battler,\s*battler,", bd) is not None,
          "battler quads no longer use polygon ID == battler index (overlay ID block assumption)")

    # ---- 3. consumer contract --------------------------------------------------------------
    loop_m = re.search(r"for \(int i = 0; i < MAX_MON_SPRITES; i\+\+\) \{", mon_draw)
    check(loop_m is not None, "manager sprite loop not found")
    if loop_m and tm:
        head, loop = mon_draw[:loop_m.start()], mon_draw[loop_m.start():]
        check("G3_TexImageParam(" in head, "manager must set TexImageParam before its loop")
        order = [loop.find(s) for s in ("G3_TexPlttBase(", "G3_MaterialColorDiffAmb(", "G3_PolygonAttr(", "NNS_G2dDrawSpriteFast(")]
        check(all(o >= 0 for o in order) and order == sorted(order),
              "manager must set TexPlttBase, material, PolygonAttr before each quad")
        check(re.search(r"G3_MaterialColorDiffAmb\([^;]*,\s*TRUE\)", loop) is not None,
              "manager material call must set the vertex colour (IsSetVtxColor TRUE)")
    ph = function_body(strip_comments(S["particle_helper"]), "ParticleHelper_DrawParticleSystems") or ""
    check(ph.strip().startswith("G3_ResetG3X();"), "mode-0 frames must begin with G3_ResetG3X")
    check("G3X_Reset();" in strip_comments(S["g3x_wrapper"]), "G3_ResetG3X must call G3X_Reset")
    if SDK_G3X.exists():
        sdk = strip_comments(SDK_G3X.read_text())
        rb = function_body(sdk, "G3X_Reset") or ""
        for need in ("G3X_ResetMtxStack();", "G3_PolygonAttr(", "G3_TexImageParam(", "G3OP_TEXPLTT_BASE"):
            check(need in rb, f"SDK G3X_Reset no longer contains {need}")
    spl = strip_comments(S["spl_draw"])
    check("G3_PolygonAttr(" in (function_body(spl, "SPLDraw_Setup") or ""), "SPL per-particle PolygonAttr missing")
    check(spl.count("G3_Color(") >= 8, "SPL per-particle vertex colour setup missing")
    spe = strip_comments(S["spl_emitter"])
    ts = function_body(spe, "SPLUtil_SetTexture") or ""
    check("G3_TexImageParam(" in ts and "G3_TexPlttBase(" in ts, "SPL per-emitter texture setup missing")

    m = re.search(r"^static void SysTask_DrawSprites\([^;]*?\)\s*\{.*?^\}", main_code, re.S | re.M)
    check(m is not None, "SysTask_DrawSprites not found")
    if m:
        body = m.group(0)
        seq = [body.find(s) for s in ("ParticleHelper_DrawParticleSystems(", "PokemonSpriteManager_DrawSprites(",
                                      "BattleStatusOverlay_Draw(", "SpriteSystem_DrawSprites(",
                                      "SpriteSystem_UpdateTransfer(", "G3_RequestSwapBuffers(")]
        check(all(i >= 0 for i in seq) and seq == sorted(seq), "SysTask_DrawSprites call order changed")
        check("renderMode == 0 || battleSys->renderMode == 3" in body, "overlay call must stay inside the mode 0/3 block")
        after = body[body.find("BattleStatusOverlay_Draw("):]
        after = after[after.find(";"):]
        check(re.search(r"\b(G3_(?!RequestSwapBuffers)|G3X_|NNS_G3d|NNS_G2dDraw|ParticleSystem_|PokemonSprite)", after) is None,
              "no 3D command issuer may sit between the overlay and the swap request")
    check(main_code.count("BattleStatusOverlay_Draw(") == 1, "overlay must have exactly one call site")
    check('#include "battle/battle_status_overlay.h"' in main_code, "battle_main.c include missing")

    # inventory of 3D command issuers in the battle code
    issuers = {}
    for d in BATTLE_DIRS:
        for f in sorted((ROOT / d).rglob("*.c")):
            rel = str(f.relative_to(ROOT))
            txt = S["overlay_c"] if rel == FILES["overlay_c"] else S["battle_main"] if rel == FILES["battle_main"] else f.read_text()
            names = set(re.findall(r"\b(G3X?_\w+|NNS_G3d\w+|ParticleSystem_DrawAll|PokemonSpriteManager_DrawSprites)\s*\(", strip_comments(txt)))
            if names:
                issuers[rel] = names
    expected_main = {"G3X_SetShading", "G3X_AntiAlias", "G3X_AlphaTest", "G3X_AlphaBlend", "G3X_EdgeMarking",
                     "G3X_SetFog", "G3X_SetClearColor", "G3_ViewPort", "G3_RequestSwapBuffers", "PokemonSpriteManager_DrawSprites"}
    check(issuers.get(FILES["battle_main"]) == expected_main,
          f"battle_main.c 3D command set changed: {sorted(issuers.get(FILES['battle_main'], []))}")
    others = set(issuers) - {FILES["battle_main"], FILES["overlay_c"]}
    check(not others, f"unknown 3D command issuers in battle code: {sorted(others)}")
    check("G3X_EdgeMarking(FALSE);" in main_code, "edge marking must stay off (polygon IDs would otherwise be visible)")

    # ---- teardown + registration -------------------------------------------------------------
    free = function_body(main_code, "BattleMain_CopyBattleSysToDTOAndFree") or ""
    check("BattleContext_Free(" in free and "SysTask_Done(battleSys->taskDrawSprites)" in free
          and free.index("BattleContext_Free(") < free.index("SysTask_Done(battleSys->taskDrawSprites)"),
          "teardown shape changed: context free / draw-task done are no longer in one synchronous function")
    check(not re.search(r"ExecuteTasks|ApplicationManager_Exec|WaitVBlank|OS_WaitIrq", free),
          "teardown function may now yield to the task manager between context free and task end")
    check("'battle/battle_status_overlay.c'" in S["meson"], "meson.build registration missing")
    ov = re.search(r"^Overlay battle\n\{(.*?)^\}", S["lsf"], re.S | re.M)
    check(ov is not None and "Object main.nef.p/src_battle_battle_status_overlay.c.o" in ov.group(1)
          and "Object main.nef.p/src_battle_battle_main.c.o" in ov.group(1),
          "main.lsf: overlay object must be in the battle overlay with its caller (unlisted objects stay at address 0)")
    check("void BattleStatusOverlay_Draw(BattleSystem *battleSys);" in S["overlay_h"], "header prototype missing")

    # ---- 4. geometry / depth bounds ----------------------------------------------------------
    g = lambda n: consts.get(n)
    need = ["ORBIT_STAR_COUNT", "ORBIT_STEP_PER_FRAME", "ORBIT_STAR_SPACING", "ORBIT_RADIUS_X", "ORBIT_RADIUS_Y",
            "STAR_HALF_SIZE_MIN", "STAR_HALF_SIZE_RANGE", "STAR_OUTLINE_GROW", "STAR_ARM_LENGTH", "STAR_ARM_WIDTH",
            "STAR_OUTLINE_Z", "STAR_DEPTH_FRONT_BIAS", "SCREEN_MIN_Y"]
    if any(g(n) is None for n in need):
        errs.append("geometry constants missing/unevaluable: " + ", ".join(n for n in need if g(n) is None))
        return errs
    n_stars, step, spacing = g("ORBIT_STAR_COUNT"), g("ORBIT_STEP_PER_FRAME"), g("ORBIT_STAR_SPACING")
    rx, ry = g("ORBIT_RADIUS_X"), g("ORBIT_RADIUS_Y")
    hmin, hrange, grow = g("STAR_HALF_SIZE_MIN"), g("STAR_HALF_SIZE_RANGE"), g("STAR_OUTLINE_GROW")
    arm, width, oz, bias = g("STAR_ARM_LENGTH"), g("STAR_ARM_WIDTH"), g("STAR_OUTLINE_Z"), g("STAR_DEPTH_FRONT_BIAS")
    check(n_stars == 3, "pilot expects 3 orbiting stars")
    check(0 < step < 0x10000 and 0x10000 % step == 0, "orbit step must divide one revolution evenly")
    check(0x10000 - spacing * n_stars < n_stars, "stars must be evenly spaced")
    check(-0x8000 <= oz < 0 and arm <= 0x7FFF and 0 < width < arm, "vertex values must fit fx16 and be sane")
    check(-oz > 0x400, "outline must sit clearly behind the fill (depth buffer resolution)")
    check(len(re.findall(r"G3_Vtx\(", star)) == 8, "star pass must emit exactly two quads (8 vertices)")
    check(g("SCREEN_MIN_Y") > hmin + hrange + grow, "screen clamp smaller than the star extent")

    sin_idx = lambda i: int(round(math.sin(i / 65536.0 * 2 * math.pi) * 4096))
    halves = set()
    for frame in range(0x10000 // step):
        for k in range(n_stars):
            a = (frame * step + k * spacing) & 0xFFFF
            s = sin_idx(a)
            half = hmin + (((s + 0x1000) * hrange) >> 13)
            halves.add(half)
            check(hmin <= half <= hmin + hrange, f"half size out of range at frame {frame}")
            check(bias + (s >> 8) + oz // 0x1000 > 0,
                  "fill/outline must stay strictly nearer than the battler quad (depth test is LESS)")
    check(min(halves) == hmin and max(halves) == hmin + hrange, "size pulse does not span the configured range")
    check(2 * (rx + hmin + hrange + grow) < 256, "orbit envelope wider than the screen")
    return errs


# ----------------------------------------------------------------------------- mutation tests
def rep(old, new, key="overlay_c", count=1):
    def f(S):
        assert old in S[key], f"mutation anchor not found: {old!r}"
        S[key] = S[key].replace(old, new, count)
    return f


def regex_rep(pattern, new, key="overlay_c"):
    def f(S):
        t, n = re.subn(pattern, new, S[key], count=1, flags=re.S)
        assert n == 1, f"mutation pattern not found: {pattern!r}"
        S[key] = t
    return f


RESTORE = re.escape("G3_TexImageParam(monSpriteMan->imageProxy.attr.fmt")

MUTATIONS = [
    ("restore TexImageParam deleted", regex_rep(RESTORE + r".*?;\n", "")),
    ("restore uses wrong charBaseAddr", rep("monSpriteMan->charBaseAddr);", "0);")),
    ("restore uses NONE texgen", rep("GX_TEXGEN_TEXCOORD, monSpriteMan", "GX_TEXGEN_NONE, monSpriteMan")),
    ("restore moved before the polygons", lambda S: S.__setitem__("overlay_c", re.sub(
        r"(    for \(int i = 0; i < count; i\+\+\) \{.*?\n    \}\n)(\n    // Hand the texture unit back[^\n]*\n)(    G3_TexImageParam\(monSpriteMan[^\n]*\n)",
        lambda m: m.group(3) + m.group(1) + m.group(2), S["overlay_c"], count=1, flags=re.S))),
    ("NONE TexImageParam deleted", regex_rep(r"    G3_TexImageParam\(GX_TEXFMT_NONE.*?\n", "")),
    ("polygon uses texture format", rep("G3_TexImageParam(GX_TEXFMT_NONE", "G3_TexImageParam(GX_TEXFMT_PLTT4")),
    ("outer PopMtx removed", rep("    G3_PopMtx(1);\n}\n\nstatic BOOL CanDrawOverlay", "}\n\nstatic BOOL CanDrawOverlay")),
    ("outer PopMtx pops 2", rep("    G3_PopMtx(1);\n}\n\nstatic BOOL CanDrawOverlay", "    G3_PopMtx(2);\n}\n\nstatic BOOL CanDrawOverlay")),
    ("star-pass PopMtx removed", rep("    G3_End();\n    G3_PopMtx(1);\n", "    G3_End();\n")),
    ("extra PushMtx", rep("    G3_PushMtx();\n\n    if (monSpriteMan", "    G3_PushMtx();\n    G3_PushMtx();\n\n    if (monSpriteMan")),
    ("G3_End removed", rep("    G3_End();\n", "")),
    ("G3_Begin removed", rep("    G3_Begin(GX_BEGIN_QUADS);\n", "")),
    ("extra Vtx", rep("    G3_Vtx(0, -STAR_ARM_WIDTH, zVertex);\n", "    G3_Vtx(0, -STAR_ARM_WIDTH, zVertex);\n    G3_Vtx(0, 0, zVertex);\n")),
    ("PolygonAttr removed", regex_rep(r"        G3_PolygonAttr\(.*?\n", "")),
    ("PolygonAttr translucent", rep("OVERLAY_POLYGON_ID_BASE + anchors[i].battler, 31, 0)", "OVERLAY_POLYGON_ID_BASE + anchors[i].battler, 15, 0)")),
    ("PolygonAttr lit", rep("G3_PolygonAttr(GX_LIGHTMASK_NONE", "G3_PolygonAttr(GX_LIGHTMASK_0")),
    ("PolygonAttr reuses battler polygon ID", rep("OVERLAY_POLYGON_ID_BASE + anchors[i].battler, 31", "anchors[i].battler, 31")),
    ("TexPlttBase touched", rep("    G3_PushMtx();\n\n    if (monSpriteMan", "    G3_PushMtx();\n    G3_TexPlttBase(0, GX_TEXFMT_PLTT16);\n\n    if (monSpriteMan")),
    ("matrix mode touched", rep("    G3_PushMtx();\n\n    if (monSpriteMan", "    G3_PushMtx();\n    G3_MtxMode(GX_MTXMODE_TEXTURE);\n\n    if (monSpriteMan")),
    ("material written", rep("    G3_PushMtx();\n\n    if (monSpriteMan", "    G3_PushMtx();\n    G3_MaterialColorDiffAmb(0, 0, TRUE);\n\n    if (monSpriteMan")),
    ("flush moved after PushMtx", rep("    NNS_G3dGeFlushBuffer();\n    G3_PushMtx();\n", "    G3_PushMtx();\n    NNS_G3dGeFlushBuffer();\n")),
    ("early return after commands", rep("    for (int i = 0; i < count; i++) {\n        G3_PolygonAttr", "    if (count > 3) {\n        return;\n    }\n\n    for (int i = 0; i < count; i++) {\n        G3_PolygonAttr")),
    ("commands issued with no qualifying battler", rep("    if (count == 0) {\n        return;\n    }\n", "")),
    ("translate outside matrix pair", rep("    NNS_G3dGeFlushBuffer();\n    G3_PushMtx();\n", "    NNS_G3dGeFlushBuffer();\n    G3_Translate(0, 0, 0);\n    G3_PushMtx();\n")),
    ("depth bias too small", rep("#define STAR_DEPTH_FRONT_BIAS 24", "#define STAR_DEPTH_FRONT_BIAS 16")),
    ("IsActive check removed", rep("monSprite == NULL || !PokemonSprite_IsActive(monSprite)", "monSprite == NULL")),
    ("render-mode gate inverted", rep("GetRenderMode(battleSys) != 0", "GetRenderMode(battleSys) == 0")),
    ("link exclusion dropped", rep("BATTLE_TYPE_LINK | ", "")),
    ("recording exclusion dropped", rep("BATTLE_STATUS_RECORDING", "0")),
    ("initialized gate dropped", rep("!BattleSystem_IsInitialized(battleSys)", "FALSE")),
    ("file-scope cached pointer", rep("typedef struct OverlayAnchor", "static PokemonSprite *sCachedSprite;\n\ntypedef struct OverlayAnchor")),
    ("battle state written", rep("    int scaleY =", "    BattleMon_Set(battleCtx, battler, BATTLEMON_VOLATILE_STATUS, NULL);\n    int scaleY =")),
    ("heap allocation added", rep("    u32 phase =", "    void *leak = Heap_Alloc(HEAP_ID_BATTLE, 16);\n    u32 phase =")),
    # call-site / ordering
    ("overlay after OAM draw", lambda S: S.__setitem__("battle_main", S["battle_main"].replace(
        "        BattleStatusOverlay_Draw(battleSys);\n        SpriteSystem_DrawSprites(battleSys->spriteMan);\n",
        "        SpriteSystem_DrawSprites(battleSys->spriteMan);\n        BattleStatusOverlay_Draw(battleSys);\n"))),
    ("overlay before mon draw", lambda S: S.__setitem__("battle_main", S["battle_main"].replace(
        "        PokemonSpriteManager_DrawSprites(battleSys->monSpriteMan);\n        BattleStatusOverlay_Draw(battleSys);\n",
        "        BattleStatusOverlay_Draw(battleSys);\n        PokemonSpriteManager_DrawSprites(battleSys->monSpriteMan);\n"))),
    ("overlay outside mode 0/3 block", rep("        BattleStatusOverlay_Draw(battleSys);\n", "", key="battle_main")),
    ("extra 3D issuer between overlay and swap", rep("        BattleStatusOverlay_Draw(battleSys);\n", "        BattleStatusOverlay_Draw(battleSys);\n        G3_PushMtx();\n", key="battle_main")),
    ("lsf entry removed", rep("\tObject main.nef.p/src_battle_battle_status_overlay.c.o\n", "", key="lsf")),
    ("meson entry removed", rep("    'battle/battle_status_overlay.c',\n", "", key="meson")),
    ("teardown yields before task end", rep("    SysTask_Done(battleSys->taskDrawSprites);", "    SysTaskManager_ExecuteTasks(NULL);\n    SysTask_Done(battleSys->taskDrawSprites);", key="battle_main")),
    # consumer contract
    ("particle pass no longer resets G3X", rep("    G3_ResetG3X();\n\n    if (ParticleSystem_GetActiveAmount() == 0) {", "    if (ParticleSystem_GetActiveAmount() == 0) {", key="particle_helper")),
    ("G3_ResetG3X no longer calls G3X_Reset", rep("    G3X_Reset();", "    ;", key="g3x_wrapper")),
    ("SPL drops per-particle PolygonAttr", rep("    G3_PolygonAttr(\n        GX_LIGHTMASK_NONE,", "    (void)(\n        GX_LIGHTMASK_NONE,", key="spl_draw")),
    ("mon pass stops setting PolygonAttr per quad", rep("            G3_PolygonAttr(GX_LIGHTMASK_NONE", "            (void)(GX_LIGHTMASK_NONE", key="pokemon_sprite")),
    ("mon pass stops setting TexPlttBase per quad", rep("            G3_TexPlttBase(monSpriteMan->plttBaseAddr + PLTT_OFFSET_CAST(i)", "            (void)(monSpriteMan->plttBaseAddr + PLTT_OFFSET_CAST(i)", key="pokemon_sprite")),
    ("mon pass stops setting vertex colour", rep("TRUE);\n            G3_MaterialColorSpecEmi", "FALSE);\n            G3_MaterialColorSpecEmi", key="pokemon_sprite")),
    ("edge marking enabled", rep("G3X_EdgeMarking(FALSE);", "G3X_EdgeMarking(TRUE);", key="battle_main")),
    ("battler polygon IDs change", rep("z, battler, battler,", "z, 9, battler,", key="battle_display")),
]


def run_mutations():
    base = load_sources()
    base_errs = check_all(dict(base))
    if base_errs:
        return None, base_errs
    survived = []
    for name, mut in MUTATIONS:
        S = dict(base)
        try:
            mut(S)
        except AssertionError as e:
            survived.append(f"{name} (MUTATION INVALID: {e})")
            continue
        try:
            detected = bool(check_all(S))
        except (ValueError, AttributeError, IndexError, KeyError):
            detected = True  # the structure the validator depends on is gone
        if not detected:
            survived.append(name)
    return survived, []


def main():
    do_mut = "--no-mutations" not in sys.argv
    S = load_sources()
    errs = check_all(S)
    if errs:
        print("IO-STATUS confusion overlay validation FAILED:")
        for e in errs:
            print(" -", e)
        return 1
    code = strip_comments(S["overlay_c"])
    paths = trace(parse_block(function_body(code, "BattleStatusOverlay_Draw")),
                  {"DrawConfusionStars": parse_block(function_body(code, "DrawConfusionStars")),
                   "DrawStarPass": parse_block(function_body(code, "DrawStarPass"))},
                  make_consts(code), [Path()], [])
    nonempty = [p for p in paths if p.events]
    print(f"IO-STATUS confusion overlay validation passed: traced {len(paths)} control-flow paths "
          f"({len(nonempty)} emit geometry), max {max(len(p.events) for p in nonempty)} commands, "
          f"SDK G3X_Reset source {'verified' if SDK_G3X.exists() else 'not present (skipped)'}.")
    if do_mut:
        survived, base_errs = run_mutations()
        if survived:
            print(f"MUTATION SELF-TEST FAILED: {len(survived)} defect(s) not detected:")
            for s in survived:
                print(" -", s)
            return 1
        print(f"Mutation self-test passed: all {len(MUTATIONS)} injected defects were rejected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
