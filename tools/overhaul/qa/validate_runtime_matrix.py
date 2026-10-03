#!/usr/bin/env python3
"""D7 anti-fabrication gate: the runtime matrix must cover every mandatory group/revision, the markdown must be current, and no
PASS/FAIL may exist without actual result + tester + date + evidence. Also reports the release-state consequence."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_runtime_matrix as b  # noqa: E402
from qa_lib import Checker  # noqa: E402
from runtime_cases import CASES, GROUPS_REQUIRED, REVISIONS  # noqa: E402


def main():
    c = Checker("runtime matrix integrity")
    led = b.load_ledger()
    ids = [x[0] for x in CASES]
    c.check(len(ids) == len(set(ids)), "duplicate case ids")
    c.check({x[1] for x in CASES} >= set(GROUPS_REQUIRED), "a mandatory D7 group has no cases")
    for key, r in led["results"].items():
        cid, _, rev = key.partition("|")
        c.check(cid in ids and rev in REVISIONS, f"ledger entry {key} references an unknown case/revision")
        c.check(r["result"] in ("PASS", "FAIL", "NOT RUN"), f"{key}: invalid result {r['result']}")
        if r["result"] in ("PASS", "FAIL"):
            c.check(all(r.get(k) for k in ("actual", "tester", "date", "evidence")), f"{key}: {r['result']} without actual/tester/date/evidence")
    c.check(markdown_current(), "RUNTIME_TEST_MATRIX.md is stale (run build_runtime_matrix.py)")
    rc = c.finish()
    counts = {"PASS": 0, "FAIL": 0, "NOT RUN": 0}
    for cid in ids:
        for rev in REVISIONS:
            counts[led["results"].get(f"{cid}|{rev}", {"result": "NOT RUN"})["result"]] += 1
    print(f"runtime evidence: {counts} -> {'FULL RUNTIME EVIDENCE PRESENT' if counts['NOT RUN'] == 0 and counts['FAIL'] == 0 else 'RUNTIME QA PENDING (not VERIFIED)'}")
    return rc


def markdown_current():
    md, _ = b.render(b.load_ledger())
    return os.path.exists(b.MD) and open(b.MD, encoding="utf-8").read() == md


if __name__ == "__main__":
    sys.exit(main())
