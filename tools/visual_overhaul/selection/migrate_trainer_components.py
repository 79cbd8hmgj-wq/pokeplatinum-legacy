#!/usr/bin/env python3
"""First migration of the trainer work onto the use-outcome model (deterministic; rewrites components/trainer_battle_sprites.json).

Direct-replacement verdicts are NOT touched (ledgers/review decisions are read-only here). This adds, on the contribution axis only:
  * Ace Trainer M/F: proposed component_donor records (HGSS group stays keep_platinum as a whole asset)
  * Arcade Star / Young Couple: digest-bound "no component found" reviews (they stay native_keep)
All records are status `proposed`: nothing here is human approval.
"""
from __future__ import annotations

import sys

from PIL import Image

from common import *  # noqa: F401,F403
import outcomes
import rules as engine

SUB = "trainer_battle_sprites"
RENDERS = "docs/visual_overhaul/catalog_extensions/hgss_trainer_sprites/renders"
EVID_DIR = "docs/visual_overhaul/selection/components/evidence"
REVIEWER = "claude (automated visual assessment; not human-approved)"
DATE = "2026-10-07"


def sha16(p: str) -> str:
    return file_sha256(ROOT / p)[:16]


def group(gid):
    return next(g for g in jload(GROUPS_JSON)["groups"] if g["group_id"] == gid)


def entry_digest(gid):
    return engine.evidence_digest(jload(SEL / "evidence" / f"{SUB}.json")["entries"][gid])


def source_block(gid):
    g = group(gid)
    cat = outcomes.catalog_index()
    assets = []
    for aid, grp in sorted(_membership().items()):
        if grp != gid:
            continue
        a = cat[aid]
        assets.append({"asset_id": aid, "source_path": a["source_path"], "source_commit": a["source_metadata"]["source_commit"],
                       "render_path": a["render_path"], "render_sha256": a["source_metadata"]["render_sha256"]})
    return {"group_id": gid, "source_id": g["source_id"], "member_digest": g["member_digest"], "assets": assets}


_M = None


def _membership():
    global _M
    if _M is None:
        import build_candidate_groups
        _M = build_candidate_groups.build(want_membership=True)["_membership"]
    return _M


def compare_png(pairs, out):
    W = Image.new("RGBA", (80 * 5 * len(pairs) * 2 + 10 * len(pairs), 80 * 5), (120, 120, 120, 255))
    x = 0
    for nat, don in pairs:
        for p in (nat, don):
            t = Image.open(ROOT / p).convert("RGBA").crop((0, 0, 80, 80)).resize((400, 400), Image.NEAREST)
            W.paste(t, (x, 0), t)
            x += 400
        x += 10
    (ROOT / out).parent.mkdir(parents=True, exist_ok=True)
    W.save(ROOT / out)


def ace(idx, tclass, gender, comps):
    gid = f"{SUB}/hgss/hgss_front_{idx}"
    nat = f"res/trainers/classes/{tclass}/front.png"
    don = f"{RENDERS}/front_{idx}.png"
    cmp_png = f"{EVID_DIR}/{tclass}_platinum_vs_hgss.png"
    compare_png([(nat, don)], cmp_png)
    recs = []
    for n, c in enumerate(comps, 1):
        recs.append({
            "record_id": f"uc:{SUB}/tc_{tclass}/{n:02d}",
            "outcome": "component_donor",
            "status": "proposed",
            "proposed_by": REVIEWER,
            "source": source_block(gid),
            "target": {"subsystem": SUB, "target_id": f"{SUB}/tc_{tclass}", "native_ref": {"path": nat, "sha256": sha16(nat)}},
            "tags": c["tags"],
            "component": {"property": c["property"], "region": None, "views": ["front"]},
            "pixel_use": "derived",
            "constraints": [
                "80x80 single-cell Platinum front contract (res/trainers/classes/<class>/front.png); no cell/animation changes",
                "must reuse the Platinum 16-color palette row of the target (no new colors introduced beyond the existing palette budget)",
                "Platinum/Sinnoh class identity stays authoritative: hair, outfit colorway and silhouette remain Platinum-native (human verdict keep_platinum on the whole HGSS asset)",
            ] + c.get("constraints", []),
            "adaptation": c["adaptation"],
            "evidence": {
                "kind": "render_comparison",
                "refs": [nat, don, cmp_png],
                "evidence_entry_digest": entry_digest(gid),
                "summary": c["evidence"],
            },
            "confidence": c["confidence"],
            "risk": c["risk"],
            "reason": c["reason"],
        })
    return recs


