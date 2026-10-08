import re, subprocess, json, os, sys, collections
# B4 Crystal evidence extractor (binding only; no rendering).
# Usage: CRYSTAL_ROOT=<checkout at pinned commit> python3 -I b4_verify_crystal.py <out.json>
R = os.environ.get('CRYSTAL_ROOT', '/home/user/pokecrystal')
PIN = '3bc8daa4173e96a7f4011dad3922eb6fa5dad5c6'
assert subprocess.check_output(['git', '-C', R, 'rev-parse', 'HEAD']).decode().strip() == PIN


def T(p):
    return open(os.path.join(R, p), encoding='utf-8', errors='replace').read()


def consts(path, prefix):
    out = []
    for l in T(path).split('\n'):
        m = re.match(r'\s*const\s+(' + prefix + r'\w+)', l)
        if m:
            out.append(m.group(1))
    return out


cc = 'constants/battle_anim_constants.asm'
gfx_names = [n for n in consts(cc, 'BATTLE_ANIM_GFX_')]
gfx_names = [g for g in gfx_names if g != 'BATTLE_ANIM_GFX_' and not g.endswith('_MAX')]
obj_names = consts(cc, 'BATTLE_ANIM_OBJ_')
fs_names = consts(cc, 'BATTLE_ANIM_FRAMESET_')
# object table (order == constants order)
objs = []
for m in re.finditer(r'^\tbattleanimobj\s+(.*)$', T('data/battle_anims/objects.asm'), re.M):
    a = [x.strip() for x in m.group(1).split(',')]
    objs.append(dict(flags=a[0], yfix=a[1], frameset=a[2], func=a[3], palette=a[4], gfx=a[5]))
assert len(objs) == len(obj_names), (len(objs), len(obj_names))
for o, n in zip(objs, obj_names):
    o['name'] = n
# gfx table: index 0 is a placeholder; entry i corresponds to constant i (constant 0 absent)
tbl = re.findall(r'anim_obj_gfx\s+(\d+),\s*(\w+)', T('data/battle_anims/object_gfx.asm'))
gfx_info = {}
for i, g in enumerate(gfx_names, 1):
    n, sym = tbl[i]
    gfx_info[g] = dict(index=i, tiles=int(n), symbol=sym)
# png for symbols
inc = T('gfx/battle_anims.asm') if os.path.exists(os.path.join(R, 'gfx/battle_anims.asm')) else ''
sym2png = {}
for m in re.finditer(r'(AnimObj\w+GFX):\s*INCBIN\s+"gfx/battle_anims/(\w+)\.2bpp', T('gfx/battle_anims.asm') if inc else T('data/battle_anims/object_gfx.asm')):
    sym2png[m.group(1)] = m.group(2)
# animation table + bodies
anim = T('data/moves/animations.asm')
table = re.findall(r'^\tdw (BattleAnim_\w+)', anim, re.M)
moves = consts('constants/move_constants.asm', '')
moves = [m for m in moves if m.isupper()]
# labels
labels = {}
cur = None
for l in anim.split('\n'):
    m = re.match(r'^(Battle\w+):', l)
    if m:
        cur = m.group(1); labels[cur] = []; continue
    if cur:
        labels[cur].append(l)
body = {}
for k, ls in labels.items():
    d = collections.defaultdict(list)
    for l in ls:
        m = re.match(r'\tanim_(\dgfx)\s+(.*)', l)
        if m: d['gfx'] += [x.strip() for x in m.group(2).split(',')]
        m = re.match(r'\tanim_obj\s+(\w+),\s*(-?\d+),\s*(-?\d+),\s*\$?(\w+)', l)
        if m: d['objs'].append(m.group(1))
        m = re.match(r'\tanim_call\s+(\w+)', l)
        if m: d['calls'].append(m.group(1))
        m = re.match(r'\tanim_bgeffect\s+(\w+)', l)
        if m: d['bg'].append(m.group(1))
        m = re.match(r'\tanim_(sound|wait|loop|bgp|obp0|obp1)\b', l)
        if m: d['n_' + m.group(1)].append(1)
    body[k] = d


def closure(k, seen=None):
    seen = seen or set()
    if k in seen or k not in body: return {}
    seen.add(k)
    d = collections.defaultdict(list)
    for kk in ('gfx', 'objs', 'bg'):
        d[kk] += body[k][kk]
    for c in body[k]['calls']:
        for kk, v in closure(c, seen).items():
            d[kk] += v
    return d


entries = []
for i, lab in enumerate(table):
    nm = moves[i] if i < len(moves) else None
    entries.append((i, nm, lab))
ev = dict(donor=dict(repo='79cbd8hmgj-wq/pokecrystal', commit=PIN), counts=dict(
    gfx_banks=len(gfx_names), anim_objects=len(obj_names), framesets=len(fs_names), anim_table_entries=len(table), anim_labels=len(labels)))
