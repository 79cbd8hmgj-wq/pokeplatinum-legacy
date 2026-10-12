"""Resolve + validate the provisional P1/P2 recipes and compute their costs.  Source-free apart from Platinum's own .spa files in res/.

Budgets enforced (same policy caps as ``opal_cue_trace.py``): <= 2 concurrent sprite managers (one OBJ palette each), <= 400 concurrent OBJ char
tiles, <= 40 concurrent OAM entries, <= 192 tiles in one NEW sheet, FX lifetime <= 180 frames.  Cadence: total frames <= native + 12 (else flagged).
All costs are STATIC ESTIMATES from catalog/provenance/replay numbers - not measurements - and every selection is PROVISIONAL until built and
run in an emulator.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

from . import candidates as C
from . import emitter_study as ES
from . import spl_emitter as E
from . import spl_sim as S
from .recipes_data import RECIPES

MAX_MANAGERS, MAX_TILES, MAX_OAM, MAX_NEW_SHEET_TILES, MAX_LIFETIME, CADENCE_SLACK = 2, 400, 40, 192, 180, 12
H_FLOOR = 8                       # budgeting assumption: the native hit lands no earlier than frame 8 (task durations are unknown lower bounds)
DEFAULT_OAM = 4                   # per Opal FX sprite, the conservative bound used by opal_budget_report/opal_cue_trace
REPLAY_FRAMES, REPLAY_SEED = 120, 0x2B7E1516
WEAK = ("WRONG_ON_SIGHT", "ILLEGIBLE_OR_TOO_SMALL")
STATUS = "PROVISIONAL_UNTIL_RUNTIME_VERIFIED"


class RecipeError(Exception):
    pass


def installed_sheets(root: Path) -> dict:
    out = {}
    for p in sorted((root / "docs/visual_overhaul/opal_installed_fx").glob("*.provenance.json")):
        d = json.loads(p.read_text())
        out[d["name"]] = {"obj_tiles": d["obj_tiles"], "variants": sorted((d.get("palette_variants_rgb555") or {}).keys()),
                          "sequences": {s["name"]: s["total_delay"] for s in d["sequences"]},
                          "donor_sources": {k: {"path": v.get("path"), "sha256": v.get("sha256")} for k, v in (d.get("donor_sources") or {}).items() if isinstance(v, dict) and "path" in v}}
    return out


def anchors(nat: dict) -> dict:
    em = nat.get("emitters") or []
    fd = nat.get("first_defender_emitter_frame_lb")
    h_lb = fd if fd is not None else (max((e["frame_lb"] for e in em), default=None))
    if h_lb is None:
        h_lb = (nat.get("native_duration_lb_frames") or 0) // 2
    return {"L": 0, "H_lb": h_lb, "H": max(h_lb, H_FLOOR), "native_lb": nat.get("native_duration_lb_frames") or 0}


def replay_cost(root: Path, spa: str, indices, cache: dict) -> dict:
    key = (spa, tuple(indices) if indices is not None else None)
    if key in cache:
        return cache[key]
    f = root / "res/graphics/battle/particles" / f"{spa}.spa"
    if not f.exists():
        raise RecipeError(f"particle archive {spa}.spa not found")
    data = f.read_bytes()
    sp = E.parse_emitters(data)
    want = [e.index for e in sp.emitters] if not indices else sorted(set(indices))
    missing = [i for i in want if i not in [e.index for e in sp.emitters]]
    if missing:
        raise RecipeError(f"{spa}.spa has no emitter(s) {missing}")
    rp = S.replay(sp, REPLAY_FRAMES, REPLAY_SEED, only=want)
    v = ES.texture_vram(data)
    active = max((i + 1 for i, n in enumerate(rp.per_frame_counts) if n), default=0)
    out = {"spa": spa, "emitters": want, "emitters_in_archive": sp.emitter_count, "active_frames": active, "peak_live_particles": max(rp.per_frame_counts) if rp.per_frame_counts else 0,
           "gx_quads_peak": max(rp.per_frame_counts) if rp.per_frame_counts else 0, "texture_vram_bytes": v["texture_vram_bytes"], "palette_vram_bytes": v["palette_vram_bytes"],
           "basis": f"offline replay of {REPLAY_FRAMES} frames, seed {REPLAY_SEED:#x} (static estimate, not a measurement)"}
    cache[key] = out
    return out


def resolve_cell(ref, move: dict, assets: dict, obs_by_asset: dict, src_rev: dict, obs_by_move: dict | None = None):
    """-> candidate-like record for a board cell (int) or a full asset id (str)."""
    if isinstance(ref, int):
        rec = next((r for r in move["candidates"] if r["board_cell_index"] == ref), None)
        if rec is None:
            raise RecipeError(f"{move['move']}: board cell {ref} does not exist")
        aid = rec["asset_id"]
    else:
        aid = ref
        if aid not in assets:
            raise RecipeError(f"{move['move']}: unknown asset id {aid}")
        a = assets[aid]
        rec = C.candidate_record(a, "recipe_reference", 0.0, {}, "recipe", 0, "", a["family"])
        rec["source_revision"] = src_rev.get(a["unit"]["library"])
    ob = (obs_by_move or {}).get(move["move"], {}).get(aid)           # judgements are move-specific: the same sprite can be right for one move and wrong for another
    if ob is None:
        others = [o for o in (obs_by_asset.get(aid) or []) if o["status"] not in WEAK]
        ob = None if others else next(iter(obs_by_asset.get(aid) or []), None)       # cross-move reference: only reject when EVERY judgement was weak
    if ob and ob["status"] in WEAK:
        raise RecipeError(f"{move['move']}: {aid} was judged {ob['status']} ({ob['note']}); a recipe may not select it")
    return rec


def at_frame(at, A) -> int:
    a, off = at
    return max(0, A["L"] + off if a == "L" else A["H"] + off)


def part_row(p, A, move, sheets, assets, obs, src_rev, root, cache, ctx_obs_by_move=None) -> dict:
    row = {"role": p["role"], "kind": p["kind"], "note": p.get("note", "")}
    if p["kind"] == "design_note":
        row.update(title=p["title"])
        return row
    if p["kind"] == "native_keep":
        row.update(emitters=p["emitters"])
        return row
    start, ln = at_frame(p["at"], A), p.get("len", 0)
    row.update(at={"anchor": p["at"][0], "offset": p["at"][1]}, start_frame=start, len_frames=ln, end_frame=start + ln, macro=p.get("macro"), copies=p.get("n", 1))
    if p["kind"] == "native_borrow":
        cost = replay_cost(root, p["spa"], p.get("emitters"), cache)
        row.update(spa=p["spa"], len_frames=min(cost["active_frames"], MAX_LIFETIME), end_frame=start + min(cost["active_frames"], MAX_LIFETIME), cost=cost,
                   provenance={"source_game": "Pokemon Platinum (this repository)", "archive_path": f"res/graphics/battle/particles/{p['spa']}.spa", "licence": "in repository; rights unverified"})
    elif p["kind"] == "sheet":
        sh = sheets.get(p["sheet"])
        if sh is None:
            raise RecipeError(f"{move['move']}: installed sheet {p['sheet']} does not exist")
        if p["seq"] not in sh["sequences"]:
            raise RecipeError(f"{move['move']}: sheet {p['sheet']} has no sequence {p['seq']} (has {sorted(sh['sequences'])})")
        if p.get("variant") and p["variant"] not in sh["variants"]:
            raise RecipeError(f"{move['move']}: sheet {p['sheet']} has no palette variant {p['variant']} (has {sh['variants']})")
        row.update(sheet=p["sheet"], seq=p["seq"], palette_variant=p.get("variant"), sequence_total_delay=sh["sequences"][p["seq"]], sheet_obj_tiles=sh["obj_tiles"],
                   provenance={"installed_sheet": p["sheet"], "provenance_file": f"docs/visual_overhaul/opal_installed_fx/{p['sheet']}.provenance.json", "donor_sources": sh["donor_sources"]})
    elif p["kind"] == "donor":
        recs = [resolve_cell(c, move, assets, obs, src_rev, ctx_obs_by_move) for c in p["cells"]]
        row.update(cells=[{"asset_id": r["asset_id"], "board_cell": r.get("board_cell_index") if r["evidence_basis"] != "recipe_reference" else None, "source_game": r["source_game"],
                           "source_revision": r["source_revision"], "archive_path": r["archive_path"], "archive_member": r["archive_member"], "sha256": r["sha256"],
                           "decode_confidence": r["decode_confidence"], "runtime_palette_dependency": r["runtime_palette_dependency"], "tile_count": r["tile_count"],
                           "palette_count": r["palette_count"], "oam_cost": r["oam_cost"], "animation_frames": r["animation_frames"], "conversion_route": r["conversion_route"],
                           "redistribution_status": r["redistribution_status"]} for r in recs], tint=p.get("tint"))
    return row


def build_recipe(variant, key, move, A, nat, ctx) -> dict:
    sheets, assets, obs, src_rev, root, cache, obs_by_move = ctx
    parts = [part_row(p, A, move, sheets, assets, obs, src_rev, root, cache, obs_by_move) for p in variant["parts"]]
    errs, notes = [], []
    # ---- sprite managers / tiles / OAM by frame
    groups = defaultdict(lambda: {"tiles": 0, "start": 10 ** 9, "end": -1, "cells": {}, "kind": None})
    for r in parts:
        if r["kind"] == "sheet":
            g = groups[r["sheet"]]
            g["tiles"], g["kind"] = r["sheet_obj_tiles"], "installed"
        elif r["kind"] == "donor":
            g = groups["(new donor sheet)"]
            g["kind"] = "new"
            for c in r["cells"]:
                g["cells"][c["asset_id"]] = c
            g["tiles"] = sum(c["tile_count"] or 0 for c in g["cells"].values())
        else:
            continue
        g["start"], g["end"] = min(g["start"], r["start_frame"]), max(g["end"], r["end_frame"])
    horizon = max([r.get("end_frame", 0) for r in parts] + [A["native_lb"], 1]) + 1
    mgr_peak = tile_peak = oam_peak = 0
    for f in range(horizon):
        live = [g for g in groups.values() if g["start"] <= f < g["end"]]
        mgr_peak, tile_peak = max(mgr_peak, len(live)), max(tile_peak, sum(g["tiles"] for g in live))
        oam = 0
        for r in parts:
            if r["kind"] in ("sheet", "donor") and r["start_frame"] <= f < r["end_frame"]:
                per = DEFAULT_OAM if r["kind"] == "sheet" else max([c["oam_cost"] or DEFAULT_OAM for c in r["cells"]])
                oam += per * r["copies"]
        oam_peak = max(oam_peak, oam)
    new = groups.get("(new donor sheet)")
    if mgr_peak > MAX_MANAGERS:
        errs.append(f"{mgr_peak} concurrent sprite managers (> {MAX_MANAGERS}); sequence the sheets (OpalSheetEnd before the next OpalSheetBegin)")
    if tile_peak > MAX_TILES:
        errs.append(f"{tile_peak} concurrent OBJ tiles (> {MAX_TILES})")
    if oam_peak > MAX_OAM:
        errs.append(f"{oam_peak} concurrent OAM entries (> {MAX_OAM})")
    if new and new["tiles"] > MAX_NEW_SHEET_TILES:
        errs.append(f"new donor sheet needs {new['tiles']} tiles (> {MAX_NEW_SHEET_TILES})")
    for r in parts:
        if r["kind"] in ("sheet", "donor") and r["len_frames"] > MAX_LIFETIME:
            errs.append(f"{r['role']} part lasts {r['len_frames']} frames (> {MAX_LIFETIME})")
    # ---- native cost
    keep = next(p for p in parts if p["kind"] == "native_keep")
    script_em = {e["index"] for e in (nat.get("emitters") or [])}
    if not set(keep["emitters"]) <= script_em:
        errs.append(f"native emitters {sorted(set(keep['emitters']) - script_em)} are not created by the native script (script creates {sorted(script_em)})")
    native = {"emitters_kept": keep["emitters"], "spa": nat.get("spa")}
    if nat.get("spa") and keep["emitters"]:
        native.update(replay_cost(root, nat["spa"], keep["emitters"], cache))
    elif not nat.get("spa"):
        native["note"] = "native script loads no particle archive (sprite/battler based)"
    borrows = [r for r in parts if r["kind"] == "native_borrow"]
    if len(borrows) > 1:
        errs.append("more than one borrowed particle archive (only a second particle resource slot is assumed free)")
    gx_peak = (native.get("peak_live_particles") or 0) + sum(b["cost"]["peak_live_particles"] for b in borrows)
    vram = (native.get("texture_vram_bytes") or 0) + sum(b["cost"]["texture_vram_bytes"] for b in borrows)
    pal = (native.get("palette_vram_bytes") or 0) + sum(b["cost"]["palette_vram_bytes"] for b in borrows)
    # ---- timing
    end = max([r.get("end_frame", 0) for r in parts] + [0])
    total = max(end, A["native_lb"])
    delta = total - A["native_lb"]
    if delta > CADENCE_SLACK:
        if A["native_lb"] >= 30:
            notes.append(f"CADENCE: extends the native lower-bound duration by {delta} frames (> {CADENCE_SLACK}); needs a payoff argument or a cut")
        else:
            notes.append(f"cadence unverifiable: the native lower bound is only {A['native_lb']} frames (task durations unknown), so +{delta} cannot be judged without a runtime measurement")
    for b in borrows:
        if b["cost"]["peak_live_particles"] > 400:
            notes.append(f"borrowed {b['spa']}.spa peaks at {b['cost']['peak_live_particles']} quads with ALL its emitters: select a subset at implementation (DS vertex RAM holds ~{ES.DS_QUAD_LIMIT} quads)")
    # ---- donor / compatibility
    cells = list(new["cells"].values()) if new else []
    colours_ub = sum(c["palette_count"] or 0 for c in cells)
    pal_dep = sorted({c["runtime_palette_dependency"].split(":")[0].split(" (")[0] for c in cells if not c["runtime_palette_dependency"].startswith("NO")})
    macros = sorted({(r["macro"] or "").split(" ")[0] for r in parts if r.get("macro")})
    variants = sorted({f"{r['sheet']}:{r['palette_variant']}" for r in parts if r["kind"] == "sheet" and r.get("palette_variant")})
    need_variant = [r["note"] for r in parts if "palette variant" in r.get("note", "") and "needs" in r.get("note", "")]
    sheet_names = sorted({r["sheet"] for r in parts if r["kind"] == "sheet"})
    return {
        "key": key, "name": variant["name"], "strategy": variant["strategy"], "summary": variant["summary"], "why": variant["why"],
        "status": STATUS, "runtime_verified": False, "visual_decision": "AWAITING_OWNER_REVIEW",
        "parts": parts,
        "timing": {"fps": 60, "anchors": {"L": 0, "H_lower_bound": A["H_lb"], "H_budget": A["H"]}, "native_duration_lower_bound": A["native_lb"], "estimated_total_frames": total,
                   "delta_vs_native_frames": delta, "basis": "script-delay lower bounds + design offsets; task durations unknown (counted 0); ordering/budget only"},
        "compatibility": {
            "uses_native_emitters": bool(keep["emitters"]), "native_borrow": [b["spa"] for b in borrows], "installed_sheets_reused": sheet_names, "palette_variants_used": variants,
            "new_donor_sheet": ({"name": f"opal_b9p_{move['slug']}", "tiles": new["tiles"], "colours_upper_bound": colours_ub, "palette_fold_required": colours_ub > 15,
                                 "cells": [c["asset_id"] for c in cells]} if new else None),
            "needs_new_palette_variant": need_variant, "macros": macros, "needs_new_macro": False, "runtime_palette_dependency": pal_dep or ["none"],
            "decode_confidence": sorted({c["decode_confidence"] for c in cells}) or ["n/a (no new donor art)"],
            "conversion": "dau1_unlock.py convert --unit <id> per donor cell -> opal_fx/build_opal_fx_sheet.py (as P0)", "contest_branch": "unchanged (only the non-contest battle path is edited, as in P0)",
            "licence": "donor art licence UNVERIFIED: new sheets/previews stay local until the owner clears release", "pipeline": "same installer as B2/B9 (res/graphics/battle/moves NARC); not run in DAU2"},
        "cost": {"new_obj_tiles": new["tiles"] if new else 0, "new_char_bytes_est": (new["tiles"] * 32 if new else 0), "concurrent_sprite_managers_peak": mgr_peak,
                 "concurrent_obj_tiles_peak": tile_peak, "concurrent_oam_peak": oam_peak, "gx_particle_quads_peak_est": gx_peak, "particle_texture_vram_bytes_est": vram,
                 "particle_palette_vram_bytes_est": pal, "native": native, "limits": {"managers": MAX_MANAGERS, "obj_tiles": MAX_TILES, "oam": MAX_OAM, "gx_quads": ES.DS_QUAD_LIMIT},
                 "basis": "static estimates (catalog tile/OAM numbers, provenance, offline replay); not measurements"},
        "violations": errs, "notes": notes}


def build(root: Path, matrix: dict, binding: dict, catalog: dict, fdoc: dict, obs_doc: dict, labels=None) -> dict:
    sheets = installed_sheets(root)
    assets = C.build_assets(catalog, fdoc, labels)
    src_rev = {s["library"]: s.get("commit") for s in catalog["sources"]}
    src_rev["platinum"] = fdoc.get("platinum_revision")
    obs_by_move = obs_doc.get("observations") or {}
    obs: dict = {}
    for mv, d in obs_by_move.items():
        for aid, o in d.items():
            obs.setdefault(aid, []).append(o)
    cache: dict = {}
    out, problems = [], []
    mmap = {m["move"]: m for m in matrix["moves"]}
    for mv in matrix["moves"]:
        name = mv["move"]
        spec = RECIPES[name]
        nat = (binding.get("native_scripts") or {}).get(mv["slug"]) or {}
        A = anchors(nat)
        ctx = (sheets, assets, obs, src_rev, root, cache, obs_by_move)
        rec = {"move": name, "tier": mv["tier"], "slug": mv["slug"], "template": mv["template"], "visual_intent": mv["visual_intent"], "anim_script": mv["anim_script"],
               "native": {"spa": nat.get("spa"), "emitters": nat.get("emitters"), "duration_lower_bound_frames": nat.get("native_duration_lb_frames"),
                          "sprite_resources": nat.get("sprite_resources"), "existing_opal_cues": nat.get("opal_cues"), "script_branches": nat.get("branches")},
               "anchors": A, "status": STATUS, "runtime_verified": False}
        try:
            rec["primary"] = build_recipe(spec["primary"], "primary", mv, A, nat, ctx)
            rec["alternatives"] = [build_recipe(v, f"alt{i}", mv, A, nat, ctx) for i, v in enumerate(spec["alts"], 1)]
        except RecipeError as e:
            problems.append(str(e))
            continue
        if len(rec["alternatives"]) > 2:
            problems.append(f"{name}: more than two alternatives")
        for r in [rec["primary"], *rec["alternatives"]]:
            problems += [f"{name}/{r['key']}: {v}" for v in r["violations"]]
        out.append(rec)
    if problems:
        raise RecipeError("\n".join(problems))
    return {"schema_version": 1, "generated_by": "tools/visual_overhaul/dau2_curate.py recipes", "status": STATUS,
            "policy": {"selections": "PROVISIONAL until built and runtime verified", "caps": {"managers": MAX_MANAGERS, "obj_tiles": MAX_TILES, "oam": MAX_OAM, "new_sheet_tiles": MAX_NEW_SHEET_TILES, "cadence_slack_frames": CADENCE_SLACK},
                       "owner_decisions": ["galleries local-only", "DAU1 excerpts removed from version control", "native Platinum emitters + new Opal sequences together", "no donor-style priority",
                                           "custom composites for Double Team / Hypnosis / Swords Dance", "unidentified HGSS cell banks excluded from automatic selection"]},
            "moves": out}
