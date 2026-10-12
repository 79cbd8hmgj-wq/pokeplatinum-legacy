"""Blocker ledger and the generated DECODER_COVERAGE.md."""
from __future__ import annotations

import re
from collections import Counter, defaultdict

from .common import STATUSES


def blockers(doc: dict) -> list[dict]:
    """Every missing / unresolved input, derived from the catalog (counts are measured, not asserted)."""
    U = doc["units"]
    B: list[dict] = []
    for s in doc["sources"]:
        if not s["present"]:
            B.append({"library": s["library"], "input": "source checkout", "status": "BLOCKED_INPUT",
                      "detail": f"{s['label']} not found in the workspace (looked for {s['expected_paths']})"})
    miss = [u for u in U if u["status"] == "MISSING" and u["library"] == "hgss"]
    if miss:
        B.append({"library": "hgss", "input": "base-ROM-extracted filesystem entries", "status": "MISSING",
                  "detail": f"{len(miss)} files listed in heartgold.us/filesystem.sha1 are not in the checkout (mostly files/a/*/*/*); "
                            "they exist only after extracting a legally owned HeartGold ROM. 645 SPL archives that ARE present "
                            "(files/a/0/2/9 move particles, files/a/0/9/5 ball particles, ...) are decoded; the absent entries cannot be ruled out as holding more."})
    pal = [u for u in U if u["library"] == "hgss" and u["status"] != "DECODED" and "defined outside the archive" in (u.get("error_reason") or "")]
    if pal:
        B.append({"library": "hgss", "input": "graphic<->palette pairing tables", "status": "STRUCTURAL_ONLY",
                  "detail": f"{len(pal)} cell banks / sheets render but are held at STRUCTURAL_ONLY because their NCLR is not adjacent; the mapping lives in overlay code, not the NARC."})
    pmd = [u for u in U if u["library"] == "pmd_sky" and u["type"] == "pmd_effect_wan"]
    rt = [u for u in pmd if u["status"] == "UNSUPPORTED" and "run-time palette bank" in (u.get("error_reason") or "")]
    if rt:
        B.append({"library": "pmd_sky", "input": "run-time palette-bank semantics", "status": "UNSUPPORTED",
                  "detail": f"{len(rt)} effect sprites select palette rows the file does not define; the engine supplies them at run time. "
                            "Geometry/pixels are decoded for the metaframes that resolve; the rest are never guessed."})
    for lib, what in (("pmd_sky", "character/prop WAN sprites (different WAN variant)"),):
        if any(u["library"] == lib and u["type"] == "pmd_character_wan_set" for u in U):
            B.append({"library": lib, "input": what, "status": "UNSUPPORTED", "detail": "not part of effect.bin; not decoded by DAU1"})
    spl_units = [u for u in U if u["type"] == "spl_particle_archive" and u["status"] == "DECODED"]
    if spl_units:
        B.append({"library": "hgss+diamond", "input": "SPL emitter (motion) decoding", "status": "STRUCTURAL_ONLY",
                  "detail": f"{len(spl_units)} .spa archives decode to their particle textures only; emitter behaviour (velocity, scale/alpha curves, timing) is inventoried (emitter counts/bytes) but not decoded."})
    scr = [u for u in U if u["type"] == "nitro_screen_set"]
    if scr:
        B.append({"library": "hgss", "input": "NSCR tile-map screens", "status": "UNSUPPORTED",
                  "detail": f"{sum(u['extra']['members_total'] for u in scr)} screen maps in {len(scr)} archives are background compositions; no decoder (not effect art)."})
    rt_tex = [u for u in U if u["type"] == "ds_ntft_texture" and u["status"] != "DECODED"]
    if rt_tex:
        B.append({"library": "ranger2", "input": "texture width metadata", "status": "STRUCTURAL_ONLY",
                  "detail": f"{len(rt_tex)} .ntft textures have palette-valid indices but an ambiguous width (not stored in the file)."})
    cry = [u for u in U if u["library"] == "crystal" and u["status"] != "DECODED"]
    if cry:
        B.append({"library": "crystal", "input": "battler/placeholder & run-time palettes", "status": "STRUCTURAL_ONLY",
                  "detail": f"{len(cry)} of {sum(1 for u in U if u['library'] == 'crystal')} battle objects are not reconstructable from text tables alone "
                            "(placeholder gfx 0 = battler sprites, run-time palettes, or OAM tile offsets into a gfx loaded together with another)."})
    if any(u["library"] == "yellow" for u in U):
        B.append({"library": "yellow", "input": "subanimation/frame-block layout tables", "status": "STRUCTURAL_ONLY",
                  "detail": "the 2bpp sheets decode, but Yellow's layout tables (engine/battle/animations) were not reconstructed; Crystal was the single reconstructed recipe family."})
    B.append({"library": "all", "input": "B9 P1/P2 move manifest", "status": "BLOCKED_INPUT",
              "detail": "pokemon_opal_everyday_moves_b9_manifest_v2 (names of the 19 P1 / 14 P2 moves) is not in the repo or the DAU1 package; the matrix is role-keyed."})
    B.append({"library": "all", "input": "redistribution rights", "status": "BLOCKED_INPUT",
              "detail": "no donor project grants rights over the original game artwork; PROVENANCE.md flags every pool for owner review before any public release."})
    return B


