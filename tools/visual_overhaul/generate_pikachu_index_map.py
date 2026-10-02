#!/usr/bin/env python3
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
im=Image.open(ROOT/'res/pokemon/pikachu/male_front.png')
frame=im.crop((80,0,160,80))
p=frame.load()
x0,x1,y0,y1=18,45,36,56
lines=['# Pikachu Frame 1 Head/Chest Index Map','',
       '`.` = transparent/index 0. Coordinates are native 80x80 frame coordinates.','',
       '```text']
header='    '+''.join(str(x//10%10) if x%10==0 else ' ' for x in range(x0,x1+1))
header2='    '+''.join(str(x%10) for x in range(x0,x1+1))
lines += [header,header2]
for y in range(y0,y1+1):
    row=[]
    for x in range(x0,x1+1):
        v=int(p[x,y])
        row.append('.' if v==0 else '0123456789ABCDEF'[v])
    lines.append(f'{y:02d}  '+''.join(row))
lines += ['```','','Palette index key is res/pokemon/pikachu/normal.pal; image edits must preserve 0..15.']
(ROOT/'docs/visual_overhaul/review/pikachu_frame1_index_map.md').write_text('\n'.join(lines)+'\n')