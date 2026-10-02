#!/usr/bin/env python3
"""C1 scope audit: only existing-move resources, C1 docs/manifests and move tooling may differ from the base commit."""
import re
import sys

from c1_lib import BASE_COMMIT, git

ALLOWED = [re.compile(p) for p in (
    r"^res/moves/[a-z0-9_]+/data\.json$", r"^res/moves/razor_wind/(script|anim)\.s$",
    r"^docs/overhaul/", r"^tools/overhaul/moves/")]
files = set(git("diff", "--name-only", BASE_COMMIT).split()) | set(git("ls-files", "--others", "--exclude-standard").split())
bad = sorted(f for f in files if not any(p.match(f) for p in ALLOWED))
print(f"{len(files)} files differ from {BASE_COMMIT[:8]}; outside C1 scope: {len(bad)}")
for f in bad:
    print("OUT OF SCOPE:", f)
sys.exit(1 if bad else 0)