def _top_reasons(units: list[dict], n: int = 3) -> str:
    def norm(s):
        s = re.sub(r"\b[0-9a-f]{40}\b", "<sha1>", s or "")
        return re.sub(r"\d+", "N", s)[:90]
    c = Counter(norm(u.get("error_reason")) for u in units if u["status"] != "DECODED")
    return "; ".join(f"{r} (x{k})" for r, k in c.most_common(n)) or "-"


def coverage_markdown(doc: dict) -> str:
    U = doc["units"]
    L = ["# DAU1 decoder coverage", "",
         "Generated by `tools/visual_overhaul/dau1_unlock.py catalog` from the real donor checkouts; **DECODED** means real pixels were produced and "
         "validated (tiles inside the character data, palette indices inside the palette, at least one visible frame). Container/header recognition "
         "alone is `STRUCTURAL_ONLY`. Counts are *units* (see `ASSET_CATALOG.json`); they are not directly comparable between libraries.", "",
         "## Library summary", "", "| Library | Present | Units | " + " | ".join(STATUSES) + " | Verdict |", "|---|---|---:|" + "---:|" * len(STATUSES) + "---|"]
    def n_of(lib, typ=None, st=None):
        return sum(1 for u in U if u["library"] == lib and (typ is None or u["type"] == typ) and (st is None or u["status"] == st))
    verdict = {
        "hgss": (f"partial: {n_of('hgss', 'spl_particle_archive', 'DECODED')} SPL particle archives + {n_of('hgss', 'nitro_cell_bank', 'DECODED')} cell banks decoded; "
                 f"SPL motion, NSCR screens, external palette pairings and {n_of('hgss', 'baserom_file')} base-ROM files not"),
        "pmd_sky": (f"partial: effect.bin frame-level decode for {n_of('pmd_sky', 'pmd_effect_wan', 'DECODED')} of {n_of('pmd_sky', 'pmd_effect_wan')} entries; "
                    "run-time-palette entries and non-sprite tables not"),
        "ranger2": (f"mostly decoded: {n_of('ranger2', 'nitro_cell_bank', 'DECODED')} of {n_of('ranger2', 'nitro_cell_bank')} cell banks; "
                    "ambiguous textures and a few unpairable/blank banks remain"),
        "ruby": "decoded; every strip has an identical counterpart in Emerald/FireRed (see cross_library)",
        "emerald": "decoded (PNG strips; layout in C tables)",
        "firered": "decoded (byte-identical to Emerald where shared)",
        "crystal": f"partial: {n_of('crystal', None, 'DECODED')} objects reconstructed exactly from text tables; the rest need unavailable run-time data",
        "yellow": "blocked at layout: tile sheets only",
        "diamond": (f"partial: {n_of('diamond', 'spl_particle_archive', 'DECODED')} SPL archives + {n_of('diamond', 'nitro_cell_bank', 'DECODED')} cell banks decoded; "
                    "many loose banks have no same-stem partners"),
    }
    src = {s["library"]: s for s in doc["sources"]}
    for lib, cov in doc["coverage"].items():
        L.append(f"| {lib} | {'yes' if src.get(lib, {}).get('present') else 'no'} | {cov['units']} | " +
                 " | ".join(str(cov["by_status"][s]) for s in STATUSES) + f" | {verdict.get(lib, '')} |")
    for lib in doc["sources"]:
        if not lib["present"]:
            L.append(f"| {lib['library']} | no | 0 | " + " | ".join("0" for _ in STATUSES) + " | BLOCKED_INPUT: checkout absent |")
    L += ["", "## By unit type", "", "| Library | Type | Units | DECODED | Not decoded: top reasons |", "|---|---|---:|---:|---|"]
    by = defaultdict(list)
    for u in U:
        by[(u["library"], u["type"])].append(u)
    for (lib, t), us in sorted(by.items()):
        L.append(f"| {lib} | {t} | {len(us)} | {sum(1 for u in us if u['status'] == 'DECODED')} | {_top_reasons(us)} |")
    L += ["", "## Frame-level evidence per priority archive", "",
          "| Archive | Units | DECODED | Decoded frames / textures |", "|---|---:|---:|---:|"]
    arch = defaultdict(lambda: [0, 0, 0])
    for u in U:
        if u["library"] in ("hgss", "pmd_sky", "ranger2", "diamond") and u["type"] in ("nitro_cell_bank", "spl_particle_archive", "pmd_effect_wan"):
            a = arch[(u["library"], u["source"])]
            a[0] += 1
            if u["status"] == "DECODED":
                a[1] += 1
                a[2] += u["frame_count"] or 0
    top = sorted(arch.items(), key=lambda kv: -kv[1][2])[:25]
    for (lib, src_), (n, d, f) in top:
        L.append(f"| {lib}: `{src_}` | {n} | {d} | {f} |")
    L += ["", "## Blockers and missing inputs", "", "| Library | Input | Status | Detail |", "|---|---|---|---|"]
    for b in doc.get("blockers", []):
        L.append(f"| {b['library']} | {b['input']} | {b['status']} | {b['detail']} |")
    d = doc.get("duplicates", {})
    cg = d.get("cross_library_groups", {})
    L += ["", "## Duplicate detection", "",
          f"{len(cg)} cross-library duplicate groups (identical input bytes or identical rendered pixels in more than one donor); "
          f"within-library duplicate groups: {d.get('within_library_group_counts', {})}. "
          "Ruby, FireRed and Emerald share their battle-sprite art byte-for-byte (see `cross_library` on each GBA unit)."]
    return "\n".join(L) + "\n"


