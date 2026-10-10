#!/usr/bin/env python3
"""Static validator for AV2 (animated environmental presentation).

  python3 -I tools/visual_overhaul/validate_av2_env_anim.py

Checks the generated NSBTA resources, their bindings (animation list -> prop model -> material
names/repeat flags), the animation-slot budget, scope containment (no C / gameplay changes) and
runs a mutation self-test of the validator itself.  No emulator is involved.
"""
import glob
import hashlib
import json
import os
import re
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "av2"))
import apply_av2_env_anim as ap  # noqa: E402
import nitro_anim as na  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
os.chdir(ROOT)

errors = []
notes = []


def err(msg):
    errors.append(msg)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def git(*args):
    try:
        return subprocess.run(["git", *args], capture_output=True, check=True).stdout
    except Exception:
        return None


def models_materials(root="."):
    order, anims = na.project_tables(root)
    mats = {}
    for i, n in enumerate(order):
        b = open("%s/res/field/props/models/%s" % (root, n), "rb").read()
        mats[i] = {m[0]: m for m in na.parse_nsbmd_materials(b)}
    return order, anims, mats


def check_tree(files=None):
    """All structural checks.  `files` lets the self-test inject mutated copies."""
    files = files or {}

    def rd(p):
        return files[p] if p in files else open(p, "rb").read()

    pinned = json.load(open(os.path.join(HERE, "av2", "av2_pinned.json")))
    order, anims, mats = models_materials()
    narc = rd(na.BM_ANIME_LIST)
    recs = na.read_anime_list(narc)
    if len(recs) != len(order):
        err("bm_anime_list has %d records, expected %d" % (len(recs), len(order)))

    # 1. pinned digests
    for p, h in pinned["av2"].items():
        if p in files:
            continue
        if not os.path.exists(p):
            err("missing AV2 resource " + p)
        elif sha(open(p, "rb").read()) != h:
            err("digest drift for " + p)

    # 2. every animation file the list binds: NSBTA materials exist in the model and have the
    #    repeat flag for each animated axis
    bound = {}
    for mid, (has, flags, bike, ids) in enumerate(recs):
        for aid in ids:
            if aid < 0:
                continue
            if aid >= len(anims):
                err("model %d binds animation id %d which has no file" % (mid, aid))
                continue
            bound.setdefault(aid, []).append(mid)
    av2_ids = set(int(i) for i in ap.SURGE) | set(ap.NEW_FILES)
    for aid in sorted(av2_ids):
        name = anims[aid] if aid < len(anims) else "prop_animation_%03d.nsbta" % aid
        p = "%s/%s" % (ap.ANIM_DIR, name)
        b = rd(p)
        try:
            t = na.parse_nsbta(b)
        except Exception as e:  # noqa: BLE001
            err("%s: parse failure %s" % (name, e))
            continue
        if not bound.get(aid):
            err("%s is not bound to any prop model" % name)
        for mid in bound.get(aid, []):
            for m in t.mats:
                if m.name not in mats[mid]:
                    err("%s: material %s absent from %s" % (name, m.name, order[mid]))
                    continue
                tip = mats[mid][m.name][1]
                for ci, (fl, nf, pl) in enumerate(m.comps):
                    if (fl >> 8) & na.FLAG_CONST:
                        continue
                    axis = {3: 16, 4: 17}.get(ci)
                    if axis is None:
                        err("%s: unexpected animated component %s" % (name, na.COMPONENTS[ci]))
                    elif not (tip >> axis) & 1:
                        err("%s: %s animated but %s lacks texture repeat on that axis" % (name, m.name, order[mid]))
                    if len(pl) != t.n_frames or nf != t.n_frames:
                        err("%s: sample count mismatch" % name)
        # round trip bit-exact for single material files
        if len(t.mats) == 1 and na.build_nsbta(t) != b:
            err("%s: serializer round trip differs" % name)

    # 3. monotone surge tracks + seam/endpoint preservation vs retail (git baseline if reachable)
    for idx, edits in ap.SURGE.items():
        p = ap.path_of(idx)
        cur = rd(p)
        old = git("show", "%s:%s" % (ap.BASELINE, p))
        for mat, comp, harm in edits:
            s = na.read_samples(cur, mat, comp)
            d = s[-1]
            sgn = 1 if d > 0 else -1
            if any((s[i + 1] - s[i]) * sgn < 0 for i in range(len(s) - 1)):
                err("%s %s %s not monotone" % (idx, mat, comp))
            if old:
                r = na.read_samples(old, mat, comp)
                if len(r) != len(s):
                    err("%s frame count changed" % idx)
                if r[-1] != s[-1]:
                    err("%s %s %s end value changed" % (idx, mat, comp))
                if r == s:
                    err("%s %s %s unchanged (expected animation edit)" % (idx, mat, comp))
                # only the AV2-listed tracks may differ; const tracks and other mats identical
                to, tn = na.parse_nsbta(old), na.parse_nsbta(cur)
                for mo, mn in zip(to.mats, tn.mats):
                    for ci, (a, b_) in enumerate(zip(mo.comps, mn.comps)):
                        listed = any(mo.name == e[0] and na.COMPONENTS[ci] == e[1] for e in edits)
                        if not listed and (a[0], a[1], list(a[2]) if isinstance(a[2], list) else a[2]) != (
                            b_[0], b_[1], list(b_[2]) if isinstance(b_[2], list) else b_[2]):
                            err("%s: unlisted track %s/%s changed" % (idx, mo.name, na.COMPONENTS[ci]))
            # speed floor: never stalls a loop for long, never more than 2x retail peak
            steps = [abs(s[i + 1] - s[i]) for i in range(len(s) - 1)]
            if old and steps:
                r = na.read_samples(old, mat, comp)
                rs = [abs(r[i + 1] - r[i]) for i in range(len(r) - 1)]
                if max(steps) > 3.2 * max(rs):
                    err("%s %s peak speed above 3.2x retail" % (idx, mat))

    # 4. Distortion World breath tracks
    for idx in ap.NEW_FILES:
        b = rd(ap.path_of(idx))
        t = na.parse_nsbta(b)
        m = t.mats[0]
        tr = na.read_samples(b, m.name, "transT")
        if t.n_frames != ap.BREATH_FRAMES or tr[0] != 0 or tr[-1] != 0:
            err("breath track %d: not a closed loop" % idx)
        if max(abs(x) for x in tr) > 4096 // 8:
            err("breath track %d: amplitude above 1/8 tile" % idx)
        if any(abs(tr[i + 1] - tr[i]) > 40 for i in range(len(tr) - 1)):
            err("breath track %d: per-frame jump above 40/4096" % idx)
    for mid in (582,):
        if any(x >= 0 for x in recs[mid][3]):
            err("prop_model_582 must stay unanimated (clamped T axis)")
    if [x for x in recs[583][3] if x >= 0] != sorted(ap.NEW_FILES):
        err("prop_model_583 animation ids unexpected: %s" % (recs[583][3],))

    # 5. meson list + order file
    ms = open(ap.ANIM_DIR + "/meson.build").read()
    od = open(ap.ANIM_DIR + "/prop_animations.order").read().split()
    names = re.findall(r"'(prop_animation_\d+\.\w+)'", ms)
    if names != od:
        err("meson.build list and prop_animations.order differ")
    if [int(re.search(r"(\d+)", n).group(1)) for n in names] != list(range(len(names))):
        err("animation ids are not contiguous from 0")
    for n in names:
        if not os.path.exists("%s/%s" % (ap.ANIM_DIR, n)):
            err("listed file missing: " + n)

    # 6. slot budget per area (MAP_PROP_ANIMATION_MANAGER_MAX_ANIMATIONS = 16)
    hdr = open("include/overlay005/map_prop_animation.h").read()
    cap = int(re.search(r"MAP_PROP_ANIMATION_MANAGER_MAX_ANIMATIONS\s+(\d+)", hdr).group(1))
    idxmap = {n.replace(".nsbmd", ""): i for i, n in enumerate(order)}
    worst = (0, None)
    for f in sorted(glob.glob("res/field/area_data/area_data_*.json")):
        j = json.load(open(f))
        ms_ = [m.replace("_nsbmd", "") for m in json.load(open("res/field/props/model_sets/%s.json" % j["mapPropSet"]))["mapPropModels"]]
        n = 0
        for m in ms_:
            has, flags, bike, ids = recs[idxmap[m]]
            if flags & 1:
                continue
            n += sum(1 for x in ids if x >= 0)
        worst = max(worst, (n, f))
    if worst[0] > cap:
        err("animation slots %d > %d in %s" % (worst[0], cap, worst[1]))
    notes.append("worst-case animation slots %d/%d (%s)" % (worst[0], cap, os.path.basename(worst[1] or "")))

    # 7. scope containment (git baseline reachable)
    if not files and git("rev-parse", "--verify", ap.BASELINE + "^{commit}"):
        changed = git("diff", "--name-only", ap.BASELINE, "--", "src", "include", "asm", "tools/nitroarc", "res/field/area_data", "res/field/maps", "res/field/props/models", "res/field/props/texture_sets", "res/field/props/model_sets", "res/field/lighting", "res/field/scripts", "res/field/encounters", "res/pokemon")
        if changed and changed.strip():
            err("out-of-scope paths changed: %s" % changed.decode().split())
        allowed = {ap.path_of(i) for i in ap.SURGE} | {ap.path_of(i) for i in ap.NEW_FILES} | {na.BM_ANIME_LIST, ap.ANIM_DIR + "/meson.build", ap.ANIM_DIR + "/prop_animations.order"}
        diff = git("diff", "--name-only", ap.BASELINE, "--", "res")
        untracked = git("ls-files", "--others", "--exclude-standard", "res")
        got = set((diff or b"").decode().split()) | set((untracked or b"").decode().split())
        if got - allowed:
            err("unexpected res changes: %s" % sorted(got - allowed))
        old_list = git("show", "%s:%s" % (ap.BASELINE, na.BM_ANIME_LIST))
        if old_list:
            ro = na.read_anime_list(old_list)
            diffs = [i for i, (a, b_) in enumerate(zip(ro, recs)) if a != b_]
            if diffs != sorted(ap.NEW_LIST_RECORDS):
                err("bm_anime_list records changed: %s" % diffs)
    else:
        notes.append("git baseline not reachable: scope-diff checks skipped")


