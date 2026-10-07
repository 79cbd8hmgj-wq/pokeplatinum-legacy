#!/usr/bin/env python3
"""Evidence-based reject classification of Lane B build-system / data-table decode_issue records.

Only records whose content is verified to be non-art are rejected:
  - .knarcignore/.narcignore/.narcorder: plain-text knarc build-list files
  - NARC archives whose members are tiny non-Nitro data blobs (height/offset tables, move lists)
3D building-model NARCs (BMD0 members) are NOT rejected; they stay decode_issue.
"""
from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

TEXT_NAMES = {".knarcignore", ".narcignore", ".narcorder"}
NITRO_MAGICS = {b"RGCN", b"RLCN", b"RECN", b"RNAN", b"RCSN", b"NSCR", b"BMD0", b"BTX0", b"BCA0", b"RNCB"}


def narc_members(b: bytes):
    pos = struct.unpack_from("<H", b, 0xC)[0]
    fat = struct.unpack_from("<I", b, pos + 4)[0]
    cnt = struct.unpack_from("<I", b, pos + 8)[0]
    ent = [struct.unpack_from("<II", b, pos + 12 + i * 8) for i in range(cnt)]
    fnt = pos + fat
    base = fnt + struct.unpack_from("<I", b, fnt + 4)[0] + 8
    return [b[base + s:base + e] for s, e in ent]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--curation", type=Path, required=True)
    ap.add_argument("--root", action="append", required=True, help="source_id=path")
    ap.add_argument("--write-json", type=Path, required=True)
    a = ap.parse_args()
    roots = dict(x.split("=", 1) for x in a.root)
    recs = json.loads(a.curation.read_text())["records"]
    decisions, kept = [], []
    for r in recs:
        if r["review_status"] != "decode_issue" or r["source_id"] not in ("diamond", "hgss"):
            continue
        p = Path(roots[r["source_id"]]) / r["source_path"]
        name = p.name
        if name in TEXT_NAMES:
            txt = p.read_bytes().decode("ascii")
            assert all(c.isprintable() or c in "\n\r\t" for c in txt)
            code, why, det = ("build_list_text_file", "Plain-text knarc build list; contains no visual data.", f"{len(txt.splitlines())} text lines")
        elif p.suffix == ".narc":
            b = p.read_bytes()
            ms = narc_members(b) if b[:4] == b"NARC" else None
            if ms is not None and not any(m[:4] in NITRO_MAGICS for m in ms) and max(map(len, ms), default=0) <= 8192 and sum(map(len, ms)) < 8192 * 4:
                code, why, det = ("small_data_table_narc", "NARC of tiny non-Nitro data records (offset/height/move-list tables), not visual art.", f"{len(ms)} members, max {max(map(len, ms))} bytes, no Nitro/3D magics")
            else:
                kept.append(r["asset_id"])
                continue
        else:
            kept.append(r["asset_id"])
            continue
        decisions.append({"asset_id": r["asset_id"], "review_status": "reject", "reason_code": code, "reason": why, "detail": det})
    a.write_json.write_text(json.dumps({"schema_version": 1, "scope": "lane_b_support_files", "decisions": decisions,
                                        "left_unclassified_count": len(kept)}, indent=1) + "\n")
    print(len(decisions), "rejected;", len(kept), "left")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
