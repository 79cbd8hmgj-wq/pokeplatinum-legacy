#!/usr/bin/env python3
"""No-ROM regression tests for deterministic donor-to-DS 4bpp conversion."""
from pathlib import Path
from tempfile import TemporaryDirectory
from PIL import Image
from convert_b1_donor_cell_to_ds4bpp import convert

with TemporaryDirectory() as temp:
    root = Path(temp)
    src = root / "test.png"
    image = Image.new("RGBA", (9, 8), (0, 0, 0, 0))
    image.putpixel((0, 0), (255, 0, 0, 255))
    image.putpixel((1, 0), (0, 255, 0, 255))
    image.putpixel((8, 7), (0, 0, 255, 255))
    image.save(src)
    report = convert(src, root / "out")
    assert report["padded_dimensions"] == [16, 8]
    assert report["tile_count"] == 2
    assert report["opaque_colours"] == 3
    tile = (root / "out" / "test.4bpp").read_bytes()
    palette = (root / "out" / "test.rgb555").read_bytes()
    assert len(tile) == 64 and len(palette) == 32
    assert tile[0] != 0 and tile[0] & 15 and tile[0] >> 4
    assert tile[32 + 7 * 4] != 0
    before = report["tiles_sha256"]
    assert convert(src, root / "out")["tiles_sha256"] == before
    # Reject source sprites requiring 8bpp or manual quantization.
    many = Image.new("RGBA", (16, 8), (0, 0, 0, 0))
    for n in range(16):
        many.putpixel((n, 0), ((n * 8), 0, 0, 255))
    many.save(src)
    try:
        convert(src, root / "bad")
    except ValueError as exc:
        assert "max 15" in str(exc)
    else:
        raise AssertionError("4bpp converter must reject excess colour count")
print("PASS: real tile packing, transparency, colour capacity and deterministic conversion")