def main() -> int:
    recs = []
    recs += ace("024", "ace_trainer_male", "m", [
        {"tags": ["clothing_detail", "shading"],
         "property": "HGSS jacket treatment: 3-tone fold shading, centre-zip highlight line and hem seam on the torso/sleeves",
         "adaptation": ["re-express the fold/zip shading in the Platinum brown torso+sleeve ramp (map HGSS dark/mid/light to the existing Platinum brown ramp)",
                        "paint on the Platinum silhouette; do not import the HGSS jacket shape or midriff coverage"],
         "evidence": "Platinum torso/sleeves are largely 2-tone flat fills; HGSS render shows 3-tone folds and a zip/hem highlight on a comparable pose region. Visual comparison only; no pixel-level overlay measured.",
         "confidence": "medium", "risk": "medium",
         "reason": "Adds depth to the Platinum outfit without changing the Sinnoh design the owner chose to keep."},
        {"tags": ["accessory"],
         "property": "Fingerless gloves on both hands",
         "adaptation": ["add glove shapes to the Platinum hand regions using existing outline/dark palette indices", "hand positions differ from HGSS pose; redraw rather than copy"],
         "evidence": "HGSS render shows fingerless gloves; Platinum hands are bare skin tone. Visual comparison only.",
         "confidence": "low", "risk": "low",
         "reason": "Small accessory that reads as an upgrade; optional and independently rejectable."},
    ])
    recs += ace("025", "ace_trainer_female", "f", [
        {"tags": ["shading"],
         "property": "Hair mass highlight banding (ponytail/crown highlight clusters)",
         "adaptation": ["re-derive highlight clusters on the Platinum green hair using its existing 3 greens", "keep Platinum hair outline and silhouette"],
         "evidence": "HGSS hair uses clustered highlight bands on a dark base; Platinum hair is a flatter two-green fill. Visual comparison only.",
         "confidence": "low", "risk": "low",
         "reason": "Hair is the most visible low-detail area of the Platinum sprite."},
        {"tags": ["clothing_detail", "shading"],
         "property": "Jacket collar, zip seam and skirt-hem highlight detail",
         "adaptation": ["translate collar/seam highlights into the Platinum brown/orange ramp", "do not import the HGSS jacket/skirt silhouette or boot shape"],
         "evidence": "HGSS render has defined collar, zip seam and hem highlights absent in the Platinum two-tone outfit. Visual comparison only.",
         "confidence": "low", "risk": "medium",
         "reason": "Outfit readability; same rationale as the male jacket treatment."},
    ])
    reviews = []
    for idx, tclass, note in (
        ("101", "arcade_star", "Only frames 4-6 differ (768 changed px each, identical-looking art); the HGSS sheet is 1px taller, so the difference is a positional/row artifact, not new art. No component worth extracting; stays native_keep."),
        ("122", "young_couple", "Recolor-only (7.1% changed px): outfit colorway change on identical line art. Platinum colorway is the class identity; no pose/shading/detail component beyond a palette swap that adds nothing. Stays native_keep."),
    ):
        gid = f"{SUB}/hgss/hgss_front_{idx}"
        g = group(gid)
        reviews.append({"group_id": gid, "target_id": g["target_id"], "member_digest": g["member_digest"], "evidence_digest": entry_digest(gid),
                        "finding": "none_found", "note": note, "reviewer": REVIEWER, "reviewed_at": DATE,
                        "basis": [f"res/trainers/classes/{tclass}/front.png", f"{RENDERS}/front_{idx}.png"]})
    for gid in (f"{SUB}/hgss/hgss_front_024", f"{SUB}/hgss/hgss_front_025"):
        g = group(gid)
        reviews.append({"group_id": gid, "target_id": g["target_id"], "member_digest": g["member_digest"], "evidence_digest": entry_digest(gid),
                        "finding": "records_proposed", "note": "Whole-asset replacement stays keep_platinum (human verdict); component candidates proposed on the contribution axis.",
                        "reviewer": REVIEWER, "reviewed_at": DATE, "basis": [f"{EVID_DIR}/{'ace_trainer_male' if gid.endswith('024') else 'ace_trainer_female'}_platinum_vs_hgss.png"]})
    reviews.sort(key=lambda r: r["group_id"])
    doc = {"schema_version": 1, "subsystem": SUB, "records": recs, "composites": [], "component_reviews": reviews}
    outcomes.COMP_DIR.mkdir(parents=True, exist_ok=True)
    jdump(outcomes.comp_path(SUB), doc)
    print(f"{len(recs)} records, {len(reviews)} component reviews")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
