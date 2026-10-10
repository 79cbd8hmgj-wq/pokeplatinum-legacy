#!/usr/bin/env python3
"""Validate the V3 Bag art that is actually installed in res/graphics/bag.

This checks source graphic formats, palette banks and tilemap references.
Runtime testing is intentionally out of scope.
"""
from pathlib import Path
import struct
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
ASSETS=ROOT/"res/graphics/bag"
PAL=((0,0,0),(250,246,244),(240,233,236),(216,202,221),
     (132,98,135),(56,53,77),(70,65,87),(102,91,117),
     (171,146,174),(194,168,123),(142,165,165),(115,137,151),
     (222,214,216),(238,221,192),(42,43,62),(255,255,255))

def validate_png_structure(path):
    """Reject corrupt PNG chunks before handing images to Pillow/nitrogfx."""
    import zlib
    data=path.read_bytes()
    assert data.startswith(b"\x89PNG\r\n\x1a\n"), f"{path}: bad PNG signature"
    pos=8
    chunks=[]
    while pos<len(data):
        assert pos+12<=len(data), f"{path}: truncated PNG chunk header"
        size=struct.unpack_from(">I",data,pos)[0]
        end=pos+12+size
        assert end<=len(data), f"{path}: invalid PNG chunk size"
        kind=data[pos+4:pos+8]
        actual=zlib.crc32(data[pos+4:pos+8+size]) & 0xffffffff
        stored=struct.unpack_from(">I",data,pos+8+size)[0]
        assert stored==actual, f"{path}: {kind!r} checksum mismatch"
        chunks.append(kind)
        pos=end
        if kind==b"IEND":
            break
    assert pos==len(data) and chunks==[b"IHDR",b"PLTE",b"IDAT",b"IEND"], f"{path}: malformed chunk layout"

def validate(screen,pngname,mapname,palname):
    p=ASSETS/pngname
    validate_png_structure(p)
    with Image.open(p) as image:
        assert image.mode=="P", f"{p}: expected 4-bit indexed source"
        w,h=image.size
        assert w%8==h%8==0 and w>0 and h>0
        used={c for _,c in image.getcolors(w*h)}
        assert max(used)<16, f"{p}: indices outside palette 0"
        tile_count=(w//8)*(h//8)
        assert tile_count<=1024
        # The generated atlas uses a physical layout of 16 columns.
        assert w==128
    header,rgb=(ASSETS/palname).read_text().splitlines()[:3],(ASSETS/palname).read_text().splitlines()[3:]
    assert header==["JASC-PAL","0100","256"]
    assert len(rgb)==256
    for i,col in enumerate(PAL):
        if i==0:
            continue
        assert tuple(map(int,rgb[i].split()))==col,(palname,i,rgb[i],col)
    blob=(ASSETS/mapname).read_bytes()
    assert len(blob)==2084 and blob[:4]==b"RCSN" and blob[16:20]==b"NRCS"
    width,height=struct.unpack_from("<HH",blob,24)
    datasize=struct.unpack_from("<I",blob,32)[0]
    assert (width,height,datasize)==(256,256,2048)
    entries=struct.unpack_from("<1024H",blob,36)
    assert all((v&1023)<tile_count for v in entries),f"{mapname}: invalid tile index"
    assert all((v&0xFC00)==0 for v in entries),f"{mapname}: unexpected palette/flip bits"
    print(f"PASS {screen}: {tile_count} tiles, 1024 map entries, palette bank 0")

def main():
    validate("main","bag_ui_main_tileset.png","bag_ui_main.NSCR","bag_ui_main.pal")
    validate("sub","pokeball_borders_tileset.png","pokeball_borders.NSCR","pokeball_borders.pal")

if __name__=="__main__":
    main()
