#!/usr/bin/env python3
"""Opal DAU2 - multi-source curation and SPL emitter research.  Tooling and evidence only; no gameplay, move data, animation script or
res/ file is modified, and no donor pixels are committed (previews stay in ``build/dau2``, which Git ignores).

  python3 tools/visual_overhaul/dau2_curate.py manifest        # verify + bind the original B9 v2 manifest (source-free)
  python3 tools/visual_overhaul/dau2_curate.py features        # donor-dependent: decode all pools, write ASSET_FEATURES.json
  python3 tools/visual_overhaul/dau2_curate.py matrix          # source-free: per-move candidate matrix + owner review queue
  python3 tools/visual_overhaul/dau2_curate.py sheets          # donor-dependent: contact sheets / per-move boards (local, build/dau2)
  python3 tools/visual_overhaul/dau2_curate.py emitters        # corpus-wide SPL emitter parse + 3 representative replays
  python3 tools/visual_overhaul/dau2_curate.py package         # zip the local previews for attaching to a review (never committed)
  python3 tools/visual_overhaul/dau2_curate.py check           # source-free CI gate over every committed DAU2 artefact
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from dau2 import cli  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--workspace", type=Path, default=ROOT.parent, help="directory holding the donor checkouts")
    p.add_argument("--out", type=Path, default=ROOT / "docs/visual_overhaul/asset_unlock/dau2")
    p.add_argument("--build", type=Path, default=ROOT / "build/dau2", help="local, untracked preview output")
    p.add_argument("--manifest", type=Path, help="B9 v2 manifest to import (default: the committed copy)")
    sub = p.add_subparsers(dest="cmd", required=True)
    for c in ("manifest", "features", "labels", "matrix", "recipes", "sheets", "emitters", "package", "check", "all"):
        sub.add_parser(c)
    a = p.parse_args()
    return cli.run(a, ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
