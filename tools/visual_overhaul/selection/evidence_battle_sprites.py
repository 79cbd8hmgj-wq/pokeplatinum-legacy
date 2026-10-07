#!/usr/bin/env python3
"""Evidence provider: pokemon_battle_sprites (HGSS direct donor, Diamond control).

Reuses tools/visual_overhaul/audit_hgss_battle_sprites.py (classify/geometry_compare) and the committed
HGSS palette audits (HGSS_BATTLE_SPRITE_PALETTE_COMPATIBILITY / _ORDER). Read-only on donor checkouts.
Group relation = most severe per-view relation (ranks below); missing-native views are excluded.
Diamond PNG view order is inferred empirically (best permutation vs Platinum natives, recorded in inputs).
"""
from __future__ import annotations

import argparse
import collections
import importlib.util
import itertools
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image

from common import *  # noqa: F401,F403

PT = ROOT / "res" / "pokemon"
VIEWS = ("female_back.png", "male_back.png", "female_front.png", "male_front.png")
HG_REL = {"female_back.png": "female/back.png", "male_back.png": "male/back.png", "female_front.png": "female/front.png", "male_front.png": "male/front.png"}
RANK = {"identical": 0, "palette_only": 1, "art_diff_minor": 2, "art_diff_geometry_close": 3, "art_diff_geometry_review": 4}
MINOR_RATIO = jload(RULES_JSON)["thresholds"]["minor_diff_ratio"]
# HGSS otherpoke variant -> Platinum forms/<folder> (documented target-identity aliases)
ALIAS = {"normal": "base", "plant": "base", "altered": "base", "land": "base", "a": "base", "west": "base",
         "exclamation_mark": "exc", "question_mark": "que", "sunshine": "sunny",
         "east": "east_sea", "fridge": "frost", "lawnmower": "mow", "oven": "heat", "washer": "wash"}
SPECIES_ALIAS = {("castform", "sun"): "sunny", ("castform", "rain"): "rainy", ("castform", "ice"): "snowy"}


