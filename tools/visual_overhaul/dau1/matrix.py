"""Cross-library Opal candidate matrix built from the DECODED catalog (for B9 P1/P2 planning, before P1 is edited).

Roles come from donor names where names exist (GBA / Game Boy sprites); anonymous donors (PMD, HGSS, Ranger, Diamond)
get a *hue hint* only and are listed as ``needs_visual_review``.  A candidate is ``shortlisted`` only if it is decoded,
within the Opal OBJ budgets, and ranks in the top few of its role; everything else carries an explicit reason.
Nothing here is a visual approval.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict

TILE_BUDGET = 192          # per-sheet OBJ tile budget used by build_opal_fx_sheet.py
COLOUR_LIMIT = 15
MAX_SHORTLIST = 3

ROLES = {
    "fire": r"ember|fire|flame|burn|blaze|heat|lava|magma",
    "water": r"water|bubble|drop|splash|wave_|rain|surf|aqua|mist",
    "ice": r"ice|snow|hail|frost|freez|blizzard|crystal_",
    "electric": r"spark|thunder|lightning|electric|zap|bolt|shock|charge",
    "grass_nature": r"leaf|vine|plant|seed|petal|spore|grass|flower|whip",
    "rock_ground": r"rock|stone|dirt|sand|mud|boulder|dust|shard|dig",
    "wind_air": r"wind|air|whirl|gust|tornado|twister|feather|speed|cutter",
    "impact_strike": r"hit|impact|punch|kick|slam|bash|star|burst|explo|pound|tackle|smack",
    "slash_bite": r"slash|scratch|claw|cut|fang|bite|jaw|tooth|teeth|horn|stab|peck|talon",
    "poison_acid": r"poison|toxic|sludge|acid|venom|smog|gas",
    "psychic_sense": r"psychic|confus|eye|leer|glare|sense|beam|ring|wave|hypno|gaze",
    "ghost_dark": r"ghost|shadow|curse|dark|night|haze|smoke|spite",
    "sound_noise": r"sound|noise|note|sing|growl|roar|screech|echo",
    "status_buff": r"status|stat|arrow|sparkle|shine|glitter|heal|recover|shield|barrier|reflect|light",
}
HUE_ROLE_HINT = {"red": "fire", "orange": "fire", "yellow": "electric", "green": "grass_nature", "cyan": "ice",
                 "blue": "water", "purple": "ghost_dark", "pink": "psychic_sense", "black": "ghost_dark",
                 "white": "unspecific_white (glow / flash / sparkle candidates)", "grey": "rock_ground"}
TIER = {"emerald": 0, "firered": 0, "ruby": 0, "crystal": 2, "yellow": 2, "pmd_sky": 1, "hgss": 1, "diamond": 1, "ranger2": 1}


def role_from_name(name: str) -> str | None:
    n = name.lower()
    for role, pat in ROLES.items():
        if re.search(pat, n):
            return role
    return None


def _name_for(u: dict, emerald_by_hash: dict) -> str | None:
    if u["library"] in ("emerald", "firered"):
        return u["source"].rsplit("/", 1)[-1]
    if u["library"] == "ruby":
        e = emerald_by_hash.get(u["sha256"])
        return e["source"].rsplit("/", 1)[-1] if e else None
    if u["library"] == "crystal":
        return u["id"].rsplit("#", 1)[-1]
    return None


def build_matrix(doc: dict) -> dict:
    units = doc["units"]
    emerald_by_hash = {u["sha256"]: u for u in units if u["library"] == "emerald" and u["sha256"]}
    seen_visual: dict[str, str] = {}
    rows, roles = [], defaultdict(list)
    for u in sorted(units, key=lambda x: (TIER.get(x["library"], 3), x["id"])):
        o = (u.get("extra") or {}).get("opal_fx")
        if u["status"] != "DECODED" or not o:
            continue
        name = _name_for(u, emerald_by_hash)
        role = role_from_name(name) if name else None
        row = {"id": u["id"], "library": u["library"], "type": u["type"], "name": name, "role": role,
               "role_basis": "donor name" if role else ("hue hint only" if o.get("hue") else "none"),
               "hue": o.get("hue"), "frames": u["frame_count"], "obj_tiles_est": o.get("obj_tiles"),
               "colours": o.get("colours"), "translucent_dropped": o.get("translucent_pixels_dropped"),
               "max_oams": o.get("max_oams_per_cell"), "largest_frame": o.get("largest_frame"),
               "sha256": u["sha256"], "visual_sha256": u["visual_sha256"], "decision": None, "rationale": None}
        reasons = []
        if not o.get("convertible"):
            reasons.append(o.get("reason", "not convertible"))
        else:
            if (o["obj_tiles"] or 0) > TILE_BUDGET:
                reasons.append(f"{o['obj_tiles']} estimated OBJ tiles > {TILE_BUDGET} budget")
            if (o["colours"] or 0) > COLOUR_LIMIT:
                reasons.append(f"{o['colours']} colours must be folded to {COLOUR_LIMIT} (lossy)")
            if (o.get("translucent_pixels_dropped") or 0) > 200:
                reasons.append(f"{o['translucent_pixels_dropped']} translucent pixels would be dropped (OBJ art is binary alpha)")
        vs = u["visual_sha256"]
        alias_of = None
        if vs in seen_visual and seen_visual[vs] != u["id"]:
            alias_of = seen_visual[vs]
        else:
            seen_visual.setdefault(vs, u["id"])
        row["blockers"] = reasons
        if alias_of:
            row["decision"] = "duplicate_alias"
            row["rationale"] = f"identical rendering of {alias_of} (counted once; the earlier-tier copy is the one evaluated)"
        elif reasons:
            row["decision"] = "rejected"
            row["rationale"] = "; ".join(reasons)
        elif role:
            row["decision"] = "candidate"
        else:
            row["decision"] = "needs_visual_review"
            row["rationale"] = ("anonymous donor art decoded from real data; role unknown without a visual pass"
                                + (f" (dominant hue {o['hue']})" if o.get("hue") else ""))
        rows.append(row)
        if role and not reasons and not alias_of:
            roles[role].append(row)
    selection = {}
    for role in ROLES:
        # Richness-weighted, one best asset per donor library so the shortlist never collapses onto a single game.
        by_lib = defaultdict(list)
        for r in roles.get(role, []):
            by_lib[r["library"]].append(r)
        for lst in by_lib.values():
            lst.sort(key=lambda r: (-min(r["obj_tiles_est"] or 0, 96), -(r["frames"] or 0), r["colours"] or 0, r["id"]))
        picked = [lst[0] for _, lst in sorted(by_lib.items(), key=lambda kv: (TIER.get(kv[0], 3), kv[0]))][:MAX_SHORTLIST]
        if len(picked) < MAX_SHORTLIST:
            pool = [r for lst in by_lib.values() for r in lst if r not in picked]
            pool.sort(key=lambda r: (-min(r["obj_tiles_est"] or 0, 96), r["id"]))
            picked += pool[:MAX_SHORTLIST - len(picked)]
        for r in picked:
            r["decision"] = "shortlisted"
            r["rationale"] = (f"{role}: best decoded {r['library']} candidate by size/frames ({r['obj_tiles_est']} est. OBJ tiles <= {TILE_BUDGET}, "
                              f"{r['colours']} colours, {r['frames']} frame(s)); needs visual QA before use")
        for r in roles.get(role, []):
            if r not in picked:
                r["rationale"] = f"{role} candidate; ranked below the shortlist, kept as an alternate"
        selection[role] = [r["id"] for r in picked]
    # Anonymous donors (PMD / HGSS / Ranger / Diamond): provisional shortlist from the dominant-hue hint ONLY.
    hint = defaultdict(list)
    for r in rows:
        if r["decision"] == "needs_visual_review" and r["hue"] in HUE_ROLE_HINT and (r["frames"] or 0) >= 3 \
                and 8 <= (r["obj_tiles_est"] or 0) <= TILE_BUDGET and (r["colours"] or 99) <= COLOUR_LIMIT:
            h = HUE_ROLE_HINT[r["hue"]]
            if h in ROLES:
                hint[h].append(r)
    hue_shortlist = {}
    for role, lst in sorted(hint.items()):
        out = []
        for lib in ("pmd_sky", "hgss", "ranger2", "diamond"):
            cs = sorted((r for r in lst if r["library"] == lib), key=lambda r: (-(r["frames"] or 0), -(r["obj_tiles_est"] or 0), r["id"]))
            out += [{"id": r["id"], "frames": r["frames"], "obj_tiles_est": r["obj_tiles_est"], "colours": r["colours"], "hue": r["hue"]}
                    for r in cs[:2]]
        hue_shortlist[role] = out
    for r in rows:                     # keep full detail only where a decision is actionable; the catalog holds the rest
        if r["decision"] in ("rejected", "needs_visual_review", "duplicate_alias"):
            for k in ("sha256", "visual_sha256", "type", "name", "role_basis", "largest_frame", "max_oams"):
                r.pop(k, None)
    hint_counts = Counter((r["library"], r["hue"]) for r in rows if r["decision"] == "needs_visual_review")
    summary = {
        "rows": len(rows),
        "by_decision": dict(sorted(Counter(r["decision"] for r in rows).items())),
        "by_library": dict(sorted(Counter(r["library"] for r in rows).items())),
        "shortlist_by_role": {k: v for k, v in sorted(selection.items())},
        "needs_visual_review_by_library_hue": {f"{a}/{b}": n for (a, b), n in sorted(hint_counts.items(), key=lambda kv: str(kv[0]))},
        "hue_to_role_hint": HUE_ROLE_HINT,
        "provisional_hue_hint_shortlist": hue_shortlist,
    }
    return {
        "schema_version": 1,
        "generated_by": "tools/visual_overhaul/dau1_unlock.py matrix",
        "budgets": {"obj_tiles_per_sheet": TILE_BUDGET, "colours": COLOUR_LIMIT},
        "p1_p2_binding": {"status": "BLOCKED_INPUT",
                          "reason": "the B9 everyday-moves manifest (pokemon_opal_everyday_moves_b9_manifest_v2) that names the 19 P1 and 14 P2 moves is not in the repository or in the DAU1 package; "
                                    "candidates are therefore keyed by effect role, not by move"},
        "summary": summary,
        "candidates": rows,
    }


def matrix_markdown(m: dict) -> str:
    s = m["summary"]
    L = ["# DAU1 - refreshed cross-library candidate matrix", "",
         "Generated from the decoded `ASSET_CATALOG.json` by `tools/visual_overhaul/dau1_unlock.py matrix`. Nothing here is a visual approval; "
         "every shortlist entry still needs owner/visual QA, and licence status is unverified (`PROVENANCE.md`).", "",
         f"**P1/P2 move binding: {m['p1_p2_binding']['status']}** - {m['p1_p2_binding']['reason']}.", "",
         f"Budgets: <= {m['budgets']['obj_tiles_per_sheet']} OBJ tiles per sheet, <= {m['budgets']['colours']} colours (index 0 transparent).", "",
         f"Decoded, Opal-convertible rows evaluated: **{s['rows']}**. Decisions: " +
         ", ".join(f"{k} {v}" for k, v in s["by_decision"].items()) + ".", "",
         "## Rows per library", "", "| Library | Rows |", "|---|---:|"]
    L += [f"| {k} | {v} |" for k, v in s["by_library"].items()]
    L += ["", "## Shortlist by effect role (named donors only)", "",
          "| Role | Shortlisted | Library | Tiles~ | Colours | Frames | Rationale |", "|---|---|---|---:|---:|---:|---|"]
    by_id = {c["id"]: c for c in m["candidates"]}
    for role, ids in s["shortlist_by_role"].items():
        if not ids:
            L.append(f"| {role} | - | - | - | - | - | no decoded, in-budget named donor found |")
        for i in ids:
            c = by_id[i]
            L.append(f"| {role} | `{c['name']}` | {c['library']} | {c['obj_tiles_est']} | {c['colours']} | {c['frames']} | {c['rationale']} |")
    L += ["", "## Provisional shortlist from anonymous donors (role inferred from dominant hue ONLY)", "",
          "PMD / HGSS / Ranger / Diamond assets have no names, so these are *hints for a human visual pass*, not classifications. "
          "Up to two per library per role, >= 3 frames, 8..192 est. OBJ tiles, <= 15 colours.", "",
          "| Hinted role | Library | Unit | Frames | Tiles~ | Colours | Hue |", "|---|---|---|---:|---:|---:|---|"]
    for role, lst in s["provisional_hue_hint_shortlist"].items():
        for c in lst:
            L.append(f"| {role} | {c['id'].split(':', 1)[0]} | `{c['id'].split(':', 1)[1][-48:]}` | {c['frames']} | {c['obj_tiles_est']} | {c['colours']} | {c['hue']} |")
    L += ["", "## Anonymous decoded donors awaiting visual role assignment", "",
          "Counts of in-budget decoded assets whose role cannot be known from a name (hue is a hint, not a classification).", "",
          "| Library / dominant hue | Count |", "|---|---:|"]
    L += [f"| {k} | {v} |" for k, v in s["needs_visual_review_by_library_hue"].items()]
    rej = Counter()
    for c in m["candidates"]:
        if c["decision"] == "rejected":
            for b in c["blockers"]:
                rej[re.sub(r"\d+", "N", b)] += 1
    L += ["", "## Rejection reasons (all libraries)", "", "| Reason | Rows |", "|---|---:|"]
    L += [f"| {k} | {v} |" for k, v in rej.most_common()]
    L += ["", "Per-row data (ids, hashes, estimates, rationale) is in `candidate_matrix.json`."]
    return "\n".join(L) + "\n"
