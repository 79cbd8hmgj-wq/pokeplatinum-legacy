"""Markdown / queue renderers for the DAU2 candidate matrix (deterministic, no pixels)."""
from __future__ import annotations


def review_queue(m: dict) -> dict:
    items = []
    for mv in m["moves"]:
        items.append({"move": mv["move"], "tier": mv["tier"], "board": mv["board"], "decision": "AWAITING_OWNER_REVIEW",
                      "status": mv["status"], "choose_per_component": sorted(mv["components"]),
                      "candidates": [{"cell": r["board_cell_index"], "asset_id": r["asset_id"], "component": r["component"],
                                      "basis": r["evidence_basis"], "decision": "AWAITING_OWNER_REVIEW"} for r in mv["candidates"]]})
    return {"schema_version": 1, "decision_vocabulary": ["AWAITING_OWNER_REVIEW", "ACCEPT", "REJECT", "NEEDS_ANOTHER_LOOK"],
            "note": "Nothing is approved. The owner fills 'decision' per cell after viewing the local board; model observations are advisory only.",
            "items": items}


def matrix_markdown(m: dict) -> str:
    s = m["summary"]
    L = ["# DAU2 - per-move cross-source candidate matrix (B9 P1 / P2)", "",
         "Generated from the committed DAU1 catalog + DAU2 feature file by `tools/visual_overhaul/dau2_curate.py matrix`. "
         "**No candidate is visually approved.** Heuristic (`feature_heuristic`) rows are search aids; only `named_*` rows carry a source-backed name.", "",
         f"Moves: **{s['moves']}** (P1 {s['p1']}, P2 {s['p2']}). Candidate references: **{s['candidate_references']}** over **{s['distinct_assets']}** distinct assets "
         f"(pool: {s['pool_assets_considered']} canonical renderings; {s['pool_alias_duplicates_collapsed']} cross-library duplicates collapsed). "
         f"Moves with candidates from >= 3 source families: **{s['moves_with_3plus_families']}/{s['moves']}**; READY (>= 3 distinct name-backed renderings AND >= 3 families): **{s['ready_for_owner_review']}/{s['moves']}**.", "",
         "Evidence basis counts: " + ", ".join(f"{k} {v}" for k, v in s["by_basis"].items()) + ". By family: " + ", ".join(f"{k} {v}" for k, v in s["by_family"].items()) + ".", ""]
    if s["insufficient_verified_candidates"]:
        L += ["`INSUFFICIENT_VERIFIED_CANDIDATES`: " + ", ".join(s["insufficient_verified_candidates"]) + ".", ""]
    L += ["| Move | Tier | Status | Families (name-backed / all) | Native Platinum particle | Candidates |", "|---|---|---|---|---|---:|"]
    for mv in m["moves"]:
        native = [r["evidence"]["particle_name"] for r in mv["candidates"] if r["evidence"].get("native_same_move")]
        L.append(f"| {mv['move']} | {mv['tier'][:2]} | {mv['status']} | {', '.join(mv['families_name_backed']) or '-'} / {', '.join(mv['families_all'])} | "
                 f"{'`' + native[0] + '.spa`' if native else '-'} | {mv['candidate_count']} |")
    L += ["", "## Per-move detail", ""]
    for mv in m["moves"]:
        L += [f"### {mv['move']} ({mv['tier'][:2]}, `{mv['template']}`) - {mv['visual_intent']}", "",
              f"Status `{mv['status']}`" + (f" - {'; '.join(mv['status_reasons'])}" if mv["status_reasons"] else "") + f". Board (local): `build/dau2/{mv['board']}`. Visual decision: **{mv['visual_decision']}**.", "",
              "| Cell | Component | Rank | Basis | Score | Library | Asset id | Tiles~ | Colours | Frames | Palette dependency |", "|---:|---|---:|---|---:|---|---|---:|---:|---:|---|"]
        for r in mv["candidates"]:
            L.append(f"| {r['board_cell_index']} | {r['component']} | {r['rank_in_component']} | {r['evidence_basis']} | {r['score']} | {r['library']} | "
                     f"`{r['asset_id'][-70:]}` | {r['tile_count']} | {r['palette_count']} | {r['animation_frames']} | {r['runtime_palette_dependency'][:40]} |")
        L.append("")
    return "\n".join(L) + "\n"


def gallery_markdown(m: dict, idx: dict, local_dir: str = "build/dau2") -> str:
    L = ["# DAU2 - owner review gallery (index of local previews)", "",
         "**Nothing in this file is an approval.** Every decision below is `AWAITING_OWNER_REVIEW`. The images are decoded Nintendo artwork and are therefore "
         f"**not committed**: they are generated into `{local_dir}/` (git-ignored) by `python3 tools/visual_overhaul/dau2_curate.py sheets` and can be zipped for review with "
         "`python3 tools/visual_overhaul/dau2_curate.py package` (also local). This file maps every preview cell to an immutable asset id; "
         "`ASSET_INDEX.json` additionally carries the SHA-256 of each rendered cell's pixels so a regenerated sheet can be verified.", "",
         "## How to review", "",
         "1. Generate the previews locally (donor checkouts next to the repository): `sheets`, then `package`.",
         "2. Open `boards/<tier>_<move>.png`. Each row is one *component* of the move (native baseline, launch / travel / impact / aftermath / reaction); candidates run left to right, "
         "numbered `#n` (the cell number used below and in `OWNER_REVIEW_QUEUE.json`). Colour of the caption: green = Platinum/DP/HGSS particle with a verified name, blue = named GBA/Crystal sprite, orange = anonymous art ranked by a hue/shape heuristic (a search aid only).",
         "3. SPL particle textures (Platinum / Diamond / HGSS) are **untinted intensity masks**: the in-game colour comes from the emitter's colour/colour-animation (see `emitter/recipes/*.emitter_recipe.json`), so grey/white previews of those are expected.",
         "4. Record accept / reject per cell in a copy of `OWNER_REVIEW_QUEUE.json` (vocabulary `ACCEPT`, `REJECT`, `NEEDS_ANOTHER_LOOK`). Model observations are advisory and made from the rendered boards; they are not decisions.", "",
         "## Pool contact sheets (indexed; every library, every canonical decoded asset)", "",
         "| Sheet (local) | Library | Cells | First asset | Last asset |", "|---|---|---:|---|---|"]
    for name, cs in sorted(idx["contact_sheets"].items()):
        cells = cs["cells"]
        L.append(f"| `{name}` | {cs['library']} | {len(cells)} | `{cells[0]['asset_id'][-56:]}` | `{cells[-1]['asset_id'][-56:]}` |")
    L += ["", "Cell numbers on a pool sheet index into `ASSET_INDEX.json` -> `contact_sheets[<sheet>].cells[n]`.", "", "## Per-move boards", ""]
    for mv in m["moves"]:
        L += [f"### {mv['move']} ({mv['tier'][:2]}) - `{mv['template']}`: {mv['visual_intent']}", "",
              f"Board: `{local_dir}/{mv['board']}` - status `{mv['status']}`; native Platinum particle: `{mv['native_platinum_particle']['status']}`.", "",
              "| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |", "|---:|---|---|---|---|---|---|"]
        for r in mv["candidates"]:
            ob = r["visual_review"]["model_observation"]
            obs = f"{ob['status']}: {ob['note']}" if ob else "-"
            L.append(f"| {r['board_cell_index']} | {r['component']} | {r['evidence_basis'].replace('_', ' ')} | {r['library']} | `{r['asset_id']}` | {obs} | AWAITING_OWNER_REVIEW |")
        L.append("")
    return "\n".join(L) + "\n"
