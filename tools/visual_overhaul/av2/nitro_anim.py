"""Minimal, round-trip-verified readers/writers for the Nitro field-prop resources AV2 touches.

Covers:
  * NSBTA (BTA0 / SRT0)  - texture SRT animation, parse + rebuild + bit-exact round trip
  * NSBMD (BMD0 / MDL0)  - material and joint name listing (read only)
  * bm_anime_list.narc   - per-prop animation list records (parse + guarded record patch)

No third-party dependencies.  Nothing here guesses archive IDs: every ID is derived from
res/field/props/models/map_prop_models.order and res/field/props/animations/meson.build.
"""
import re
import struct
from dataclasses import dataclass, field

# --------------------------------------------------------------------------- dictionaries


def read_dict(b, off):
    """Nitro resource dictionary -> list of (name, entry_bytes_offset) and entry size."""
    rev, n, size = struct.unpack_from("<BBH", b, off)
    hdr, tree = struct.unpack_from("<HH", b, off + 4)
    p = off + 8 + 4 * (n + 1)  # tree nodes (n + 1 incl. root)
    unit, total = struct.unpack_from("<HH", b, p)
    ent = p + 4
    names_at = ent + unit * n
    out = []
    for i in range(n):
        name = b[names_at + 16 * i : names_at + 16 * i + 16].split(b"\0")[0].decode("ascii")
        out.append((name, ent + unit * i))
    return out, unit, size


def write_dict_single(name, unit_bytes, tree_hdr=(8, 0x10), root=(0x7F, 1, 0, 0), node=(0x2E, 0, 1, 0)):
    """Single-entry dictionary used by every AV2 file (n == 1).  Verified bit-exact vs retail."""
    unit = len(unit_bytes)
    size = 8 + 4 * 2 + 4 + unit + 16
    out = struct.pack("<BBH", 0, 1, size)
    out += struct.pack("<HH", *tree_hdr)
    out += bytes(root) + bytes(node)
    out += struct.pack("<HH", unit, unit + 4)
    out += unit_bytes
    out += name.encode("ascii").ljust(16, b"\0")
    return out


# --------------------------------------------------------------------------- NSBTA

COMPONENTS = ("scaleS", "scaleT", "rot", "transS", "transT")
FLAG_CONST = 0x20
FLAG_PRESENT = 0x10


class Samples(list):
    """s16 sample array; remembers its retail offset so the retail array order is preserved."""

    orig_off = 1 << 30


@dataclass
class SrtMat:
    name: str
    n_frames: int
    # per component: (flags_byte, header_u16, payload).  payload is an int (const / 32-bit
    # raw) or a list of s16 samples when animated.
    comps: list = field(default_factory=list)


@dataclass
class Nsbta:
    anim_name: str
    n_frames: int
    mats: list
    raw: bytes = b""
    tail: bytes = b""  # retail trailing bytes after the last (4-aligned) sample array


def _tail(b, mats, aoff):
    end = None
    for m in mats:
        for (flags_hi, nf, payload) in m.comps:
            pass
    # recompute sample end from the file itself: last array end
    last = 0
    blk = struct.unpack_from("<I", b, 0x10)[0]
    ments, munit, _ = read_dict(b, aoff + 8)
    for _, ent in ments:
        for c in range(5):
            hdr, val = struct.unpack_from("<II", b, ent + 8 * c)
            if not (hdr >> 24) & FLAG_CONST:
                last = max(last, aoff + val + 2 * (hdr & 0xFFFF))
    last = (last + 3) & ~3
    return b[last:] if last else b""


