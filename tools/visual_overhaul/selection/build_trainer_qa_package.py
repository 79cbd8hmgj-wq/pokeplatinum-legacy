#!/usr/bin/env python3
"""Visual QA review package for the preferred trainer battle-sprite candidates.

Reads only committed artifacts (trainer ledger, HGSS decoded renders, Platinum PNGs). Writes under
docs/visual_overhaul/selection/review/trainer_sprites/: contact sheets, REVIEW_MANIFEST.json, REVIEW_CHECKLIST.md.
Metrics are advisory; nothing here promotes or imports anything. Decisions stay `pending_human_review`.
"""
from __future__ import annotations

import argparse
import collections
import subprocess

from PIL import Image, ImageDraw

from common import *  # noqa: F401,F403
import evidence_trainer_sprites as cmp

OUT = SEL / "review" / "trainer_sprites"
BG = (70, 70, 90, 255)
SCALE = 2
GAP = 4
NEGLIGIBLE_PIXELS = 40      # total changed pixels over all compared frames
NEGLIGIBLE_RATIO = 0.02     # ... and changed/opaque-union below this


def frames_rgba(im: Image.Image, fh: int) -> list[Image.Image]:
    out = []
    for f in cmp.split_frames(im, fh, 1):
        pal = f.getpalette()
        a = Image.new("RGBA", f.size, (0, 0, 0, 0))
        px = []
        for i in f.tobytes():
            px.append((0, 0, 0, 0) if i == 0 else (pal[3 * i], pal[3 * i + 1], pal[3 * i + 2], 255))
        a.putdata(px)
        out.append(a)
    return out


def q5(p):
    return (p[0] >> 3, p[1] >> 3, p[2] >> 3, p[3] and 255)


def frame_metrics(d: Image.Image, n: Image.Image) -> dict:
    A, B = list(d.getdata()), list(n.getdata())
    union = inter = diff = same_mask_color_diff = 0
    for x, y in zip(A, B):
        ox, oy = x[3] > 0, y[3] > 0
        if ox or oy:
            union += 1
        if ox and oy:
            inter += 1
        if (ox or oy) and q5(x) != q5(y):
            diff += 1
    mask_equal = all((x[3] > 0) == (y[3] > 0) for x, y in zip(A, B))
    db, nb = cmp.bbox([1 if p[3] else 0 for p in A], d.width, d.height), cmp.bbox([1 if p[3] else 0 for p in B], n.width, n.height)
    geo = None
    if db and nb:
        geo = {"bottom_shift": db[3] - nb[3], "center_shift": [((db[0] + db[2]) - (nb[0] + nb[2])) / 2, ((db[1] + db[3]) - (nb[1] + nb[3])) / 2],
               "bbox_size_delta": [(db[2] - db[0]) - (nb[2] - nb[0]), (db[3] - db[1]) - (nb[3] - nb[1])]}
    return {"changed_pixels": diff, "opaque_union": union, "diff_ratio": round(diff / union, 4) if union else 0.0,
            "mask_iou": round(inter / union, 3) if union else 1.0, "mask_equal": mask_equal,
            "kind": "identical" if diff == 0 else ("recolor_only" if mask_equal else "artwork"), "geometry": geo}


def diff_image(d: Image.Image, n: Image.Image) -> Image.Image:
    out = Image.new("RGBA", d.size, (30, 30, 40, 255))
    px = []
    for x, y in zip(d.getdata(), n.getdata()):
        ox, oy = x[3] > 0, y[3] > 0
        if not (ox or oy):
            px.append((30, 30, 40, 255))
        elif q5(x) == q5(y):
            px.append((90, 90, 100, 255))
        elif ox and oy:
            px.append((255, 200, 0, 255))      # both opaque, colour differs
        elif ox:
            px.append((0, 220, 120, 255))      # HGSS only
        else:
            px.append((230, 40, 160, 255))     # Platinum only
    out.putdata(px)
    return out


