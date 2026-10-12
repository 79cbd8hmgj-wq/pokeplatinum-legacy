"""Per-move, cross-source candidate matrix for the 33 B9 P1/P2 moves (source-free: derived from committed catalog + feature files).

Evidence bases, in decreasing strength, are kept explicit on every candidate and never merged:
  named_move_particle  Platinum/Diamond/HGSS move-particle whose *name* is known (Platinum file name; DP/HGSS via texture-verified alignment)
  named_source         GBA sprite / Crystal object with a real source name matching the component query
  feature_heuristic    anonymous art (PMD, Ranger 2, cell banks, unverified SPL) ranked by hue/shape - a search aid only
Nothing here is a visual approval.  ``visual_review.status`` is always AWAITING_OWNER_REVIEW.
"""
from __future__ import annotations

import re
from collections import defaultdict

from . import assets as A
from .roles import MOVE_QUERIES

FAMILIES = {   # library -> counting family (GBA libraries carry byte/pixel-identical art, so they count once)
    "emerald": "gba", "firered": "gba", "ruby": "gba", "crystal": "gb_crystal", "platinum": "nds_spl", "diamond": "nds_spl",
    "hgss": "nds_spl", "pmd_sky": "pmd_sky", "ranger2": "ranger2",
}
FAMILY_RANK = {"nds_spl": 0, "gba": 1, "gb_crystal": 2, "pmd_sky": 3, "ranger2": 4}
LIB_RANK = {"platinum": 0, "emerald": 1, "firered": 2, "ruby": 3, "diamond": 4, "hgss": 5, "crystal": 6, "pmd_sky": 7, "ranger2": 8}
GAME = {"platinum": "Pokemon Platinum (this repository)", "diamond": "Pokemon Diamond/Pearl (pokediamond)",
        "hgss": "Pokemon HeartGold/SoulSilver (pokeheartgold)", "emerald": "Pokemon Emerald (pokeemerald)",
        "firered": "Pokemon FireRed/LeafGreen (pokefirered)", "ruby": "Pokemon Ruby/Sapphire (pokeruby)",
        "crystal": "Pokemon Crystal (pokecrystal)", "pmd_sky": "Pokemon Mystery Dungeon: Explorers of Sky (pmd-sky)",
        "ranger2": "Pokemon Ranger: Shadows of Almia (pokeranger2)"}
NAMED_PER_COMPONENT = 3
HEUR_PER_COMPONENT = 2
REUSE_DISCOUNT = 0.9
FEATURE_THRESHOLD = 0.62
MIN_NAME_BACKED = 3         # distinct renderings with a source-backed name (heuristics never count as verified)
MIN_FAMILIES = 3            # source families spanned by all candidates (cross-library)
TILE_BUDGET = 192


def build_assets(catalog: dict, fdoc: dict) -> dict[str, dict]:
    """All convertible DECODED units (+ Platinum-native) with name/alignment, features, and visual-duplicate grouping."""
    units = [u for u in catalog["units"] if u["status"] == "DECODED"] + [u for u in fdoc["platinum_units"] if u["status"] == "DECODED"]
    align = A.spl_alignment(catalog["units"] + fdoc["platinum_units"], fdoc["platinum_order"])
    out = {}
    for u in units:
        o = (u.get("extra") or {}).get("opal_fx")
        if not o or not o.get("convertible"):
            continue
        lib = u["library"]
        name, basis = None, None
        if lib in ("emerald", "firered", "ruby") and u["type"] == "gba_indexed_png":
            name, basis = u["source"].rsplit("/", 1)[-1][:-4], "named_source"
        elif lib == "crystal":
            name, basis = u["id"].rsplit("#", 1)[-1].replace("BATTLE_ANIM_OBJ_", "").lower(), "named_source"
        elif u["id"] in align:
            al = align[u["id"]]
            name = al["name"]
            basis = "named_move_particle" if al["basis"] in ("EXACT_FILENAME", "TEXTURE_VERIFIED") else None
            if basis is None:
                name = None
        feat = fdoc["features"].get(u["id"], {"usable": False})
        out[u["id"]] = {"unit": u, "name": name, "name_basis": basis, "alignment": align.get(u["id"], {}).get("basis"),
                        "features": feat, "family": FAMILIES[lib]}
    # visual duplicate groups: one canonical per rendering (platinum > gba order > diamond > hgss ...)
    groups = defaultdict(list)
    for i, a in out.items():
        groups[a["unit"]["visual_sha256"]].append(i)
    for vs, ids in groups.items():
        ids.sort(key=lambda i: (LIB_RANK[out[i]["unit"]["library"]], i))
        out[ids[0]]["also_in"] = ids[1:]
        out[ids[0]]["names_all"] = sorted({out[i]["name"] for i in ids if out[i]["name_basis"] == "named_move_particle"})
        for i in ids[1:]:
            out[i]["alias_of"] = ids[0]
    return out


