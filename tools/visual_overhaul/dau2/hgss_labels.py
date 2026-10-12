"""Evidence-tiered labels for HGSS Nitro cell-bank containers.  UNIDENTIFIED containers are never selected automatically.

HGSS ``files/a/X/Y/Z`` containers have numeric names only.  A container is *identified* when (in decreasing strength):
  OWNER_LABEL       a human recorded a label in ``hgss_cell_bank_label_overrides.json`` (the workflow for continuing the labelling);
  NAMED_CONTAINER   the container has a real name (``files/data/slot.narc``, ``files/pbr/zukan.narc`` ...);
  SOURCE_REFERENCE  the decomp source references ``NARC_a_X_Y_Z`` from named source files (category from those file names).
Everything else is ``UNIDENTIFIED``.  Only the categories in ``AUTO_ELIGIBLE`` may enter the automatic candidate selection; a
source reference proves *where the container is used*, not what each bank looks like, so the label is the container's, and the
matrix still needs a visual pass before anything is chosen.
"""
from __future__ import annotations

import json
import os
import re
from collections import Counter
from pathlib import Path

AUTO_ELIGIBLE = {"battle_move_effect", "field_weather_effect"}
CATEGORIES = ["battle_move_effect", "field_weather_effect", "battle_ui", "pokemon_graphic", "menu_ui", "minigame", "underground", "cutin_ui",
              "pbr_interface", "demo", "unidentified"]
NAMED = {"slot.narc": ("minigame", "slot machine"), "weather_sys.narc": ("field_weather_effect", "weather system sprites"),
         "ug_trap.narc": ("underground", "underground trap sprites"), "field_cutin.narc": ("cutin_ui", "field cut-in"),
         "batt_obj.narc": ("pbr_interface", "Pokemon Battle Revolution battle objects"), "poketch.narc": ("pbr_interface", "PBR interface"),
         "zukan.narc": ("pbr_interface", "PBR interface"), "pst_gra.narc": ("pbr_interface", "PBR interface"),
         "bag_gra.narc": ("pbr_interface", "PBR interface"), "plist_gra.narc": ("pbr_interface", "PBR interface")}
KEYWORDS = [("pokepic", "pokemon_graphic"), ("pokemon.c", "pokemon_graphic"), ("battle_", "battle_ui"), ("hall_of_fame", "demo"),
            ("menu", "menu_ui"), ("shop", "menu_ui"), ("naming", "menu_ui"), ("options", "menu_ui"), ("save", "menu_ui"), ("start_menu", "menu_ui"),
            ("alph_puzzle", "minigame"), ("pokegear", "menu_ui"), ("party", "menu_ui"), ("bag", "menu_ui"), ("trainer_card", "menu_ui")]


def reference_index(h: Path) -> dict[str, set[str]]:
    ref: dict[str, set[str]] = {}
    pat = re.compile(r"NARC_a_\d+_\d+_\d+")
    for base in ("src", "include", "asm", "lib/src", "sub", "files/battledata"):
        for dp, dn, fn in os.walk(h / base):
            dn.sort()
            for f in sorted(fn):
                if f.endswith((".c", ".h", ".s", ".inc")):
                    p = Path(dp) / f
                    if p.name == "filesystem_files_def.h":
                        continue
                    for m in set(pat.findall(p.read_text(errors="ignore"))):
                        ref.setdefault(m, set()).add(p.relative_to(h).as_posix())
    return ref


