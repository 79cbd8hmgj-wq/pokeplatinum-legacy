"""Shared helpers for the donor selection pipeline (no Platinum resources are touched)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VO = ROOT / "docs" / "visual_overhaul"
SEL = VO / "selection"

BASE_LEDGERS = [
    VO / "LANE_A_RECOVERED_CURATION.json",
    VO / "LANE_B_RECOVERED_CURATION.json",
    VO / "LANE_CDE_RECOVERED_CURATION.json",
]
EXT_DIR = VO / "catalog_extensions"
EXT_MANIFEST = EXT_DIR / "MANIFEST.json"


def extensions() -> list[dict]:
    return json.loads(EXT_MANIFEST.read_text())["extensions"] if EXT_MANIFEST.is_file() else []


RECOVERED_LEDGERS = BASE_LEDGERS + [EXT_DIR / e["curation"] for e in extensions()]


def ledger_label(p: Path) -> str:
    return p.name if p.parent == VO else f"{p.parent.name}/{p.name}"
STATUS_JSON = VO / "DONOR_CURATION_STATUS.json"
SUBSYSTEMS_JSON = SEL / "SUBSYSTEMS.json"
RULES_JSON = SEL / "SELECTION_RULES.json"
GROUPS_JSON = SEL / "CANDIDATE_GROUPS.json"


def jload(path: Path):
    return json.loads(Path(path).read_text())


def jdump(path: Path, obj) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, indent=1, sort_keys=True) + "\n")


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def digest_ids(ids) -> str:
    h = hashlib.sha256()
    for i in sorted(ids):
        h.update(i.encode())
        h.update(b"\n")
    return h.hexdigest()[:20]


def load_recovered_records() -> dict[str, dict]:
    """asset_id -> authoritative recovered curation record (all three lanes)."""
    out: dict[str, dict] = {}
    for p in RECOVERED_LEDGERS:
        for r in jload(p)["records"]:
            r["_ledger"] = ledger_label(p)
            if r["asset_id"] in out:
                raise SystemExit(f"duplicate asset across recovered ledgers: {r['asset_id']}")
            out[r["asset_id"]] = r
    return out


def ledger_hashes() -> dict[str, str]:
    return {ledger_label(p): file_sha256(p) for p in RECOVERED_LEDGERS}


def species_constants() -> list[str]:
    lines = [l.strip() for l in (ROOT / "generated" / "species.txt").read_text().splitlines() if l.strip()]
    return lines[: lines.index("SPECIES_ARCEUS") + 1]


def subsystem_groups_digest(groups) -> str:
    """Digest over (group_id, member_digest, member_count) of a subsystem's groups."""
    return digest_ids(f"{g['group_id']}|{g['member_digest']}|{g['member_count']}" for g in groups)
