#!/usr/bin/env python3
"""Evolution scope audit: only evolution data, minimal evolution-engine plumbing, docs and tooling may differ from base."""
import json
import re
import sys

from evo_lib import BASE_COMMIT, LOCKED_FINAL, ROOT, git

ALLOWED = [re.compile(p) for p in (
    r"^res/pokemon/(%s)/data\.json$" % "|".join(sorted(LOCKED_FINAL)),
    r"^src/pokemon\.c$", r"^tools/dataproc/src/speciesproc\.c$", r"^generated/evolution_methods\.txt$",
    r"^docs/datafiles/pokemon\.md$", r"^docs/overhaul/", r"^tools/overhaul/evolution/")]

files = set(git("diff", "--name-only", BASE_COMMIT).split()) | set(git("ls-files", "--others", "--exclude-standard").split())
bad = sorted(f for f in files if not any(p.match(f) for p in ALLOWED))
print(f"{len(files)} files differ from {BASE_COMMIT[:8]}; outside evolution scope: {len(bad)}")
for f in bad:
    print("OUT OF SCOPE:", f)

# Species data files may differ ONLY in the `evolutions` key.
leak = []
for f in sorted(files):
    if f.startswith("res/pokemon/") and f.endswith("/data.json"):
        old, new = json.loads(git("show", f"{BASE_COMMIT}:{f}")), json.load(open(f"{ROOT}/{f}"))
        diff = sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k))
        if diff != ["evolutions"]:
            leak.append((f, diff))
for f, d in leak:
    print("NON-EVOLUTION FIELD CHANGED:", f, d)

# Engine changes are additive except for removal of Kadabra's vanilla Everstone-bypass special case,
# which would be incorrect once Kadabra evolves normally by level.
patch = git("diff", "-U0", BASE_COMMIT, "--", "src/pokemon.c", "tools/dataproc/src/speciesproc.c")
removed = [l for l in patch.splitlines() if l.startswith("-") and not l.startswith("---")]
allowed_removed = {"-    if (monSpecies != SPECIES_KADABRA", "-        && itemHoldEffect == HOLD_EFFECT_NO_EVOLVE"}
unexpected_removed = [l for l in removed if l not in allowed_removed]
print(f"engine source deletions: {len(removed)} (unexpected: {len(unexpected_removed)})")
for l in unexpected_removed:
    print("UNEXPECTED ENGINE DELETION:", l)
sys.exit(1 if bad or leak or unexpected_removed else 0)