def classify(container: str, refs: list[str]) -> tuple[str, str, str, str]:
    """-> (category, basis, label, evidence)"""
    name = container.rsplit("/", 1)[-1]
    if container.startswith("files/pbr/") and name not in NAMED:
        return "pbr_interface", "NAMED_CONTAINER", "Pokemon Battle Revolution interface data (files/pbr)", container
    if container.startswith("files/data/") and name not in NAMED:
        if "ug" in name or "underg" in name:
            return "underground", "NAMED_CONTAINER", f"underground feature ({name})", container
        if "wifi" in name or "trade" in name:
            return "menu_ui", "NAMED_CONTAINER", f"communication menu ({name})", container
    if name in NAMED:
        c, lab = NAMED[name]
        return c, "NAMED_CONTAINER", lab, container
    if refs:
        names = [r.rsplit("/", 1)[-1] for r in refs]
        for kw, cat in KEYWORDS:
            if any(kw in n for n in names):
                return cat, "SOURCE_REFERENCE", f"used by {', '.join(names[:3])}", "; ".join(refs[:4])
        return "unidentified", "SOURCE_REFERENCE_NO_CATEGORY", f"referenced only by {', '.join(names[:3])} (anonymous overlay code)", "; ".join(refs[:4])
    return "unidentified", "UNIDENTIFIED", "no named source reference", ""


def build_labels(ws: Path, catalog: dict, overrides: dict | None = None, model_labels: dict | None = None) -> dict:
    h = ws / "pokeheartgold"
    ref = reference_index(h) if h.is_dir() else {}
    banks: dict[str, Counter] = {}
    for u in catalog["units"]:
        if u["library"] == "hgss" and u["type"] == "nitro_cell_bank":
            banks.setdefault(u["source"], Counter())[u["status"]] += 1
    rows = []
    ov = (overrides or {}).get("labels", {})
    for cont in sorted(banks):
        m = re.match(r"files/a/(\d+)/(\d+)/(\d+)$", cont)
        refs = sorted(ref.get(f"NARC_a_{m.group(1)}_{m.group(2)}_{m.group(3)}", [])) if m else []
        cat, basis, label, ev = classify(cont, refs)
        if cont in ov:
            o = ov[cont]
            cat, basis, label, ev = o["category"], "OWNER_LABEL", o.get("label", ""), f"labelled by {o.get('labeled_by', 'owner')}"
        c = banks[cont]
        adv = (model_labels or {}).get("labels", {}).get(cont)
        rows.append({"model_visual_label": ({k: adv[k] for k in ("model_visual_category", "note", "owner_confirmation_requested")} if adv and cat == "unidentified" else None),
                     "container": cont, "category": cat, "basis": basis, "label": label, "evidence": ev,
                     "banks": sum(c.values()), "banks_decoded": c.get("DECODED", 0), "auto_eligible": cat in AUTO_ELIGIBLE})
    tot = Counter()
    for r in rows:
        tot[(r["category"], "decoded")] += r["banks_decoded"]
        tot[(r["category"], "banks")] += r["banks"]
    ident = [r for r in rows if r["category"] != "unidentified"]
    return {"schema_version": 1, "generated_by": "tools/visual_overhaul/dau2_curate.py labels", "auto_eligible_categories": sorted(AUTO_ELIGIBLE),
            "policy": "UNIDENTIFIED containers are excluded from automatic selection; identification is per container (where it is used), not per bank. model_visual_label is advisory only.",
            "summary": {"containers": len(rows), "identified": len(ident), "unidentified": len(rows) - len(ident),
                        "banks_total": sum(r["banks"] for r in rows), "banks_decoded_total": sum(r["banks_decoded"] for r in rows),
                        "banks_decoded_identified": sum(r["banks_decoded"] for r in ident),
                        "banks_decoded_unidentified": sum(r["banks_decoded"] for r in rows if r["category"] == "unidentified"),
                        "banks_decoded_auto_eligible": sum(r["banks_decoded"] for r in rows if r["auto_eligible"]),
                        "unidentified_with_decoded_banks": sum(1 for r in rows if r["category"] == "unidentified" and r["banks_decoded"]),
                        "model_visual_effect_like_pending_owner": sum(1 for r in rows if r["model_visual_label"] and r["model_visual_label"]["owner_confirmation_requested"]),
                        "by_category_decoded": {c: tot[(c, "decoded")] for c in CATEGORIES if tot[(c, "banks")]}},
            "containers": rows}