def parse_nsbta(b):
    assert b[:4] == b"BTA0"
    assert struct.unpack_from("<I", b, 8)[0] == len(b)
    blk = struct.unpack_from("<I", b, 0x10)[0]
    assert b[blk : blk + 4] == b"SRT0"
    anims, unit, _ = read_dict(b, blk + 8)
    assert len(anims) == 1, "AV2 only handles single-animation NSBTA"
    aname, aent = anims[0]
    aoff = blk + struct.unpack_from("<I", b, aent)[0]
    assert b[aoff : aoff + 4] == b"M\x00AT", b[aoff : aoff + 4]
    n_frames = struct.unpack_from("<H", b, aoff + 4)[0]
    hdr_word = struct.unpack_from("<H", b, aoff + 6)[0]
    mats, munit, _ = read_dict(b, aoff + 8)
    assert munit == 0x28
    out = []
    for mname, ment in mats:
        comps = []
        for c in range(5):
            hdr, val = struct.unpack_from("<II", b, ment + 8 * c)
            nf, flags_hi = hdr & 0xFFFF, hdr >> 16
            flags = flags_hi >> 8
            if flags & FLAG_CONST:
                comps.append((flags_hi, nf, val))
            else:
                samples = Samples(struct.unpack_from("<%dh" % nf, b, aoff + val))
                samples.orig_off = val
                comps.append((flags_hi, nf, samples))
        out.append(SrtMat(mname, n_frames, comps))
    t = Nsbta(aname, n_frames, out, b)
    t.hdr_word = hdr_word
    t.tail = _tail(b, out, aoff)
    return t


def build_nsbta(t):
    """Re-serialise (single animation).  Sample arrays follow the dictionaries in file order."""
    mats = t.mats
    n_m = len(mats)
    # dictionary sizes (entries 0x28 each)
    def dict_size(n, unit):
        return 8 + 4 * (n + 1) + 4 + unit * n + 16 * n

    # Build dictionaries generically for n >= 1 using the retail tree encoding found in files.
    return _build_generic(t, dict_size)


def _tree_nodes(n):
    # Retail trees for these tiny dictionaries: root + n nodes. We reproduce retail bytes by
    # copying the original node block when the entry count is unchanged (see _build_generic).
    raise NotImplementedError


def _build_generic(t, dict_size):
    b = t.raw
    blk = struct.unpack_from("<I", b, 0x10)[0]
    anims, aunit, _ = read_dict(b, blk + 8)
    aname, aent = anims[0]
    aoff_rel = struct.unpack_from("<I", b, aent)[0]
    aoff = blk + aoff_rel
    mats_old, munit, _ = read_dict(b, aoff + 8)
    n = len(mats_old)
    assert n == len(t.mats)
    # Copy the retail animation header + material dictionary shell (tree + names) verbatim,
    # then regenerate only unit payloads.
    dict_start = aoff + 8
    ent0 = mats_old[0][1]
    shell_head = b[dict_start:ent0]  # header + tree + unit sizes
    names = b[ent0 + munit * n : ent0 + munit * n + 16 * n]
    names_end = ent0 + munit * n + 16 * n
    offs = [struct.unpack_from("<I", b, ent0 + munit * mi + 8 * c + 4)[0]
            for mi in range(n) for c in range(5)
            if not (struct.unpack_from("<I", b, ent0 + munit * mi + 8 * c)[0] >> 24) & FLAG_CONST]
    first_sample = aoff + min(offs) if offs else len(b)
    pool = b[names_end:first_sample]  # constant pool between dictionary and sample arrays
    data_start = names_end + len(pool) - aoff  # relative offset of sample area
    arrays = []  # (sort_key, mat, comp)
    for mi, m in enumerate(t.mats):
        for ci, (flags_hi, nf, payload) in enumerate(m.comps):
            if not (flags_hi >> 8) & FLAG_CONST:
                arrays.append((getattr(payload, "orig_off", 1 << 30), mi, ci))
    arrays.sort()
    samples = bytearray()
    where = {}
    placed = {}  # (orig_off, tuple(samples)) -> offset; retail shares identical arrays
    for key, mi, ci in arrays:
        payload = t.mats[mi].comps[ci][2]
        ident = (key, tuple(payload))
        if ident in placed:
            where[(mi, ci)] = placed[ident]
            continue
        where[(mi, ci)] = placed[ident] = data_start + len(samples)
        samples += struct.pack("<%dh" % len(payload), *payload)
        while len(samples) % 4:
            samples += b"\0"
    units = bytearray()
    for mi, m in enumerate(t.mats):
        for ci, (flags_hi, nf, payload) in enumerate(m.comps):
            if (flags_hi >> 8) & FLAG_CONST:
                units += struct.pack("<II", (flags_hi << 16) | nf, payload)
            else:
                units += struct.pack("<II", (flags_hi << 16) | len(payload), where[(mi, ci)])
    anim = b"M\x00AT" + struct.pack("<HH", t.n_frames, getattr(t, "hdr_word", 0)) + shell_head + bytes(units) + names + pool + bytes(samples) + t.tail
    out = bytearray(b[:aoff]) + anim  # everything before the animation is unchanged
    struct.pack_into("<I", out, blk + 4, len(out) - blk)
    struct.pack_into("<I", out, 8, len(out))
    return bytes(out)


