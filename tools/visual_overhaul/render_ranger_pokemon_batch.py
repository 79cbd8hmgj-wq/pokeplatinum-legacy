#!/usr/bin/env python3
"""Batch-render Pokémon Ranger donor packages.

This scales the verified single-package renderer across a Ranger poke directory,
records successes/failures, and writes a machine-readable summary. It does not
modify donor repositories or Platinum assets.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from render_ranger_pokemon_package import render_package

PKG_RE = re.compile(r"^p(?P<species>\d{3})_(?P<variant>\d{2})_LZ\.bin$")


def discover(root: Path):
    for path in sorted(root.glob("p???_??_LZ.bin")):
        m = PKG_RE.match(path.name)
        if not m:
            continue
        yield {
            "path": path,
            "species": int(m.group("species")),
            "variant": int(m.group("variant")),
        }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--ranger-root", required=True, type=Path)
    p.add_argument("--output-dir", required=True, type=Path)
    p.add_argument("--species", action="append", type=int, default=[])
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--write-json", type=Path)
    p.add_argument("--vram-stride-tiles", type=int, default=32)
    args = p.parse_args()

    donor = args.ranger_root.expanduser().resolve()
    source = donor / "res" / "prebuilt" / "data" / "poke"
    output = args.output_dir.expanduser().resolve()
    wanted = set(args.species)

    packages = list(discover(source))
    if wanted:
        packages = [x for x in packages if x["species"] in wanted]
    if args.limit:
        packages = packages[: args.limit]

    rows = []
    for item in packages:
        pkg = item["path"]
        rel_out = output / f'{item["species"]:03d}' / f'{item["variant"]:02d}'
        row = {
            "species": item["species"],
            "variant": item["variant"],
            "package": str(pkg.relative_to(donor)),
            "output": str(rel_out),
        }
        try:
            rendered = render_package(pkg, rel_out, args.vram_stride_tiles)
            row["status"] = "ok"
            row["rendered_cells"] = rendered
        except Exception as exc:
            row["status"] = "error"
            row["error"] = f"{type(exc).__name__}: {exc}"
        rows.append(row)

    summary = {
        "schema_version": 1,
        "ranger_root": str(donor),
        "packages_considered": len(rows),
        "successes": sum(r["status"] == "ok" for r in rows),
        "failures": sum(r["status"] == "error" for r in rows),
        "rendered_cells": sum(r.get("rendered_cells", 0) for r in rows),
        "rows": rows,
    }

    print(
        f"Ranger batch: {summary['successes']} ok / "
        f"{summary['failures']} failed; "
        f"{summary['rendered_cells']} cells rendered"
    )
    for row in rows:
        if row["status"] == "error":
            print(
                f"ERROR p{row['species']:03d}_{row['variant']:02d}: "
                f"{row['error']}"
            )

    if args.write_json:
        args.write_json.parent.mkdir(parents=True, exist_ok=True)
        args.write_json.write_text(json.dumps(summary, indent=2) + "\n")
        print(f"Wrote {args.write_json}")

    return 1 if summary["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
