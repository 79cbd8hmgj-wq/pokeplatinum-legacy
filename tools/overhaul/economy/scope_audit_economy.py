#!/usr/bin/env python3
"""Economy scope audit: only EXP/economy-owned files may differ from the pinned base."""
import re
import sys

from economy_lib import BASE_COMMIT, git

ALLOWED = [re.compile(p) for p in (
    r"^src/battle/battle_script\.c$", r"^include/battle/battle_context\.h$", r"^include/constants/battle\.h$",
    r"^include/data/trainer_class_prize_mul\.h$", r"^include/data/mart_items\.h$", r"^generated/mart_specialties_id\.txt$",
    r"^res/items/data/(potion|super_potion|hyper_potion|max_potion|full_restore|revive|hp_up|protein|iron|calcium|zinc|carbos|"
    r"antidote|burn_heal|ice_heal|awakening|parlyz_heal|full_heal|rare_candy)\.json$",
    r"^res/field/scripts/scripts_pastoria_city_east_house\.s$", r"^res/text/pastoria_city_east_house\.json$",
    r"^res/pokemon/move_tutors\.json$",
    r"^res/field/scripts/scripts_fight_area_mart\.s$",
    r"^docs/overhaul/STATUS\.md$", r"^docs/overhaul/implementation/economy/", r"^tools/overhaul/economy/")]
files = set(git("diff", "--name-only", BASE_COMMIT).split()) | set(git("ls-files", "--others", "--exclude-standard").split())
bad = sorted(f for f in files if not any(p.match(f) for p in ALLOWED))
print(f"{len(files)} files differ from {BASE_COMMIT[:8]}; outside economy scope: {len(bad)}")
for f in bad:
    print("OUT OF SCOPE:", f)
sys.exit(1 if bad else 0)