# per-gfx binding
cands = ['AEROBLAST', 'ANGELS', 'GLOBE', 'NOISE', 'REFLECT', 'ROPE', 'SHAPES', 'SHINE', 'WAVE', 'WEB', 'WIND']
bind = {}
for c in cands:
    g = 'BATTLE_ANIM_GFX_' + c
    gi = gfx_info[g]
    o_def = [o for o in objs if o['gfx'] == g]
    onames = {o['name'] for o in o_def}
    users = []
    for i, nm, lab in entries:
        cl = closure(lab)
        loaded = g in cl.get('gfx', [])
        used = sorted({x for x in cl.get('objs', []) if x in onames})
        if loaded or used:
            users.append(dict(table_index=i, move=nm, label=lab, loads_bank=loaded, objects_used=used,
                              bg_effects=sorted(set(cl.get('bg', [])))))
    bind[c] = dict(gfx_constant=g, index=gi['index'], tiles=gi['tiles'], symbol=gi['symbol'], png=f'gfx/battle_anims/{c.lower()}.png',
                   objects=[dict(name=o['name'], frameset=o['frameset'], func=o['func'], palette=o['palette']) for o in o_def],
                   users=users, n_users=len([u for u in users if u['objects_used']]))
ev['candidate_binding'] = bind
# funcs unique to candidate objects (what choreography each uses)
ev['all_gfx_bank_users_count'] = {g: sum(1 for i, nm, lab in entries if g in closure(lab).get('gfx', [])) for g in gfx_names}

# ---- Platinum comparison (script-level; no rendering) ----
P = os.environ.get('PLATINUM_ROOT', '/home/user/pokeplatinum-legacy')
rename = {'SONICBOOM': 'sonic_boom', 'DOUBLESLAP': 'double_slap'}
cmp_rows = {}
for c, b in bind.items():
    for u in b['users']:
        if not u['objects_used'] or not u['move'] or u['move'].startswith('ANIM_'):
            continue
        d = rename.get(u['move'], u['move'].lower())
        f = os.path.join(P, 'res/moves', d, 'anim.s')
        if not os.path.exists(f):
            cmp_rows[u['move']] = dict(platinum_dir=d, exists=False); continue
        t = open(f).read()
        cmp_rows[u['move']] = dict(
            platinum_dir=d, exists=True, family=c, lines=len([l for l in t.split('\n') if l.strip()]),
            particle_system=('LoadParticleResource' in t), sprite_manager=('InitSpriteManager' in t),
            bg_switch_or_fade=bool(re.search(r'SwitchBg|Func_FadeBg|Func_ShakeBg', t)),
            battler_effects=bool(re.search(r'MoveBattler|ScaleBattler|Func_Shake |FadeBattlerSprite|AddPokemonSprite', t)),
            own_particle_file=os.path.exists(os.path.join(P, 'res/graphics/battle/particles', d + '.spa')))
ev['platinum_comparison'] = dict(moves=cmp_rows, bound_moves=len(cmp_rows),
                                 missing_in_platinum=[m for m, r in cmp_rows.items() if not r['exists']],
                                 total_platinum_move_dirs=len(os.listdir(os.path.join(P, 'res/moves'))))
# ---- WAVE bank orphan check ----
loaders = [lab for lab in labels if 'BATTLE_ANIM_GFX_WAVE' in ''.join(labels[lab])]
ev['wave_bank'] = dict(bank_loaders=loaders, objects_using_bank=[o['name'] for o in objs if o['gfx'] == 'BATTLE_ANIM_GFX_WAVE'],
                       object_named_wave=[dict(name=o['name'], gfx=o['gfx']) for o in objs if o['name'] == 'BATTLE_ANIM_OBJ_WAVE'])
# ---- transitions ----
bt = T('engine/battle/battle_transition.asm')
ev['transitions'] = dict(path='engine/battle/battle_transition.asm',
    outros=sorted(set(re.findall(r'dw (StartTrainerBattle_(?:SineWave|ZoomToBlack|SpinToBlack|SpeckleToBlack))', bt))),
    selector='lead level + 3 vs enemy level (flash count) x cave/dungeon environment -> 4 starting points',
    starting_points=re.findall(r'db (BATTLETRANSITION_\w+)', bt)[:4])
# ---- per-turn residual animations ----
ev['residual_anims'] = [a for a in table if re.search(r'BattleAnim_In', a)]

json.dump(ev, open(sys.argv[1], 'w'), indent=1)
print(json.dumps(ev['counts']))
for c, b in bind.items():
    print(c, 'tiles', b['tiles'], 'objs', len(b['objects']), 'users', b['n_users'], [u['move'] or u['label'] for u in b['users'] if u['objects_used']][:12])