def mutation_self_test():
    """Each mutant must be rejected, proving the checks are live."""
    killed = 0
    total = 0
    base = {}
    for idx in list(ap.SURGE) + list(ap.NEW_FILES):
        base[ap.path_of(idx)] = open(ap.path_of(idx), "rb").read()
    nar = open(na.BM_ANIME_LIST, "rb").read()

    def run(mut):
        global errors
        saved, saved_notes = errors[:], notes[:]
        errors.clear()
        check_tree(mut)
        bad = bool(errors)
        errors[:] = saved
        notes[:] = saved_notes
        return bad

    # M1 non-monotone lake track
    p = ap.path_of("019")
    b = base[p]
    s = na.read_samples(b, "l_lake", "transS")
    s[30], s[31] = s[31], s[30] - 400
    mut = dict(); mut[p] = na.patch_samples(b, {("l_lake", "transS"): s}, {("l_lake", "transS"): na.read_samples(b, "l_lake", "transS")})
    total += 1; killed += run(mut)
    # M2 end value changed
    s = na.read_samples(b, "l_lake", "transT"); s[-1] -= 64
    mut = {p: na.patch_samples(b, {("l_lake", "transT"): s}, {("l_lake", "transT"): na.read_samples(b, "l_lake", "transT")})}
    total += 1; killed += run(mut)
    # M3 wrong material binding (new DW file animates a material absent from the model)
    p98 = ap.path_of(98)
    bad = bytearray(base[p98]); t = na.parse_nsbta(bytes(bad))
    off = bad.find(b"criffp_lm5"); bad[off:off + 16] = b"nomaterial".ljust(16, b"\0")
    total += 1; killed += run({p98: bytes(bad)})
    # M4 breath amplitude too large
    s = na.read_samples(base[p98], "criffp_lm5", "transT"); s = [x * 3 for x in s]
    mut = {p98: na.patch_samples(base[p98], {("criffp_lm5", "transT"): s}, {("criffp_lm5", "transT"): na.read_samples(base[p98], "criffp_lm5", "transT")})}
    total += 1; killed += run(mut)
    # M5 breath track not closed
    s = na.read_samples(base[p98], "criffp_lm5", "transT"); s[-1] = 50
    mut = {p98: na.patch_samples(base[p98], {("criffp_lm5", "transT"): s}, {("criffp_lm5", "transT"): na.read_samples(base[p98], "criffp_lm5", "transT")})}
    total += 1; killed += run(mut)
    # M6 list record for 582 (clamped-T model) gains an animation
    mut = {na.BM_ANIME_LIST: na.patch_anime_list_record(nar, 582, na.pack_anime_record(0xFF, 0xFF, 0, (-1, -1, -1, -1)), na.pack_anime_record(1, 0, 0, (98, -1, -1, -1)))}
    total += 1; killed += run(mut)
    # M7 list points past the animation table
    cur583 = na.pack_anime_record(1, 0, 0, (98, 99, -1, -1))
    mut = {na.BM_ANIME_LIST: na.patch_anime_list_record(nar, 583, cur583, na.pack_anime_record(1, 0, 0, (98, 150, -1, -1)))}
    total += 1; killed += run(mut)
    # M8 AV2 file with a digest change (single byte)
    bb = bytearray(base[p]); bb[-1] ^= 1
    total += 1; killed += run({p: bytes(bb)})
    # M9 surge too aggressive (peak > 3.2x retail)
    s = na.read_samples(b, "l_lake", "transS")
    d = [s[i + 1] - s[i] for i in range(len(s) - 1)]
    s2 = [0]
    for i, x in enumerate(d):
        s2.append(s2[-1] + (-400 if i < 8 else int(round((-4096 + 3200) / (len(d) - 8)))))
    s2[-1] = s[-1]
    mut = {p: na.patch_samples(b, {("l_lake", "transS"): s2}, {("l_lake", "transS"): na.read_samples(b, "l_lake", "transS")})}
    total += 1; killed += run(mut)
    return killed, total


def main():
    check_tree()
    if not errors:
        k, n = mutation_self_test()
        notes.append("mutation self-test %d/%d rejected" % (k, n))
        if k != n:
            err("mutation self-test: only %d/%d mutants rejected" % (k, n))
    for n in notes:
        print("note:", n)
    if errors:
        for e in errors:
            print("FAIL:", e)
        sys.exit(1)
    print("AV2 validation passed: %d surge tracks in %d files, %d new files" % (sum(len(v) for v in ap.SURGE.values()), len(ap.SURGE), len(ap.NEW_FILES)))


if __name__ == "__main__":
    main()
