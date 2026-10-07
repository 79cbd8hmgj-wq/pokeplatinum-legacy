#!/usr/bin/env python3
"""Technical recovery pass for Lane B PMD Sky .wan/.wte/.wtu/.wat/.wba resources.

Uses the SkyTemple file library (skytemple-files) as the reference decoder rather than a
bespoke implementation.  Every frame of every WAN is rendered; WTE textures are converted
to RGBA.  A resource is valid only if decode succeeds and at least one nonblank image is
produced.  WTU (texture-unit table) is a companion of a valid same-stem WTE.
No Platinum resources are modified.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def nonblank(im) -> bool:
    return im.convert("RGBA").getchannel("A").getbbox() is not None


def eval_wan(data: bytes) -> tuple[str, str]:
    from skytemple_files.graphics.wan_wat.handler import WanHandler
    w = WanHandler.deserialize(data)
    total = len(w.frames)
    ok = 0
    for f in w.frames:
        im, _ = w.render_frame(f)
        ok += nonblank(im)
    if not total:
        return "blank_render", "no frames"
    if not ok:
        return "blank_render", f"{total} frames all blank"
    return "valid_render", f"{ok}/{total} nonblank frames, {len(w.anim_groups)} animation groups"


def eval_wte(data: bytes) -> tuple[str, str]:
    from skytemple_files.graphics.wte.handler import WteHandler
    t = WteHandler.deserialize(data)
    if not t.has_image():
        return "blank_render", "no image"
    im = t.to_pil()
    if not nonblank(im.convert("RGBA")) and im.getbbox() is None:
        return "blank_render", "blank texture"
    return "valid_render", f"{t.width}x{t.height} texture"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--curation", type=Path, required=True)
    ap.add_argument("--pmd-root", type=Path, required=True)
    ap.add_argument("--write-json", type=Path, required=True)
    ap.add_argument("--write-md", type=Path, required=True)
    a = ap.parse_args()
    recs = json.loads(a.curation.read_text())["records"]
    todo = [r for r in recs if r["source_id"] == "pmd_sky" and r["review_status"] == "decode_issue"]
    rows = {}
    for r in todo:
        p = a.pmd_root / r["source_path"]
        ext = p.suffix
        try:
            if ext in (".wan", ".wat", ".wba"):
                st, det = eval_wan(p.read_bytes())
            elif ext == ".wte":
                st, det = eval_wte(p.read_bytes())
            elif ext == ".wtu":
                from skytemple_files.graphics.wtu.handler import WtuHandler
                WtuHandler.deserialize(p.read_bytes())
                st, det = "wtu_parsed", ""
            else:
                st, det = "unsupported_format", ext
        except Exception as e:  # noqa: BLE001
            st, det = "decode_failure", str(e)[:140]
        rows[r["asset_id"]] = {"asset_id": r["asset_id"], "source_path": r["source_path"], "suffix": ext,
                               "technical_state": st, "detail": det}
    valid_wte = {Path(x["source_path"]).with_suffix("").as_posix() for x in rows.values()
                 if x["suffix"] == ".wte" and x["technical_state"] == "valid_render"}
    for x in rows.values():
        if x["suffix"] == ".wtu" and x["technical_state"] == "wtu_parsed":
            if Path(x["source_path"]).with_suffix("").as_posix() in valid_wte:
                x["technical_state"], x["detail"] = "companion_of_valid", "texture-unit table of valid same-stem WTE"
            else:
                x["technical_state"], x["detail"] = "no_pair", "no valid same-stem WTE"
    out = sorted(rows.values(), key=lambda x: x["asset_id"])
    decisions = []
    for x in out:
        if x["technical_state"] == "valid_render":
            code, why = ("pmd_valid_render_plausible_use",
                         "PMD Sky resource decodes with the SkyTemple reference decoder to nonblank imagery (sprite/effect/texture material) with plausible Platinum use.")
        elif x["technical_state"] == "companion_of_valid":
            code, why = ("pmd_wtu_companion_of_valid_wte",
                         "Texture-unit table paired with a valid same-stem WTE texture; kept with its usable texture.")
        else:
            continue
        decisions.append({"asset_id": x["asset_id"], "review_status": "usable", "reason_code": code, "reason": why,
                          "technical_state": x["technical_state"], "detail": x["detail"]})
    states = Counter(x["technical_state"] for x in out)
    suffix_states = {f"{s}:{k}": v for (s, k), v in sorted(Counter((x["suffix"], x["technical_state"]) for x in out).items())}
    res = {"schema_version": 1, "scope": "lane_b_pmd_sky", "decoder": "skytemple-files 1.8.5",
           "asset_count": len(out), "technical_state_counts": dict(states),
           "suffix_state_counts": suffix_states, "records": out, "decisions": decisions}
    a.write_json.write_text(json.dumps(res, indent=1) + "\n")
    md = ["# Lane B PMD Sky Recovery", "",
          "Decode audit using the SkyTemple reference library. No Platinum resources are modified.", "",
          f"- Assets: **{len(out)}**", "", "| Suffix:state | Assets |", "|---|---:|"]
    md += [f"| {k} | {v} |" for k, v in suffix_states.items()]
    a.write_md.write_text("\n".join(md) + "\n")
    print(dict(states))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
