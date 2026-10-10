#!/usr/bin/env python3
"""Static integration guard for the Opal Pokedex reference screen.

Catches the mistakes that compile fine but break on hardware / silently drop code:
  * new sources missing from platinum.us/main.lsf (objects not listed are dropped, symbols read 0),
  * screen-table array sizes out of sync across pokedex_app.h / pokedex_main.c,
  * graphics members missing from pokedex.order / meson.build,
  * Opal tilemaps referencing tiles/palette banks outside the shipped data,
  * every pl_msg_pokedex_opal_* id used by C exists in res/text/pokedex.json,
  * local-only QA harness edits leaking into tracked sources.
With --build-dir it also checks the compiled zukan.narc contains the Opal members.
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nitro_preview as np_  # noqa: E402

fails = []
checks = 0


def check(cond, msg):
    global checks
    checks += 1
    if not cond:
        fails.append(msg)


def rd(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return f.read()


SOURCES = ["opal_data", "opalref", "opalref_sub"]


def sources():
    lsf = rd("platinum.us/main.lsf")
    meson = rd("src/meson.build")
    block = re.search(r"Overlay pokedex\n\{(.*?)\n\}", lsf, re.S)
    check(block is not None, "main.lsf: Overlay pokedex block not found")
    body = block.group(1) if block else ""
    for s in SOURCES:
        check("src_applications_pokedex_%s.c.o" % s in body, "main.lsf: %s.c.o missing from Overlay pokedex" % s)
        check("'applications/pokedex/%s.c'" % s in meson, "src/meson.build: %s.c missing" % s)
    for text, name in ((lsf, "main.lsf"), (meson, "src/meson.build")):
        check("qa_harness" not in text, "%s references the local-only QA harness" % name)
    check("OPAL_QA_LOCAL" not in rd("src/game_start.c"), "src/game_start.c contains local QA edits")


def tables():
    app = rd("include/applications/pokedex/pokedex_app.h")
    main = rd("src/applications/pokedex/pokedex_main.c")
    check("unk_1A94[11]" in app and "unk_1C24[9]" in app, "pokedex_app.h: screen manager arrays not 11/9")
    check("Unk_ov21_021E9B74[11]" in main, "pokedex_main.c: main screen table not 11 entries")
    check("Unk_ov21_021E9B34[9]" in main, "pokedex_main.c: sub screen table not 9 entries")


def assets():
    order = rd("res/graphics/pokedex/pokedex.order")
    meson = rd("res/graphics/pokedex/meson.build")
    members = ["opal_ref.NCLR", "opal_ref_main.NCGR.lz", "opal_ref_main.NSCR.lz", "opal_ref_sub.NCGR.lz",
               "opal_ref_sub.NSCR.lz", "opal_entry.NCGR.lz", "opal_entry.NSCR.lz", "opal_locations.bin"]
    names = [l.strip() for l in order.splitlines() if l.strip()]
    for m in members:
        check(m in names, "pokedex.order: %s missing" % m)
    check(len(names) == len(set(names)), "pokedex.order has duplicate members")
    for m in ("opal_ref_main.png", "opal_ref_sub.png", "opal_entry.png", "opal_ref.pal", "opal_locations.bin"):
        check("'%s'" % m in meson, "res/graphics/pokedex/meson.build: %s missing" % m)

    # tilemap sanity: entries stay inside the 512/1024-tile char space and palette banks 0..15
    for name, max_tiles in (("opal_ref_main", 512), ("opal_ref_sub", 480), ("opal_entry", 512)):
        nscr = open(os.path.join(ROOT, "res/graphics/pokedex", name + ".NSCR"), "rb").read()
        w, h, entries = np_.read_nscr(nscr)
        check(len(entries) == w * h, "%s.NSCR: entry count %d != %dx%d" % (name, len(entries), w, h))
        used = max((e & 0x3FF) for e in entries)
        check(used < max_tiles, "%s.NSCR: tile %d >= %d" % (name, used, max_tiles))
    pal = os.path.join(ROOT, "res/graphics/pokedex/opal_ref.pal")
    check(os.path.getsize(pal) > 0, "opal_ref.pal empty")


def strings():
    doc = json.loads(rd("res/text/pokedex.json"))
    ids = {m["id"] for m in doc["messages"]}
    used = set()
    for p in ("opal_data.c", "opalref.c", "opalref_sub.c"):
        used |= set(re.findall(r"pl_msg_pokedex_opal_\w+", rd("src/applications/pokedex/" + p)))
    for u in sorted(used):
        check(u in ids, "pokedex.json: %s used by C but not defined" % u)
    check(len(used) > 100, "suspiciously few Opal string references (%d)" % len(used))


def geometry():
    h = rd("include/applications/pokedex/opalref.h")

    def const(n):
        m = re.search(r"#define\s+%s\s+(\d+)" % n, h)
        return int(m.group(1)) if m else None
    for n, v in (("OPALREF_VIEW_TOP", 30), ("OPALREF_VIEW_LINES", 9)):
        check(const(n) == v, "opalref.h: %s expected %d, got %r" % (n, v, const(n)))
    check(rd("src/applications/pokedex/opal_data.c").count("OPAL_MAX_ROWS") >= 1, "row cap not enforced in opal_data.c")


def build(build_dir):
    from narc_reader import read_narc
    path = None
    for dp, _, fs in os.walk(build_dir):
        for f in fs:
            if f == "zukan.narc":
                path = os.path.join(dp, f)
    check(path is not None, "zukan.narc not found in %s" % build_dir)
    if path:
        members = read_narc(path)
        order = [l.strip() for l in rd("res/graphics/pokedex/pokedex.order").splitlines() if l.strip()]
        check(len(members) == len(order), "zukan.narc has %d members, pokedex.order lists %d" % (len(members), len(order)))
        i = order.index("opal_locations.bin")
        src = open(os.path.join(ROOT, "res/graphics/pokedex/opal_locations.bin"), "rb").read()
        check(members[i] == src, "zukan.narc opal_locations.bin differs from source")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build-dir")
    a = ap.parse_args()
    sources()
    tables()
    assets()
    strings()
    geometry()
    if a.build_dir:
        build(a.build_dir)
    if fails:
        for f in fails:
            print("FAIL:", f)
        sys.exit(1)
    print("PASS: %d Opal integration checks" % checks)


if __name__ == "__main__":
    main()
