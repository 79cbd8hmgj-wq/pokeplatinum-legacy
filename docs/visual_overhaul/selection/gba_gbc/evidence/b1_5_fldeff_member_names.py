"""B1.5: recover internal resource names for the fldeff.narc members that Platinum's generic field-effect
renderers load. Read-only; parses res/prebuilt/data/mmodel/fldeff.narc from the repo checkout.
Usage: python3 -I b1_5_fldeff_member_names.py <repo_root> <out.json>"""
import json, re, struct, sys, hashlib

def members(path):
    d = open(path, 'rb').read()
    assert d[:4] == b'NARC'
    off = 0x10
    assert d[off:off + 4] == b'BTAF'
    sz, cnt = struct.unpack_from('<IH', d, off + 4)
    ents = [struct.unpack_from('<II', d, off + 12 + 8 * i) for i in range(cnt)]
    off2 = off + sz
    assert d[off2:off2 + 4] == b'BTNF'
    off3 = off2 + struct.unpack_from('<I', d, off2 + 4)[0]
    assert d[off3:off3 + 4] == b'GMIF'
    base = off3 + 8
    return d, [d[base + s:base + e] for s, e in ents]

SKIP = {'BMD0', 'BTX0', 'BTP0', 'BCA0', 'BMA0', 'BTA0', 'MDL0', 'TEX0', 'PLTT', 'JNT0', 'INF0', 'SHP0', 'MAT0', 'PAT0', 'SRT0'}

def strings(m):
    out = [s.decode() for s in re.findall(rb'[A-Za-z][A-Za-z0-9_.]{3,15}', m[:4000])]
    return [s for s in dict.fromkeys(out) if s not in SKIP][:4]

# member index -> (renderer/loader that uses it, generic family). Indices come from the call sites listed in
# GBA_GBC_OPPORTUNITY_POOL.json (ov5_021DF9E0/ov5_021DFA3C/FieldEffectManager_LoadModel/LoadAnimation arguments).
WANT = {}
def add(idxs, fam): 
    for i in idxs: WANT[i] = fam
add([17], 'shadow'); add([0, 1, 2, 3, 83, 84], 'grass'); add([8, 89], 'grass_very_tall'); add([9, 90], 'grass_mud')
add(range(59, 69), 'footprints_tracks_sand'); add(range(93, 103), 'footprints_tracks_snow')
add([15, 160], 'ripple_puddle'); add([16, 161], 'ripple_mud'); add([5, 86], 'splash')
add([7, 88, 157, 158, 159], 'dust'); add([14, 109], 'sparkle')

if __name__ == '__main__':
    root = sys.argv[1].rstrip('/')
    p = root + '/res/prebuilt/data/mmodel/fldeff.narc'
    raw, mem = members(p)
    res = {'narc': 'res/prebuilt/data/mmodel/fldeff.narc', 'sha256': hashlib.sha256(raw).hexdigest(),
           'member_count': len(mem), 'members': {}}
    for i in sorted(WANT):
        res['members'][str(i)] = {'family': WANT[i], 'magic': mem[i][:4].decode('latin1'), 'size': len(mem[i]),
                                  'names': strings(mem[i])}
    json.dump(res, open(sys.argv[2], 'w'), indent=1)
    print(len(res['members']), 'members recorded of', len(mem))
