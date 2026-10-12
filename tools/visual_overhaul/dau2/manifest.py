"""Import and bind the original B9 v2 move manifest (planning input only - no move or script is touched).

The attached manifest is copied byte-for-byte into ``docs/visual_overhaul/asset_unlock/dau2/source/`` and pinned by SHA-256.
``bind()`` resolves each of the 33 P1/P2 moves to the repository's existing move directory/animation script and records every
discrepancy it can detect instead of normalising it away.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

PINNED_SHA256 = "419c17818fbdabf20bf65b729ef40bd123c09899398c75fdb0258a8c8561be37"
EXPECTED = {"P0_early_frequent": 19, "P1_mid_staples": 19, "P2_status_utility": 14}
# Manifest spelling -> repository directory, where plain snake_casing does not match.
SLUG_ALIAS = {"ThunderShock": "thunder_shock", "BubbleBeam": "bubble_beam"}


class ManifestError(Exception):
    pass


def slug(name: str) -> str:
    return SLUG_ALIAS.get(name) or re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    digest = sha256_file(path)
    if digest != PINNED_SHA256:
        raise ManifestError(f"{path}: sha256 {digest} != pinned {PINNED_SHA256}")
    doc = json.loads(path.read_text())
    tiers = {}
    for m in doc["moves"]:
        tiers.setdefault(m["tier"], []).append(m["move"])
    if {k: len(v) for k, v in tiers.items()} != EXPECTED:
        raise ManifestError(f"tier counts {({k: len(v) for k, v in tiers.items()})} != {EXPECTED}")
    names = [m["move"] for m in doc["moves"]]
    if len(set(names)) != len(names):
        raise ManifestError("duplicate move names in manifest")
    return doc


def parse_index_md(text: str) -> dict[str, dict]:
    """``- Headbutt — heavy_contact: shoulder/head impact`` rows of the recovered P1_P2_MOVE_INDEX.md -> {tier: {move: (role, intent)}}."""
    out: dict[str, dict] = {}
    tier = None
    for line in text.splitlines():
        if line.startswith("## P1"):
            tier = "P1_mid_staples"
        elif line.startswith("## P2"):
            tier = "P2_status_utility"
        m = re.match(r"- (.+?) — (\w+): (.+)$", line)
        if tier and m:
            out.setdefault(tier, {})[m.group(1)] = (m.group(2), m.group(3))
    return out


def bind(doc: dict, root: Path, index_md: str | None = None) -> dict:
    """Resolve P1/P2 moves against the repository.  Returns {'moves': [...], 'discrepancies': [...], 'summary': {...}}."""
    disc: list[dict] = []
    cue = {}
    cp = root / "docs/visual_overhaul/opal_b2_b8/cue_trace_baseline.json"
    if cp.exists():
        cue = json.loads(cp.read_text())
    p0_repo = {}
    mp = root / "docs/visual_overhaul/opal_b9/candidate_matrix.json"
    if mp.exists():
        p0_repo = {r["move"]: r for r in json.loads(mp.read_text()).get("per_move", [])}
    b2 = {}
    bp = root / "docs/visual_overhaul/B2_B8_MOVE_ARCHETYPE_MAPPING.json"
    if bp.exists():
        b2 = {a["move"]: a for a in json.loads(bp.read_text())["assignments"]}
    idx = parse_index_md(index_md) if index_md else {}
    rows = []
    for m in doc["moves"]:
        s = slug(m["move"])
        d = root / "res/moves" / s
        anim = d / "anim.s"
        row = {"move": m["move"], "tier": m["tier"], "template": m["template"], "visual_intent": m["visual_intent"],
               "slug": s, "move_dir_exists": d.is_dir(), "anim_script": f"res/moves/{s}/anim.s" if anim.exists() else None,
               "anim_script_sha256": sha256_file(anim) if anim.exists() else None,
               "data_json": f"res/moves/{s}/data.json" if (d / "data.json").exists() else None,
               "opal_cue_baseline_entry": s in cue, "b2_b8_assignment": b2.get(s, {}).get("archetype"),
               "manifest_status": m["status"], "manifest_source_animation": m["source_animation"]}
        if m["move"] != s and m["move"].lower().replace(" ", "_") != s:
            disc.append({"move": m["move"], "kind": "NAME_ALIAS", "detail": f"manifest spelling {m['move']!r} maps to repository directory res/moves/{s}/ (explicit alias)"})
        if not anim.exists():
            disc.append({"move": m["move"], "kind": "MISSING_SCRIPT", "detail": f"res/moves/{s}/anim.s not found"})
        if m["tier"] != "P0_early_frequent":
            if s in cue:
                disc.append({"move": m["move"], "kind": "ALREADY_OPAL_CUED", "detail": "an Opal cue-trace baseline entry exists - P1/P2 target already carries Opal cues; audit before replacing"})
            if s in b2:
                disc.append({"move": m["move"], "kind": "B2_B8_OVERLAP", "detail": f"already assigned archetype {b2[s]['archetype']!r} in the B2-B8 mapping"})
            ix = idx.get(m["tier"], {}).get(m["move"])
            if idx and ix is None:
                disc.append({"move": m["move"], "kind": "INDEX_MISSING", "detail": "move not present in recovered P1_P2_MOVE_INDEX.md"})
            elif ix and (ix[0] != m["template"] or ix[1] != m["visual_intent"]):
                disc.append({"move": m["move"], "kind": "INDEX_MISMATCH", "detail": f"index says {ix}, manifest says {(m['template'], m['visual_intent'])}"})
        rows.append(row)
    p0 = [r for r in rows if r["tier"] == "P0_early_frequent"]
    if p0_repo:
        repo_p0 = {slug(k) for k in p0_repo}
        man_p0 = {r["slug"] for r in p0}
        if repo_p0 != man_p0:
            disc.append({"move": "(P0 set)", "kind": "P0_SET_DIFFERS", "detail": f"manifest-only {sorted(man_p0 - repo_p0)}; repository-only {sorted(repo_p0 - man_p0)}"})
    for r in rows:
        if r["manifest_status"] != "design_proposal_unverified":
            disc.append({"move": r["move"], "kind": "STATUS_CHANGED", "detail": r["manifest_status"]})
    disc.append({"move": "(all)", "kind": "SOURCE_ANIMATION_UNRESOLVED", "detail": "every manifest entry carries source_animation='locate_in_pr110_head'; resolved here to the repository's res/moves/<slug>/anim.s"})
    summary = {"moves": len(rows), "by_tier": {t: sum(1 for r in rows if r["tier"] == t) for t in EXPECTED},
               "p1_p2_scripts_found": sum(1 for r in rows if r["tier"] != "P0_early_frequent" and r["anim_script"]),
               "p1_p2_total": sum(1 for r in rows if r["tier"] != "P0_early_frequent")}
    return {"moves": rows, "discrepancies": disc, "summary": summary}