def strip(frames, scale=SCALE):
    w = sum(f.width * scale + GAP for f in frames)
    h = max(f.height for f in frames) * scale
    s = Image.new("RGBA", (w, h), BG)
    x = 0
    for f in frames:
        t = Image.new("RGBA", f.size, BG)
        t.alpha_composite(f)
        s.paste(t.resize((f.width * scale, f.height * scale), Image.NEAREST), (x, 0))
        x += f.width * scale + GAP
    return s


def block(title, plat, hg, diffs, notes):
    sp, sh, sd = strip(plat), strip(hg), strip(diffs)
    if len(plat) == 1:  # single frame: Platinum | HGSS | diff side by side
        w = max(sp.width * 3 + 2 * GAP, 330)
        b = Image.new("RGBA", (w, sp.height + 28), (40, 40, 52, 255))
        dr = ImageDraw.Draw(b)
        dr.text((2, 1), title, fill=(255, 255, 255, 255))
        for k, (lab, im) in enumerate((("Platinum", sp), ("HGSS", sh), ("diff", sd))):
            b.paste(im, (k * (sp.width + GAP), 14))
            dr.text((k * (sp.width + GAP) + 2, 15), lab, fill=(255, 255, 160, 255))
        dr.text((2, sp.height + 16), notes, fill=(200, 200, 200, 255))
        return b
    w = max(sp.width, 520)
    h = 14 + sp.height + 3 + sh.height + 3 + sd.height + 12 + 6
    b = Image.new("RGBA", (w, h), (40, 40, 52, 255))
    dr = ImageDraw.Draw(b)
    dr.text((2, 1), title, fill=(255, 255, 255, 255))
    y = 14
    for lab, s in (("Platinum", sp), ("HGSS", sh), ("diff", sd)):
        b.paste(s, (0, y))
        dr.text((w - 52, y + 2), lab, fill=(255, 255, 160, 255))
        y += s.height + 3
    dr.text((2, y), notes, fill=(200, 200, 200, 255))
    return b


def paginate(blocks, name, max_w=1700, max_h=1700):
    """Row-pack blocks left to right (wrapping at max_w), paginate at max_h."""
    rows, cur, w = [], [], 0
    for b in blocks:
        if cur and w + b.width + 6 > max_w:
            rows.append(cur)
            cur, w = [], 0
        cur.append(b)
        w += b.width + 6
    if cur:
        rows.append(cur)
    pages, pg, h = [], [], 0
    for r in rows:
        rh = max(b.height for b in r) + 6
        if pg and h + rh > max_h:
            pages.append(pg)
            pg, h = [], 0
        pg.append(r)
        h += rh
    if pg:
        pages.append(pg)
    files = []
    for i, pgrows in enumerate(pages, 1):
        W = max(sum(b.width + 6 for b in r) for r in pgrows)
        H = sum(max(b.height for b in r) + 6 for r in pgrows)
        im = Image.new("RGBA", (W, H), (20, 20, 28, 255))
        y = 0
        for r in pgrows:
            x = 0
            for b in r:
                im.paste(b, (x, y))
                x += b.width + 6
            y += max(b.height for b in r) + 6
        fn = f"{name}_{i:02d}.png"
        im.convert("RGB").save(OUT / fn, optimize=True)
        files.append(fn)
    return files


