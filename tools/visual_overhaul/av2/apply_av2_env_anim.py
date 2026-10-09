#!/usr/bin/env python3
"""AV2 - animated environmental presentation (field props).

Idempotent, fail-closed source generator.  Every output is derived from a retail Platinum
resource whose SHA-256 is pinned below; the script refuses to touch a file in any other state.

  python3 -I tools/visual_overhaul/av2/apply_av2_env_anim.py          # apply (no-op if applied)
  python3 -I tools/visual_overhaul/av2/apply_av2_env_anim.py --check  # verify tree == AV2 output

Techniques (all native NSBTA texture-SRT animation; no new C, no particles, no palette edits):
  * "surge" profiles: retail linear scrolls are re-timed with a progress warp g(p) that keeps
    g(0)=0, g(1)=1 and stays monotone, so total travel, frame count, loop seam and first/last
    sample are identical to retail - only the in-loop speed varies (pulses / gusts / ripples).
  * "breath" profile: new sinusoidal texture-T oscillation tracks for Distortion World cliffs.
"""
import hashlib
import json
import math
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nitro_anim as na  # noqa: E402

ANIM_DIR = "res/field/props/animations"
LIST_NARC = na.BM_ANIME_LIST

BASELINE = "e91ee103"  # main at AV2 start (merge of PR #101)

# --------------------------------------------------------------------------- profiles

# harmonics: {k: (amplitude, phase)}  speed(p) = 1 + sum a_k cos(2 pi k (p - phase_k)); sum|a| < 1
SURGE = {
    # ---- A. lake water surface (models prop_model_074 / prop_model_311, material l_lake)
    "019": [
        ("l_lake", "transS", {1: (0.30, 0.00), 2: (0.10, 0.25)}),
        ("l_lake", "transT", {1: (0.15, 0.50), 2: (0.35, 0.15)}),
    ],
    # ---- D. waterfall flow gusts (taki / taki_top share one retail track; kemuri untouched)
    "018": [
        ("taki", "transT", {1: (0.35, 0.00), 2: (0.20, 0.30)}),
        ("taki_top", "transT", {1: (0.35, 0.00), 2: (0.20, 0.30)}),
    ],
    # ---- C. Galactic machinery / energy strips
    "022": [("ma_l03_2", "transS", {1: (0.60, 0.00), 2: (0.25, 0.20)})],
    "044": [("m_l04b", "transS", {1: (0.55, 0.50), 2: (0.25, 0.00)})],
    "004": [
        ("lab_01_2", "transS", {1: (0.55, 0.00), 2: (0.20, 0.25)}),
        ("lab_01_3", "transS", {1: (0.55, 0.50), 2: (0.20, 0.75)}),  # counter-phase panel
    ],
    "046": [("d26_o01b", "transT", {1: (0.60, 0.25), 2: (0.20, 0.00)})],
    "047": [("d26_o03b", "transS", {1: (0.60, 0.75), 2: (0.20, 0.50)})],
    "048": [("d26_o02c_lm1", "transT", {1: (0.50, 0.00), 2: (0.25, 0.50)})],
}

# ---- B. Distortion World: two new single-material tracks bound to prop_model_583 materials
BREATH_FRAMES = 121
BREATH_AMP = 320  # 0.078 tile ~ 2.5 texels (peak ~2.8 with 2nd harmonic) of the 32x32 cliff texture, texture-T (repeat T set)
NEW_FILES = {
    # file index -> (template, animation name, material, polarity)
    98: ("046", "dw_cliff_a", "criffp_lm5", +1),
    99: ("046", "dw_cliff_b", "file1Material", -1),
}
NEW_LIST_RECORDS = {
    583: dict(
        expect=na.pack_anime_record(0xFF, 0xFF, 0, (-1, -1, -1, -1)),
        new=na.pack_anime_record(1, 0, 0, (98, 99, -1, -1)),
    ),
}


def warp(p, harmonics):
    g = p
    for k, (a, ph) in harmonics.items():
        g += a / (2 * math.pi * k) * (math.sin(2 * math.pi * k * (p - ph)) + math.sin(2 * math.pi * k * ph))
    return g


def surge_samples(retail, harmonics):
    assert sum(abs(a) for a, _ in harmonics.values()) < 0.95, "speed profile must stay monotone"
    d = retail[-1]
    assert d != 0
    out = []
    for x in retail:
        p = x / d
        out.append(int(round(d * warp(p, harmonics))))
    out[-1] = retail[-1]
    # rounding may not break monotonicity in the travel direction
    sgn = 1 if d > 0 else -1
    for i in range(1, len(out)):
        assert (out[i] - out[i - 1]) * sgn >= 0, "non monotone at %d" % i
    return out


