#!/usr/bin/env python3
"""C2 scope audit: only HM/TM/vendor sources, minimal text, C2 docs/manifests and C2 tooling may differ from base."""
import re
import sys

from c2_lib import BASE_COMMIT, git

ALLOWED = [re.compile(p) for p in (
    r"^res/moves/(cut|fly|rock_smash|rock_climb)/data\.json$",
    r"^res/battle/scripts/subscripts/subscript_defog\.s$",
    r"^res/items/data/tm(21|78)\.json$",
    r"^src/applications/party_menu/callbacks\.c$",
    r"^src/scrcmd_game_corner_prize\.c$", r"^src/overlay007/shop_menu\.c$", r"^src/unk_020494DC\.c$", r"^src/scrcmd\.c$",
    r"^res/field/scripts/scripts_veilstone_city_prize_exchange\.s$",
    r"^res/field/scripts/scripts_route_204_north\.s$",
    r"^res/field/scripts/scripts_victory_road_1f\.s$",
    r"^res/text/(unk_0543|veilstone_city_prize_exchange|oreburgh_city|route_204_north)\.json$",
    r"^docs/overhaul/", r"^tools/overhaul/c2/")]
files = set(git("diff", "--name-only", BASE_COMMIT).split()) | set(git("ls-files", "--others", "--exclude-standard").split())
bad = sorted(f for f in files if not any(p.match(f) for p in ALLOWED))
print(f"{len(files)} files differ from {BASE_COMMIT[:8]}; outside C2 scope: {len(bad)}")
for f in bad:
    print("OUT OF SCOPE:", f)
sys.exit(1 if bad else 0)