def write_checklist(doc: dict) -> None:
    c = doc["counts"]
    L = ["# Trainer Sprite Visual QA Checklist", "",
         "Status: **pending human review**. Nothing is promoted or imported; automated metrics only describe *difference*, not *quality*.", "",
         f"- Candidates under review (currently `preferred`): **{c['candidates']}** ({c['front']} front, {c['back']} back)",
         f"- Needing later-frame inspection (frame 0 identical, a later frame differs): **{c['later_frame_inspection']}**",
         f"- Automated classes: {c['by_class']}",
         f"- Withdrawn from the earlier 21 after a decoder fix: **{doc['withdrawn_after_decoder_fix']['count']}** (see below)", "",
         "Contact sheets: " + ", ".join(f"`{f}`" for f in doc["contact_sheets"]["front"] + doc["contact_sheets"]["back"]) +
         ". Legend: " + doc["legend"]["diff"] + ".", "",
         "## Review criteria (per candidate)", "",
         "1. Same character/class identity as Platinum's (a redraw changes the class's look, not just quality).",
         "2. Art quality and consistency with neighbouring Platinum trainer art (outline, palette, shading).",
         "3. All animation frames present, in the same order, with no popping (frame count must match or exceed Platinum's).",
         "4. Geometry: feet/bottom anchor and centre within a few px of Platinum (battle placement is not re-tuned).",
         "5. Palette: 16-colour limit and index 0 transparency preserved (decoded palette fits Platinum's trainer palette slot).", "",
         "## Candidates", "",
         "| Done | ID | View | Class | Automated class | Changed px / % | Frames (HGSS/Plat) | Identical frames | Verdict |",
         "|---|---|---|---|---|---|---|---|---|"]
    for m in doc["candidates"]:
        t = m["totals"]
        L.append(f"| [ ] | {m['candidate_id'].split('/')[-1]} | {m['view']} | {m['platinum_target_class']} | {m['automated_class']} | "
                 f"{t['changed_pixels']} / {t['diff_ratio']:.1%} | {m['dimensions']['frames_hgss']}/{m['dimensions']['frames_platinum']} | "
                 f"{m['identical_frame_indices']} | _pending_ |")
    w = doc["withdrawn_after_decoder_fix"]
    L += ["", "## Withdrawn after decoder fix", "",
          w["reason"] + " After decoding each cell from its own VRAM-transfer chunk, these now compare as follows:", "",
          "| ID | Class | Now | Relation |", "|---|---|---|---|"]
    for e in w["entries"]:
        L.append(f"| {e['candidate_id'].split('/')[-1]} | {e['platinum_class']} | {e['now_role']} | {e['now_relation']} |")
    (OUT / "REVIEW_CHECKLIST.md").write_text("\n".join(L) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prior-ref", help="git ref of an earlier ledger; candidates preferred there but not now are listed as withdrawn")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    led = jload(SEL / "ledgers" / "trainer_battle_sprites.json")
    cat = {a["source_path"]: a for a in jload(EXT_DIR / "hgss_trainer_sprites" / "CATALOG.json")["assets"]}
    align = jload(SEL / "alignment" / "trainer_classes.json")
    cands = sorted([d for d in led["decisions"] if d["role"] == "preferred"], key=lambda d: d["group_id"])
    manifest = []
    blocks = {"front": [], "back": []}
    for d in cands:
        unit = d["asset_identity"]["unit"]
        _, view, idx = unit.split("_")
        sp = d["asset_identity"]["sample_paths"][0]
        asset = cat[sp]
        det = d["visual_evidence"]["detail"]
        pclass = det["platinum_class"]
        fh = asset["source_metadata"]["cell_dims"][0][1]
        donor_im = Image.open(ROOT / asset["render_path"])
        nat_path = ROOT / det["native_path"]
        nat_im = Image.open(nat_path)
        df, nf = frames_rgba(donor_im, fh), frames_rgba(nat_im, fh)
        n = min(len(df), len(nf))
        per = [frame_metrics(df[i], nf[i]) for i in range(n)]
        diffs = [diff_image(df[i], nf[i]) for i in range(n)]
        # frame reorder probe: is each donor frame pixel-identical to *some* native frame?
        def sig(f):
            return tuple(q5(p) for p in f.getdata())
        nsig = {sig(f): i for i, f in enumerate(nf)}
        match_any = [nsig.get(sig(f)) for f in df]
        changed = sum(m["changed_pixels"] for m in per)
        union = sum(m["opaque_union"] for m in per)
        ratio = changed / union if union else 0.0
        ident = [i for i, m in enumerate(per) if m["kind"] == "identical"]
        later_only = bool(per) and per[0]["kind"] == "identical" and len(ident) < n
        kinds = collections.Counter(m["kind"] for m in per)
        if changed == 0 and len(df) <= len(nf):
            cls = "identical"
        elif changed <= NEGLIGIBLE_PIXELS and ratio < NEGLIGIBLE_RATIO:
            cls = "effectively_negligible"
        elif later_only:
            cls = "later_frames_differ"
        elif kinds.get("artwork") and per[0]["mask_iou"] < 0.7:
            cls = "redrawn_artwork"
        elif kinds.get("artwork"):
            cls = "artwork_changed"
        else:
            cls = "recolor_only"
        title = f"{unit.split('_')[1]} {idx}  {pclass}  [{d['target_id'].split('/')[-1]}]"
        notes = f"frames {len(df)}v{len(nf)}  changed {changed}px ({ratio:.1%})  class={cls}  identical frames {ident}"
        blocks[view].append((later_only, block(title, nf[:n], df[:n], diffs, notes)))
        manifest.append({
            "candidate_id": d["group_id"], "view": view, "hgss_class_index": idx, "hgss_name": align["hgss_" + view][idx]["name"],
            "platinum_target_class": pclass, "target_id": d["target_id"], "alignment_method": det["alignment_method"],
            "hgss_source_path": sp, "hgss_render": asset["render_path"], "platinum_png": det["native_path"],
            "dimensions": {"hgss": list(donor_im.size), "platinum": list(nat_im.size), "frame_height": fh,
                           "frames_hgss": len(df), "frames_platinum": len(nf)},
            "frames_compared": n, "frame_metrics": per, "identical_frame_indices": ident,
            "first_frame_identical": bool(per and per[0]["kind"] == "identical"),
            "requires_later_frame_inspection": later_only,
            "donor_frames_identical_to_some_native_frame": match_any,
            "totals": {"changed_pixels": changed, "opaque_union": union, "diff_ratio": round(ratio, 4)},
            "change_kind_counts": dict(kinds), "automated_class": cls,
            "palette_only": cls == "recolor_only", "risk_flags": d["visual_evidence"]["risk_flags"], "risk": d["scores"]["risk"],
            "ledger_relation": d["visual_evidence"]["native_relation"], "needs_runtime_validation": d["needs_runtime_validation"],
            "review": {"status": "pending_human_review", "verdict": None, "notes": None},
        })
    withdrawn = []
    if args.prior_ref:
        prior = json.loads(subprocess.check_output(["git", "show", f"{args.prior_ref}:docs/visual_overhaul/selection/ledgers/trainer_battle_sprites.json"], cwd=ROOT, text=True))
        now = {d["group_id"]: d for d in led["decisions"]}
        for d in prior["decisions"]:
            if d["role"] == "preferred" and now[d["group_id"]]["role"] != "preferred":
                n_ = now[d["group_id"]]
                withdrawn.append({"candidate_id": d["group_id"], "platinum_class": d["visual_evidence"]["detail"]["platinum_class"],
                                  "now_role": n_["role"], "now_reason": n_["reason_code"], "now_relation": n_["visual_evidence"]["native_relation"]})
    sheets = {}
    sheets["front"] = paginate([b for _, b in blocks["front"]], "front")
    sheets["back"] = paginate([b for _, b in blocks["back"]], "back") if blocks["back"] else []
    doc = {"schema_version": 1, "review_of": "trainer_battle_sprites preferred candidates", "rules_version": led["rules_version"],
           "ledger_sha256": file_sha256(SEL / "ledgers" / "trainer_battle_sprites.json"),
           "legend": {"diff": "yellow=both opaque but colour differs, green=HGSS-only pixel, magenta=Platinum-only pixel, grey=same, comparison in BGR555 space"},
           "thresholds": {"negligible_changed_pixels": NEGLIGIBLE_PIXELS, "negligible_ratio": NEGLIGIBLE_RATIO},
           "contact_sheets": sheets, "counts": {"candidates": len(manifest), "front": len(blocks["front"]), "back": len(blocks["back"]),
                                                 "later_frame_inspection": sum(m["requires_later_frame_inspection"] for m in manifest),
                                                 "by_class": dict(collections.Counter(m["automated_class"] for m in manifest))},
           "withdrawn_after_decoder_fix": {"prior_ref": args.prior_ref, "count": len(withdrawn), "entries": withdrawn,
                                           "reason": "Earlier renders ignored the NCER per-cell VRAM transfer table, so later animation frames were mis-decoded."},
           "candidates": manifest}
    jdump(OUT / "REVIEW_MANIFEST.json", doc)
    write_checklist(doc)
    print(json.dumps(doc["counts"]), sheets)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
