#!/usr/bin/env python3
"""Recover the exact historical C3H species ledgers from the archived workflow.

This is a provenance/recovery utility, not a design generator. It extracts the five
base64+gzip JSON ledgers embedded in the historical C3H application workflow and
refuses to continue unless their operation counts match the locked 225-op set.
"""
from __future__ import annotations

import argparse
import ast
import base64
import gzip
import json
import re
from pathlib import Path

EXPECTED_COUNTS = [67, 27, 40, 53, 38]
EXPECTED_TOTAL = 225
NAMES = [
    "platinum_c3h_l1_guarded_ledger_v1.json",
    "platinum_c3h_l2_gen1_guarded_ledger_v1.json",
    "platinum_c3h_l3_gen2_guarded_ledger_v1.json",
    "platinum_c3h_l4_gen3_guarded_ledger_v1.json",
    "platinum_c3h_l5_sinnoh_guarded_ledger_v1.json",
]


def decode_ledgers(workflow_text: str) -> list[dict]:
    match = re.search(r"^\s*BLOBS=(\[.*\])\s*$", workflow_text, flags=re.M)
    if not match:
        raise SystemExit("historical BLOBS array not found")
    blobs = ast.literal_eval(match.group(1))
    if len(blobs) != 5:
        raise SystemExit(f"expected 5 ledger blobs, found {len(blobs)}")
    ledgers = [json.loads(gzip.decompress(base64.b64decode(blob))) for blob in blobs]
    counts = [len(ledger.get("changes", [])) for ledger in ledgers]
    if counts != EXPECTED_COUNTS:
        raise SystemExit(f"ledger counts mismatch: expected {EXPECTED_COUNTS}, got {counts}")
    if sum(counts) != EXPECTED_TOTAL:
        raise SystemExit(f"expected {EXPECTED_TOTAL} operations, got {sum(counts)}")
    for index, ledger in enumerate(ledgers):
        if ledger.get("version") != 1 or ledger.get("domain") != "pokemon":
            raise SystemExit(f"ledger {index + 1} has unexpected metadata")
    return ledgers


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("docs/overhaul/implementation/archive/c3h-apply-species-original.yml"),
        help="Archived historical workflow containing the exact five ledger blobs.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("docs/overhaul/implementation/ledgers"),
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write/reconcile extracted ledgers. Without this flag the script only verifies them.",
    )
    args = parser.parse_args()

    ledgers = decode_ledgers(args.source.read_text(encoding="utf-8"))
    args.output_dir.mkdir(parents=True, exist_ok=True)

    mismatches: list[str] = []
    for ledger, name in zip(ledgers, NAMES):
        encoded = json.dumps(ledger, indent=2) + "\n"
        path = args.output_dir / name
        if path.exists():
            current = path.read_text(encoding="utf-8")
            if current != encoded:
                mismatches.append(str(path))
                if args.write:
                    path.write_text(encoded, encoding="utf-8")
        elif args.write:
            path.write_text(encoded, encoding="utf-8")
        else:
            mismatches.append(str(path))

    provenance = {
        "historical_commit": "dceb548782be5c3ed30afba39a8b5727fdd6716d",
        "historical_workflow_blob_sha": "c45362c9913899aae07e6a84fa5bc62e9ee7edb0",
        "counts": EXPECTED_COUNTS,
        "total_operations": EXPECTED_TOTAL,
        "files": NAMES,
    }

    if args.write:
        (args.output_dir / "C3H_LEDGER_PROVENANCE.json").write_text(
            json.dumps(provenance, indent=2) + "\n", encoding="utf-8"
        )
        # Re-read and verify that the written files exactly match the historical payload.
        for ledger, name in zip(ledgers, NAMES):
            path = args.output_dir / name
            if json.loads(path.read_text(encoding="utf-8")) != ledger:
                raise SystemExit(f"post-write verification failed for {path}")

    print(json.dumps({**provenance, "mismatches_or_missing": mismatches}, indent=2))
    if mismatches and not args.write:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
