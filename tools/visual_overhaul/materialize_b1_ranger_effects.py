#!/usr/bin/env python3
"""Materialize source-verified Ranger 2 battle effect resources.

Uses the existing B1 import preflight and the already-tested Ranger LZ10/NARC
decoder. Does not pretend unpacked Nitro resources are ready for Platinum.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from b1_donor_effect_import_preflight import make_report
from inspect_ranger_assets import extract_narc_members
from nitro_narc import lz10_decompress


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def materialize(donor_root: Path, output: Path) -> dict:
    records = []
    for record in make_report()["entries"]:
        unit = Path(record["source_unit"]).name
        assert unit.startswith("e") and unit[1:].isdigit(), unit
        src = donor_root / "res" / "prebuilt" / "data" / "effect" / f"{unit}_LZ.bin"
        if not src.is_file():
            raise FileNotFoundError(f"Missing Ranger 2 donor package: {src}")
        raw = src.read_bytes()
        if not raw or raw[0] != 0x10:
            raise ValueError(f"{src}: expected Nintendo LZ10 resource")
        unpacked = lz10_decompress(raw)
        if unpacked[:4] != b"NARC":
            raise ValueError(f"{src}: expected embedded NARC, got {unpacked[:4]!r}")
        dest = output / unit / "members"
        member_paths = extract_narc_members(unpacked, dest)
        members = []
        for name in member_paths:
            member = Path(name)
            if not member.is_relative_to(dest):
                raise ValueError(f"Unexpected extracted path outside output root: {member}")
            data = member.read_bytes()
            members.append({
                "path": str(member.relative_to(output)),
                "bytes": len(data),
                "sha256": digest(data),
                "signature": data[:4].hex(),
            })
        records.append({
            "donor": "ranger2",
            "source_unit": record["source_unit"],
            "source_file": str(src.relative_to(donor_root)),
            "source_sha256": digest(raw),
            "narc_sha256": digest(unpacked),
            "host": record["host"],
            "format_family": record["format_family"],
            "members": members,
            "conversion_state": "source_extracted_not_installed",
            "runtime_acceptance": "deferred_to_owner",
        })
    result = {"schema_version": 1, "source": "docs/visual_overhaul/selection/ledgers/battle_effects_particles.json",
              "packages": records}
    output.mkdir(parents=True, exist_ok=True)
    (output / "provenance.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ranger-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = materialize(args.ranger_root.resolve(), args.output.resolve())
    print(json.dumps({"packages": len(result["packages"]),
                      "members": sum(len(r["members"]) for r in result["packages"]),
                      "ledger": str(args.output / "provenance.json")}, indent=2))


if __name__ == "__main__":
    main()