def _shape_score(tag: str, f: dict) -> float:
    """Continuous 0..1 closeness to a coarse silhouette class (a search aid, not a classifier)."""
    fill, el, hol, comp = f.get("fill", 0), f.get("elong", 1), f.get("hollow", 0), f.get("components", 1)
    clamp = lambda v: max(0.0, min(1.0, v))                                       # noqa: E731
    if tag == "burst":
        return clamp(1 - abs(fill - 0.4) / 0.5) * clamp(1 - (el - 1) / 3) * (1.0 if hol < 0.5 else 0.5)
    if tag == "streak":
        return clamp((el - 1.2) / 2.0) * clamp(1.2 - fill)
    if tag == "ring":
        return 0.5 + 0.5 * clamp(hol) if hol >= 0.5 else 0.25 * clamp(1 - fill)
    if tag == "orb":
        return clamp((fill - 0.3) / 0.4) * clamp(1.6 - (el - 1) / 1.2)
    if tag == "shard":
        return clamp(1 - abs(el - 2.3) / 2.0) * clamp(1 - abs(fill - 0.5) / 0.5)
    if tag == "specks":
        return clamp((comp - 1) / 5) * clamp(1.1 - fill / 0.6)
    return 0.3


def feature_score(f: dict, spec: dict, ignore_hue: bool = False) -> float:
    """``ignore_hue``: SPL particle textures are untinted intensity masks (the in-game colour comes from the emitter), so hue is meaningless."""
    if not f.get("usable"):
        return 0.0
    want = set(spec["hues"])
    dom = f.get("dominant_hues", [])
    neutral = f.get("neutral")
    if ignore_hue:
        hue = 0.5
    elif dom and dom[0] in want:
        hue = 1.0
    elif len(dom) > 1 and dom[1] in want:
        hue = 0.6
    elif neutral and neutral in want:
        hue = 0.8
    elif not dom and neutral is None:
        hue = 0.3
    else:
        hue = 0.0
    size = 1.0 if 8 <= max(f.get("bw", 0), f.get("bh", 0)) <= 96 else 0.5
    return round(0.45 * hue + 0.45 * _shape_score(spec["shape"], f) + 0.10 * size, 3)


def _quality(a: dict) -> float:
    o = a["unit"]["extra"]["opal_fx"]
    t = o.get("obj_tiles") or 0
    q = 1.0 if t <= TILE_BUDGET else (0.85 if t <= 400 else 0.7)
    return q * (0.9 + 0.1 * min(a["unit"]["frame_count"] or 1, 6) / 6)


def heuristic_scope(a: dict) -> str | None:
    """Anonymous art is searched only inside containers that are *effect-labelled by path*; returns the provenance reason, else None.
    (HGSS cell banks carry no effect/UI label - they are deliberately not searched by hue/shape.)"""
    u = a["unit"]
    lib, src, t = u["library"], u["source"], u["type"]
    if lib == "pmd_sky" and t == "pmd_effect_wan":
        return "pmd_sky effect.bin entry"
    if lib == "ranger2" and t == "nitro_cell_bank" and "/effect/" in src:
        return "ranger2 res/prebuilt/data/**/effect/ package"
    if lib == "diamond" and "wazaeffect" in src:
        return "diamond files/wazaeffect move-effect cell bank"
    if t == "spl_particle_archive" and (src == A.HGSS_MOVE_NARC or src.startswith(A.DIAMOND_MOVE_DIR)):
        return "move-particle archive whose index alignment to a Platinum name is not texture-verified"
    return None


def _fit(a: dict, spec: dict) -> float:
    return feature_score(a["features"], spec["feat"], a["unit"]["type"] == "spl_particle_archive") if a["features"].get("usable") else 0.5


