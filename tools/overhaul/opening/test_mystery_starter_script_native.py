#!/usr/bin/env python3
import importlib.util
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
MOD_PATH = HERE / "validate_mystery_starter_script_native.py"
spec = importlib.util.spec_from_file_location("d8_native", MOD_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

route = mod.read(mod.ROUTE)
thresholds, assignments = mod.parse_route(route)
sim = mod.simulate(thresholds, assignments)

assert len(sim) == 100
assert [r for r, _, _ in sim] == list(range(100))
assert Counter(species for _, species, _ in sim) == Counter(mod.EXPECTED_COUNTS)
assert sim[0][1] == "SPECIES_BULBASAUR"
assert sim[2][1] == "SPECIES_BULBASAUR"
assert sim[3][1] == "SPECIES_CHARMANDER"
assert sim[8][1] == "SPECIES_SQUIRTLE"
assert sim[9][1] == "SPECIES_PIKACHU"
assert sim[10][1] == "SPECIES_CHIKORITA"
assert sim[89][1] == "SPECIES_CHIMCHAR"
assert sim[90][1] == "SPECIES_PIPLUP"
assert sim[99][1] == "SPECIES_PIPLUP"

for _, species, branch in sim:
    if species == "SPECIES_PIKACHU":
        assert branch == "SPECIES_PIPLUP"

assert mod.main() == 0
print("OK: D8 script-native resolver boundary/weight tests passed")
