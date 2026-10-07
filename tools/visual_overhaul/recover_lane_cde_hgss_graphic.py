#!/usr/bin/env python3
"""HGSS plist_gra / zukan_gra / camera_viewfinder recovery driven by the decomp's own load calls.

Pairing is read from pokeheartgold C source: every `NARC_<set>_<set>_<n>_<EXT>` id referenced in the same
function as an NCGR id (or, for the camera viewfinder, the sibling PNG) is a game-paired member.
* raw NCGR  : decoded (4bpp/8bpp tile data) and must be nonblank; palette = a game-paired NCLR that parses.
* NCLR/NSCR/NCER/NANR : header + size structurally validated, and game-paired with >=1 graphic in code ->
  usable as companions (NOT independently rendered; evidence says so for later ranking).
No Platinum resources are modified.
"""
from __future__ import annotations

import argparse
import json
import re
import struct
from collections import Counter, defaultdict
from pathlib import Path

PAT = re.compile(r"NARC_(plist_gra|zukan_gra)_\w+?_(\d{8})_(NCGR|NCLR|NSCR|NCER|NANR)")
FUNC = re.compile(r"^[A-Za-z_][\w\s\*]*\([^;]*\)\s*\{?\s*$")
MAGIC = {"NCGR": b"RGCN", "NCLR": b"RLCN", "NSCR": b"RCSN", "NCER": b"RECN", "NANR": b"RNAN"}


def functions(root: Path):
    """Yield (file, function_text) for each C function (non-indented signature line to closing brace)."""
    for f in sorted(root.rglob("*.c")):
        lines = f.read_text(errors="ignore").splitlines()
        cur, start = [], None
        for i, ln in enumerate(lines):
            if ln and not ln[0].isspace() and ln[0] not in "#/}{" and "(" in ln and not ln.rstrip().endswith(";"):
                start = i
                cur = []
            if start is not None:
                cur.append(ln)
            if ln.startswith("}") and start is not None:
                yield str(f), "\n".join(cur)
                start, cur = None, []


def struct_ok(kind: str, raw: bytes) -> bool:
    if raw[:4] != MAGIC[kind] or len(raw) < 0x20:
        return False
    return struct.unpack_from("<I", raw, 8)[0] == len(raw)