def load_audit():
    spec = importlib.util.spec_from_file_location("audit_hs", ROOT / "tools/visual_overhaul/audit_hgss_battle_sprites.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["audit_hs"] = m
    spec.loader.exec_module(m)
    return m


def git_head(repo: Path) -> str:
    return subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()


def to_relation(audit, pt: Path, dn: Path) -> tuple[str, dict]:
    st = audit.classify(pt, dn)
    if st in ("identical", "palette-metadata-only", "index-remap-only"):
        return "identical", {"audit_status": st}
    if st == "palette-only":
        return "palette_only", {"audit_status": st}
    if st == "art-diff":
        with Image.open(pt) as a_, Image.open(dn) as b_:
            ra, rb = audit.rendered_rgba(a_), audit.rendered_rgba(b_)
        px = [(ra[i:i + 4], rb[i:i + 4]) for i in range(0, len(ra), 4)]
        union = sum(1 for x, y in px if x[3] or y[3])
        ratio = sum(1 for x, y in px if x != y) / union if union else 0.0
        if ratio < MINOR_RATIO:
            return "art_diff_minor", {"audit_status": st, "diff_ratio": round(ratio, 4)}
        geo = audit.geometry_compare(pt, dn)
        rel = "art_diff_geometry_close" if geo.status == "geometry-close" else "art_diff_geometry_review"
        return rel, {"audit_status": st, "geometry": geo.status, "geometry_reasons": geo.reasons[:3], "diff_ratio": round(ratio, 4)}
    return "contract_mismatch", {"audit_status": st}


def aggregate(views: dict[str, dict]) -> tuple[str, list[str]]:
    comparable = [v for v in views.values() if v["relation"] in RANK]
    odd = [v for v in views.values() if v["relation"] == "contract_mismatch"]
    if odd:
        return "contract_mismatch", []
    if not comparable:
        return ("missing_in_native" if views else "unmeasured"), []
    rel = max((v["relation"] for v in comparable), key=lambda r: RANK[r])
    flags = []
    if rel == "art_diff_geometry_review":
        flags.append("geometry_review")
    return rel, flags


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hgss-root", required=True, type=Path)
    ap.add_argument("--diamond-root", required=True, type=Path)
    a = ap.parse_args()
    audit = load_audit()
    species = species_constants()
    groups = [g for g in jload(GROUPS_JSON)["groups"] if g["subsystem"] == "pokemon_battle_sprites"]
    pal = jload(VO / "HGSS_BATTLE_SPRITE_PALETTE_COMPATIBILITY.json")
    order = jload(VO / "HGSS_BATTLE_SPRITE_PALETTE_ORDER.json")
    pal_status = collections.defaultdict(dict)  # species const -> view -> status
    for e in pal["entries"]:
        pal_status[e["species"]][e["view"]] = e["status"]
    reorder = set(order["reorder_suspected_species"])
    ident_order = set(order["identity_order_candidate_species"])

    hg_pg = a.hgss_root / "files/poketool/pokegra/pokegra"
    hg_op = a.hgss_root / "files/poketool/pokegra/otherpoke"
    dp_pg = a.diamond_root / "files/poketool/pokegra/pokegra"

    # --- Diamond view-order inference (species 1..493, 6 narc members per species) ---
    def dp_png(sp, k):
        p = dp_pg / f"narc_{sp * 6 + k:04d}.png"
        return p if p.is_file() else None

    perm_score = collections.Counter()
    for sp in range(1, 494):
        pdir = PT / species[sp].removeprefix("SPECIES_").lower()
        hit = {}
        for vi in range(4):
            for k in range(4):
                pt, dn = pdir / VIEWS[vi], dp_png(sp, k)
                hit[(vi, k)] = bool(
                    dn is not None and pt.is_file() and pt.stat().st_size and dn.stat().st_size and audit.classify(pt, dn) == "identical"
                )
        for perm in itertools.permutations(range(4)):
            perm_score[perm] += sum(hit[(vi, k)] for vi, k in enumerate(perm))
    best_perm, best_hits = perm_score.most_common(1)[0]

    entries = {}
    for g in groups:
        gid = g["group_id"]
        views: dict[str, dict] = {}
        flags: list[str] = []
        detail: dict = {}
        if g["source_id"] == "hgss" and g["unit_kind"] == "species":
            sp = int(g["unit"].split("_")[1])
            const = species[sp] if sp < len(species) else None
            pdir = PT / const.removeprefix("SPECIES_").lower() if const else None
            for v in VIEWS:
                dn = hg_pg / f"{sp:04d}" / HG_REL[v]
                if not dn.is_file():
                    continue
                pt = pdir / v if pdir else None
                if pt is None or not pt.is_file():
                    views[v] = {"relation": "missing_in_native"}
                    continue
                rel, d = to_relation(audit, pt, dn)
                views[v] = {"relation": rel, **d}
            rel, flags = aggregate(views)
            if const:
                ps = pal_status.get(const, {})
                if any(s == "palette-mismatch" for s in ps.values()):
                    flags.append("palette_mismatch")
                if const in reorder:
                    flags = [f for f in flags if f != "palette_mismatch"] + ["palette_reorder_suspected"]
                detail["palette_audit"] = sorted(set(ps.values())) or None
                detail["palette_order"] = "reorder_suspected" if const in reorder else ("identity_order_candidate" if const in ident_order else None)
        elif g["source_id"] == "hgss":  # otherpoke forms
            name, _, var = g["unit"].removeprefix("form_").partition("_")
            if name == "egg":  # egg/<variant>.png single front image
                dn = hg_op / "egg" / (var + ".png")
                nat = PT / "egg" / ("front.png" if var == "normal" else f"forms/{var}/front.png")
                if dn.is_file():
                    views["front.png"] = {"relation": "missing_in_native"} if not nat.is_file() else {"relation": to_relation(audit, nat, dn)[0], "native": str(nat.relative_to(ROOT))}
                var = "__done__"
            # unit "form_<name>_<variant...>"; names are single tokens in HGSS otherpoke
            vdir = hg_op / name / var
            for hv, nv in (("front.png", "front.png"), ("back.png", "back.png")):
                dn = vdir / hv
                if not dn.is_file():
                    continue
                folder = SPECIES_ALIAS.get((name, var), ALIAS.get(var, var))
                cands = [PT / name / "forms" / folder / nv]
                if folder == "base":
                    cands.append(PT / name / ("male_" + nv))
                if name == "substitute":
                    cands = [PT / ".shared" / f"substitute_{nv}"]
                pt = next((c for c in cands if c.is_file()), None)
                if pt is None:
                    views[nv] = {"relation": "missing_in_native"}
                else:
                    rel, d = to_relation(audit, pt, dn)
                    views[nv] = {"relation": rel, "native": str(pt.relative_to(ROOT)), **d}
            rel, flags = aggregate(views)
        elif g["source_id"] == "diamond" and g["unit_kind"] == "species":
            sp = int(g["unit"].split("_")[1])
            const = species[sp] if sp < len(species) else None
            for vi, k in enumerate(best_perm):
                dn = dp_png(sp, k)
                if dn is None or not const:
                    continue
                pt = PT / const.removeprefix("SPECIES_").lower() / VIEWS[vi]
                if not pt.is_file():
                    views[VIEWS[vi]] = {"relation": "missing_in_native"}
                    continue
                rel, d = to_relation(audit, pt, dn)
                views[VIEWS[vi]] = {"relation": rel, **d}
            rel, flags = aggregate(views)
        else:  # Diamond otherpoke raw NCGR: control, not compared
            rel = "unmeasured"
        detail["views"] = {k: {kk: vv for kk, vv in v.items() if kk in ("relation", "audit_status", "geometry", "native")} for k, v in sorted(views.items())}
        entry = {"native_relation": rel, "member_digest": g["member_digest"], "detail": detail}
        if flags:
            entry["risk_flags"] = sorted(set(flags))
        entries[gid] = entry

    summary = collections.Counter(f'{k.split("/")[1]}:{v["native_relation"]}' for k, v in entries.items())
    doc = {
        "schema_version": 1,
        "subsystem": "pokemon_battle_sprites",
        "provider": "battle_sprites",
        "generated_by": "tools/visual_overhaul/selection/evidence_battle_sprites.py",
        "inputs": {
            "hgss_commit": git_head(a.hgss_root),
            "diamond_commit": git_head(a.diamond_root),
            "method": "audit_hgss_battle_sprites.classify/geometry_compare per view; palette flags from HGSS_BATTLE_SPRITE_PALETTE_{COMPATIBILITY,ORDER}.json",
            "diamond_view_order_perm": list(best_perm),
            "diamond_view_order_identical_hits": best_hits,
            "palette_audit_sha256": [file_sha256(VO / "HGSS_BATTLE_SPRITE_PALETTE_COMPATIBILITY.json"), file_sha256(VO / "HGSS_BATTLE_SPRITE_PALETTE_ORDER.json")],
        },
        "summary": dict(sorted(summary.items())),
        "entries": entries,
    }
    jdump(SEL / "evidence" / "pokemon_battle_sprites.json", doc)
    print(doc["summary"], "dp_perm", best_perm, best_hits)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