def breath_samples(polarity):
    out = []
    for i in range(BREATH_FRAMES):
        p = i / (BREATH_FRAMES - 1)
        v = math.sin(2 * math.pi * p) + 0.30 * math.sin(4 * math.pi * p)
        out.append(int(round(polarity * BREATH_AMP * v)))
    assert out[0] == 0 and abs(out[-1]) <= 1
    out[-1] = 0
    return out


def sha(b):
    return hashlib.sha256(b).hexdigest()


def path_of(idx, kind="nsbta"):
    return "%s/prop_animation_%03d.%s" % (ANIM_DIR, int(idx), kind)


def build_outputs(retail_files):
    """retail_files: {path: retail_bytes} for existing_paths().  Returns {path: new_bytes} (incl. new files + NARC)."""
    outs = {}
    for idx, edits in SURGE.items():
        p = path_of(idx)
        b = retail_files[p]
        e, g = {}, {}
        for mat, comp, harm in edits:
            cur = na.read_samples(b, mat, comp)
            g[(mat, comp)] = cur
            e[(mat, comp)] = surge_samples(cur, harm)
        outs[p] = na.patch_samples(b, e, g)
    for idx, (tpl, aname, mat, pol) in NEW_FILES.items():
        t = retail_files[path_of(tpl)]  # retail template, taken before the surge edit
        outs[path_of(idx)] = na.retarget_single_material(t, aname, mat, BREATH_FRAMES, trans_t=breath_samples(pol))
    narc = retail_files[LIST_NARC]
    for model, rec in NEW_LIST_RECORDS.items():
        narc = na.patch_anime_list_record(narc, model, rec["expect"], rec["new"])
    outs[LIST_NARC] = narc
    return outs


def meson_and_order_edits():
    """Append the two new files to meson.build + prop_animations.order (idempotent)."""
    changed = []
    mp = ANIM_DIR + "/meson.build"
    op = ANIM_DIR + "/prop_animations.order"
    s = open(mp).read()
    o = open(op).read()
    for idx in NEW_FILES:
        name = "prop_animation_%03d.nsbta" % idx
        if "'%s'" % name not in s:
            anchor = "    'prop_animation_%03d.%s',\n" % (idx - 1, "nsbtp" if idx == 98 else "nsbta")
            assert anchor in s, anchor
            s = s.replace(anchor, anchor + "    '%s',\n" % name)
            changed.append(mp)
        if name not in o.split():
            o = o.rstrip("\n") + "\n" + name + "\n"
            changed.append(op)
    return s, o, sorted(set(changed))


PINNED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "av2_pinned.json")


def existing_paths():
    return [path_of(i) for i in SURGE] + [LIST_NARC]


def main():
    mode = "check" if "--check" in sys.argv else "pin" if "--pin" in sys.argv else "apply"
    paths = existing_paths()
    cur = {p: open(p, "rb").read() for p in paths}
    if mode == "pin":
        retail = cur
        outs = build_outputs(retail)
        json.dump(
            {"baseline": BASELINE, "retail": {p: sha(b) for p, b in retail.items()}, "av2": {p: sha(b) for p, b in outs.items()}},
            open(PINNED, "w"),
            indent=2,
            sort_keys=True,
        )
        print("pinned %d retail / %d av2 digests" % (len(retail), len(outs)))
        return
    pinned = json.load(open(PINNED))
    states = set()
    for p in paths:
        h = sha(cur[p])
        if h == pinned["retail"][p]:
            states.add("retail")
        elif h == pinned["av2"][p]:
            states.add("applied")
        else:
            sys.exit("FAIL-CLOSED: %s is neither the pinned retail nor the AV2 output (sha %s)" % (p, h))
    if len(states) != 1:
        sys.exit("FAIL-CLOSED: mixed retail/applied tree")
    if states == {"applied"}:
        for p, h in pinned["av2"].items():
            if not os.path.exists(p) or sha(open(p, "rb").read()) != h:
                sys.exit("MISMATCH " + p)
        print("AV2 already applied (%d resources verified by digest)" % len(pinned["av2"]))
        return
    if mode == "check":
        sys.exit("tree is not in the AV2 state")
    outs = build_outputs(cur)
    for p, b in outs.items():
        if sha(b) != pinned["av2"][p]:
            sys.exit("pinned AV2 digest mismatch for %s (%s)" % (p, sha(b)))
    for p, b in outs.items():
        open(p, "wb").write(b)
    s, o, _ = meson_and_order_edits()
    open(ANIM_DIR + "/meson.build", "w").write(s)
    open(ANIM_DIR + "/prop_animations.order", "w").write(o)
    print("AV2 applied: %d resources, meson/order updated" % len(outs))


if __name__ == "__main__":
    main()