# --------------------------------------------------------------------------- NSBMD (read only)


def parse_nsbmd_materials(b):
    """Return [(material_name, texImageParam, texPlttBase, origW, origH)] of the first model.

    texImageParam bits 16/17 = repeat S/T, 18/19 = flip S/T (DS TEXIMAGE_PARAM)."""
    assert b[:4] == b"BMD0"
    nblk = struct.unpack_from("<H", b, 14)[0]
    mdl = None
    for i in range(nblk):
        off = struct.unpack_from("<I", b, 16 + 4 * i)[0]
        if b[off : off + 4] == b"MDL0":
            mdl = off
    assert mdl is not None
    models, _, _ = read_dict(b, mdl + 8)
    moff = mdl + struct.unpack_from("<I", b, models[0][1])[0]
    matblk = moff + struct.unpack_from("<I", b, moff + 8)[0]
    ments, _, _ = read_dict(b, matblk + 4)
    out = []
    for name, e in ments:
        d = matblk + struct.unpack_from("<I", b, e)[0]
        tip = struct.unpack_from("<I", b, d + 20)[0]
        base, flag, w, h = struct.unpack_from("<HHHH", b, d + 28)
        out.append((name, tip, base, w, h))
    return out


def parse_nsbmd_textures(b):
    """Return [(texture_name, format, width, height)] from the model's embedded TEX0 (if any)."""
    nblk = struct.unpack_from("<H", b, 14)[0]
    res = []
    for i in range(nblk):
        off = struct.unpack_from("<I", b, 16 + 4 * i)[0]
        if b[off : off + 4] != b"TEX0":
            continue
        tex_off = struct.unpack_from("<I", b, off + 0x0E)[0]  # texture info block offset (u16 at +0xE)
        tex_off = struct.unpack_from("<H", b, off + 0x0E)[0]
        ents, unit, _ = read_dict(b, off + tex_off + 4)
        for name, e in ents:
            param = struct.unpack_from("<I", b, e + 2)[0]
            fmt = (param >> 26) & 7
            w = 8 << ((param >> 20) & 7)
            h = 8 << ((param >> 23) & 7)
            res.append((name, fmt, w, h))
    return res


# --------------------------------------------------------------------------- bm_anime_list

BM_ANIME_LIST = "res/prebuilt/arc/bm_anime_list.narc"


def narc_members(d):
    off = 16
    assert d[off : off + 4] == b"BTAF"
    sz, n = struct.unpack_from("<IH", d, off + 4)
    ents = [struct.unpack_from("<II", d, off + 12 + 8 * i) for i in range(n)]
    off += sz
    assert d[off : off + 4] == b"BTNF"
    off += struct.unpack_from("<I", d, off + 4)[0]
    assert d[off : off + 4] == b"GMIF"
    return off + 8, ents


def read_anime_list(d):
    base, ents = narc_members(d)
    recs = []
    for s, e in ents:
        f = d[base + s : base + e]
        assert len(f) == 20
        has, flags, bike, _ = f[:4]
        recs.append((has, flags, bike, struct.unpack_from("<4i", f, 4)))
    return recs


def patch_anime_list_record(d, model_id, expect, new):
    """Replace one 20-byte record in-place.  `expect`/`new` are 20-byte records; guard on before-value."""
    base, ents = narc_members(d)
    s, e = ents[model_id]
    cur = d[base + s : base + e]
    if cur != expect:
        raise ValueError("bm_anime_list[%d] guard failed: %s != %s" % (model_id, cur.hex(), expect.hex()))
    assert len(new) == 20
    out = bytearray(d)
    out[base + s : base + e] = new
    return bytes(out)


