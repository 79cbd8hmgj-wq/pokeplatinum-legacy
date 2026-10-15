#!/usr/bin/env python3
"""Tiny NARC reader (FATB/FNTB/FIMG) used to inspect compiled gameplay tables."""
import struct


def read_narc(path):
    d = open(path, "rb").read()
    magic, _bom, _ver, _size, _hsize, nsec = struct.unpack_from("<4sHHIHH", d, 0)
    if magic != b"NARC":
        raise ValueError("not a NARC: %s" % path)
    pos = 16
    fatb = None
    img = None
    for _ in range(nsec):
        tag, size = struct.unpack_from("<4sI", d, pos)
        body = d[pos + 8:pos + size]
        if tag == b"BTAF":
            fatb = body
        elif tag == b"GMIF":
            img = body
        pos += size
    count = struct.unpack_from("<HH", fatb, 0)[0]
    members = []
    for i in range(count):
        start, end = struct.unpack_from("<II", fatb, 4 + 8 * i)
        members.append(img[start:end])
    return members
