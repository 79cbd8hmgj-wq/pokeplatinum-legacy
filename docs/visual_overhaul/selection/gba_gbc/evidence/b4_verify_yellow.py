import re, subprocess, json, os, sys
# B4 Yellow evidence extractor (trace only; no rendering).
# Usage: YELLOW_ROOT=<checkout at pinned commit> PLATINUM_ROOT=<pokeplatinum-legacy> python3 -I b4_verify_yellow.py <out.json>
Y = os.environ.get('YELLOW_ROOT', '/home/user/pokeyellow')
P = os.environ.get('PLATINUM_ROOT', '/home/user/pokeplatinum-legacy')
PIN = 'e89ead154b9968aa50eed9328ff2b38b6c194382'
assert subprocess.check_output(['git', '-C', Y, 'rev-parse', 'HEAD']).decode().strip() == PIN


def T(root, p):
    return open(os.path.join(root, p), encoding='utf-8', errors='replace').read()


def L(root, p, pat, after=0):
    rx = re.compile(pat)
    for i, l in enumerate(T(root, p).split('\n'), 1):
        if i > after and rx.search(l):
            return i
    raise AssertionError((p, pat))


ev = dict(donor=dict(repo='79cbd8hmgj-wq/pokeyellow', commit=PIN), platinum_checkout_note='Platinum anchors are from the repo checkout this file is committed in; they are not donor-pinned.')

# 1. entrance animation
e = T(Y, 'engine/battle/pikachu_entrance_anim.asm')
assert 'cp 9' in e and 'ld c, 2\n\tcall DelayFrames' in e and 'ld d, 7 * 13' in e
core = 'engine/battle/core.asm'
ev['entrance'] = dict(
    routine='engine/battle/pikachu_entrance_anim.asm:StarterPikachuBattleEntranceAnimation',
    lines=len(e.strip().split('\n')),
    passes=8, frames_per_pass=2, column_height_tiles=7, region_tiles='7x7 at hlcoord 0,5 sweeping to the right',
    behaviour='8 passes x 2 frames: each pass writes the party-pic tile block into one more column of a 7-row region as a diagonal staircase (tile ids below 7*7 are blanked), so the pic is revealed left to right in ~16 frames with no ball or poof',
    call_site=dict(path=core, line=L(Y, core, r'callfar StarterPikachuBattleEntranceAnimation')),
    regular_path=dict(path=core, poof_line=L(Y, core, r'ld a, POOF_ANIM'), send_out_line=L(Y, core, r'predef AnimateSendingOutMon', after=L(Y, core, r'ld a, POOF_ANIM'))),
    retreat=dict(path=core, starter_line=L(Y, core, r'callfar AnimationSlideMonOff'), regular='two-stage downscale (CopyDownscaledMonTiles) then clear'),
    sleep_aware_cry=dict(path=core, asleep=L(Y, core, r'ldpikacry e, PikachuCry37'), awake=L(Y, core, r'ldpikacry e, PikachuCry11')),
    faint_cry=dict(path=core, line=L(Y, core, r'ldpikacry e, PikachuCry4$')),
    oak_battle_cry=dict(path='engine/battle/common_text.asm', line=L(Y, 'engine/battle/common_text.asm', r'BATTLE_TYPE_PIKACHU')),
)

# 2. pic animation / emotions
pa = T(Y, 'engine/pikachu/pikachu_pic_animation.asm')
moods = re.findall(r"^\tdb\s+(\d+),\s*(\d+)\s*$", pa[pa.index('\nPikachuMoodLookupTable:'):pa.index('\nPikaPicAnimationScriptPointerLookupTable:')], re.M)
tbl = pa[pa.index('\nPikaPicAnimationScriptPointerLookupTable:'):]
bands = re.findall(r'^\tdb (\d+)\n((?:\tdpikapic \w+\n){5})', tbl, re.M)
assert len(moods) == 5 and len(bands) == 7, (len(moods), len(bands))
anim = T(Y, 'data/pikachu/pikachu_pic_animation.asm')
scripts = sorted(set(re.findall(r'^(PikaPicAnimScript\d+):', anim, re.M)), key=lambda s: int(s[len("PikaPicAnimScript"):]))
emo = T(Y, 'engine/pikachu/pikachu_emotions.asm')
n_emo = len(re.findall(r'pikaemotion_def PikachuEmotion\d+', emo))
pk = T(Y, 'gfx/pikachu.asm')
ev['pic_animation'] = dict(
    mood_thresholds=[int(a) for a, b in moods], happiness_bands=[int(b[0]) for b in bands], mood_columns=5,
    distinct_scripts_referenced=len(set(re.findall(r'dpikapic (\w+)', tbl))),
    script_labels_defined=len(scripts), loadgfx_commands=len(re.findall(r'pikapic_loadgfx', anim)),
    pikachu_gfx_incbin=len(re.findall(r'INCBIN', pk)), pikachu_png=len([f for f in os.listdir(os.path.join(Y, 'gfx/pikachu')) if f.endswith('.png')]),
    emotion_table_entries=n_emo,
    selector=dict(path='engine/pikachu/pikachu_pic_animation.asm', line=L(Y, 'engine/pikachu/pikachu_pic_animation.asm', r'^GetPikaPicAnimationScriptIndex')),
    only_caller=dict(path='engine/pikachu/pikachu_emotions.asm', line=L(Y, 'engine/pikachu/pikachu_emotions.asm', r'call GetPikaPicAnimationScriptIndex')),
    emote_bubble=dict(path='engine/pikachu/pikachu_emotions.asm', line=L(Y, 'engine/pikachu/pikachu_emotions.asm', r'^ShowPikachuEmoteBubble')),
    context='overworld talk-to-Pikachu portrait reaction (follower mechanic); not a battle sequence',
)