def _match(a: dict, spec: dict, move_slug: str) -> tuple[str, float, dict] | None:
    name = a["name"]
    ev = {}
    if a["name_basis"] == "named_move_particle":
        names = a.get("names_all") or [name]                  # files with pixel-identical textures share one canonical rendering
        hit = [n for n in spec["plat"] if n in names]
        if hit and move_slug not in names:                    # a rendering equal to the same-move file is the native_baseline, not a new candidate
            fit = _fit(a, spec)
            ev = {"native_same_move": False, "particle_name": hit[0], "shape_hue_fit": round(fit, 2)}
            if len(names) > 1:
                ev["textures_shared_with_particles"] = [n for n in names if n != hit[0]]
            return "named_move_particle", (0.9 - 0.02 * spec["plat"].index(hit[0])) * _quality(a) * (0.65 + 0.35 * fit), ev
        return None
    if a["name_basis"] == "named_source":
        if re.search(spec["names"], name):
            fit = _fit(a, spec)
            return "named_source", 0.88 * _quality(a) * (0.65 + 0.35 * fit), {"source_name": name, "shape_hue_fit": round(fit, 2)}
        return None
    if a["alignment"] == "UNVERIFIED_INDEX_ALIGNMENT":
        ev["note"] = "SPL entry aligned by position only (textures differ from the Platinum file at that index): no name-based role"
    scope = heuristic_scope(a)
    if scope is None:
        return None
    s = feature_score(a["features"], spec["feat"], a["unit"]["type"] == "spl_particle_archive")
    if s >= FEATURE_THRESHOLD:
        return "feature_heuristic", s * 0.7 * _quality(a), ev | {"scope": scope, "feature_score": s, "features": {k: a["features"].get(k) for k in ("dominant_hues", "neutral", "fill", "elong", "hollow", "components")}}
    return None


def decode_confidence(u: dict) -> tuple[str, str]:
    """(confidence, runtime_palette_dependency) from DAU1 decode facts."""
    x, t = u.get("extra") or {}, u["type"]
    if t == "gba_indexed_png":
        return "EXACT_INDEXED_PNG", "NO"
    if t == "gb_recipe_object":
        return "EXACT_FROM_ASM_TABLES", "NO"
    if t == "spl_particle_archive":
        return "TEXTURE_EXACT", "NO (texture palettes are embedded in the .spa)"
    if t == "pmd_effect_wan":
        bad, tot = x.get("invalid_metaframes", 0), x.get("metaframes", 0)
        return ("HIGH" if not bad else "PARTIAL"), (f"YES: {bad} of {tot} metaframes select palette rows the file does not define" if bad else "NO")
    if t == "nitro_cell_bank":
        pr = x.get("pairing", "")
        if pr.startswith("stem"):
            return "HIGH", "NO"
        return "MEDIUM_PALETTE_PAIRING_HEURISTIC", f"PAIRING_UNVERIFIED ({pr})"
    if t == "ds_ntft_texture":
        return "HIGH", "NO"
    return "UNKNOWN", "UNKNOWN"


ROUTES = {
    "gba_indexed_png": "dau1_unlock.py convert --unit <id> (indexed PNG -> Opal FX sheet; direct)",
    "gb_recipe_object": "dau1_unlock.py convert --unit <id> (recipe-built frames -> Opal FX sheet)",
    "spl_particle_archive": "texture frame(s) -> Opal FX sheet via dau1 convert (static quad art); motion needs a hand-authored macro using emitter_recipe.json (no runtime interpreter)",
    "pmd_effect_wan": "dau1_unlock.py convert --unit <id> (effect-WAN frames; palette rows beyond the file are unresolved)",
    "nitro_cell_bank": "dau1_unlock.py convert --unit <id> (rendered OAM cells -> Opal FX sheet)",
    "ds_ntft_texture": "dau1_unlock.py convert --unit <id> (A5I3 texture; translucency is dropped by OBJ binary alpha)",
}