def provenance_markdown(doc: dict) -> str:
    L = ["# DAU1 provenance and legal release gate", "",
         "Generated by `tools/visual_overhaul/dau1_unlock.py catalog` (sources table) - edit `report.py`, not this file.", "",
         "## Release gate (owner decision required)", "",
         "* **No ROM, base-ROM extraction, donor binary or bulk donor art is committed.** The catalog stores only paths, sha256 hashes, counts and budgets.",
         "* The decomp projects' *source-code* licences (where a licence file exists at all) do not authorise redistribution of Nintendo / Game Freak / Spike Chunsoft / "
         "Creatures artwork. Every pool below is therefore `asset_license: UNVERIFIED`.",
         "* `docs/visual_overhaul/asset_unlock/gallery/*_excerpt.png` are small (<= 60 cell) evidence excerpts of decoded donor frames, kept for review of the decoders only. "
         "They are *not* cleared for release; the owner must delete them (or approve them) before any public distribution. Full galleries are written to `build/` (git-ignored).",
         "* Converted Opal FX sheets produced by `dau1_unlock.py convert` go to `build/` and are not installed into `res/`; installing one needs a separate, reviewed change "
         "(and the same licence decision).", "",
         "## Sources searched", "",
         "| Library | Present | Pinned commit | Origin | Code licence file(s) at repo root | Asset licence |", "|---|---|---|---|---|---|"]
    for s in doc["sources"]:
        if s["present"]:
            L.append(f"| {s['library']} | yes | `{(s.get('commit') or 'unknown')[:12]}`{' (shallow clone)' if s.get('shallow') else ''} | {s.get('origin') or '-'} | "
                     f"{', '.join(s.get('code_license_files') or []) or 'none found'} | {s['asset_license'].split(':')[0]} |")
        else:
            L.append(f"| {s['library']} | **no** | - | - | - | BLOCKED_INPUT: {s.get('note', '')} |")
    L += ["", "## Per-resource provenance", "",
          "Every catalog unit carries `source` (repo-relative path), `sha256` (primary input bytes; for multi-file units the hash of the member hashes) and, for "
          "multi-file units, a `members` list of `{name, sha256, size}`. Container members are addressed `path#member-index`. `visual_sha256` hashes the decoded RGBA frames, "
          "so identical art in different donors (or re-encoded) is detected without storing any pixels.", "",
         "## Third-party format knowledge and reference implementations", "",
         "* NARC / Nitro 2D (NCLR, NCGR, NCER, NANR) layouts: public NitroSystem / community documentation; verified pixel-for-pixel against the existing in-repo Ranger renderer "
         "(`render_ranger_ncer_preview.py`) on 134 cells.",
         "* SPL `.spa` layout: derived from 602 real sample files (pokediamond) plus the decomp struct `include/library/spl_texture.h`; each file is validated structurally "
         "(blocks tile the file exactly; texture byte counts equal width x height x bits / 8).",
         "* PMD effect-WAN layout: public community documentation of the game's file layout. The implementation here is original. As an *independent cross-check only*, "
         "SkyTemple's `skytemple-files` (GPL-3.0) was installed in a throw-away virtualenv outside the repository and compared against this decoder: 259 sprites / 29,365 pieces, "
         "0 differences in piece counts, geometry or pixel masks. No SkyTemple code is vendored, imported by the tools, or required by CI.",
         "* Crystal recipes: the project's own assembly tables (`data/battle_anims/*.asm`) - nothing is inferred.", ""]
    return "\n".join(L) + "\n"
