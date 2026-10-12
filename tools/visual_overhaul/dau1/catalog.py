"""Catalog record model, schema validation, deterministic serialisation and duplicate detection.

One ``Unit`` is the smallest independently decodable thing a donor library offers (a cell bundle, an effect sprite,
a PNG strip ...).  The committed ``ASSET_CATALOG.json`` is a list of these plus per-library coverage and a source
ledger.  No donor pixels are stored in the catalog - only hashes, counts and budgets.
"""
from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .common import STATUSES

SCHEMA_VERSION = 1

REQUIRED_FIELDS = (
    "id", "library", "source", "sha256", "type", "frame_count", "palette_size", "dimensions",
    "tile_budget", "oam_budget", "status", "error_reason",
)


@dataclass
class Unit:
    id: str                              # stable id: "<library>:<path>[#member...]"
    library: str                         # e.g. hgss, pmd_sky, ranger2, emerald, ruby, crystal ...
    source: str                          # repo-relative path of the container / file
    sha256: str | None                   # sha256 of the unit's primary input bytes (None when MISSING / BLOCKED_INPUT)
    type: str                            # nitro_cell_bank, pmd_effect_wan, gba_indexed_png, ...
    status: str
    frame_count: int | None = None
    palette_size: int | None = None      # number of palette entries actually used/available
    dimensions: dict | None = None       # {"min": [w,h], "max": [w,h]} over frames
    tile_budget: int | None = None       # estimated distinct 8x8 OBJ tiles needed
    oam_budget: int | None = None        # max OBJ (OAM) entries in any single frame
    error_reason: str | None = None
    members: list = field(default_factory=list)       # [{"name", "sha256", "size"}]
    warnings: list = field(default_factory=list)
    visual_sha256: str | None = None     # hash of the rendered frames (cross-library duplicate detection)
    sheet: str | None = None             # contact-sheet name this unit appears on (file kept out of Git)
    extra: dict = field(default_factory=dict)

    def to_json(self) -> dict:
        d = asdict(self)
        if len(d["members"]) == 1 and d["members"][0]["sha256"] == d["sha256"]:
            d["members"] = []                      # the unit IS its single member; nothing to add to the hash index
        extra = d.pop("extra")
        d.update(extra and {"extra": extra} or {})
        return d


def validate_unit(u: dict) -> list[str]:
    """Return a list of schema problems for one serialised unit (empty list = valid)."""
    errs = []
    for k in REQUIRED_FIELDS:
        if k not in u:
            errs.append(f"missing field {k}")
    if errs:
        return errs
    if u["status"] not in STATUSES:
        errs.append(f"bad status {u['status']!r}")
    if u["status"] == "DECODED":
        if not u["sha256"]:
            errs.append("DECODED unit needs sha256")
        if not u["frame_count"]:
            errs.append("DECODED unit needs frame_count > 0")
        if u["dimensions"] is None:
            errs.append("DECODED unit needs dimensions")
        if u["error_reason"]:
            errs.append("DECODED unit must not carry error_reason")
        if not u.get("visual_sha256"):
            errs.append("DECODED unit needs visual_sha256")
    else:
        if not u["error_reason"]:
            errs.append(f"{u['status']} unit needs error_reason")
    if u["status"] in ("MISSING", "BLOCKED_INPUT") and u["sha256"]:
        errs.append(f"{u['status']} unit cannot have a sha256")
    for k in ("frame_count", "palette_size", "tile_budget", "oam_budget"):
        v = u[k]
        if v is not None and (not isinstance(v, int) or isinstance(v, bool) or v < 0):
            errs.append(f"{k} must be a non-negative int or null")
    if u["sha256"] is not None and not (isinstance(u["sha256"], str) and len(u["sha256"]) == 64):
        errs.append("sha256 must be 64 hex chars")
    d = u["dimensions"]
    if d is not None and not (isinstance(d, dict) and {"min", "max"} <= set(d)):
        errs.append("dimensions must be {min,max}")
    return errs


def validate_catalog(doc: dict) -> list[str]:
    errs = []
    if doc.get("schema_version") != SCHEMA_VERSION:
        errs.append("schema_version mismatch")
    ids = set()
    for i, u in enumerate(doc.get("units", [])):
        for e in validate_unit(u):
            errs.append(f"unit[{i}] {u.get('id')}: {e}")
        if u.get("id") in ids:
            errs.append(f"duplicate unit id {u.get('id')}")
        ids.add(u.get("id"))
    for lib, cov in doc.get("coverage", {}).items():
        if sum(cov.get("by_status", {}).values()) != cov.get("units"):
            errs.append(f"coverage[{lib}] status counts do not sum to units")
    n = sum(c["units"] for c in doc.get("coverage", {}).values())
    if n != len(doc.get("units", [])):
        errs.append("coverage totals do not match unit count")
    return errs


def find_duplicates(units: list[dict]) -> dict:
    """Group units sharing identical input bytes (sha256) or an identical rendering (visual_sha256).

    Groups spanning more than one library are listed in full (they are the cross-donor duplicates); groups that stay
    inside a single library are only counted, to keep the catalog reviewable.
    """
    cross: dict[str, list[str]] = {}
    within: dict[str, int] = defaultdict(int)
    for key in ("sha256", "visual_sha256"):
        groups = defaultdict(list)
        for u in units:
            if u.get(key) and u["type"] not in ("nitro_char_sheet_set", "nitro_screen_set"):
                groups[u[key]].append(u)
        for h, us in sorted(groups.items()):
            if len(us) < 2:
                continue
            libs = sorted({u["library"] for u in us})
            if len(libs) > 1:
                cross[f"{key}:{h}"] = sorted(u["id"] for u in us)
            else:
                within[f"{libs[0]}:{key}"] += 1
    return {"cross_library_groups": cross, "within_library_group_counts": dict(sorted(within.items()))}


def coverage(units: list[dict]) -> dict:
    cov: dict[str, dict] = {}
    for u in units:
        c = cov.setdefault(u["library"], {"units": 0, "by_status": {s: 0 for s in STATUSES}, "by_type": {}})
        c["units"] += 1
        c["by_status"][u["status"]] += 1
        c["by_type"][u["type"]] = c["by_type"].get(u["type"], 0) + 1
    return {k: cov[k] for k in sorted(cov)}


def dump_catalog(doc: dict, path: Path) -> None:
    """Deterministic, diff-friendly JSON: header keys first, then one compact unit per line (sorted keys, no timestamps)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    enc = lambda o: json.dumps(o, sort_keys=True, ensure_ascii=True, separators=(",", ":"))   # noqa: E731
    head = {k: v for k, v in doc.items() if k != "units"}
    lines = ["{"]
    for k in sorted(head):
        lines.append(f'{json.dumps(k)}:{enc(head[k])},')
    lines.append('"units":[')
    lines.append(",\n".join(enc(u) for u in doc["units"]))
    lines.append("]}")
    path.write_text("\n".join(lines) + "\n")


def dump_json_lines(doc: dict, key: str, path: Path) -> None:
    """Same layout for any document whose bulk lives under ``key`` (used by the candidate matrix)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    enc = lambda o: json.dumps(o, sort_keys=True, ensure_ascii=True, separators=(",", ":"))   # noqa: E731
    head = {k: v for k, v in doc.items() if k != key}
    lines = ["{"]
    for k in sorted(head):
        lines.append(f'{json.dumps(k)}:{enc(head[k])},')
    lines.append(f'{json.dumps(key)}:[')
    lines.append(",\n".join(enc(u) for u in doc[key]))
    lines.append("]}")
    path.write_text("\n".join(lines) + "\n")