def candidate_record(a: dict, basis: str, score: float, ev: dict, component: str, rank: int, board: str, family_name: str) -> dict:
    u = a["unit"]
    o = u["extra"]["opal_fx"]
    conf, rtp = decode_confidence(u)
    lib = u["library"]
    member = u["id"].split("#", 1)[1] if "#" in u["id"] else None
    return {
        "asset_id": u["id"], "component": component, "rank_in_component": rank, "evidence_basis": basis, "score": round(score, 3),
        "evidence": ev, "source_game": GAME[lib], "library": lib, "family": family_name, "source_revision": None,   # filled by caller from catalog sources
        "archive_path": u["source"], "archive_member": member,
        "frame_or_cell": {"spl_particle_archive": "decoded visible textures", "nitro_cell_bank": "cells 0..n-1", "pmd_effect_wan": "metaframes",
                          "gba_indexed_png": "frame 0", "gb_recipe_object": "frameset frames"}.get(u["type"], "frame 0"),
        "sha256": u["sha256"], "visual_sha256": u["visual_sha256"], "decode_confidence": conf,
        "role_candidates": [{"role": component, "basis": basis}],
        "preview_path": board, "dimensions": u["dimensions"], "palette_count": o.get("colours"), "tile_count": o.get("obj_tiles"),
        "oam_cost": o.get("max_oams_per_cell"), "animation_frames": u["frame_count"], "conversion_route": ROUTES.get(u["type"], "unknown"),
        "runtime_palette_dependency": rtp,
        "redistribution_status": ("IN_REPOSITORY_ALREADY; rights unverified (same status as existing res/)" if lib == "platinum"
                                  else "UNVERIFIED; do not commit pixels; local preview only"),
        "budget_notes": ([f"{o['obj_tiles']} est. OBJ tiles > {TILE_BUDGET}/sheet (needs splitting)"] if (o.get("obj_tiles") or 0) > TILE_BUDGET else [])
                        + ([f"{o['colours']} colours > 15 (lossy fold)"] if (o.get("colours") or 0) > 15 else [])
                        + ([f"{o['translucent_pixels_dropped']} translucent px dropped"] if (o.get("translucent_pixels_dropped") or 0) > 200 else []),
        "also_in": a.get("also_in", []),
        "visual_review": {"status": "AWAITING_OWNER_REVIEW", "owner_decision": None, "model_observation": None},
    }


