"""Command implementations for dau2_curate.py."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from dau1.catalog import dump_json_lines
from . import manifest as M

CATALOG = "docs/visual_overhaul/asset_unlock/ASSET_CATALOG.json"
SRC_DIR = "source"
MANIFEST_NAME = "B9_MOVE_MANIFEST_v2.json"


def _enc(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=True, separators=(",", ":"))


def write_json(path: Path, doc, pretty=True):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, sort_keys=True, indent=1, ensure_ascii=True) + "\n" if pretty else _enc(doc) + "\n")


def load_catalog(root: Path) -> dict:
    return json.loads((root / CATALOG).read_text())


def committed_manifest(a) -> Path:
    return a.out / SRC_DIR / MANIFEST_NAME


def cmd_manifest(a, root: Path) -> int:
    dst = committed_manifest(a)
    if a.manifest:                                                  # importing: verify SHA BEFORE copying, copy byte-for-byte
        M.load(a.manifest)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(a.manifest, dst)
        (dst.parent / (MANIFEST_NAME + ".sha256")).write_text(f"{M.PINNED_SHA256}  {MANIFEST_NAME}\n")
    doc = M.load(dst)
    idx = (dst.parent / "P1_P2_MOVE_INDEX.md")
    bound = M.bind(doc, root, idx.read_text() if idx.exists() else None)
    bound["manifest"] = {"file": f"docs/visual_overhaul/asset_unlock/dau2/{SRC_DIR}/{MANIFEST_NAME}", "sha256": M.PINNED_SHA256,
                         "id": doc["id"], "state": doc["state"], "scope": doc["scope"]}
    write_json(a.out / "B9_P1_P2_BINDING.json", bound)
    print(f"manifest OK sha256={M.PINNED_SHA256[:16]}...; {bound['summary']}; {len(bound['discrepancies'])} discrepancy note(s)")
    return 0


def cmd_features(a, root: Path) -> int:
    try:
        import numpy  # noqa: F401
    except ImportError:
        print("features needs numpy (host-side only)", file=sys.stderr)
        return 2
    from . import assets as A
    doc, punits, feats, order, _, _ = A.build_features(a.workspace.resolve(), root)
    rev = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    out = {"schema_version": 1, "generated_by": "tools/visual_overhaul/dau2_curate.py features",
           "platinum_revision": rev, "platinum_order": order, "platinum_units": punits,
           "libraries_present": sorted({u["library"] for u in doc["units"]}),
           "feature_rows": [{"id": k, **v} for k, v in sorted(feats.items())]}
    p = a.out / "ASSET_FEATURES.json"
    dump_json_lines(out, "feature_rows", p)
    print(f"features for {len(feats)} units, {len(punits)} platinum units -> {p} ({p.stat().st_size // 1024} KiB)")
    return 0


def load_features(a) -> dict:
    d = json.loads((a.out / "ASSET_FEATURES.json").read_text())
    d["features"] = {r["id"]: {"usable": "bw" in r, **{k: v for k, v in r.items() if k != "id"}} for r in d["feature_rows"]}
    return d


def cmd_matrix(a, root: Path) -> int:
    from . import candidates as C
    binding = json.loads((a.out / "B9_P1_P2_BINDING.json").read_text())
    obs_p = a.out / "model_visual_observations.json"
    obs = json.loads(obs_p.read_text())["observations"] if obs_p.exists() else {}
    m = C.build_matrix(load_catalog(root), load_features(a), binding, obs)
    dump_json_lines(m, "moves", a.out / "MOVE_CANDIDATE_MATRIX.json")
    from .report import matrix_markdown, review_queue
    (a.out / "MOVE_CANDIDATE_MATRIX.md").write_text(matrix_markdown(m))
    write_json(a.out / "OWNER_REVIEW_QUEUE.json", review_queue(m))
    ip = a.out / "ASSET_INDEX.json"
    if ip.exists():                                               # keep the gallery in step with the matrix (observations / candidates)
        from .report import gallery_markdown
        (a.out / "OWNER_REVIEW_GALLERY.md").write_text(gallery_markdown(m, json.loads(ip.read_text())))
    print(json.dumps(m["summary"], indent=1))
    return 0


def run(a, root: Path) -> int:
    fn = {"manifest": cmd_manifest, "features": cmd_features, "matrix": cmd_matrix}.get(a.cmd)
    if a.cmd in ("sheets", "emitters", "check", "all", "package"):
        from . import cli2
        fn = getattr(cli2, "cmd_" + a.cmd)
    return fn(a, root)
