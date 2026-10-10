#!/usr/bin/env python3
"""Convert MO1 indexed panel source PNG into deduplicated 8x8 tiles + map.

Usage:
    python tools/opal_bag/generate_v3_panels.py --output build/mo1_bag
    python tools/opal_bag/tile_v3_panels.py --input build/mo1_bag

Produces indexed 4bpp-compatible atlas PNG, a tile index layout JSON and
a round-trip image. Does not overwrite retail bag graphics or NARC files.
"""
import argparse
import json
from pathlib import Path
from PIL import Image

TILE=8
SCREEN=(256,192)
ATLAS_COLUMNS=16

def process(src: Path, out: Path):
    with Image.open(src) as input_image:
        im=input_image.copy()
    if im.mode!="P" or im.size!=SCREEN:
        raise ValueError(f"{src}: expected indexed 256x192 image")
    palette=im.getpalette()
    if palette is None:
        raise ValueError(f"{src}: missing palette")
    counts=im.getcolors(im.width*im.height) or []
    used={idx for _,idx in counts}
    if len(used)>16 or any(idx>15 for idx in used):
        raise ValueError(f"{src}: exceeds one 4bpp palette")
    tile_indices=[]
    patterns={}
    tiles=[]
    for y in range(0,SCREEN[1],TILE):
        row=[]
        for x in range(0,SCREEN[0],TILE):
            tile=tuple(im.crop((x,y,x+TILE,y+TILE)).getdata())
            if tile not in patterns:
                patterns[tile]=len(tiles)
                tiles.append(tile)
            row.append(patterns[tile])
        tile_indices.append(row)
    if len(tiles)>1024:
        raise ValueError(f"{src}: {len(tiles)} unique tiles exceed 10-bit map range")
    atlas_rows=(len(tiles)+ATLAS_COLUMNS-1)//ATLAS_COLUMNS
    atlas=Image.new("P",(ATLAS_COLUMNS*TILE,atlas_rows*TILE))
    atlas.putpalette(palette)
    pixels=atlas.load()
    for i,tile in enumerate(tiles):
        ox=(i%ATLAS_COLUMNS)*TILE
        oy=(i//ATLAS_COLUMNS)*TILE
        for p,index in enumerate(tile):
            pixels[ox+p%TILE,oy+p//TILE]=index
    reconstruction=Image.new("P",SCREEN)
    reconstruction.putpalette(palette)
    for row_i,row in enumerate(tile_indices):
        for col_i,tile_id in enumerate(row):
            tile=atlas.crop(((tile_id%ATLAS_COLUMNS)*TILE,(tile_id//ATLAS_COLUMNS)*TILE,
                (tile_id%ATLAS_COLUMNS+1)*TILE,(tile_id//ATLAS_COLUMNS+1)*TILE))
            reconstruction.paste(tile,(col_i*TILE,row_i*TILE))
    if reconstruction.tobytes()!=im.tobytes():
        raise AssertionError(f"{src}: tile roundtrip mismatch")
    out.mkdir(parents=True,exist_ok=True)
    prefix=src.stem
    atlas.save(out/f"{prefix}_atlas.png")
    reconstruction.save(out/f"{prefix}_roundtrip.png")
    metadata={"source":src.name,"screen_width":256,"screen_height":192,
        "tile_width":8,"tile_height":8,"map_width_tiles":32,
        "map_height_tiles":24,"atlas_width_tiles":ATLAS_COLUMNS,
        "unique_tiles":len(tiles),"palette_slots_used":sorted(used),
        "tile_indices":tile_indices}
    (out/f"{prefix}_tilemap.json").write_text(json.dumps(metadata,indent=2)+"\n",encoding="utf-8")
    print(f"{src.name}: {len(tiles)} unique tiles, roundtrip PASS")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",type=Path,default=Path("build/mo1_bag"))
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    out=args.output or args.input/"tiled"
    for name in ("opal_v3_main_panel_source.png","opal_v3_sub_panel_source.png"):
        src=args.input/name
        if not src.is_file():
            parser.error(f"missing generated source: {src}")
        process(src,out)
    print("SOURCE TILE ATLAS ONLY — no game-facing NSCR/NCGR/NCLR integration yet.")

if __name__=="__main__":
    main()
