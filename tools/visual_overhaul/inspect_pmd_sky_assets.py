#!/usr/bin/env python3
"""Inspect PMD: Explorers of Sky donor resources without modifying them.

This establishes deterministic family/header metadata before decoder work.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

DEFAULT_ROOTS = ("GROUND", "MAP_BG", "BACK", "TOP", "MONSTER", "EFFECT")
PMD_EXTENSIONS = {".wan", ".bgp", ".bma", ".bpc", ".bpl", ".bpa", ".bin"}


def classify_header(data: bytes) -> str:
    if data.startswith(b"SIR0"):
        return "sir0"
    if data.startswith(b"AT4PX"):
        return "at4px"
    if data.startswith(b"PKDPX"):
        return "pkdpx"
    if not data:
        return "empty"
    return "raw_or_unknown"


def inspect_file(path: Path, donor_root: Path) -> dict:
    size = path.stat().st_size
    with path.open("rb") as f:
        head = f.read(32)
    return {
        "path": str(path.relative_to(donor_root)),
        "extension": path.suffix.lower() or "<none>",
        "size": size,
        "header_kind": classify_header(head),
        "head_hex": head[:16].hex(" "),
    }


def map_bg_groups(root: Path, donor_root: Path) -> list[dict]:
    groups = defaultdict(list)
    for path in sorted(root.iterdir()):
        if not path.is_file():
            continue
        groups[path.stem].append(path)
    rows = []
    for stem, files in sorted(groups.items()):
        rows.append(
            {
                "stem": stem,
                "members": [
                    {
                        "path": str(path.relative_to(donor_root)),
                        "extension": path.suffix.lower(),
                        "size": path.stat().st_size,
                    }
                    for path in files
                ],
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pmd-root", required=True, type=Path)
    parser.add_argument("--asset-root", action="append", default=[])
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--write-json", type=Path)
    args = parser.parse_args()

    donor_root = args.pmd_root.expanduser().resolve()
    files_root = donor_root / "files"
    roots = args.asset_root or list(DEFAULT_ROOTS)

    records = []
    inspected = 0
    missing = []
    map_groups = []

    for relative in roots:
        root = files_root / relative
        if not root.exists():
            missing.append(relative)
            continue
        if relative == "MAP_BG" and root.is_dir():
            map_groups = map_bg_groups(root, donor_root)
        paths = [root] if root.is_file() else sorted(root.rglob("*"))
        for path in paths:
            if not path.is_file():
                continue
            if path.suffix.lower() not in PMD_EXTENSIONS:
                continue
            records.append(inspect_file(path, donor_root))
            inspected += 1
            if args.limit and inspected >= args.limit:
                break
        if args.limit and inspected >= args.limit:
            break

    ext_counts = Counter(r["extension"] for r in records)
    header_counts = Counter(r["header_kind"] for r in records)

    report = {
        "schema_version": 1,
        "pmd_root": str(donor_root),
        "roots": roots,
        "files": inspected,
        "missing_roots": missing,
        "extension_counts": dict(sorted(ext_counts.items())),
        "header_counts": dict(sorted(header_counts.items())),
        "map_bg_groups": map_groups,
        "records": records,
    }

    print(f"PMD Sky files inspected: {inspected}")
    print("Extensions:", report["extension_counts"])
    print("Headers:", report["header_counts"])
    if missing:
        print("Missing roots:", ", ".join(missing))

    if args.write_json:
        args.write_json.parent.mkdir(parents=True, exist_ok=True)
        args.write_json.write_text(json.dumps(report, indent=2) + "\n")
        print(f"Wrote {args.write_json}")

    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
