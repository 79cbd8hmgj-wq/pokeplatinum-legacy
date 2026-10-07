#!/usr/bin/env python3
"""Build trfgra.narc from two git refs with the project's own nitrogfx/nitroarc commands and diff the members.

Proves: archive member count/order unchanged; only the six pilot classes' NCGR/NCLR/scan members change (NCER/NANR do not);
changed members equal the HGSS originals. Writes ARCHIVE_CHECK.json beside the pilot manifest.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nitro_narc import read_narc  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
PILOT = ROOT / "docs/visual_overhaul/pilots/trainer_front_pilot_v1"
NCGR_ARGS = ["-version101", "-vram", "-clobbersize", "-mappingtype", "64", "-convertTo4Bpp"]


def tool(src_glob: list[str], out: Path, libs: list[str], extra=()):
    subprocess.check_call(["gcc", "-O1", "-w", "-std=gnu17", *extra, "-o", str(out), *src_glob, *libs])


def build(ref: str, work: Path, nitrogfx: Path, nitroarc: Path) -> list[bytes]:
    tree = work / ref.replace("/", "_")
    tree.mkdir()
    data = subprocess.check_output(["git", "archive", ref, "res/trainers/classes", "generated/trainer_classes.txt"], cwd=ROOT)
    tarfile.open(fileobj=io.BytesIO(data)).extractall(tree, filter="data")
    classes = [l.strip().removeprefix("TRAINER_CLASS_").lower() for l in (tree / "generated/trainer_classes.txt").read_text().splitlines() if l.strip()]
    root = tree / "res/trainers/classes"
    priv = tree / "priv"
    order = []
    for c in classes:
        d = priv / c
        d.mkdir(parents=True)
        src = root / c
        args = [str(nitrogfx)]

        def run(*a):
            subprocess.check_call([str(nitrogfx), *map(str, a)], cwd=src, stdout=subprocess.DEVNULL)

        if c == "castle_valet":
            run("front.png", d / "front.NCGR", "-cell", root / "castle_valet/front_cell_key.json", *NCGR_ARGS)
        else:
            run("front.png", d / "front.NCGR", "-cell", "-preservepath", *NCGR_ARGS)
        run("front.png", d / "front.NCLR", "-bitdepth", "4")
        run("front_cell.json", d / "front_cell.NCER")
        run("front_anim.json", d / "front_anim.NANR")
        run("front_scan.png", d / "front_scan.NCGR", "-encodefronttoback", "-scan")
        order += [f"{c}/front.NCGR", f"{c}/front.NCLR", f"{c}/front_cell.NCER", f"{c}/front_anim.NANR", f"{c}/front_scan.NCGR"]
    (tree / "trfgra.order").write_text("\n".join(order) + "\n")
    out = tree / "trfgra.narc"
    subprocess.check_call([str(nitroarc), "--create", "--index", "--files-from", str(tree / "trfgra.order"), "--file", str(out), str(priv)], stdout=subprocess.DEVNULL)
    return read_narc(out)[0], order


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--head", default="HEAD")
    a = ap.parse_args()
    man = json.loads((PILOT / "PILOT_MANIFEST.json").read_text())
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        ng, na = t / "nitrogfx", t / "nitroarc"
        tool(sorted(map(str, (ROOT / "tools/nitrogfx").glob("*.c"))), ng, ["-lpng", "-lz", "-lm"])
        tool([*map(str, (ROOT / "tools/nitroarc/src").glob("*.c")), str(ROOT / "tools/nitroarc/lib/nitroarc.c")], na, [],
             ["-I", str(ROOT / "tools/nitroarc/lib/include"), "-I", str(ROOT / "tools/nitroarc/src")])
        base, order = build(a.base, t, ng, na)
        head, order2 = build(a.head, t, ng, na)
    assert order == order2, "archive member order changed"
    assert len(base) == len(head) == len(order), "archive member count changed"
    changed = [i for i in range(len(base)) if base[i] != head[i]]
    expect = set()
    for e in man["entries"]:
        b = e["platinum_class_index"] * 5
        expect |= {b, b + 1, b + 4}
    ok_set = set(changed) == expect
    hgss_match = all(hashlib.sha256(head[e["platinum_class_index"] * 5 + k]).hexdigest()[:16] == e["hgss_source"]["member_sha256_prefix"][n]
                     for e in man["entries"] for k, n in ((0, "ncgr"), (2, "ncer"), (3, "nanr"), (4, "ncbr")))
    res = {"base": a.base, "head": a.head, "members": len(head), "order_identical": True, "changed_member_indices": changed,
           "expected_changed_indices": sorted(expect), "changed_set_matches_pilot": ok_set,
           "ncgr_ncer_nanr_scan_equal_hgss_members": hgss_match,
           "changed_by_class": {e["class"]: [order[i] for i in changed if i // 5 == e["platinum_class_index"]] for e in man["entries"]}}
    (PILOT / "ARCHIVE_CHECK.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k != "changed_by_class"}))
    if not (ok_set and hgss_match):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
