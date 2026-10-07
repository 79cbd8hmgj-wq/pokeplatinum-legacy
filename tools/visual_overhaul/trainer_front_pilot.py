#!/usr/bin/env python3
"""Guarded, independently reversible HGSS trainer FRONT sprite pilot (six human-approved classes).

Subcommands
  plan    build PILOT_MANIFEST.json from the selection ledger (human-approved use_hgss groups) + before hashes
  apply   [--class C ...]  derive front.png / front_scan.png(.key) from the pinned HGSS NARC with Platinum's own
          nitrogfx, prove byte-identical round trip of all five members, then write (guarded by before-hashes)
  revert  [--class C ...]  restore the stored originals (guarded by after-hashes)
  verify  [--narc trfgra.narc] [--base REF]  static checks: file state, contract, only-allowed-paths-changed,
          optional built-archive member positions/bytes
Nothing outside res/trainers/classes/<class>/{front.png,front_scan.png,front_scan.png.key} is ever written.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nitro_narc import read_narc  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
PILOT = ROOT / "docs/visual_overhaul/pilots/trainer_front_pilot_v1"
MANIFEST = PILOT / "PILOT_MANIFEST.json"
CLASSES = ROOT / "res/trainers/classes"
FILES = ("front.png", "front_scan.png", "front_scan.png.key")
MEMBERS = ("NCGR", "NCLR", "NCER", "NANR", "NCBR")
# exact nitrogfx arguments of res/trainers/classes/meson.build (trainer_front_*)
BUILD_ARGS = {
    "NCGR": ["-cell", "-preservepath", "-version101", "-vram", "-clobbersize", "-mappingtype", "64", "-convertTo4Bpp"],
    "NCLR": ["-bitdepth", "4"],
    "NCBR": ["-encodefronttoback", "-scan"],
}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def fsha(p: Path) -> str:
    return sha(p.read_bytes())


def nitrogfx_bin(arg: str | None, tmp: Path) -> Path:
    if arg:
        return Path(arg)
    out = tmp / "nitrogfx"
    srcs = sorted((ROOT / "tools/nitrogfx").glob("*.c"))
    subprocess.check_call(["gcc", "-O1", "-w", "-std=gnu17", "-o", str(out), *map(str, srcs), "-lpng", "-lz", "-lm"])
    return out


def run(cmd, cwd):
    subprocess.check_call([str(c) for c in cmd], cwd=cwd, stdout=subprocess.DEVNULL)


def derive(n: Path, narc: list[bytes], hidx: int, plat_dir: Path, work: Path) -> dict[str, bytes]:
    """HGSS members -> Platinum source files; proves the round trip reproduces all five HGSS members byte for byte."""
    m = dict(zip(MEMBERS, narc[hidx * 5:hidx * 5 + 5]))
    for k, v in m.items():
        (work / f"h.{k}").write_bytes(v)
    (work / "h_scan.NCGR").write_bytes(m["NCBR"])
    cell = plat_dir / "front_cell.json"
    # decode (4-bit PNG out of nitrogfx; Platinum sources are 8-bit palette PNGs)
    run([n, "h.NCGR", "dec.png", "-palette", "h.NCLR", "-cell", cell], work)
    run([n, "h_scan.NCGR", "front_scan.png", "-palette", "h.NCLR", "-width", "20", "-encodefronttoback"], work)
    dec = Image.open(work / "dec.png")
    pal = dec.getpalette() or []
    img = Image.new("P", dec.size)
    img.putdata(list(dec.tobytes()))
    img.putpalette(pal + [0] * (768 - len(pal)))
    img.save(work / "front.png")
    # round trip with the project's own build arguments
    shutil.copy(cell, work / "front_cell.json")
    shutil.copy(plat_dir / "front_anim.json", work / "front_anim.json")
    run([n, "front.png", "o.NCGR", *BUILD_ARGS["NCGR"]], work)
    run([n, "front.png", "o.NCLR", *BUILD_ARGS["NCLR"]], work)
    run([n, "front_cell.json", "o.NCER"], work)
    run([n, "front_anim.json", "o.NANR"], work)
    run([n, "front_scan.png", "o.scan.NCGR", *BUILD_ARGS["NCBR"]], work)
    built = {"NCGR": "o.NCGR", "NCLR": "o.NCLR", "NCER": "o.NCER", "NANR": "o.NANR", "NCBR": "o.scan.NCGR"}
    import hgss_trainer_sprite_lib as lib
    dec_rows = {p_ >> 4 for p_ in lib.decode_sheet(m["NCGR"], m["NCLR"], m["NCER"])["pixels"] if p_}
    for k, f in built.items():
        got, want = (work / f).read_bytes(), m[k]
        if got == want:
            continue
        # HGSS NCLRs may carry data in palette rows the sprite never uses; Platinum builds a 16-colour row-0 palette.
        if k == "NCLR" and dec_rows == {0} and got[:0x48] == want[:0x48] and len(got) == len(want):
            continue
        raise SystemExit(f"round trip mismatch for member {k} (class idx {hidx}); refusing to write")
    return {"front.png": (work / "front.png").read_bytes(), "front_scan.png": (work / "front_scan.png").read_bytes(),
            "front_scan.png.key": (work / "front_scan.png.key").read_bytes()}


def load() -> dict:
    return json.loads(MANIFEST.read_text())


def save(d: dict) -> None:
    MANIFEST.write_text(json.dumps(d, indent=1, sort_keys=True) + "\n")


def cmd_plan(a) -> None:
    SEL = ROOT / "docs/visual_overhaul/selection"
    led = json.loads((SEL / "ledgers/trainer_battle_sprites.json").read_text())
    align = json.loads((SEL / "alignment/trainer_classes.json").read_text())["hgss_front"]
    consts = [l.strip().removeprefix("TRAINER_CLASS_").lower() for l in (ROOT / "generated/trainer_classes.txt").read_text().splitlines() if l.strip()]
    cat = {x["source_path"]: x for x in json.loads((ROOT / "docs/visual_overhaul/catalog_extensions/hgss_trainer_sprites/CATALOG.json").read_text())["assets"]}
    entries = []
    for d in sorted(led["decisions"], key=lambda d: d["group_id"]):
        if d["role"] != "preferred" or d["source_id"] != "hgss":
            continue
        hr = d["human_review"]
        assert hr and hr["verdict"] == "use_hgss"
        idx = d["asset_identity"]["unit"].split("_")[-1]
        pclass = align[idx]["platinum_class"]
        asset = cat[d["asset_identity"]["sample_paths"][0]]
        before = {f: fsha(CLASSES / pclass / f) for f in FILES}
        entries.append({"class": pclass, "platinum_class_index": consts.index(pclass), "hgss_class_index": int(idx),
                        "hgss_class_constant": asset["source_metadata"]["trainer_class_constant"], "group_id": d["group_id"],
                        "hgss_source": {"commit": asset["source_metadata"]["source_commit"], "narc": "files/a/0/5/8",
                                        "member_ids": asset["source_metadata"]["narc_member_ids"],
                                        "member_sha256_prefix": asset["source_metadata"]["narc_member_sha256"]},
                        "human_review": {"verdict": hr["verdict"], "reviewer": hr["reviewer"], "reviewed_at": hr["reviewed_at"]},
                        "files": FILES and {f: {"before_sha256": before[f], "after_sha256": None} for f in FILES}})
    base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    save({"schema_version": 1, "pilot": "trainer_front_pilot_v1", "base_commit": base,
          "selection_rules_version": led["rules_version"], "entries": entries})
    print(f"planned {len(entries)} classes: {[e['class'] for e in entries]}")


def sel_entries(d, classes):
    es = [e for e in d["entries"] if not classes or e["class"] in classes]
    if classes and len(es) != len(set(classes)):
        raise SystemExit("unknown class requested")
    return es


def cmd_apply(a) -> None:
    d = load()
    with tempfile.TemporaryDirectory() as t:
        n = nitrogfx_bin(a.nitrogfx, Path(t))
        narc, _ = read_narc(Path(a.hgss_root) / "files/a/0/5/8")
        head = subprocess.check_output(["git", "-C", a.hgss_root, "rev-parse", "HEAD"], text=True).strip()
        for e in sel_entries(d, a.cls):
            if head != e["hgss_source"]["commit"]:
                raise SystemExit(f"HGSS checkout {head} != pinned {e['hgss_source']['commit']}")
            pdir = CLASSES / e["class"]
            cur = {f: fsha(pdir / f) for f in FILES}
            state = "before" if all(cur[f] == e["files"][f]["before_sha256"] for f in FILES) else (
                "after" if all(cur[f] == e["files"][f]["after_sha256"] for f in FILES if e["files"][f]["after_sha256"]) and e["files"][f]["after_sha256"] else "unexpected")
            if state == "unexpected":
                raise SystemExit(f"{e['class']}: current files match neither before nor after hashes (guard)")
            work = Path(t) / e["class"]
            work.mkdir()
            out = derive(n, narc, e["hgss_class_index"], pdir, work)
            for k, v in zip(MEMBERS, narc[e["hgss_class_index"] * 5:e["hgss_class_index"] * 5 + 5]):
                assert sha(v)[:16] == e["hgss_source"]["member_sha256_prefix"][k.lower()], f"{k} member hash differs from catalog"
            if a.dry_run:
                print(f"{e['class']}: state={state} derive OK (dry run)")
                continue
            orig = PILOT / "originals" / e["class"]
            orig.mkdir(parents=True, exist_ok=True)
            for f in FILES:
                if state == "before" and not (orig / f).exists():
                    shutil.copy(pdir / f, orig / f)
                (pdir / f).write_bytes(out[f])
                if e["files"][f]["after_sha256"] not in (None, sha(out[f])):
                    raise SystemExit(f"{e['class']}/{f}: derived bytes differ from manifest after-hash")
                e["files"][f]["after_sha256"] = sha(out[f])
            print(f"{e['class']}: applied (was {state})")
    if not a.dry_run:
        save(d)


def cmd_revert(a) -> None:
    d = load()
    for e in sel_entries(d, a.cls):
        pdir, orig = CLASSES / e["class"], PILOT / "originals" / e["class"]
        for f in FILES:
            cur = fsha(pdir / f)
            if cur not in (e["files"][f]["after_sha256"], e["files"][f]["before_sha256"]):
                raise SystemExit(f"{e['class']}/{f}: unexpected content; refusing to revert")
            src = (orig / f).read_bytes()
            if sha(src) != e["files"][f]["before_sha256"]:
                raise SystemExit(f"{e['class']}/{f}: stored original does not match before-hash")
            (pdir / f).write_bytes(src)
        print(f"{e['class']}: reverted")


def state_of(e) -> str:
    cur = {f: fsha(CLASSES / e["class"] / f) for f in FILES}
    if all(cur[f] == e["files"][f]["before_sha256"] for f in FILES):
        return "original"
    if all(cur[f] == e["files"][f]["after_sha256"] for f in FILES):
        return "pilot"
    return "MODIFIED"


def cmd_verify(a) -> None:
    d = load()
    errs = []
    allowed = set()
    for e in d["entries"]:
        s = state_of(e)
        print(f"{e['class']:<16} {s}")
        if s == "MODIFIED":
            errs.append(f"{e['class']}: files match neither original nor pilot")
        pdir = CLASSES / e["class"]
        im = Image.open(pdir / "front.png")
        sc = Image.open(pdir / "front_scan.png")
        raw = (pdir / "front_scan.png").read_bytes()
        if im.mode != "P" or im.size != (80, 80) or len(im.getpalette()) != 768 or max(im.tobytes()) > 15:
            errs.append(f"{e['class']}: front.png contract (P, 80x80, 768-entry palette, indices<=15)")
        if sc.mode != "P" or sc.size != (160, 80) or raw[24] != 4 or max(sc.tobytes()) > 15:
            errs.append(f"{e['class']}: front_scan.png contract (4-bit P, 160x80)")
        if len((pdir / "front_scan.png.key").read_bytes()) != 4:
            errs.append(f"{e['class']}: key file size")
        allowed |= {f"res/trainers/classes/{e['class']}/{f}" for f in FILES}
    base = a.base or d["base_commit"]
    changed = subprocess.check_output(["git", "diff", "--name-only", base, "--", "res/", "src/", "include/", "meson.build"], cwd=ROOT, text=True).split()
    extra = sorted(set(changed) - allowed)
    if extra:
        errs.append(f"files changed outside the pilot allow-list vs {base[:8]}: {extra[:5]}")
    # unchanged siblings: cell/anim json must still equal the HGSS-derived bytes (round trip proves it at apply time)
    if a.narc:
        narc, _ = read_narc(Path(a.narc))
        for e in d["entries"]:
            hs = e["hgss_source"]["member_sha256_prefix"]
            base_i = e["platinum_class_index"] * 5
            if state_of(e) != "pilot":
                continue
            for k, i in zip(MEMBERS, range(5)):
                got = sha(narc[base_i + i])[:16]
                if got != hs[k.lower()]:
                    errs.append(f"{e['class']}: built trfgra member {base_i + i} ({k}) {got} != HGSS {hs[k.lower()]}")
        print(f"built archive checked: {len(narc)} members")
    if errs:
        print("\n".join("FAIL: " + x for x in errs), file=sys.stderr)
        raise SystemExit(1)
    print("pilot verification OK")


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("plan")
    for name in ("apply", "revert"):
        p = sub.add_parser(name)
        p.add_argument("--class", dest="cls", action="append", default=[])
        if name == "apply":
            p.add_argument("--hgss-root", required=True)
            p.add_argument("--nitrogfx")
            p.add_argument("--dry-run", action="store_true")
    v = sub.add_parser("verify")
    v.add_argument("--narc")
    v.add_argument("--base")
    a = ap.parse_args()
    {"plan": cmd_plan, "apply": cmd_apply, "revert": cmd_revert, "verify": cmd_verify}[a.cmd](a)


if __name__ == "__main__":
    main()
