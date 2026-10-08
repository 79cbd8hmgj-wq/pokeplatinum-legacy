import re,subprocess,json,os,sys
# B2 FireRed evidence extractor. Usage: FIRERED_ROOT=<checkout at pinned commit> python3 -I b2_verify_firered.py <out.json>
R=os.environ.get('FIRERED_ROOT','/home/user/pokefirered')
sha=subprocess.check_output(['git','-C',R,'rev-parse','HEAD']).decode().strip()
assert sha=='037335f4c725d7c9aecdac87066f2002b4bd7e14',sha
def lines(p): return open(os.path.join(R,p),encoding='utf-8',errors='replace').read().split('\n')
def line_of(p,pat):
    rx=re.compile(pat); hits=[i for i,l in enumerate(lines(p),1) if rx.search(l)]
    assert hits,(p,pat); return hits[0]
spec={
 'src/map_preview_screen.c':[r'sMapPreviewScreenData\[MPS_COUNT\] =',r'^static u8 GetMapPreviewScreenIdx',r'^bool8 MapHasPreviewScreen\(',r'^bool32 MapHasPreviewScreen_HandleQLState2',r'^void MapPreview_LoadGfx',r'LoadPalette\(sMapPreviewScreenData\[idx\]\.palptr, BG_PLTT_ID\(13\)',r'^void MapPreview_StartForestTransition',r'^u16 MapPreview_CreateMapNameWindow',r'^static void Task_RunMapPreviewScreenForest',r'^const struct MapPreviewScreen \* GetDungeonMapPreviewScreenInfo',r'^u16 MapPreview_GetDuration',r'^void MapPreview_SetFlag'],
 'include/map_preview_screen.h':[r'^struct MapPreviewScreen',r'#define MPS_TYPE_CAVE',r'MPS_COUNT'],
 'src/overworld.c':[r'MapMapHasPreviewScreen_HandleQLState2\(gMapHeader.regionMapSectionId, MPS_TYPE_FOREST\)|MapHasPreviewScreen_HandleQLState2\(gMapHeader\.regionMapSectionId, MPS_TYPE_FOREST\)'],
 'src/fldeff_flash.c':[r'MapHasPreviewScreen_HandleQLState2\(gMapHeader\.regionMapSectionId, MPS_TYPE_CAVE\)',r'^static void Task_MapPreviewScreen_0',r'JOY_HELD\(B_BUTTON\)'],
 'src/field_fadetransition.c':[r'MapHasPreviewScreen\(header->regionMapSectionId, MPS_TYPE_CAVE\)'],
 'src/region_map.c':[r'GetDungeonMapPreviewScreenInfo\(mapsec\)'],
 'src/scrcmd.c':[r'MapPreview_SetFlag\(value\)'],
 'src/field_specials.c':[r'^static const u16 sEliteFourLightingPalettes',r'^static const u16 sChampionRoomLightingPalettes',r'^static const u8 sEliteFourLightingTimers',r'^static const u8 sChampionRoomLightingTimers',r'^void DoPokemonLeagueLightingEffect',r'^static void Task_RunPokemonLeagueLightingEffect\(u8 taskId\)$',r'^static void Task_CancelPokemonLeagueLightingEffect\(u8 taskId\)$',r'^void StopPokemonLeagueLightingEffectTask',r'^static const u16 sDeoxysObjectPals',r'^static const u8 sDeoxysCoords',r'^static const u8 sDeoxysStepCaps',r'^void DoDeoxysTriangleInteraction',r'^static void Task_DoDeoxysTriangleInteraction\(u8 taskId\)$',r'^static void MoveDeoxysObject\(u8 num\)$',r'^void IncrementBirthIslandRockStepCount',r'^void SetDeoxysTrianglePalette'],
 'src/field_special_scene.c':[r'^void FieldCB_ShowPortholeView'],
 'src/field_effect.c':[r'^u32 FldEff_MoveDeoxysRock',r'^static void Task_MoveDeoxysRock_Step\(u8 taskId\)$',r'^u32 FldEff_DestroyDeoxysRock',r'^static void Task_DeoxysRockCameraShake',r'^static void CreateDeoxysRockFragments\(struct Sprite \*sprite\)$'],
 'data/scripts/pokemon_league.inc':[r'^PokemonLeague_EventScript_DoLightingEffect',r'^PokemonLeague_EventScript_EnterRoom',r'^PokemonLeague_EventScript_OpenDoor'],
 'data/maps/PokemonLeague_ChampionsRoom/scripts.inc':[r'setflag FLAG_TEMP_3'],
 'data/maps/BirthIsland_Exterior/scripts.inc':[r'special SetDeoxysTrianglePalette',r'setvar VAR_DEOXYS_INTERACTION_NUM, 0',r'special DoDeoxysTriangleInteraction',r'dofieldeffect FLDEFF_DESTROY_DEOXYS_ROCK'],
 'data/field_effect_scripts.s':[r'FLDEFF_MOVE_DEOXYS_ROCK',r'FLDEFF_DESTROY_DEOXYS_ROCK'],
 'include/constants/songs.h':[r'#define SE_DEOXYS_MOVE'],
}
sym={}
for p,pats in spec.items():
    for pat in pats:
        if 'MapMapHas' in pat: pat=pat.split('|')[1]
        sym[f'{p}::{pat}']=line_of(p,pat)
