import sys; sys.path.insert(0,'.')
from trainer_lib import *
import locked_teams as L, curated_sets as C
T={**L.GALACTIC,**L.ELITE}
ALLOW={('AURA_BURST','TOXICROAK'),('SOUL_SIPHON','SPIRITOMB')}
for t,sets in [(k,v) for k,v in C.CURATED.items() if k in T]:
    for (sp,lv,it,_),mv in zip(T[t],sets):
        leg=legal_moves('SPECIES_'+sp,lv)
        bad=[m for m in mv if 'MOVE_'+m not in move_set()]
        ill=[m for m in mv if 'MOVE_'+m in move_set() and 'MOVE_'+m not in leg and (m,sp) not in ALLOW]
        if bad or ill: print(t,sp,lv,'MISSING',bad,'ILLEGAL',ill)
print('-- rematch')
for t,sp in L.REMATCH_SPECIES.items():
    d=load_trainer(t)
    for s,pm,mv in zip(sp,d['party'],C.CURATED[t]):
        lv=pm['level']; leg=legal_moves('SPECIES_'+s,lv)
        bad=[m for m in mv if 'MOVE_'+m not in move_set()]
        ill=[m for m in mv if 'MOVE_'+m in move_set() and 'MOVE_'+m not in leg and (m,s) not in {('STATIC_STRIKE','ELECTIVIRE'),('SOUL_SIPHON','SPIRITOMB'),('FROST_RUSH','GLALIE'),('METAL_RAY','RAICHU'),('MAGNET_VOLLEY','PROBOPASS'),('CROSS_CHOP','ELECTIVIRE')}]
        if bad or ill: print(t,s,lv,'MISSING',bad,'ILLEGAL',ill)
