import re,subprocess,json,os,sys
# B1 Emerald evidence extractor. Usage: EMERALD_ROOT=<checkout at pinned commit> python3 -I b1_verify_emerald.py <out.json>
R=os.environ.get('EMERALD_ROOT','/home/user/pokeemerald')
sha=subprocess.check_output(['git','-C',R,'rev-parse','HEAD']).decode().strip()
assert sha=='a81cfacbe53bcc229fc4d93cb10b56a58e77a15f',sha
def lines(path): return open(os.path.join(R,path),encoding='utf-8',errors='replace').read().split('\n')
def find(path,pat,defn=True):
    rx=re.compile(pat)
    out=[]
    for i,l in enumerate(lines(path),1):
        if rx.search(l): out.append(i)
    return out
spec={
 'src/field_effect.c':[r'^static void Task_FieldMoveShowMonOutdoors\(u8 taskId\)',r'^static void FieldMoveShowMonOutdoorsEffect_LoadGfx\(struct Task \*task\)',r'^static void Task_FieldMoveShowMonIndoors\(u8 taskId\)',r'^static void FieldMoveShowMonIndoorsEffect_LoadGfx\(struct Task \*task\)',r'^bool8 FldEff_FieldMoveShowMon\(void\)',r'^bool8 FldEff_FieldMoveShowMonInit\(void\)',r'^static u8 InitFieldMoveMonSprite\(',r'^static void SpriteCB_FieldMoveMonSlideOnscreen',r'^static void Task_SurfFieldEffect\(u8 taskId\)',r'^static void SurfFieldEffect_FieldMovePose',r'^static void SurfFieldEffect_ShowMon',r'^static void SurfFieldEffect_JumpOnSurfBlob',r'^static void Task_FlyOut\(u8 taskId\)',r'^static void FlyOutFieldEffect_ShowMon',r'^static void FlyOutFieldEffect_BirdLeaveBall',r'^static void FlyOutFieldEffect_BirdSwoopDown',r'^static void FlyOutFieldEffect_JumpOnBird',r'^static void Task_FlyIn\(u8 taskId\)',r'^static void FlyInFieldEffect_JumpOffBird',r'^static void Task_UseWaterfall\(u8 taskId\)',r'^static bool8 WaterfallFieldEffect_ShowMon',r'^static bool8 WaterfallFieldEffect_RideUp',r'^static bool8 DiveFieldEffect_ShowMon',r'^static void Task_TeleportWarpOut\(u8 taskId\)',r'^static void TeleportWarpOutFieldEffect_SpinExit',r'^u8 FldEff_AshLaunch',r'^u8 FldEff_AshPuff',r'^u8 FldEff_RayquazaSpotlight',r'^bool8 FldEff_DestroyDeoxysRock',r'^static void Task_DeoxysRockCameraShake'],
 'src/field_effect_helpers.c':[r'^u32 FldEff_(Shadow|TallGrass|JumpTallGrass|LongGrass|JumpLongGrass|ShortGrass|SandFootprints|DeepSandFootprints|BikeTireTracks|Splash|JumpSmallSplash|JumpBigSplash|FeetInFlowingWater|Ripple|HotSpringsWater|WaterSurfacing|Ash|SurfBlob|Dust|SandPile|Bubbles|BerryTreeGrowthSparkle|Sparkle)\(void\)'],
 'data/field_effect_scripts.s':[r'^gFieldEffectScriptPointers::',r'FLDEFF_(FIELD_MOVE_SHOW_MON|FIELD_MOVE_SHOW_MON_INIT|USE_SURF|USE_FLY|FLY_IN|USE_WATERFALL|USE_DIVE|USE_TELEPORT|ASH_PUFF|ASH_LAUNCH|SAND_PILLAR|BUBBLES|SPARKLE|DUST|RAYQUAZA_SPOTLIGHT|DESTROY_DEOXYS_ROCK)\s*$'],
 'data/scripts/field_move_scripts.inc':[r'dofieldeffect FLDEFF_'],
 'src/fldeff_misc.c':[r'SpriteCB_SandPillar_BreakTop\(struct Sprite \*sprite\)$'],
}
res={}
for p,pats in spec.items():
    for pat in pats:
        if p.endswith('.c') and 'FldEff_(' in pat:
            for i in find(p,pat):
                name=re.search(r'FldEff_\w+',lines(p)[i-1]).group(0); res[f'{p}::{name}']=i
        elif 'FLDEFF_(' in pat or 'dofieldeffect' in pat:
            for i in find(p,pat):
                l=lines(p)[i-1].strip(); res[f'{p}::{l}']=i
        else:
            f=find(p,pat)
            assert f,(p,pat)
            res[f"{p}::{pat}"]=f[-1]
gfx=[ 'graphics/field_effects/pics/'+x for x in 'field_move_streaks.png field_move_streaks_indoors.png field_move_streaks.bin field_move_streaks_indoors.bin ash_puff.png ash_launch.png ash.png ground_impact_dust.png sparkle.png small_sparkle.png bubbles.png splash.png jump_big_splash.png jump_small_splash.png ripple.png water_surfacing.png surf_blob.png bird.png spotlight.png sand_pillar/0.png sand_pillar/1.png sand_pillar/2.png deoxys_rock_fragment_top_left.png hot_springs_water.png sand_pile.png deep_sand_footprints.png sand_footprints.png bike_tire_tracks.png short_grass.png tall_grass.png long_grass.png pokeball_glow.png'.split()]
miss=[g for g in gfx if not os.path.exists(os.path.join(R,g))]
print('missing gfx',miss)
json.dump({'commit':sha,'symbols':res,'gfx_existing':[g for g in gfx if g not in miss]},open(sys.argv[1],'w'),indent=1)
print(len(res),'symbols')