def build_matrix(catalog: dict, fdoc: dict, binding: dict, observations: dict | None = None) -> dict:
    assets = build_assets(catalog, fdoc)
    src_rev = {s["library"]: s.get("commit") for s in catalog["sources"]}
    src_rev["platinum"] = fdoc.get("platinum_revision")
    canon = {i: a for i, a in assets.items() if "alias_of" not in a}
    plat_by_name = {u["source"].rsplit("/", 1)[-1][:-4]: u for u in fdoc["platinum_units"] if "/pokeballs/" not in u["source"]}

    def native_status(slug_: str) -> dict:
        u = plat_by_name.get(slug_)
        if u is None:
            return {"file": None, "status": "NO_PLATINUM_PARTICLE_FILE", "note": "this move has no .spa in res/graphics/battle/particles (its vanilla animation is script/sprite based)"}
        if u["status"] == "DECODED":
            return {"file": u["source"], "status": "DECODED", "emitters": (u.get("extra") or {}).get("emitters")}
        return {"file": u["source"], "status": "EMPTY_OR_UNDECODABLE", "emitters": (u.get("extra") or {}).get("emitters"),
                "textures": (u.get("extra") or {}).get("textures"), "note": u.get("error_reason")}
    moves_out = []
    heur_use = defaultdict(int)
    for row in binding["moves"]:
        if row["tier"] == "P0_early_frequent":
            continue
        q = MOVE_QUERIES[row["move"]]
        mslug = row["slug"]
        board = f"boards/{'P1' if row['tier'].startswith('P1') else 'P2'}_{mslug}.png"
        comps, cand_list = {}, []
        native_id = next((i for i, a in assets.items() if a["name_basis"] == "named_move_particle" and a["name"] == mslug
                          and a["unit"]["library"] == "platinum"), None)     # the exact Platinum file, even when its textures alias another
        if native_id is not None:
            nev = {"native_same_move": True, "particle_name": mslug}
            if "alias_of" in assets[native_id]:
                nev["textures_identical_to"] = assets[native_id]["alias_of"]
            rec = candidate_record(assets[native_id], "named_move_particle", 1.0, nev,
                                   "native_baseline", 0, board, assets[native_id]["family"])
            rec["source_revision"] = src_rev.get(assets[native_id]["unit"]["library"])
            cand_list.append(rec)
            comps["native_baseline"] = {"considered": 1, "picked": [native_id]}
        for comp, spec in q.items():
            named, heur = [], []
            for i, a in canon.items():
                m = _match(a, spec, mslug)
                if not m:
                    continue
                basis, sc, ev = m
                if basis == "feature_heuristic":
                    sc *= REUSE_DISCOUNT ** heur_use[i]
                    heur.append((sc, basis, ev, i))
                else:
                    named.append((sc, basis, ev, i))
            order = lambda t: (-t[0], FAMILY_RANK[canon[t[3]]["family"]], t[3])      # noqa: E731
            named.sort(key=order)
            heur.sort(key=order)
            def diverse(lst, cap):
                picks, seen = [], set()
                for t in lst:                                    # one per family first (cross-library), then best remaining
                    f = canon[t[3]]["family"]
                    if f not in seen and len(picks) < cap:
                        picks.append(t); seen.add(f)
                for t in lst:
                    if len(picks) >= cap:
                        break
                    if t not in picks:
                        picks.append(t)
                return sorted(picks, key=order)
            picks = diverse(named, NAMED_PER_COMPONENT) + diverse(heur, HEUR_PER_COMPONENT)
            comps[comp] = {"considered_named": len(named), "considered_heuristic": len(heur), "picked": [t[3] for t in picks]}
            for rank, (sc, basis, ev, i) in enumerate(picks, 1):
                rec = candidate_record(canon[i], basis, sc, ev, comp, rank, board, canon[i]["family"])
                rec["source_revision"] = src_rev.get(canon[i]["unit"]["library"])
                cand_list.append(rec)
                if basis == "feature_heuristic":
                    heur_use[i] += 1
        chosen = {n: r for n, r in enumerate(cand_list)}
        cands = sorted(chosen.values(), key=lambda r: (r["component"] != "native_baseline", r["component"], r["rank_in_component"], r["asset_id"]))
        for n, r in enumerate(cands):
            r["board_cell_index"] = n
            ob = (observations or {}).get(row["move"], {}).get(r["asset_id"])
            if ob:
                r["visual_review"]["model_observation"] = ob
        fam_all = sorted({r["family"] for r in cands})
        fam_verified = sorted({r["family"] for r in cands if r["evidence_basis"] != "feature_heuristic"})
        n_named = len({r["visual_sha256"] for r in cands if r["evidence_basis"] != "feature_heuristic"})
        native = [r["asset_id"] for r in cands if r["evidence"].get("native_same_move")]
        status = "READY_FOR_OWNER_REVIEW" if (n_named >= MIN_NAME_BACKED and len(fam_all) >= MIN_FAMILIES) else "INSUFFICIENT_VERIFIED_CANDIDATES"
        reasons = []
        if status != "READY_FOR_OWNER_REVIEW":
            reasons.append(f"{n_named} distinct name-backed rendering(s) (need {MIN_NAME_BACKED}) across {len(fam_all)} famil(ies) (need {MIN_FAMILIES}); "
                           f"name-backed families: {', '.join(fam_verified) or 'none'}")
        if not native:
            reasons.append(f"no usable same-move Platinum particle: {native_status(mslug)['status']}")
        moves_out.append({
            "move": row["move"], "tier": row["tier"], "slug": mslug, "template": row["template"], "visual_intent": row["visual_intent"],
            "anim_script": row["anim_script"], "native_platinum_particle": native_status(mslug), "board": board, "status": status, "status_reasons": reasons,
            "families_all": fam_all, "families_name_backed": fam_verified, "name_backed_renderings": n_named, "candidate_count": len(cands),
            "components": comps, "candidates": cands,
            "visual_decision": "AWAITING_OWNER_REVIEW",
        })
    summary = {
        "moves": len(moves_out), "p1": sum(1 for m in moves_out if m["tier"].startswith("P1")), "p2": sum(1 for m in moves_out if m["tier"].startswith("P2")),
        "ready_for_owner_review": sum(1 for m in moves_out if m["status"] == "READY_FOR_OWNER_REVIEW"),
        "insufficient_verified_candidates": [m["move"] for m in moves_out if m["status"] != "READY_FOR_OWNER_REVIEW"],
        "candidate_references": sum(m["candidate_count"] for m in moves_out),
        "distinct_assets": len({r["asset_id"] for m in moves_out for r in m["candidates"]}),
        "by_basis": {b: sum(1 for m in moves_out for r in m["candidates"] if r["evidence_basis"] == b)
                     for b in ("named_move_particle", "named_source", "feature_heuristic")},
        "by_family": {f: sum(1 for m in moves_out for r in m["candidates"] if r["family"] == f)
                      for f in sorted({r["family"] for m in moves_out for r in m["candidates"]})},
        "moves_with_3plus_families": sum(1 for m in moves_out if len(m["families_all"]) >= 3),
        "pool_assets_considered": len(canon), "pool_alias_duplicates_collapsed": len(assets) - len(canon),
    }
    return {"schema_version": 1, "generated_by": "tools/visual_overhaul/dau2_curate.py matrix",
            "policy": {"min_name_backed_renderings": MIN_NAME_BACKED, "min_families": MIN_FAMILIES, "named_per_component": NAMED_PER_COMPONENT, "heuristic_per_component": HEUR_PER_COMPONENT, "feature_threshold": FEATURE_THRESHOLD,
                       "heuristics_never_approve": True},
            "summary": summary, "moves": moves_out}
