#!/bin/sh
# Rebuild the manifests from the pinned base and re-apply them (resets res/trainers/data to the base first).
set -e
cd "$(dirname "$0")/../../.."
BASE=77ff7a74ec0a46fcb594850db1d03d2768ddc775
git checkout "$BASE" -- res/trainers/data
python3 tools/overhaul/trainers/build_manifest.py
python3 tools/overhaul/trainers/apply_manifest.py
python3 tools/overhaul/trainers/validate_trainers.py