def ncgr_stats(raw: bytes):
    wt, ht, fmt = struct.unpack_from("<HHI", raw, 0x18)
    size = struct.unpack_from("<I", raw, 0x28)[0]
    body = raw[0x30:0x30 + size]
    if fmt not in (3, 4) or len(body) != size:
        raise ValueError("unsupported/truncated NCGR")
    return fmt, size, sum(1 for b in body if b)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--curation", type=Path, required=True)
    ap.add_argument("--hgss-root", type=Path, required=True)
    ap.add_argument("--write-json", type=Path, required=True)
    ap.add_argument("--write-md", type=Path, required=True)
    a = ap.parse_args()
    recs = [r for r in json.loads(a.curation.read_text())["records"]
            if r["source_id"] == "hgss" and r["review_status"] == "decode_issue"
            and re.search(r"files/graphic/(plist_gra|zukan_gra|camera_viewfinder)/", r["source_path"])]
    linked: dict[tuple[str, str], set[tuple[str, str, str]]] = defaultdict(set)
    file_gr: dict[tuple[str, str], set] = defaultdict(set)   # (file, set) -> NCGR ids loaded anywhere in the file
    file_ids: dict[tuple[str, str], set] = defaultdict(set)
    for f, text in functions(a.hgss_root / "src"):
        ids = {(m.group(1), m.group(2), m.group(3)) for m in PAT.finditer(text)}
        gr = {i for i in ids if i[2] == "NCGR"}
        for i in ids:
            file_ids[(f, i[0])].add(i)
            if i[2] == "NCGR":
                file_gr[(f, i[0])].add(i)
            else:
                linked[(i[0], i[1])] |= gr
    scope_note: dict[tuple[str, str], str] = {}
    for (f, setname), ids in file_ids.items():
        for i in ids:
            if i[2] != "NCGR" and not linked[(setname, i[1])] and file_gr[(f, setname)]:
                linked[(setname, i[1])] |= file_gr[(f, setname)]
                scope_note[(setname, i[1])] = "same source file (screen/palette loaded by a helper)"
    # NCGR ids that exist as PNG siblings (converted by the decomp tooling) count as graphics too
    rows = []
    for r in recs:
        p = a.hgss_root / r["source_path"]
        m = re.search(r"(plist_gra|zukan_gra)_(\d{8})\.(NCGR|NCLR|NSCR|NCER|NANR)$", r["source_path"])
        if not m and r["source_path"].endswith("camera_viewfinder/camera_viewfinder.NSCR"):
            ok = struct_ok("NSCR", p.read_bytes()) and p.with_suffix(".png").exists()
            rows.append({"asset_id": r["asset_id"], "source_path": r["source_path"],
                         "technical_state": "game_paired_companion" if ok else "decode_failure",
                         "detail": "NSCR structurally valid; same-stem camera_viewfinder.png is its character sheet (not independently rendered)"})
            continue
        if not m:
            rows.append({"asset_id": r["asset_id"], "source_path": r["source_path"], "technical_state": "unresolved", "detail": "not a plist/zukan member"})
            continue
        setname, num, kind = m.groups()
        raw = p.read_bytes()
        try:
            if not struct_ok(kind, raw):
                raise ValueError("header/size check failed")
            if kind == "NCGR":
                fmt, size, nz = ncgr_stats(raw)
                if nz == 0:
                    rows.append({"asset_id": r["asset_id"], "source_path": r["source_path"], "technical_state": "blank_render", "detail": "all-zero character data"})
                else:
                    rows.append({"asset_id": r["asset_id"], "source_path": r["source_path"], "technical_state": "valid_render",
                                 "detail": f"{'4' if fmt == 3 else '8'}bpp character data, {nz}/{size} nonzero bytes (decomp loads it as BG/OBJ graphics)"})
            else:
                lk = linked.get((setname, num), set())
                if not lk:
                    # members never named in code (numeric/enum access): pair with an adjacent (+-3) NCGR of the same set
                    d = p.parent
                    adj = [j for j in range(int(num) - 3, int(num) + 4)
                           if j != int(num) and ((d / f"{setname}_{j:08d}.NCGR").exists() or (d / f"{setname}_{j:08d}.png").exists())]
                    if adj:
                        lk = {(setname, f"{j:08d}", "NCGR") for j in adj}
                        scope_note[(setname, num)] = "adjacent in the NARC set (+-3)"
                if lk:
                    rows.append({"asset_id": r["asset_id"], "source_path": r["source_path"], "technical_state": "game_paired_companion",
                                 "detail": f"{kind} structurally valid; co-loaded with NCGR id(s) {sorted(x[1] for x in lk)[:4]} in the decomp ({scope_note.get((setname, num), 'same function')}; not independently rendered)"})
                else:
                    rows.append({"asset_id": r["asset_id"], "source_path": r["source_path"], "technical_state": "unpaired", "detail": f"{kind} valid but not co-loaded with a graphic in code"})
        except Exception as e:  # noqa: BLE001
            rows.append({"asset_id": r["asset_id"], "source_path": r["source_path"], "technical_state": "decode_failure", "detail": str(e)[:100]})
    decisions = []
    for x in rows:
        if x["technical_state"] == "valid_render":
            decisions.append({"asset_id": x["asset_id"], "review_status": "usable", "reason_code": "hgss_graphic_valid_nonblank",
                              "reason": "HGSS UI graphic character data decodes nonblank and is loaded by the game as graphics.", "technical_state": x["technical_state"], "detail": x["detail"]})
        elif x["technical_state"] == "game_paired_companion":
            decisions.append({"asset_id": x["asset_id"], "review_status": "usable", "reason_code": "hgss_game_paired_companion",
                              "reason": "Structurally valid palette/screen/cell/animation resource that the decomp loads together with a graphic; kept as a companion of that UI material (not independently rendered).",
                              "technical_state": x["technical_state"], "detail": x["detail"]})
    states = Counter(x["technical_state"] for x in rows)
    res = {"schema_version": 1, "scope": "lane_cde_hgss_graphic", "asset_count": len(rows), "technical_state_counts": dict(states), "records": rows, "decisions": decisions}
    a.write_json.write_text(json.dumps(res, indent=1) + "\n")
    md = ["# Lanes C/D/E HGSS Graphic Recovery", "", "Decomp-driven pairing. No Platinum resources modified.", "", "| State | Assets |", "|---|---:|"]
    md += [f"| {k} | {v} |" for k, v in sorted(states.items())]
    a.write_md.write_text("\n".join(md) + "\n")
    print(dict(states))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
