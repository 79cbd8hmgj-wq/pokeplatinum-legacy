import re, subprocess, json, os, struct, sys
# B3 PMD Red evidence extractor.
# Usage: PMDRED_ROOT=<checkout at pinned commit> PLATINUM_ROOT=<pokeplatinum-legacy> python3 -I b3_verify_pmd_red.py <out.json>
R = os.environ.get('PMDRED_ROOT', '/home/user/pmd-red')
P = os.environ.get('PLATINUM_ROOT', '/home/user/pokeplatinum-legacy')
PIN = 'aefe6a46bcc5df13142225ef673a1ee2ac1b760b'
sha = subprocess.check_output(['git', '-C', R, 'rev-parse', 'HEAD']).decode().strip()
assert sha == PIN, sha


def text(root, p):
    return open(os.path.join(root, p), encoding='utf-8', errors='replace').read()


def line_of(root, p, pat):
    rx = re.compile(pat)
    for i, l in enumerate(text(root, p).split('\n'), 1):
        if rx.search(l):
            return i
    raise AssertionError((p, pat))


# ---------- 1. status-bit ids ----------
sh = text(R, 'include/constants/status.h')
ids = {m.group(1): int(m.group(2)) for m in re.finditer(r'#define STATUS_SPRITE_ID_(\w+)\s+(\d+)', sh) if m.group(1) != 'LAST'}
last = int(re.search(r'#define STATUS_SPRITE_ID_LAST\s+(\d+)', sh).group(1))
assert sorted(ids.values()) == list(range(last + 1)) and len(ids) == 29, (len(ids), last)
id_name = {v: k for k, v in ids.items()}

# ---------- 2. bit -> (gfx, palette) ----------
dps = text(R, 'src/dungeon_pokemon_sprites.c')
gfx_enum = re.search(r'enum \{(.*?)\};', dps[dps.index('STATUS_GFX_NONE,') - 20:], re.S).group(1)
gfx_names = [x.strip().rstrip(',') for x in gfx_enum.split('\n') if x.strip().startswith('STATUS_GFX_')]
ginfo = {}
for m in re.finditer(r'\[(STATUS_GFX_\w+)\]\s*=\s*\{(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*TILE_SIZE_2BPP \* (\d+)\s*\}', dps):
    n, w, h, vram, unk, cnt, off = m.group(1), *map(int, m.groups()[1:])
    ginfo[n] = dict(w_tiles=w, h_tiles=h, vram_tile_index=vram, unused_field=unk, frames=cnt, offset_tiles2bpp=off)
sinfo = {}
for m in re.finditer(r'\[STATUS_SPRITE_ID_(\w+) \+ 1\]\s*=\s*\{(STATUS_GFX_\w+),\s*(\d+)\}', dps):
    sinfo[m.group(1)] = dict(gfx=m.group(2), obj_palette_bank=int(m.group(3)))
assert set(sinfo) == set(ids), set(ids) ^ set(sinfo)
gfx_files = re.findall(r'graphics/status/(\w+)\.4bpp', dps)
order_gfx = [g for g in gfx_names if g not in ('STATUS_GFX_NONE',)]
assert [g.replace('STATUS_GFX_', '').lower() for g in order_gfx] == [f if f != 'cross_eyed' else 'cross_eyed' for f in gfx_files], (order_gfx, gfx_files)

