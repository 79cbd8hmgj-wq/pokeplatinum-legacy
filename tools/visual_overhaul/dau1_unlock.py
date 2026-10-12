#!/usr/bin/env python3
"""Opal DAU1 - universal donor asset unlock: one entry point for catalog / matrix / convert / check.

  python3 tools/visual_overhaul/dau1_unlock.py catalog            # decode every present donor, write catalog + matrix + docs + galleries
  python3 tools/visual_overhaul/dau1_unlock.py check              # source-free CI check of the committed catalog / matrix schema
  python3 tools/visual_overhaul/dau1_unlock.py matrix             # rebuild the candidate matrix from the committed catalog
  python3 tools/visual_overhaul/dau1_unlock.py convert --unit ID  # decoded unit -> Opal FX sheet/cell/anim + cost checks (local output)

Donor checkouts are looked up next to this repository (``--workspace``, default: the parent directory).  Absent sources
are reported, never invented.  No donor bytes are written to the catalog; full galleries are written outside Git
(``--gallery-dir``, default ``build/dau1_gallery``) and only a small excerpt is written to the docs directory.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from dau1 import catalog as cat                       # noqa: E402
from dau1 import gallery, matrix, pipeline, report    # noqa: E402

DOCS = ROOT / "docs/visual_overhaul/asset_unlock"


def cmd_catalog(a) -> int:
    ws = a.workspace.resolve()
    doc, sheets, previews = pipeline.run(ws, a.only)
    doc["blockers"] = report.blockers(doc)
    out = a.out.resolve()
    gal_full = a.gallery_dir.resolve()
    index = gallery.build_galleries(doc, sheets, gal_full, out / "gallery" if not a.no_excerpts else None)
    doc["galleries"] = index
    errs = cat.validate_catalog(doc)
    if errs:
        print("catalog validation FAILED:\n  " + "\n  ".join(errs[:20]), file=sys.stderr)
        return 1
    cat.dump_catalog(doc, out / "ASSET_CATALOG.json")
    (out / "DECODER_COVERAGE.md").write_text(report.coverage_markdown(doc))
    (out / "PROVENANCE.md").write_text(report.provenance_markdown(doc))
    m = matrix.build_matrix(doc)
    cat.dump_json_lines(m, "candidates", out / "CANDIDATE_MATRIX.json")
    (out / "CANDIDATE_MATRIX.md").write_text(matrix.matrix_markdown(m))
    for lib, cov in doc["coverage"].items():
        print(f"{lib:9s} units={cov['units']:5d} " + " ".join(f"{k}={v}" for k, v in cov["by_status"].items()))
    absent = [s["library"] for s in doc["sources"] if not s["present"]]
    print("absent sources:", ", ".join(absent) if absent else "none")
    print(f"wrote {out / 'ASSET_CATALOG.json'} ({len(doc['units'])} units), matrix rows={m['summary']['rows']}, galleries={len(index)}")
    return 0


def cmd_check(a) -> int:
    cpath = a.out / "ASSET_CATALOG.json"
    if not cpath.exists():
        print(f"missing {cpath}", file=sys.stderr)
        return 1
    doc = json.loads(cpath.read_text())
    errs = cat.validate_catalog(doc)
    for need in ("sources", "coverage", "blockers", "galleries", "duplicates"):
        if need not in doc:
            errs.append(f"catalog lacks '{need}'")
    mpath = a.out / "CANDIDATE_MATRIX.json"
    if not mpath.exists():
        errs.append("missing CANDIDATE_MATRIX.json")
    else:
        mm = json.loads(mpath.read_text())
        # the committed matrix must be exactly what the committed catalog yields (determinism / staleness check)
        again = matrix.build_matrix(doc)
        if json.dumps(again["summary"], sort_keys=True) != json.dumps(mm["summary"], sort_keys=True):
            errs.append("CANDIDATE_MATRIX.json summary is stale relative to ASSET_CATALOG.json (rerun 'matrix')")
        if again["candidates"] != mm["candidates"]:
            errs.append("CANDIDATE_MATRIX.json candidates differ from a fresh derivation")
    for n in ("README.md", "DECODER_COVERAGE.md", "PROVENANCE.md", "P1_READY.md"):
        if not (a.out / n).exists():
            errs.append(f"missing {n}")
    for g in doc.get("galleries", []):
        if g["committed_excerpt"] and not (a.out / "gallery" / g["file"]).exists():
            errs.append(f"gallery excerpt {g['file']} listed but missing")
    if any(u["status"] == "DECODED" and (u["library"] in ("hgss", "pmd_sky", "ranger2")) for u in doc["units"]) is False:
        errs.append("no DECODED unit for a priority library")
    if errs:
        print("\n".join(errs[:30]), file=sys.stderr)
        return 1
    print(f"OK: {len(doc['units'])} units, {len(doc['sources'])} sources, {len(doc['blockers'])} blockers, matrix consistent")
    return 0


def cmd_matrix(a) -> int:
    doc = json.loads((a.out / "ASSET_CATALOG.json").read_text())
    m = matrix.build_matrix(doc)
    cat.dump_json_lines(m, "candidates", a.out / "CANDIDATE_MATRIX.json")
    (a.out / "CANDIDATE_MATRIX.md").write_text(matrix.matrix_markdown(m))
    print(json.dumps(m["summary"]["by_decision"]))
    return 0


def cmd_convert(a) -> int:
    from dau1 import fx_convert
    lib = a.unit.split(":", 1)[0]
    doc, sheets, _ = pipeline.run(a.workspace.resolve(), [lib])
    units = {u["id"]: u for u in doc["units"]}
    if a.unit not in units:
        print(f"unknown unit {a.unit}", file=sys.stderr)
        return 1
    u = units[a.unit]
    if u["status"] != "DECODED" or a.unit not in sheets.get(lib, {}):
        print(f"{a.unit} is {u['status']}: {u['error_reason']}", file=sys.stderr)
        return 1
    frames = sheets[lib][a.unit][: a.max_frames]
    name = a.name or "dau1_" + "".join(c if c.isalnum() else "_" for c in a.unit.split(":", 1)[1])[-48:].strip("_").lower()
    rep = fx_convert.convert(name, frames, a.out_dir.resolve(), max_tiles=a.max_tiles,
                             source_note={"unit": a.unit, "sha256": u["sha256"], "library": lib})
    print(json.dumps(rep, indent=1, sort_keys=True))
    return 0 if rep["ok"] else 2


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--workspace", type=Path, default=ROOT.parent, help="directory holding the donor checkouts")
    p.add_argument("--out", type=Path, default=DOCS, help="catalog/docs directory")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("catalog")
    c.add_argument("--only", nargs="*", help="restrict to these library ids")
    c.add_argument("--gallery-dir", type=Path, default=ROOT / "build/dau1_gallery")
    c.add_argument("--no-excerpts", action="store_true")
    c.set_defaults(fn=cmd_catalog)
    sub.add_parser("check").set_defaults(fn=cmd_check)
    sub.add_parser("matrix").set_defaults(fn=cmd_matrix)
    v = sub.add_parser("convert")
    v.add_argument("--unit", required=True)
    v.add_argument("--out-dir", type=Path, default=ROOT / "build/dau1_fx")
    v.add_argument("--name")
    v.add_argument("--max-frames", type=int, default=12)
    v.add_argument("--max-tiles", type=int, default=192)
    v.set_defaults(fn=cmd_convert)
    a = p.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    raise SystemExit(main())
