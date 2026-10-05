#!/usr/bin/env python3
"""Inventory configured Nintendo DS donor repositories for Platinum visual work.

This is deliberately format-agnostic. It proves repository/path availability and
builds a deterministic file-extension/count baseline before decoder work begins.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "docs/visual_overhaul/ds_donor_asset_pools.json"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    p.add_argument(
        "--workspace",
        type=Path,
        required=True,
        help="Directory containing sibling donor repository checkouts.",
    )
    p.add_argument("--report", type=Path)
    return p.parse_args()


def extension_counts(root: Path) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        suffix = path.suffix.lower() or "<none>"
        counts[suffix] += 1
    return dict(sorted(counts.items()))


def repo_dir(workspace: Path, repo_full_name: str) -> Path:
    return workspace / repo_full_name.split("/", 1)[1]


def main() -> int:
    args = parse_args()
    manifest = json.loads(args.manifest.read_text())
    rows = []

    all_entries = [manifest["target"], *manifest["donors"]]
    for entry in all_entries:
        repo = repo_dir(args.workspace, entry["repo"])
        roots = entry.get("roots", [])
        record = {
            "id": entry["id"],
            "repo": entry["repo"],
            "checkout": str(repo),
            "repo_exists": repo.is_dir(),
            "roots": [],
        }
        for rel in roots:
            path = repo / rel
            rec = {
                "path": rel,
                "exists": path.exists(),
                "is_dir": path.is_dir(),
            }
            if path.is_dir():
                files = [p for p in path.rglob("*") if p.is_file()]
                rec["file_count"] = len(files)
                rec["extensions"] = extension_counts(path)
            elif path.is_file():
                rec["file_count"] = 1
                rec["extensions"] = extension_counts(path.parent)
            record["roots"].append(rec)
        rows.append(record)

    output = {
        "manifest_version": manifest["version"],
        "workspace": str(args.workspace.resolve()),
        "pools": rows,
    }

    text = json.dumps(output, indent=2, sort_keys=True) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text)
        print(f"Wrote {args.report}")
    else:
        print(text, end="")

    missing_repos = [r["id"] for r in rows if not r["repo_exists"]]
    missing_roots = [
        f'{r["id"]}:{x["path"]}'
        for r in rows
        for x in r["roots"]
        if not x["exists"]
    ]
    if missing_repos:
        print("Missing repositories:", ", ".join(missing_repos))
    if missing_roots:
        print("Missing configured roots:", ", ".join(missing_roots))
    return 1 if missing_repos else 0


if __name__ == "__main__":
    raise SystemExit(main())
