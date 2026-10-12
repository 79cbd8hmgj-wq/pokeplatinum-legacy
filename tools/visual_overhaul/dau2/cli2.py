"""Donor-dependent and gate commands: sheets, emitters, check, all."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from dau1.catalog import dump_json_lines
from . import cli as K
from . import manifest as M

SURVEY_PAGE = 100


def _short(uid: str) -> str:
    lib, rest = uid.split(":", 1)
    return f"{lib}:{rest.rsplit('/', 1)[-1]}"


def cmd_sheets(a, root: Path) -> int:
    from dau1 import pipeline
    from dau1.render import save_png
    from . import assets as A, candidates as C, sheets as SH
    ws = a.workspace.resolve()
    matrix = json.loads((a.out / "MOVE_CANDIDATE_MATRIX.json").read_text())
    doc, sheets, _ = pipeline.run(ws, None)
    punits, pframes = A.platinum_units(root)
    frames = {}
    for per in sheets.values():
        frames.update(per)
    frames.update(pframes)
    fdoc = K.load_features(a)
    catalog = doc
    assets = C.build_assets({"units": catalog["units"], "sources": catalog["sources"]}, fdoc)
    canon = sorted((i for i, x in assets.items() if "alias_of" not in x and i in frames),
                   key=lambda i: (C.LIB_RANK[assets[i]["unit"]["library"]], i))

    def frames_of(uid):
        return frames.get(uid) or frames.get(assets.get(uid, {}).get("alias_of", ""), [])

    out = a.build.resolve()
    index = {"schema_version": 1, "note": "thumb_pixel_sha256 hashes raw RGB pixels of each rendered cell (stable across PNG encoders); images are local only",
             "boards": {}, "contact_sheets": {}}
    missing = []
    for mv in matrix["moves"]:
        if any(not frames_of(r["asset_id"]) for r in mv["candidates"]):
            missing += [r["asset_id"] for r in mv["candidates"] if not frames_of(r["asset_id"])]
            continue
        im, cells = SH.board(mv, frames_of, _short)
        save_png(im, out / mv["board"])
        index["boards"][mv["board"]] = {"move": mv["move"], "cells": cells}
    by_lib = {}
    for i in canon:
        by_lib.setdefault(assets[i]["unit"]["library"], []).append(i)
    for lib, ids in sorted(by_lib.items(), key=lambda kv: C.LIB_RANK[kv[0]]):
        for p in range(0, len(ids), SURVEY_PAGE):
            page = ids[p:p + SURVEY_PAGE]
            name = f"contact/{lib}_p{p // SURVEY_PAGE + 1:02d}.png"
            im, cells = SH.survey_page(page, frames_of, _short, f"{C.GAME[lib]}  page {p // SURVEY_PAGE + 1}  ({len(page)} cells; index -> ASSET_INDEX.json)")
            save_png(im, out / name)
            index["contact_sheets"][name] = {"library": lib, "cells": cells}
    _dump_index(index, a.out / "ASSET_INDEX.json")
    from .report import gallery_markdown
    (a.out / "OWNER_REVIEW_GALLERY.md").write_text(gallery_markdown(matrix, index))
    print(f"boards {len(index['boards'])}/33, contact sheets {len(index['contact_sheets'])}, assets indexed "
          f"{sum(len(v['cells']) for v in index['contact_sheets'].values())}; missing frames for {len(set(missing))} candidate(s) -> {out}")
    return 0 if not missing else 1


def _dump_index(index, path):
    import json as j
    lines = ["{"]
    lines.append(f'"boards":{K._enc(index["boards"])},')
    lines.append(f'"note":{j.dumps(index["note"])},')
    lines.append(f'"schema_version":1,')
    lines.append('"contact_sheets":{')
    items = sorted(index["contact_sheets"].items())
    lines.append(",\n".join(f"{j.dumps(k)}:{K._enc(v)}" for k, v in items))
    lines.append("}}")
    path.write_text("\n".join(lines) + "\n")


# ------------------------------------------------------------------------------------------------ emitters
REPRESENTATIVE = [("contact", "headbutt", "Headbutt (P1 heavy_contact)"), ("element", "flame_wheel", "Flame Wheel (P1 fire_contact)"),
                  ("status", "sleep_powder", "Sleep Powder (P2 status_powder)")]
REPLAY_FRAMES = 60
REPLAY_SEED = 0x2B7E1516


def _plausibility(rows_emitters) -> dict:
    n = len(rows_emitters)
    def share(pred):
        return round(sum(1 for h in rows_emitters if pred(h)) / n, 4) if n else None
    return {"emitters": n,
            "air_resistance_is_128_(neutral_drag_in_lib/spl)": share(lambda h: h["air_resistance"] == 128),
            "aspect_is_1.0": share(lambda h: h["aspect_fx16"] == 4096),
            "base_alpha_le_31": share(lambda h: h["base_alpha"] <= 31),
            "user_flags_zero": share(lambda h: h["user_flags"] == 0),
            "emission_count_is_whole_number": share(lambda h: h["emission_count_fx32"] % 4096 == 0),
            "loop_frames_ge_1": share(lambda h: h["loop_frames"] >= 1),
            "emission_interval_ge_1": share(lambda h: h["emission_interval"] >= 1),
            "particle_life_between_1_and_600": share(lambda h: 0 < h["particle_life"] <= 600)}


def cmd_emitters(a, root: Path) -> int:
    from collections import Counter
    from . import assets as A, emitter_preview as EP, emitter_study as ES, spl_emitter as E, spl_sim as S
    from dau1 import spl as dspl
    ws = a.workspace.resolve()
    catalog = K.load_catalog(root)
    fdoc = K.load_features(a)
    rows, data_of, all_headers = [], {}, []
    for lib, uid, rel, mem, data in ES.iter_corpus(ws, root):
        rows.append(ES.study_archive(lib, uid, data))
        data_of[uid] = data
        if rows[-1].get("emitters"):
            all_headers += [e.header for e in E.parse_emitters(data).emitters]
    rows.sort(key=lambda r: r["id"])
    dau1 = {u["id"]: u for u in catalog["units"]}
    for u in fdoc["platinum_units"]:
        dau1[u["id"]] = u
    cov = {}
    for lib in ("hgss", "diamond", "platinum"):
        rs = [r for r in rows if r["library"] == lib]
        base = [u for u in dau1.values() if u["library"] == lib and u["type"] == "spl_particle_archive"]
        cov[lib] = {
            "archives_in_checkout": len(rs),
            "DECODED_TEXTURE_ONLY_baseline_dau1": sum(1 for u in base if u["status"] == "DECODED"),
            "texture_structural_only_dau1_(blank_or_4x4_compressed)": sum(1 for u in base if u["status"] == "STRUCTURAL_ONLY"),
            "EMITTER_FIELDS_VERIFIED": sum(1 for r in rs if r["category"] == "EMITTER_FIELDS_VERIFIED"),
            "EMITTER_FIELDS_PARSED_WITH_ANOMALIES": sum(1 for r in rs if r["category"] == "EMITTER_FIELDS_PARSED_WITH_ANOMALIES"),
            "PARSE_FAILED": sum(1 for r in rs if r["category"] == "DECODED_TEXTURE_ONLY"),
            "emitters_parsed": sum(r.get("emitters", 0) for r in rs),
            "EMITTER_PREVIEW_VERIFIED": 0, "CANDIDATE_REVIEWED": 0,
            "BLOCKED_SOURCE": sum(1 for u in dau1.values() if u["library"] == lib and u["status"] == "MISSING"),
        }
    # ----- three representative effects, replayed in every game that carries them
    align = A.spl_alignment(list(dau1.values()), fdoc["platinum_order"])
    by_name = {}
    for uid, al in align.items():
        if al["basis"] in ("EXACT_FILENAME", "TEXTURE_VERIFIED"):
            by_name.setdefault(al["name"], {})[uid.split(":", 1)[0]] = uid
    rdir = a.out / "emitter" / "recipes"
    ldir = a.build.resolve() / "emitter"
    recipes, summaries = [], []
    for kind, name, label in REPRESENTATIVE:
        versions = {lib: uid for lib, uid in by_name.get(name, {}).items() if uid in data_of}
        plat_uid = versions.get("platinum")
        if not plat_uid:
            print(f"{name}: no Platinum file", file=sys.stderr)
            continue
        parsed = {lib: E.parse_emitters(data_of[uid]) for lib, uid in versions.items()}
        base = parsed["platinum"]
        cross = {}
        for lib, sp in parsed.items():
            if lib == "platinum":
                continue
            same = len(sp.emitters) == len(base.emitters) and all(
                x.header == y.header and x.flags == y.flags and x.behaviors == y.behaviors and x.scale == y.scale and x.color == y.color
                and x.alpha == y.alpha and x.tex == y.tex and x.child == y.child for x, y in zip(sp.emitters, base.emitters))
            diff = [] if same else sorted({k for x, y in zip(sp.emitters, base.emitters) for k in ("header", "flags", "behaviors", "scale", "color", "alpha", "tex", "child")
                                           if getattr(x, k) != getattr(y, k)})
            cross[lib] = {"unit": versions[lib], "sha256": ES.hashlib.sha256(data_of[versions[lib]]).hexdigest(), "emitter_records_identical_to_platinum": same,
                          "differing_blocks": diff, "emitters": len(sp.emitters), "textures_identical_by_visual_sha": dau1[versions[lib]].get("visual_sha256") == dau1[plat_uid].get("visual_sha256")}
        rp = S.replay(base, REPLAY_FRAMES, REPLAY_SEED)
        rp2 = S.replay(base, REPLAY_FRAMES, REPLAY_SEED)
        inv = ES.replay_invariants(base, rp, REPLAY_FRAMES)
        inv["deterministic"] = rp.frames == rp2.frames
        imgs, scale, undecoded = EP.render_replay(data_of[plat_uid], rp)
        ldir.mkdir(parents=True, exist_ok=True)
        step = max(1, REPLAY_FRAMES // 12)
        sel = list(range(0, REPLAY_FRAMES, step))[:12]
        from dau1.render import save_png
        save_png(EP.timeline_sheet([imgs[i] for i in sel], [f"f{i} n={rp.per_frame_counts[i]}" for i in sel]), ldir / f"{name}_timeline.png")
        imgs[0].save(ldir / f"{name}.gif", save_all=True, append_images=imgs[1:], duration=33, loop=0, optimize=False)
        o = dau1[plat_uid]["extra"].get("opal_fx")
        rec = ES.recipe(label, {"game": "Pokemon Platinum (this repository)", "unit": plat_uid, "archive_path": dau1[plat_uid]["source"], "sha256": dau1[plat_uid]["sha256"],
                                "effect_kind": kind, "move": label}, base, data_of[plat_uid], rp, inv, cross, REPLAY_FRAMES, o)
        rec["replay"]["pixel_scale"] = scale
        rec["replay"]["preview_frames_sha256"] = EP.frames_hash(imgs)
        rec["replay"]["state_sha256"] = ES.hashlib.sha256(json.dumps(rp.frames, sort_keys=True).encode()).hexdigest()
        rec["replay"]["undecoded_texture_indices"] = undecoded
        rec["replay"]["local_preview_files"] = [f"build/dau2/emitter/{name}_timeline.png", f"build/dau2/emitter/{name}.gif"]
        K.write_json(rdir / f"{name}.emitter_recipe.json", rec)
        recipes.append(name)
        ok = inv["spawn_schedule_matches"] and inv["particle_age_within_life"] and inv["deterministic"] and inv["within_ds_quad_limit"]
        for lib in versions:
            if ok and lib in cov:
                cov[lib]["EMITTER_PREVIEW_VERIFIED"] += 1
        summaries.append({"effect": name, "kind": kind, "label": label, "emitters": len(base.emitters), "peak_live": inv["peak_live_particles"],
                          "invariants_ok": ok, "cross_game": {k: v["emitter_records_identical_to_platinum"] for k, v in cross.items()},
                          "games_replayed": sorted(versions), "preview_frames_sha256": rec["replay"]["preview_frames_sha256"]})
    doc = {"schema_version": 1, "generated_by": "tools/visual_overhaul/dau2_curate.py emitters",
           "coverage_by_library": cov, "plausibility_across_corpus": _plausibility(all_headers),
           "representative_effects": summaries, "replay": {"frames": REPLAY_FRAMES, "seed": REPLAY_SEED},
           "category_definitions": ES.__doc__, "archives": [{k: v for k, v in r.items() if k != "features"} | {"features": r.get("features")} for r in rows]}
    dump_json_lines(doc, "archives", a.out / "EMITTER_COVERAGE.json")
    from .emitter_report import research_markdown
    (a.out / "EMITTER_RESEARCH.md").write_text(research_markdown(doc))
    print(json.dumps({"coverage": cov, "effects": summaries}, indent=1))
    return 0


# ------------------------------------------------------------------------------------------------ check
IMAGE_SUFFIXES = (".png", ".gif", ".jpg", ".jpeg", ".bmp", ".webp", ".spa", ".narc", ".nclr", ".ncgr", ".ncer", ".nanr", ".nscr", ".bin", ".zip")
OBS_VOCAB = {"PLAUSIBLE_ON_SIGHT", "WRONG_ON_SIGHT", "ILLEGIBLE_OR_TOO_SMALL", "NEEDS_CLOSER_LOOK"}


def _tracked_binaries(root: Path, dirs: list[str]) -> list[str]:
    try:
        out = subprocess.run(["git", "-C", str(root), "ls-files", "--", *dirs], capture_output=True, text=True, check=True).stdout.split("\n")
    except Exception:                                                  # noqa: BLE001 - no git: scan the working tree
        out = [p.relative_to(root).as_posix() for d in dirs for p in (root / d).rglob("*") if p.is_file()]
    return [p for p in out if p.lower().endswith(IMAGE_SUFFIXES)]


def cmd_check(a, root: Path) -> int:
    from . import candidates as C
    errs: list[str] = []
    e = errs.append
    src = a.out / K.SRC_DIR / K.MANIFEST_NAME
    try:
        doc = M.load(src)
    except Exception as ex:                                            # noqa: BLE001
        print(f"manifest: {ex}", file=sys.stderr)
        return 1
    sha_file = (src.parent / (K.MANIFEST_NAME + ".sha256")).read_text().split()[0]
    if sha_file != M.PINNED_SHA256:
        e("source/*.sha256 does not carry the pinned digest")
    p1 = [m["move"] for m in doc["moves"] if m["tier"] == "P1_mid_staples"]
    p2 = [m["move"] for m in doc["moves"] if m["tier"] == "P2_status_utility"]
    if (len(p1), len(p2)) != (19, 14):
        e(f"manifest P1/P2 counts {(len(p1), len(p2))} != (19, 14)")
    idx = a.out / K.SRC_DIR / "P1_P2_MOVE_INDEX.md"
    binding_fresh = M.bind(doc, root, idx.read_text() if idx.exists() else None)
    binding = json.loads((a.out / "B9_P1_P2_BINDING.json").read_text())
    if binding["moves"] != binding_fresh["moves"]:
        changed = [x["move"] for x, y in zip(binding["moves"], binding_fresh["moves"]) if x != y]
        e(f"B9_P1_P2_BINDING.json is stale / a bound move script changed: {changed[:6]} (P1/P2 must stay unimplemented in DAU2; "
          "re-run 'manifest' only after an approved implementation batch)")
    if binding["discrepancies"] != binding_fresh["discrepancies"]:
        e("B9_P1_P2_BINDING.json discrepancy list is stale")
    mpath = a.out / "MOVE_CANDIDATE_MATRIX.json"
    m = json.loads(mpath.read_text())
    names = [x["move"] for x in m["moves"]]
    if names != p1 + p2:
        e("matrix move names/order do not exactly match manifest P1 + P2")
    catalog = K.load_catalog(root)
    fdoc = K.load_features(a)
    units = {u["id"]: u for u in catalog["units"]} | {u["id"]: u for u in fdoc["platinum_units"]}
    for mv in m["moves"]:
        fam = {r["family"] for r in mv["candidates"]}
        if len(fam) < 3:
            e(f"{mv['move']}: candidates span only {sorted(fam)}")
        if mv["visual_decision"] != "AWAITING_OWNER_REVIEW":
            e(f"{mv['move']}: visual decision must stay AWAITING_OWNER_REVIEW")
        for r in mv["candidates"]:
            u = units.get(r["asset_id"])
            if not u:
                e(f"{mv['move']}: unknown asset {r['asset_id']}")
                continue
            if u["sha256"] != r["sha256"] or u["visual_sha256"] != r["visual_sha256"]:
                e(f"{mv['move']}: {r['asset_id']} hash differs from the catalog")
            if r["evidence_basis"] not in ("named_move_particle", "named_source", "feature_heuristic"):
                e(f"{mv['move']}: bad basis {r['evidence_basis']}")
            vr = r["visual_review"]
            if vr["status"] != "AWAITING_OWNER_REVIEW" or vr["owner_decision"] is not None:
                e(f"{mv['move']}: {r['asset_id']} carries a review decision it may not have")
            ob = vr.get("model_observation")
            if ob and (ob.get("status") not in OBS_VOCAB or ob.get("is_approval") is not False):
                e(f"{mv['move']}: {r['asset_id']} model observation is not in the advisory vocabulary")
            for k in ("source_game", "source_revision", "archive_path", "sha256", "decode_confidence", "role_candidates", "preview_path", "dimensions",
                      "palette_count", "tile_count", "oam_cost", "animation_frames", "conversion_route", "runtime_palette_dependency", "redistribution_status"):
                if k not in r:
                    e(f"{mv['move']}: candidate lacks {k}")
    obs_p = a.out / "model_visual_observations.json"
    obs = json.loads(obs_p.read_text())["observations"] if obs_p.exists() else {}
    again = C.build_matrix(catalog, fdoc, binding, obs)
    if again != m:
        e("MOVE_CANDIDATE_MATRIX.json is stale relative to catalog/features/binding/observations (re-run 'matrix')")
    # ASSET_INDEX <-> matrix
    ip = a.out / "ASSET_INDEX.json"
    if ip.exists():
        idx_doc = json.loads(ip.read_text())
        for mv in m["moves"]:
            b = idx_doc["boards"].get(mv["board"])
            if not b:
                e(f"ASSET_INDEX lacks board {mv['board']}")
                continue
            if [c["asset_id"] for c in b["cells"]] != [r["asset_id"] for r in mv["candidates"]] or \
                    [c["cell"] for c in b["cells"]] != [r["board_cell_index"] for r in mv["candidates"]]:
                e(f"ASSET_INDEX board {mv['board']} does not match the matrix cells")
        for name, cs in idx_doc["contact_sheets"].items():
            for c in cs["cells"]:
                if c["asset_id"] not in units:
                    e(f"ASSET_INDEX {name}: unknown asset {c['asset_id']}")
    else:
        e("missing ASSET_INDEX.json (run 'sheets')")
    # emitter artefacts
    cp = a.out / "EMITTER_COVERAGE.json"
    if not cp.exists():
        e("missing EMITTER_COVERAGE.json")
    else:
        cov = json.loads(cp.read_text())
        for lib, c in cov["coverage_by_library"].items():
            if c["EMITTER_FIELDS_VERIFIED"] + c["EMITTER_FIELDS_PARSED_WITH_ANOMALIES"] + c["PARSE_FAILED"] != c["archives_in_checkout"]:
                e(f"coverage[{lib}] categories do not sum to the archive count")
            if c["CANDIDATE_REVIEWED"] != 0:
                e(f"coverage[{lib}] CANDIDATE_REVIEWED must be 0 until the owner reviews")
        if len(cov["archives"]) != sum(c["archives_in_checkout"] for c in cov["coverage_by_library"].values()):
            e("EMITTER_COVERAGE archive rows do not match the coverage totals")
        recipes = sorted((a.out / "emitter" / "recipes").glob("*.emitter_recipe.json"))
        if len(recipes) < 3:
            e(f"only {len(recipes)} emitter recipes (need 3)")
        for p in recipes:
            r = json.loads(p.read_text())
            if r.get("schema") != "emitter_recipe/1" or len(r["source"]["sha256"]) != 64 or not r["unknowns"] or not r["verified_fields"]["emitters"]:
                e(f"{p.name}: malformed recipe")
            inv = r["replay"]["invariants"]
            if not (inv["spawn_schedule_matches"] and inv["particle_age_within_life"] and inv["deterministic"] and inv["within_ds_quad_limit"]):
                e(f"{p.name}: replay invariants fail")
            if "NOT_RUNTIME_CAPTURED" not in r["status"]:
                e(f"{p.name}: status must say it is not runtime captured")
    bad = _tracked_binaries(root, ["docs/visual_overhaul/asset_unlock/dau2", "tools/visual_overhaul/dau2", "tools/visual_overhaul/dau2_curate.py"])
    if bad:
        e(f"image/binary artefacts are tracked under DAU2 paths (previews must stay local): {bad[:5]}")
    for n in ("README.md", "GAP_REPORT.md", "OWNER_REVIEW_GALLERY.md", "EMITTER_RESEARCH.md", "MOVE_CANDIDATE_MATRIX.md", "OWNER_REVIEW_QUEUE.json"):
        if not (a.out / n).exists():
            e(f"missing {n}")
    if errs:
        print("\n".join(errs[:40]), file=sys.stderr)
        return 1
    s = m["summary"]
    print(f"OK: {s['moves']} moves (P1 {s['p1']} / P2 {s['p2']}), {s['candidate_references']} candidate refs over {s['distinct_assets']} assets, "
          f"manifest sha {M.PINNED_SHA256[:12]}..., {len(recipes)} emitter recipes, no tracked binaries")
    return 0


def cmd_all(a, root: Path) -> int:
    for fn in (K.cmd_manifest, K.cmd_features, K.cmd_matrix, cmd_sheets, cmd_emitters):
        if fn(a, root):
            return 1
    return 0


def cmd_package(a, root: Path) -> int:
    """Zip the local previews + gallery index into build/dau2 for attaching to a review (never written under tracked paths)."""
    import zipfile
    out = a.build.resolve()
    if not (out / "boards").is_dir():
        print("no previews: run 'sheets' (and 'emitters') first", file=sys.stderr)
        return 1
    zp = out / "dau2_owner_review_pack.zip"
    files = sorted(p for p in out.rglob("*") if p.is_file() and p.suffix in (".png", ".gif"))
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files:
            z.write(p, p.relative_to(out).as_posix())
        for n in ("OWNER_REVIEW_GALLERY.md", "OWNER_REVIEW_QUEUE.json", "ASSET_INDEX.json", "MOVE_CANDIDATE_MATRIX.md"):
            z.write(a.out / n, n)
    print(f"{zp} ({zp.stat().st_size // 1024} KiB, {len(files)} images) - LOCAL ONLY: contains decoded game art, do not commit")
    return 0
