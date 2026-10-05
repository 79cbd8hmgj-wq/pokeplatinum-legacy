#!/usr/bin/env python3
"""Inspect Pokémon Ranger: Shadows of Almia donor resources.

Ranger's checked-in donor resources commonly use Nintendo DS LZ10 streams whose
payload is a NARC archive. This tool never mutates donor files. It decompresses,
classifies the payload and, for NARC files, inventories member signatures and
names where the BTNF table is simple enough to recover them.
"""
from __future__ import annotations

import argparse
import json
import struct
from collections import Counter
from pathlib import Path

from nitro_narc import lz10_decompress

SIGNATURES = {
    b"NARC": "narc",
    b"RGCN": "ncgr",
    b"RLCN": "nclr",
    b"RECN": "ncer",
    b"RNAN": "nanr",
    b"RCSN": "nscr",
    b"BMD0": "nsbmd",
    b"BTX0": "nsbtx",
    b"BCA0": "nsbca",
    b"BTA0": "nsbta",
    b"BTP0": "nsbtp",
    b"BMA0": "nsbma",
}

DEFAULT_ROOTS = ("poke", "pokeOBJ", "effect", "interface", "menu")


def u32(data: bytes, offset: int) -> int:
    if offset + 4 > len(data):
        raise ValueError("truncated u32")
    return struct.unpack_from("<I", data, offset)[0]


def classify_magic(data: bytes) -> str:
    if len(data) < 4:
        return "short"
    return SIGNATURES.get(data[:4], data[:4].hex())


def parse_flat_btnf_names(raw: bytes, expected: int) -> list[str | None]:
    """Best-effort parser for the common one-directory Nitro FNT layout."""
    names: list[str | None] = [None] * expected
    if len(raw) < 16 or raw[:4] != b"BTNF":
        return names
    body = raw[8:]
    if len(body) < 8:
        return names
    subtable_offset, first_file_id, parent = struct.unpack_from("<IHH", body, 0)
    if parent == 0 or subtable_offset >= len(body):
        return names

    pos = subtable_offset
    file_id = first_file_id
    while pos < len(body) and file_id < expected:
        length = body[pos]
        pos += 1
        if length == 0:
            break
        is_dir = bool(length & 0x80)
        n = length & 0x7F
        if pos + n > len(body):
            break
        name = body[pos:pos+n].decode("ascii", errors="replace")
        pos += n
        if is_dir:
            if pos + 2 > len(body):
                break
            pos += 2
            continue
        names[file_id] = name
        file_id += 1
    return names


def inspect_narc(data: bytes) -> dict:
    if data[:4] != b"NARC" or len(data) < 16:
        raise ValueError("not a NARC")
    header_size = struct.unpack_from("<H", data, 0x0C)[0]
    pos = header_size
    if data[pos:pos+4] != b"BTAF":
        raise ValueError("NARC missing BTAF")
    fat_size = u32(data, pos + 4)
    count = u32(data, pos + 8)
    entries = [
        struct.unpack_from("<II", data, pos + 12 + i * 8)
        for i in range(count)
    ]
    fnt = pos + fat_size
    if data[fnt:fnt+4] != b"BTNF":
        raise ValueError("NARC missing BTNF")
    fnt_size = u32(data, fnt + 4)
    fnt_raw = data[fnt:fnt+fnt_size]
    fimg = fnt + fnt_size
    if data[fimg:fimg+4] != b"GMIF":
        raise ValueError("NARC missing GMIF")
    base = fimg + 8
    names = parse_flat_btnf_names(fnt_raw, count)

    members = []
    type_counts: Counter[str] = Counter()
    for index, (start, end) in enumerate(entries):
        if start > end or base + end > len(data):
            kind = "invalid_range"
            size = max(0, end - start)
        else:
            member = data[base+start:base+end]
            kind = classify_magic(member)
            size = len(member)
        type_counts[kind] += 1
        members.append(
            {
                "index": index,
                "name": names[index] if index < len(names) else None,
                "offset": start,
                "size": size,
                "kind": kind,
            }
        )

    return {
        "member_count": count,
        "member_types": dict(sorted(type_counts.items())),
        "members": members,
    }


def inspect_file(path: Path, donor_root: Path) -> dict:
    src = path.read_bytes()
    record = {
        "path": str(path.relative_to(donor_root)),
        "compressed_size": len(src),
    }
    if not src:
        record["status"] = "empty"
        return record

    if src[0] != 0x10:
        record.update(
            {
                "status": "not_lz10",
                "outer_magic": classify_magic(src),
            }
        )
        return record

    declared_size = src[1] | src[2] << 8 | src[3] << 16
    try:
        payload = lz10_decompress(src)
    except Exception as exc:
        record.update(
            {
                "status": "lz10_error",
                "declared_size": declared_size,
                "error": str(exc),
            }
        )
        return record

    record.update(
        {
            "status": "ok",
            "declared_size": declared_size,
            "decompressed_size": len(payload),
            "payload_kind": classify_magic(payload),
        }
    )
    if payload[:4] == b"NARC":
        try:
            record["narc"] = inspect_narc(payload)
        except Exception as exc:
            record["narc_error"] = str(exc)
    return record


def iter_candidates(root: Path):
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name.lower().endswith("_lz.bin"):
            yield path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ranger-root",
        required=True,
        type=Path,
        help="Path to a pokeranger2 checkout.",
    )
    parser.add_argument(
        "--asset-root",
        action="append",
        default=[],
        help="Relative asset root under res/prebuilt/data; repeatable.",
    )
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--write-json", type=Path)
    args = parser.parse_args()

    donor_root = args.ranger_root.expanduser().resolve()
    data_root = donor_root / "res" / "prebuilt" / "data"
    roots = args.asset_root or list(DEFAULT_ROOTS)

    records = []
    inspected = 0
    for relative in roots:
        root = data_root / relative
        if not root.exists():
            records.append(
                {
                    "path": str(Path("res/prebuilt/data") / relative),
                    "status": "missing_root",
                }
            )
            continue
        for path in iter_candidates(root):
            records.append(inspect_file(path, donor_root))
            inspected += 1
            if args.limit and inspected >= args.limit:
                break
        if args.limit and inspected >= args.limit:
            break

    statuses = Counter(r["status"] for r in records)
    payloads = Counter(
        r.get("payload_kind", "<none>")
        for r in records
        if r["status"] == "ok"
    )
    member_types: Counter[str] = Counter()
    for record in records:
        for kind, count in record.get("narc", {}).get("member_types", {}).items():
            member_types[kind] += count

    report = {
        "schema_version": 1,
        "ranger_root": str(donor_root),
        "roots": roots,
        "files": inspected,
        "status_counts": dict(sorted(statuses.items())),
        "payload_counts": dict(sorted(payloads.items())),
        "narc_member_type_counts": dict(sorted(member_types.items())),
        "records": records,
    }

    print(f"Ranger files inspected: {report['files']}")
    print("Statuses:", report["status_counts"])
    print("Payloads:", report["payload_counts"])
    print("NARC member types:", report["narc_member_type_counts"])

    if args.write_json:
        args.write_json.parent.mkdir(parents=True, exist_ok=True)
        args.write_json.write_text(json.dumps(report, indent=2) + "\n")
        print(f"Wrote {args.write_json}")

    return 1 if statuses.get("lz10_error") else 0


if __name__ == "__main__":
    raise SystemExit(main())
