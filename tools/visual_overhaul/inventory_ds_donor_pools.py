#!/usr/bin/env python3
"""Inventory Nintendo DS donor asset pools for the Platinum overhaul.

This tool does not copy or modify donor assets. It records what is exposed by each
checked-out donor repository so later converters can work from a reproducible
manifest instead of ad-hoc file hunting.
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "tools" / "visual_overhaul" / "ds_donor_manifest.json"

DIRECT_EDITABLE = {".png", ".pal", ".json"}
NITRO_2D = {".ncgr", ".nclr", ".ncer", ".nanr", ".nscr", ".ncbr", ".ntft", ".ntfp"}
NITRO_3D = {".nsbmd", ".nsbtx", ".nsbca", ".nsbta", ".nsbtp", ".nsbma"}
PMD_FORMATS = {".wan", ".bgp", ".bma", ".bpc", ".bpl", ".bpa", ".wte", ".wtu", ".wat", ".wba"}
TEXT_META = {".txt", ".csv", ".mk"}


def classify(path: Path) -> str:
    name = path.name.lower()
    ext = path.suffix.lower()
    if name.endswith("_lz.bin"):
        return "compressed_binary"
    if ext in DIRECT_EDITABLE:
        return "direct_editable"
    if ext in NITRO_2D:
        return "nitro_2d"
    if ext in NITRO_3D:
        return "nitro_3d"
    if ext in PMD_FORMATS:
        return "donor_specific"
    if ext in {".narc", ".bin"}:
        return "container_or_binary"
    if ext in TEXT_META:
        return "metadata"
    return "other"


def iter_files(root: Path) -> Iterable[Path]:
    if root.is_file():
        yield root
        return
    if root.is_dir():
        for path in root.rglob("*"):
            if path.is_file():
                yield path


def scan_root(repo_root: Path, relative: str) -> dict:
    path = repo_root / relative
    ext_counts: collections.Counter[str] = collections.Counter()
    class_counts: collections.Counter[str] = collections.Counter()
    class_bytes: collections.Counter[str] = collections.Counter()
    total_bytes = 0
    total_files = 0

    for file_path in iter_files(path):
        try:
            size = file_path.stat().st_size
        except OSError:
            continue
        ext = file_path.suffix.lower() or "<none>"
        kind = classify(file_path)
        ext_counts[ext] += 1
        class_counts[kind] += 1
        class_bytes[kind] += size
        total_files += 1
        total_bytes += size

    return {
        "path": relative,
        "exists": path.exists(),
        "files": total_files,
        "bytes": total_bytes,
        "extensions": dict(sorted(ext_counts.items())),
        "classes": {
            key: {"files": class_counts[key], "bytes": class_bytes[key]}
            for key in sorted(class_counts)
        },
    }


def parse_root(values: list[str]) -> dict[str, Path]:
    roots: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise SystemExit(f"--root expects ID=PATH, got: {value}")
        donor_id, raw_path = value.split("=", 1)
        roots[donor_id.strip()] = Path(raw_path).expanduser().resolve()
    return roots


def resolve_roots(
    manifest: dict, workspace: Path | None, overrides: dict[str, Path]
) -> dict[str, Path]:
    roots: dict[str, Path] = {}
    entries = [manifest["target"], *manifest["donors"]]
    for entry in entries:
        donor_id = entry["id"]
        if donor_id in overrides:
            roots[donor_id] = overrides[donor_id]
        elif workspace is not None:
            roots[donor_id] = (workspace / entry["local_name"]).resolve()
    return roots


def inventory(manifest: dict, roots: dict[str, Path]) -> dict:
    result = {
        "schema_version": 1,
        "scope": manifest["scope"],
        "pools": [],
    }
    entries = [manifest["target"], *manifest["donors"]]
    for entry in entries:
        donor_id = entry["id"]
        repo_root = roots.get(donor_id)
        pool = {
            "id": donor_id,
            "game": entry["game"],
            "repository": entry["repository"],
            "role": entry["role"],
            "priority": entry["priority"],
            "repo_root": str(repo_root) if repo_root else None,
            "repo_exists": bool(repo_root and repo_root.is_dir()),
            "roots": [],
        }
        if repo_root and repo_root.is_dir():
            for root_spec in entry["asset_roots"]:
                scan = scan_root(repo_root, root_spec["path"])
                scan["asset_classes"] = root_spec["asset_classes"]
                scan["compatibility"] = root_spec["compatibility"]
                pool["roots"].append(scan)
        else:
            for root_spec in entry["asset_roots"]:
                pool["roots"].append(
                    {
                        "path": root_spec["path"],
                        "exists": False,
                        "files": 0,
                        "bytes": 0,
                        "extensions": {},
                        "classes": {},
                        "asset_classes": root_spec["asset_classes"],
                        "compatibility": root_spec["compatibility"],
                    }
                )
        pool["total_files"] = sum(root["files"] for root in pool["roots"])
        pool["total_bytes"] = sum(root["bytes"] for root in pool["roots"])
        result["pools"].append(pool)
    return result


def markdown_report(data: dict) -> str:
    lines = [
        "# Nintendo DS Donor Asset Inventory",
        "",
        "Generated by `tools/visual_overhaul/inventory_ds_donor_pools.py`.",
        "",
        "The inventory is descriptive only. It does not authorize bulk asset imports.",
        "",
        "## Pool summary",
        "",
        "| Pool | Role | Priority | Checkout | Files in known roots |",
        "|---|---|---:|---|---:|",
    ]
    for pool in data["pools"]:
        checkout = "yes" if pool["repo_exists"] else "no"
        lines.append(
            f"| {pool['game']} | {pool['role']} | {pool['priority']} | "
            f"{checkout} | {pool['total_files']} |"
        )

    for pool in data["pools"]:
        local_root = (
            f"- Local root: `{pool['repo_root']}`"
            if pool["repo_root"]
            else "- Local root: not supplied"
        )
        lines.extend(
            [
                "",
                f"## {pool['game']}",
                "",
                f"- Repository: `{pool['repository']}`",
                local_root,
                f"- Known-root files: **{pool['total_files']}**",
                "",
                "| Asset root | Compatibility | Files | Detected classes |",
                "|---|---|---:|---|",
            ]
        )
        for root in pool["roots"]:
            classes = ", ".join(
                f"{name}:{values['files']}"
                for name, values in root["classes"].items()
            ) or "none"
            lines.append(
                f"| `{root['path']}` | {root['compatibility']} | "
                f"{root['files']} | {classes} |"
            )

    lines.extend(
        [
            "",
            "## Status vocabulary",
            "",
            "- `direct`: same/close Gen IV resource family; compare contract before copying.",
            "- `convertible`: deterministic donor-specific conversion is expected.",
            "- `reference`: useful for design or structure, not direct transfer.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument(
        "--workspace",
        type=Path,
        help=(
            "Parent directory containing sibling donor checkouts using manifest "
            "local_name values."
        ),
    )
    parser.add_argument(
        "--root",
        action="append",
        default=[],
        metavar="ID=PATH",
        help="Override/add a checkout root. Repeatable.",
    )
    parser.add_argument("--write-json", type=Path)
    parser.add_argument("--write-md", type=Path)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if a configured repository or known asset root is missing.",
    )
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text())
    overrides = parse_root(args.root)
    workspace = args.workspace.expanduser().resolve() if args.workspace else None
    roots = resolve_roots(manifest, workspace, overrides)
    data = inventory(manifest, roots)

    missing_repos = [pool["id"] for pool in data["pools"] if not pool["repo_exists"]]
    missing_roots = [
        f"{pool['id']}:{root['path']}"
        for pool in data["pools"]
        if pool["repo_exists"]
        for root in pool["roots"]
        if not root["exists"]
    ]

    print(f"DS donor pools: {len(data['pools'])}")
    for pool in data["pools"]:
        print(
            f"{pool['id']}: repo={'yes' if pool['repo_exists'] else 'no'} "
            f"known-root-files={pool['total_files']}"
        )

    if args.write_json:
        args.write_json.parent.mkdir(parents=True, exist_ok=True)
        args.write_json.write_text(json.dumps(data, indent=2) + "\n")
        print(f"Wrote JSON: {args.write_json}")

    if args.write_md:
        args.write_md.parent.mkdir(parents=True, exist_ok=True)
        args.write_md.write_text(markdown_report(data))
        print(f"Wrote Markdown: {args.write_md}")

    if missing_repos:
        print("Missing checkouts:", ", ".join(missing_repos))
    if missing_roots:
        print("Missing known roots:", ", ".join(missing_roots))

    if args.strict and (missing_repos or missing_roots):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
