"""Tiny NSBTX/TEX0 reader used by AV2 to *look at* texture identities (formats 1-5 and 6).
Read only; never writes game resources."""
import struct
from nitro_anim import read_dict


def read_tex0(b):
    nblk = struct.unpack_from("<H", b, 14)[0]
    for i in range(nblk):
        off = struct.unpack_from("<I", b, 16 + 4 * i)[0]
        if b[off : off + 4] == b"TEX0":
            break
    else:
        return []
    ofs_tex_data = struct.unpack_from("<I", b, off + 0x14)[0]
    ofs_dict = struct.unpack_from("<H", b, off + 0x0E)[0]
    ofs_pdict = struct.unpack_from("<I", b, off + 0x34)[0]
    ofs_pdata = struct.unpack_from("<I", b, off + 0x38)[0]
    texs, unit, _ = read_dict(b, off + ofs_dict)
    plts, punit, _ = read_dict(b, off + ofs_pdict)
    pal = {}
    sizes = []
    for n, e in plts:
        o = struct.unpack_from("<H", b, e)[0] << 3
        sizes.append((o, n))
    sizes.sort()
    for i, (o, n) in enumerate(sizes):
        end = sizes[i + 1][0] if i + 1 < len(sizes) else (struct.unpack_from("<I", b, off + 0x30)[0])
        raw = b[off + ofs_pdata + o : off + ofs_pdata + end]
        pal[n] = struct.unpack("<%dH" % (len(raw) // 2), raw)
    out = []
    for n, e in texs:
        o = struct.unpack_from("<H", b, e)[0] << 3
        param = struct.unpack_from("<H", b, e + 2)[0]
        fmt = (param >> 10) & 7
        w = 8 << ((param >> 4) & 7)
        h = 8 << ((param >> 7) & 7)
        c0 = (param >> 13) & 1
        out.append(dict(name=n, off=off + ofs_tex_data + o, fmt=fmt, w=w, h=h, c0=c0))
    return out, pal, b


def rgb(c):
    return ((c & 31) * 255 // 31, ((c >> 5) & 31) * 255 // 31, ((c >> 10) & 31) * 255 // 31)


def decode(b, t, palette):
    w, h, fmt = t["w"], t["h"], t["fmt"]
    o = t["off"]
    px = []
    if fmt == 2:
        for i in range(w * h):
            px.append((b[o + i // 4] >> (2 * (i % 4))) & 3)
    elif fmt == 3:
        for i in range(w * h):
            px.append((b[o + i // 2] >> (4 * (i % 2))) & 15)
    elif fmt == 4:
        px = list(b[o : o + w * h])
    elif fmt == 1:
        px = [b[o + i] & 31 for i in range(w * h)]
    elif fmt == 6:
        px = [b[o + i] & 7 for i in range(w * h)]
    else:
        return None
    img = []
    for v in px:
        if v < len(palette):
            r, g, bl = rgb(palette[v])
        else:
            r = g = bl = 255
        img.append((r, g, bl, 0 if (t["c0"] and v == 0 and fmt in (2, 3, 4)) else 255))
    return img