# parse resources
def jasc(p):
    L=open(os.path.join(R,p)).read().split(); assert L[0]=='JASC-PAL'
    n=int(L[2]); return [tuple(map(int,L[3+3*k:6+3*k])) for k in range(n)]
def anim(prefix,count):
    P=[jasc(f'graphics/field_specials/{prefix}_{i}.pal') for i in range(count)]
    return {'frames':count,'colors_per_frame':len(P[0]),'animated_color_indices':[k for k in range(len(P[0])) if len({p[k] for p in P})>1],'distinct_frames':len({tuple(p) for p in P})}
src=open(os.path.join(R,'src/field_specials.c')).read()
def arr(name):
    m=re.search(name+r'\[\] = \{(.*?)\};',src,re.S); return [int(x) for x in re.findall(r'\b\d+\b',m.group(1))]
e4=arr('sEliteFourLightingTimers'); ch=arr('sChampionRoomLightingTimers'); caps=arr('sDeoxysStepCaps')
coords=[tuple(map(int,x)) for x in re.findall(r'\{\s*(\d+),\s*(\d+)\}',re.search(r'sDeoxysCoords\[\]\[2\] = \{(.*?)\};',src,re.S).group(1))]
mp=open(os.path.join(R,'src/map_preview_screen.c')).read()
body=mp[mp.index('sMapPreviewScreenData[MPS_COUNT]'):mp.index('sMapNameWindow')]
ents=re.findall(r'\.mapsec = (\w+),\s*\.type = (\w+),\s*\.flagId = (\w+),\s*\.tilesptr = (\w+)',body)
from collections import Counter
dirs=sorted(os.listdir(os.path.join(R,'graphics/map_preview')))
for d in dirs:
    assert os.path.exists(os.path.join(R,'graphics/map_preview',d,'tilemap.bin')) and os.path.exists(os.path.join(R,'graphics/map_preview',d,'tiles.png'))
tm=os.path.getsize(os.path.join(R,'graphics/map_preview/viridian_forest/tilemap.bin'))
dp=jasc('graphics/field_specials/deoxys_rock_0.pal'); dl=[jasc(f'graphics/field_specials/deoxys_rock_{i}.pal') for i in range(11)]
frag=[f'graphics/field_effects/pics/deoxys_rock_fragment_{x}.png' for x in ('top_left','top_right','bottom_left','bottom_right')]
assert all(os.path.exists(os.path.join(R,f)) for f in frag)
out={'commit':sha,'symbols':sym,
 'map_preview':{'table_entries':len(ents),'by_type':dict(Counter(e[1] for e in ents)),'unique_art_sets':len({e[3] for e in ents}),'art_dirs':dirs,'tilemap_bytes':tm,'tilemap_entries':tm//2,'tilemap_layout':'640 u16 entries (one 32x20 screen if row-major 32 wide; width inferred, not decoded)','palette_slot':'BG_PLTT_ID(13), 3 palettes (48 colors)','gating':'cave: world-map flag of the mapsec; forest: sHasVisitedMapBefore set by MapPreview_SetFlag; both skipped when mapsec unchanged or quest-log playback','duration_frames':{'first_visit':120,'repeat':40}},
 'palette_sequences':{'elite_four':{**anim('elite_four_lighting',12),'timers':e4,'timer_count':len(e4),'loop_frames_used':11,'loop_frames_total_ticks':sum(e4),'final_state_frame':11},
   'champion_room':{**anim('champion_room_lighting',9),'timers':ch,'timer_count':len(ch),'loop_frames_used':8,'loop_frames_total_ticks':sum(ch),'final_state_frame':8},
   'destination':'BG palette slot 7 (16 colors) via LoadPalette + ApplyGlobalTintToPaletteSlot(7,1)','task_priority':8},
 'deoxys':{'stages':11,'palette_frames':11,'palette_destination':'OBJ_PLTT_ID(10), 4 colors (PLTT_SIZEOF(4))','animated_color_indices':[k for k in range(len(dp)) if len({p[k] for p in dl})>1],'colors_in_pal':len(dp),'step_caps':caps,'step_caps_count':len(caps),'coords':coords,'coord_count':len(coords),'move_frames_normal':5,'move_frames_reset':60,'fragment_pngs':frag,'fragment_size':'8x8 x4'}}
json.dump(out,open(sys.argv[1],'w'),indent=1)
print(len(sym),'symbols')
