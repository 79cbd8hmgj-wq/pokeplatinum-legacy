#!/usr/bin/env python3
"""Negative/positive tests for the mined opportunity pool (in-memory mutations; no files modified)."""
from __future__ import annotations

import copy
import sys

from common import *  # noqa: F401,F403
import build_candidate_groups as BCG
import mine_pool
import validate_pool as VP

doc = BCG.build(want_membership=True)
membership = doc.pop("_membership")
groups = {g["group_id"]: g for g in doc["groups"]}
POOL = jload(mine_pool.POOL_JSON)
fails = 0


def mined(p, cls=None, **kw):
    return next(r for r in p["records"] if r["origin"] == "mined" and (cls is None or r["classification"] == cls) and all(r.get(k) == v for k, v in kw.items()))


def expect(name, mutate, needle):
    global fails
    p = copy.deepcopy(POOL)
    mutate(p)
    errs = VP.validate_pool(groups, membership, p, check_reproducible=False)
    if not any(needle in e for e in errs):
        print(f"FAIL {name}: expected '{needle}', got {errs[:3]}")
        fails += 1
    else:
        print(f"ok   {name}")


base = VP.validate_pool(groups, membership, copy.deepcopy(POOL), check_reproducible=False)
assert base == [], base[:3]
print("ok   baseline valid")
expect("duplicate id", lambda p: p["records"].append(copy.deepcopy(mined(p))), "duplicate opportunity_id")
expect("missing group", lambda p: mined(p).update(group_id="nope/none/x"), "does not exist")
expect("stale digest", lambda p: mined(p).update(member_digest="0" * 20), "provenance differs")
expect("foreign member", lambda p: mined(p)["member_sample"].append("hgss:not:a:member"), "not in the group")
expect("diamond without exception", lambda p: mined(p).update(source_id="diamond"), "Diamond is control")
expect("non-DS donor", lambda p: mined(p).update(source_id="firered"), "outside the DS phase scope")
expect("deferred id in pool", lambda p: mined(p).update(opportunity_id=__import__("opportunities").load_deferred()["findings"][0]["finding_id"]), "deferred GBA/GBC")
expect("technique reusing pixels", lambda p: mined(p, "technique_donor").update(pixel_use="donor_pixels", donor_pixels_intended=True), "must not reuse donor pixels")
expect("component as whole asset", lambda p: mined(p, "component_donor").update(use_mode="whole_asset"), "inconsistent")
expect("replacement not preferred", lambda p: mined(p, "replacement_candidate")["ledger"].update(role="alternate"), "ledger-preferred")
expect("replacement with novelty", lambda p: mined(p, "replacement_candidate")["dims"].update(novelty=4), "composite does not match")
expect("bad composite", lambda p: mined(p).update(composite=1.0), "composite does not match")
expect("missing evidence pointer", lambda p: mined(p)["evidence_pointers"].append("docs/none.json"), "evidence pointer")
expect("missing host ref", lambda p: mined(p)["platinum_host"]["refs"].append("src/none.c"), "host ref")
expect("explicit finding dropped", lambda p: p["records"].__setitem__(slice(None), [r for r in p["records"] if r["origin"] != "explicit"]), "explicit findings not integrated")
expect("stale ledger input", lambda p: p["inputs"]["ledgers"].update(pokemon_icons="0"), "stale vs ledger")
expect("reference promoted", lambda p: mined(p).update(classification="reference_only"), "group dispositions")
# properties of the real pool
recs = POOL["records"]
assert POOL["groups_processed"] == len(groups)
assert not [r for r in recs if r["origin"] == "mined" and r["source_id"] == "diamond"], "Diamond mined records leaked"
import collections
per = collections.Counter(r["group_id"] for r in recs if r["origin"] == "mined")
assert max(per.values()) > 1, "no group yields multiple opportunity records"
print("ok   groups can legitimately yield multiple records")
top = sorted([r for r in recs if r.get("composite") and not r.get("subsumed_by")], key=lambda r: -r["composite"])[:20]
assert not any(r["classification"] == "replacement_candidate" for r in top), "replacement in the top 20"
rep = max(r["composite"] for r in recs if r["classification"] == "replacement_candidate")
non = max(r["composite"] for r in recs if r["classification"] in ("component_donor", "technique_donor", "novel_detail", "novel_capability"))
assert rep < non, "replacement outranks component/technique/novel work"
print("ok   replacement does not outrank component/technique/novel work")
q = jload(SEL / "IMPLEMENTATION_QUEUE.json")
assert q["phase"] == "ds_only" and all(i["source_id"].split(",")[0] in ("hgss", "pmd_sky", "ranger2") for i in q["ranked"])
print("ok   queue is DS-only and built from the pool")
sys.exit(1 if fails else 0)