def pack_anime_record(has, flags, bike, ids):
    return bytes([has, flags, bike, 0]) + struct.pack("<4i", *ids)


def project_tables(root="."):
    order = [l.strip() for l in open(root + "/res/field/props/models/map_prop_models.order") if l.strip()]
    anims = re.findall(r"'(prop_animation_\d+\.\w+)'", open(root + "/res/field/props/animations/meson.build").read())
    return order, anims


# --------------------------------------------------------------------------- AV2 edit helpers


def sample_locations(b):
    """{(material, component_name): (file_offset, count)} for every animated (non-const) track."""
    assert b[:4] == b"BTA0"
    blk = struct.unpack_from("<I", b, 0x10)[0]
    anims, _, _ = read_dict(b, blk + 8)
    aoff = blk + struct.unpack_from("<I", b, anims[0][1])[0]
    mats, _, _ = read_dict(b, aoff + 8)
    out = {}
    for mname, ent in mats:
        for c in range(5):
            hdr, val = struct.unpack_from("<II", b, ent + 8 * c)
            if not (hdr >> 24) & FLAG_CONST:
                out[(mname, COMPONENTS[c])] = (aoff + val, hdr & 0xFFFF)
    return out


def read_samples(b, mat, comp):
    off, n = sample_locations(b)[(mat, comp)]
    return list(struct.unpack_from("<%dh" % n, b, off))


def patch_samples(b, edits, guards):
    """In-place same-length s16 track replacement.

    edits  : {(mat, comp): new_samples}
    guards : {(mat, comp): expected_current_samples}  - fail closed on any mismatch
    Tracks that are shared between materials (same file offset) must receive identical data."""
    loc = sample_locations(b)
    out = bytearray(b)
    written = {}
    for key, new in edits.items():
        off, n = loc[key]
        cur = list(struct.unpack_from("<%dh" % n, b, off))
        if cur != list(guards[key]):
            raise ValueError("guard failed for %s" % (key,))
        if len(new) != n:
            raise ValueError("length change not allowed for %s" % (key,))
        if off in written and written[off] != list(new):
            raise ValueError("shared track %s patched with differing data" % (key,))
        written[off] = list(new)
        struct.pack_into("<%dh" % n, out, off, *new)
    return bytes(out)


def retarget_single_material(template, anim_name, mat_name, n_frames, trans_s=None, trans_t=None):
    """Build a new single-material NSBTA from a retail single-material template.

    The template's animated/constant flag layout is kept: a track that is animated in the
    template gets the supplied samples (len == n_frames); a constant track keeps its constant.
    The container layout is regenerated by build_nsbta (bit-exact for retail single-material
    files, verified by the validator's round-trip check)."""
    t = parse_nsbta(template)
    assert len(t.mats) == 1
    m = t.mats[0]
    new = []
    for ci, (flags_hi, nf, payload) in enumerate(m.comps):
        want = {3: trans_s, 4: trans_t}.get(ci)
        if (flags_hi >> 8) & FLAG_CONST:
            assert want is None, "component %s is constant in the template" % COMPONENTS[ci]
            new.append((flags_hi, n_frames, payload))
        else:
            assert want is not None and len(want) == n_frames
            s = Samples(want)
            s.orig_off = getattr(payload, "orig_off", 1 << 30)
            new.append((flags_hi, n_frames, s))
    m.comps = new
    t.n_frames = n_frames
    out = bytearray(build_nsbta(t))
    # names: animation dictionary name and material dictionary name (16-byte slots)
    blk = struct.unpack_from("<I", out, 0x10)[0]
    anims, aunit, _ = read_dict(out, blk + 8)
    aent = anims[0][1]
    out[aent + aunit : aent + aunit + 16] = anim_name.encode("ascii").ljust(16, b"\0")
    aoff = blk + struct.unpack_from("<I", out, aent)[0]
    mats, munit, _ = read_dict(out, aoff + 8)
    ent0 = mats[0][1]
    out[ent0 + munit : ent0 + munit + 16] = mat_name.encode("ascii").ljust(16, b"\0")
    return bytes(out)