# PNG cross-check: frames stacked vertically, frame = w_tiles x h_tiles tiles
png = {}
for g, gi in ginfo.items():
    f = g.replace('STATUS_GFX_', '').lower()
    d = open(os.path.join(R, 'graphics/status', f + '.png'), 'rb').read()
    w, h, bd, ct = struct.unpack('>IIBB', d[16:26])
    assert (w, bd, ct) == (gi['w_tiles'] * 8, 4, 3), (f, w, bd, ct)
    assert h == gi['frames'] * gi['h_tiles'] * 8, (f, h)
    png[g] = dict(file=f'graphics/status/{f}.png', width=w, height=h, frame_px=[w, gi['h_tiles'] * 8], frames=h // (gi['h_tiles'] * 8), indexed_4bpp=True)

shared = {}
for k, v in sinfo.items():
    shared.setdefault(v['gfx'], []).append(dict(bit=ids[k], name=k, obj_palette_bank=v['obj_palette_bank']))
for g in shared:
    shared[g].sort(key=lambda e: e['bit'])

# ---------- 3. logical condition -> bit ----------
src = text(R, 'src/dungeon_8041AD0.c')
tables = {}
for m in re.finditer(r'static const u32 sStatusSpriteMasks_(\w+)\[\] = \{(.*?)\n\};', src, re.S):
    rows = []
    for r in re.finditer(r'(?:/\*(.*?)\*/)?\[(\w+|\d+)\]\s*=\s*(\w+)', m.group(2)):
        rows.append((r.group(2), r.group(3)))
    tables[m.group(1)] = rows
assert len(tables) == 13, list(tables)
logical = []
for t, rows in tables.items():
    for state, mask in rows:
        if mask != '0' and mask != 'STATUS_NONE':
            logical.append(dict(class_table=t, state=state, bit=ids[mask.replace('STATUS_SPRITE_', '')]))
        elif state not in ('STATUS_NONE', '1') or (state == '1' and mask != '0'):
            pass
silent = sum(1 for t, rows in tables.items() for s, m in rows if m == '0' and s != 'STATUS_NONE')
by_bit = {}
for e in logical:
    by_bit.setdefault(id_name[e['bit']], []).append(f"{e['class_table']}:{e['state']}")

# extra (non-table) sources, from UpdateStatusIconFlags
upd = src[src.index('void UpdateStatusIconFlags'):src.index('void sub_8041AD0')]
extras = dict(
    grudge='entityInfo->grudge -> GRUDGE' in upd.replace('\n', ' ') or ('->grudge' in upd and 'STATUS_SPRITE_GRUDGE' in upd),
    exposed=('->exposed' in upd and 'STATUS_SPRITE_EXPOSED' in upd),
    lowhp_team_hp_below_quarter=('maxHPStat' in upd and '>>= 2' in upd and 'STATUS_SPRITE_LOWHP' in upd),
    lowhp_item_holder_identified=('itemHoldersIdentified' in upd),
    stat_down_any_of_10_checks=len(re.findall(r'(offensiveMultipliers|defensiveMultipliers|offensiveStages|defensiveStages|hitChanceStages)\[\d\]', upd)),
    sleep_class_suppressed_when_id_0xb9_and_turns_eq_0x7f=('0xb9' in upd),
)
assert all(v for v in extras.values()), extras
assert extras['stat_down_any_of_10_checks'] == 10

# ---------- 4. faithful port of GetNextStatusSymbol / UpdateStatusSprite ----------
LAST = last


def next_symbol(sprite_status, slot, cur):
    last_bit = (1 << LAST) if slot != 0 else 1
    second_last = (1 << LAST) if slot != 0 else (1 << (LAST - 1))
    n = LAST if slot == 0 else 1
    if sprite_status == 0:
        return 0
    bits = cur if cur != 0 else last_bit
    for _ in range(n):
        bits = (bits << 1) & 0xFFFFFFFF
        if bits > second_last:
            bits = last_bit
        if sprite_status & bits:
            return bits
    return 0


def simulate(status_bits, updates, mask_change=None):
    """Return per-slot list of (first_update, bit_index) transitions. One update == one FrameUpdateDungeonStatusSprites call."""
    slots = [dict(status=0, frame=0), dict(status=0, frame=0)]
    log = [[], []]
    st = status_bits
    for u in range(updates):
        if mask_change and u in mask_change:
            st = mask_change[u]
        for i, s in enumerate(slots):
            if st == 0:
                s['status'] = 0
                continue
            if s['status'] == 0:
                s['frame'] = 0
            if s['frame'] < 1:
                sym = next_symbol(st, i, s['status'])
                s['status'] = sym
                nf = 60
            else:
                nf = s['frame'] - 1
            s['frame'] = nf
            cur = s['status'].bit_length() - 1 if s['status'] else None
            if not log[i] or log[i][-1][1] != cur:
                log[i].append((u, cur))
    return log


def nm(b):
    return None if b is None else id_name[b]


def bit(n):
    return 1 << ids[n]


cases = {}
c = simulate(bit('BURNED') | bit('CONFUSED') | bit('LOWHP'), 61 * 5)
cases['burned+confused+lowhp (3 non-frozen bits)'] = [[(u, nm(b)) for u, b in s] for s in c]
c = simulate(bit('SLEEPLESS') | bit('STAT_DOWN'), 61 * 5)
cases['sleepless(bit0)+stat_down(bit27): wrap from top to bit0'] = [[(u, nm(b)) for u, b in s] for s in c]
c = simulate(bit('SLEEPLESS'), 61 * 3)
cases['sleepless only (bit 0 is reachable only through wrap)'] = [[(u, nm(b)) for u, b in s] for s in c]
c = simulate(bit('FROZEN'), 61 * 3)
cases['frozen only (slot 0 can never select bit 28)'] = [[(u, nm(b)) for u, b in s] for s in c]
c = simulate(bit('FROZEN') | bit('POISONED') | bit('CONFUSED'), 61 * 4)
cases['frozen+poisoned+confused (frozen in slot 1, others cycle in slot 0)'] = [[(u, nm(b)) for u, b in s] for s in c]
c = simulate(bit('POISONED') | bit('CONFUSED'), 61 * 2, {30: bit('CONFUSED')})
cases['poisoned+confused, poison cured at update 30 mid-hold: poison glyph is still drawn until update 61 (stale glyph; only a fully empty mask clears at once)'] = [[(u, nm(b)) for u, b in s] for s in c]
# hold length: first two transitions of a 2-bit mask
hold = simulate(bit('BURNED') | bit('CONFUSED'), 61 * 3)[0]
hold_updates = hold[1][0] - hold[0][0]
assert hold_updates == 61, hold_updates
# full cycle order for all 28 slot-0 bits
allmask = sum(1 << i for i in range(LAST))  # bits 0..27
seq = [x[1] for x in simulate(allmask, 61 * 29)[0]]
cycle_order = [nm(b) for b in seq]
# idle start tests bit 1 first (bit 0 only after wrapping past bit 27): order = bits 1..27, then 0, then 1 again
assert cycle_order == [id_name[i] for i in list(range(1, LAST)) + [0, 1]], cycle_order

# ---------- 5. draw geometry ----------
draw = dps[dps.index('static void DrawStatusSprite'):dps.index('static void LoadStatusGraphics')]
shape_size = {'0,0': [8, 8], '0,1': [16, 16], '0,2': [32, 32], '1,2': [32, 16], '2,0': [8, 16]}
geom = {}
for cs in re.finditer(r'((?:\s*case STATUS_GFX_\w+:)+)(.*?)break;', draw, re.S):
    names = re.findall(r'STATUS_GFX_(\w+)', cs.group(1))
    body = cs.group(2)
    sp = int(re.search(r'SpriteSetShape\(&sStatusSpriteOAM, (\d)\)', body).group(1))
    sz = int(re.search(r'SpriteSetSize\(&sStatusSpriteOAM, (\d)\)', body).group(1))
    xo = re.search(r'SpriteSetX\(&sStatusSpriteOAM, posX( \+ 8)?\)', body)
    yv = 'posY' if re.search(r'SpriteSetY\(&sStatusSpriteOAM, posY\)', body) else 'posY - 16'
    for n in names:
        geom['STATUS_GFX_' + n] = dict(oam_shape=sp, oam_size=sz, oam_px=shape_size[f'{sp},{sz}'], x_extra=8 if xo.group(1) else 0, y_expr=yv)
assert len(geom) == 16, len(geom)
for g, gm in geom.items():
    gi = ginfo[g]
    assert gm['oam_px'] == [gi['w_tiles'] * 8, gi['h_tiles'] * 8], (g, gm, gi)

# ---------- 6. anchors ----------
anch = {
    'include/constants/status.h': [r'#define STATUS_SPRITE_ID_SLEEPLESS', r'#define STATUS_SPRITE_ID_LAST', r'#define STATUS_SPRITE_SHIELD_BLUE'],
    'src/dungeon_pokemon_sprites.c': [r'^typedef struct DungeonPokemonStatusSprite', r'^typedef struct DungeonPokemonSprite$', r'^static const struct StatusGraphicsInfo sStatusGfxInfo', r'^static const u8 sStatusGfx\[\]', r'^static const struct StatusSprite sStatusSpritesInfo', r'^static u32 GetNextStatusSymbol', r'^static u32 StatusSymbolBitToIndex', r'^static void UpdateStatusSprite', r'^static void DrawStatusSprite\(s16', r'^static void LoadStatusGraphics', r'^void InitDungeonPokemonSprites', r'^void UpdateDungeonPokemonSprite\(', r'^void UpdateDungeonPokemonSprite2', r'^void FrameUpdateDungeonStatusSprites', r'newFrame = 60;', r'% graphicsCount;', r'switch \(sDungeonPokemonSprites->frame % 4\)'],
    'src/dungeon_8041AD0.c': [r'^u32 EntityGetStatusSprites', r'^void UpdateStatusIconFlags', r'^static const u32 sStatusSpriteMasks_SleepClassStatus', r'^static const u32 sStatusSpriteMasks_MuzzledStatus', r'entityInfo->id == 0xb9', r'itemHoldersIdentified', r'spriteStatus = spriteStatus \| STATUS_SPRITE_STAT_DOWN'],
    'src/dungeon_mon_sprite_render.c': [r'sub_8005700\(posArray', r'UpdateDungeonPokemonSprite2\(entInfo', r'statusSprites = EntityGetStatusSprites', r'UpdateDungeonPokemonSprite\(entInfo'],
    'src/dungeon_vram.c': [r'FrameUpdateDungeonStatusSprites\('],
    'src/dungeon_util.c': [r'UpdateDungeonPokemonSprite\(info->dungeonSpriteId'],
    'src/sprite.c': [r'^void sub_8005700'],
    'include/structs/axdata.h': [r'#define AX_POSITION_SETS_COUNT'],
    'src/status_checks.c': [r'^bool8 HasStatusThatPreventsActing'],
}
anchors = {f'{p}::{pat}': line_of(R, p, pat) for p, pats in anch.items() for pat in pats}

# ---------- 7. Platinum side ----------
pl = {
    'src/battle/healthbox.c': [r'HEALTHBOX_PART_STATUS_HEALTHY_0,', r'if \(flags & HEALTHBOX_INFO_STATUS\)', r'^static void HealthBox_DrawStatusIcon\(.*\)$'],
    'src/battle/battle_lib.c': [r'^enum BattleSubAnimation Battler_StatusCondition', r'^static const enum BattleSubAnimation sEffectsAlwaysShown', r'^BOOL BattleSystem_ShouldShowStatusEffect'],
    'src/battle/battle_display.c': [r'^void BattleDisplay_SetStatusIcon'],
    'src/battle/battle_controller.c': [r'healthboxData.status = Battler_StatusCondition', r'message.status = Battler_StatusCondition'],
    'src/battle/indicator.c': [r'^Indicator \*Indicator_New'],
    'src/battle_sub_menus/battle_bag_sprites.c': [r'Indicator_New\(spriteSystem'],
    'src/battle_anim/script_funcs_status.c': [r'^void BattleAnimSpriteFunc_Sleep', r'^void BattleAnimSpriteFunc_Freeze', r'^void BattleAnimSpriteFunc_Burn', r'^void BattleAnimSpriteFunc_ConfusionStatus', r'#define SLEEP_SPRITE_ANIM_FRAMES', r'#define BURN_SPRITE_VISIBLE_FRAMES', r'#define CONFUSION_STATUS_SPRITE_ORB_REV_FRAMES'],
    'include/battle/healthbox.h': [r'ManagedSprite \*mainSprite;'],
}
panch = {f'{p}::{pat}': line_of(P, p, pat) for p, pats in pl.items() for pat in pats}
# script-level uses of status animations (transient, event driven)
scr = {}
sdir = os.path.join(P, 'res/battle/scripts/subscripts')
for fn in sorted(os.listdir(sdir)):
    for i, l in enumerate(text(P, 'res/battle/scripts/subscripts/' + fn).split('\n'), 1):
        m = re.search(r'(PlayBattleAnimation|SetHealthBoxStatusIcon) \w+, (BATTLE_ANIMATION_(?:ASLEEP|POISONED|BURNED|FROZEN|PARALYZED|CONFUSED|INFATUATED))', l)
        if m:
            scr.setdefault(m.group(2), []).append(f'{fn}:{i}:{m.group(1)}')
# persistent volatile-condition display: no volatile symbol in healthbox/battle_display
hb = text(P, 'src/battle/healthbox.c') + text(P, 'src/battle/battle_display.c')
volatile_refs = len(re.findall(r'statusVolatile|VOLATILE_CONDITION', hb))
hb_cases = re.findall(r'case BATTLE_ANIMATION_(\w+):', text(P, 'src/battle/healthbox.c')[text(P, 'src/battle/healthbox.c').index('if (flags & HEALTHBOX_INFO_STATUS)'):][:900])

out = dict(
    schema_version=1,
    batch='B3_pmd_red_status_close',
    donor=dict(repo='79cbd8hmgj-wq/pmd-red', commit=PIN),
    platinum_checkout_note='Platinum anchors are from the repo checkout this file is committed in; they are not donor-pinned.',
    status_bit_ids=ids, status_bit_count=len(ids),
    bit_to_graphic_and_palette=sinfo,
    graphic_table=ginfo, png_crosscheck=png,
    graphics_shared_by_multiple_bits={g: v for g, v in shared.items() if len(v) > 1},
    graphics_count=len(ginfo),
    logical_condition_to_bit=logical,
    logical_conditions_with_a_symbol=len(logical),
    logical_states_deliberately_without_a_symbol=silent,
    bit_sources=by_bit,
    non_table_sources_verified=extras,
    slot_model=dict(
        slots=2,
        slot0='bits 0..27 (all except FROZEN); a search from idle tests bit 1 first, bit 0 is reached only after wrapping past bit 27',
        slot1='FROZEN (bit 28) only',
        hold_updates_per_glyph=hold_updates,
        update_cadence='FrameUpdateDungeonStatusSprites is called once per DungeonRunFrameActions tick (dungeon_vram.c sub_803E490); wall-clock = ~1 s per glyph is inferred from the 60-count and the 4-frame art cadence, vblank pacing of DungeonRunFrameActions not traced',
    ),
    cycle_order_slot0_all_bits_active=cycle_order,
    simulated_cases=cases,
    draw_geometry=geom,
    anchors=anchors,
    platinum=dict(
        anchors=panch,
        healthbox_status_cases=hb_cases,
        battler_status_condition_priority=['ASLEEP', 'POISONED (poison)', 'BURNED', 'FROZEN', 'PARALYZED', 'POISONED (toxic)'],
        status_animation_script_uses=scr,
        volatile_condition_refs_in_healthbox_and_battle_display=volatile_refs,
    ),
)
json.dump(out, open(sys.argv[1], 'w'), indent=1)
print('ok', len(anchors), 'donor anchors', len(panch), 'platinum anchors')
