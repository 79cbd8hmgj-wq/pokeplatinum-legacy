#!/usr/bin/env python3
"""Batch-inspect and render Pokémon Ranger 2 Pokémon packages.

The script owns corpus discovery, package decompression, NARC extraction, resource
inventory, variant preservation, failure isolation, deterministic manifest output,
and optional invocation of a rendering backend.

The backend contract is intentionally explicit. For each package it is invoked as:

  <backend...> --package-dir DIR --output-dir DIR --manifest PATH

The backend writes a JSON object with a top-level "renders" array. Each render record
should contain at minimum "render_path" and may include cell_id/group/resources.
This lets the batch layer remain reliable while the Ranger-specific NCER/.cac cell
decoder evolves independently.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
from typing import Any

from ranger_package import RangerPackageError, classify_member, extract_package

PACKAGE_RE = re.compile(r"^p(?P<dex>\d{3})_(?P<variant>\d{2})_LZ\.bin$", re.I)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--poke-root", required=True, type=Path)
    p.add_argument("--output-root", required=True, type=Path)
    p.add_argument("--manifest", required=True, type=Path)
    p.add_argument(
        "--render-command",
        help="Optional renderer backend command. If omitted, structural census only.",
    )
    p.add_argument("--keep-extracted", action="store_true")
    p.add_argument("--include-p000", action="store_true")
    return p.parse_args()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def discover(root: Path, include_p000: bool) -> list[tuple[int, int, Path]]:
    found: list[tuple[int, int, Path]] = []
    for path in root.glob("p???_??_LZ.bin"):
        m = PACKAGE_RE.match(path.name)
        if not m:
            continue
        dex = int(m.group("dex"))
        variant = int(m.group("variant"))
        if dex == 0 and not include_p000:
            continue
        found.append((dex, variant, path))
    return sorted(found, key=lambda x: (x[0], x[1], x[2].name))


def group_resources(inventory: list[dict[str, Any]]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for item in inventory:
        name = item["name"]
        stem = Path(name).stem
        # Ranger group names observed in the recovered work are suffix-like
        # identifiers such as a01/a02/p01/s/t/w. Preserve the full stem when
        # a stronger grouping rule cannot be proven from the package itself.
        groups.setdefault(stem, []).append(name)
    return {k: sorted(v) for k, v in sorted(groups.items())}


def run_backend(command: str, package_dir: Path, output_dir: Path) -> dict[str, Any]:
    backend_manifest = output_dir / "backend_manifest.json"
    output_dir.mkdir(parents=True, exist_ok=True)
    argv = shlex.split(command) + [
        "--package-dir", str(package_dir),
        "--output-dir", str(output_dir),
        "--manifest", str(backend_manifest),
    ]
    proc = subprocess.run(argv, text=True, capture_output=True)
    result: dict[str, Any] = {
        "command": argv,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }
    if proc.returncode != 0:
        raise RuntimeError(
            f"renderer backend exited {proc.returncode}: {proc.stderr.strip()}"
        )
    if not backend_manifest.exists():
        raise RuntimeError("renderer backend did not create its manifest")
    payload = json.loads(backend_manifest.read_text())
    if not isinstance(payload, dict) or not isinstance(payload.get("renders"), list):
        raise RuntimeError("backend manifest must be an object with a renders array")
    result["manifest"] = payload
    return result


def main() -> None:
    args = parse_args()
    root = args.poke_root.resolve()
    output_root = args.output_root.resolve()
    manifest_path = args.manifest.resolve()
    packages = discover(root, args.include_p000)
    output_root.mkdir(parents=True, exist_ok=True)

    records: list[dict[str, Any]] = []
    success = 0
    failed = 0
    rendered = 0

    for dex, variant, path in packages:
        record: dict[str, Any] = {
            "national_dex": dex,
            "package_variant": variant,
            "source_package": path.name,
            "source_sha256": sha256_bytes(path.read_bytes()),
            "status": "pending",
            "warnings": [],
            "resources": [],
            "groups": {},
            "renders": [],
        }
        pkg_out = output_root / f"{dex:03d}_{variant:02d}"
        try:
            decompressed, members = extract_package(path)
            record["decompressed_sha256"] = sha256_bytes(decompressed)
            record["narc_member_count"] = len(members)

            if args.keep_extracted or args.render_command:
                extract_dir = pkg_out / "extracted"
                extract_dir.mkdir(parents=True, exist_ok=True)
            else:
                extract_dir = None

            inventory: list[dict[str, Any]] = []
            type_counts: dict[str, int] = {}
            for member in members:
                kind = classify_member(member.name, member.data)
                type_counts[kind] = type_counts.get(kind, 0) + 1
                item = {
                    "index": member.index,
                    "name": member.name,
                    "kind": kind,
                    "size": len(member.data),
                    "sha256": sha256_bytes(member.data),
                }
                inventory.append(item)
                if extract_dir is not None:
                    safe = Path(member.name).name
                    (extract_dir / safe).write_bytes(member.data)

            record["resources"] = inventory
            record["resource_type_counts"] = dict(sorted(type_counts.items()))
            record["groups"] = group_resources(inventory)

            missing = [k for k in ("nclr", "ncbr", "ncer") if type_counts.get(k, 0) == 0]
            if missing:
                record["warnings"].append(
                    "package does not expose expected resource type(s): " + ", ".join(missing)
                )

            if args.render_command:
                assert extract_dir is not None
                backend = run_backend(args.render_command, extract_dir, pkg_out / "rendered")
                record["backend"] = {
                    "returncode": backend["returncode"],
                    "stdout": backend["stdout"],
                    "stderr": backend["stderr"],
                }
                record["renders"] = backend["manifest"]["renders"]
                rendered += len(record["renders"])
                record["status"] = "rendered"
            else:
                record["status"] = "structural_ok"

            success += 1
        except Exception as exc:
            failed += 1
            record["status"] = "failed"
            record["error"] = f"{type(exc).__name__}: {exc}"
        records.append(record)

    summary = {
        "schema_version": 2,
        "mode": "render" if args.render_command else "structural_census",
        "packages_discovered": len(packages),
        "packages_successful": success,
        "packages_failed": failed,
        "render_candidates_emitted": rendered,
    }
    payload = {"summary": summary, "packages": records}
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    print(
        f"Ranger batch: {len(packages)} packages, {success} successful, "
        f"{failed} failed, {rendered} rendered candidates."
    )
    if failed:
        sys.exit(2)


if __name__ == "__main__":
    main()