# 3. transitions
bt = T(Y, 'engine/battle/battle_transitions.asm')
tt = re.findall(r'dw (BattleTransition_\w+)\s+; %(\d+)', bt)
assert len(tt) == 8
ev['transitions'] = dict(path='engine/battle/battle_transitions.asm', table_line=L(Y, 'engine/battle/battle_transitions.asm', r'^BattleTransitions:'),
                         selector_bits=['trainer', 'enemy >= lead+3 (also sets spiral direction)', 'dungeon map'],
                         table=[dict(bits=b, routine=r) for r, b in tt], distinct=sorted({r for r, b in tt}))
se = T(Y, 'data/battle_anims/special_effects.asm')
ev['special_effects'] = dict(path='data/battle_anims/special_effects.asm', entries=len(re.findall(r'anim_special_effect \w+,', se)),
                             routines=sorted(set(re.findall(r'anim_special_effect \w+,\s+(\w+)', se))))

# 4. surfing pikachu
ev['surfing_pikachu'] = dict(minigame=dict(path='engine/minigame/surfing_pikachu.asm', line=L(Y, 'engine/minigame/surfing_pikachu.asm', r'^SurfingPikachuMinigame::')),
                             gfx_files=sorted(os.listdir(os.path.join(Y, 'gfx/surfing_pikachu'))),
                             other_use=dict(path='engine/printer/printer.asm', line=L(Y, 'engine/printer/printer.asm', r'ld de, SurfingPikachu2Graphics')),
                             context='stand-alone minigame + Game Boy Printer layouts; no battle or field presentation use')

# 5. Platinum anchors
ee = 'src/overlay005/encounter_effect.c'
ev['platinum_anchors'] = dict(
    encounter_effects=dict(path=ee, table_line=L(P, ee, r'sEncounterEffectTaskFuncs\[\]'), entries=31, enum='include/enc_effects.h:enum EncEffectCutIn'),
    slice_split=dict(path=ee, slice=L(P, ee, r'^void EncounterEffect_ScreenSlice'), split=L(P, ee, r'^void EncounterEffect_ScreenSplit')),
    sendout=dict(path='src/battle/battle_display.c', quick=L(P, 'src/battle/battle_display.c', r'monShowData->isQuickSendOut == 1'), ball_rotation=L(P, 'src/battle/battle_display.c', r'ballRotation\) != 0 && monShowData->isQuickSendOut')),
    common_anims=sorted(f for f in os.listdir(os.path.join(P, 'res/battle/scripts/common_anims')) if f in ('happy.s', 'shiny.s', 'level_up.s', 'sub_in.s', 'sub_out.s', 'infatuation.s', 'sleep.s')),
    friendship_checker=dict(path='src/applications/poketch/friendship_checker/graphics.c', icon_actions_enum=L(P, 'src/applications/poketch/friendship_checker/graphics.c', r'^enum IconActions'), level_fn=dict(path='src/applications/poketch/friendship_checker/main.c', line=L(P, 'src/applications/poketch/friendship_checker/main.c', r'^static u32 GetFriendshipLevel')), actions=['WANDER', 'GATHER', 'RUN_AWAY', 'SHOW_LIKE', 'SHOW_DISLIKE', 'JUMP']),
    overworld_emotes='include/comm_player_manager.h:enum Emote; include/unk_020655F4.h gMovementActionFuncs_Emote*',
)
json.dump(ev, open(sys.argv[1], 'w'), indent=1)
print(json.dumps(ev, indent=1)[:3500])
