#!/usr/bin/env python3
"""Pack Opal V3 8x8 tile-index maps into Nitro Screen (NSCR) files.

A DS text background is 32 x 32 tiles here, even when only the first
24 rows are visible. This emits a standalone NSCR using a *source*
32x32 Bag NSCR as an exact header template. It does not replace the
existing in-game maps (their tile-index contracts must be migrated first).

Usage:
    python tools/opal_bag/pack_v3_nscr.py --template res/graphics/bag/bag_ui_main.NSCR \
      --maps build/mo1_bag/tiled --output build/mo1_bag/nscr
"""
import argparse
import json
from pathlib import Path
import struct

HEADER_LEN=36
MAP_W=32
MAP_H=32
VISIBLE_H=24

def build(template:bytes, manifest:dict)->bytes:
    if len(template)<HEADER_LEN+MAP_W*MAP_H*2 or template[:4]!=b"RCSN" or template[16:20]!=b"NRCS":
        raise ValueError("expected 32x32 Nitro NSCR template")
    width,height=struct.unpack_from("<HH",template,24)
    data_len=struct.unpack_from("<I",template,32)[0]
    if (width,height)!=(256,256) or data_len!=2048:
        raise ValueError(f"unexpected NSCR map size {(width,height,data_len)}")
    if (manifest["map_width_tiles"],manifest["map_height_tiles"])!=(MAP_W,VISIBLE_H):
        raise ValueError("unexpected 32x24 prototype map")
    rows=manifest["tile_indices"]
    if len(rows)!=VISIBLE_H or any(len(row)!=MAP_W for row in rows):
        raise ValueError("invalid prototype row count")
    out=bytearray(template[:HEADER_LEN+data_len])
    for y in range(MAP_H):
        for x in range(MAP_W):
            tile=rows[y][x] if y<VISIBLE_H else 0
            if not 0<=tile<1024:
                raise ValueError("tile index exceeds 10-bit NSCR limit")
            # Palette bank zero: generator is one 16-color palette. No flip bits.
            struct.pack_into("<H",out,HEADER_LEN+(y*MAP_W+x)*2,tile)
    return bytes(out)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--template",type=Path,required=True)
    p.add_argument("--maps",type=Path,default=Path("build/mo1_bag/tiled"))
    p.add_argument("--output",type=Path,default=Path("build/mo1_bag/nscr"))
    args=p.parse_args()
    template=args.template.read_bytes()
    args.output.mkdir(parents=True,exist_ok=True)
    for screen in ("main","sub"):
        name=f"opal_v3_{screen}_panel_source"
        manifest=json.loads((args.maps/f"{name}_tilemap.json").read_text())
        raw=build(template,manifest)
        assert len(raw)==HEADER_LEN+2048
        filename=args.output/f"{name}.NSCR"
        filename.write_bytes(raw)
        print(filename, len(raw), "bytes")
    print("STANDALONE NSCR GENERATED; not installed into Bag NARC.")

if __name__=="__main__":
    main()
