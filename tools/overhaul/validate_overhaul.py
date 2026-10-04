#!/usr/bin/env python3
"""D7 master validator: orchestrates every existing overhaul validator (never re-implements them) in the order fixed by the
D7 plan, plus the D7 completion graphs and the subsystem mutation/regression suites. Fails (exit 1) if ANY child fails.

    python3 tools/overhaul/validate_overhaul.py            # run everything, write the report + JSON summary
    python3 tools/overhaul/validate_overhaul.py --no-write # run only
    python3 tools/overhaul/validate_overhaul.py --skip-suites   # validators only (fast)

Output: docs/overhaul/qa/MASTER_VALIDATION_REPORT.md and docs/overhaul/qa/master_validation_summary.json (no timestamps, so
reruns on an unchanged tree are byte-stable). Static validation only: a green master run is NOT runtime verification.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PY = sys.executable
T = "tools/overhaul"
REPORT = "docs/overhaul/qa/MASTER_VALIDATION_REPORT.md"
SUMMARY = "docs/overhaul/qa/master_validation_summary.json"

# (phase, id, title, argv relative to ROOT)
VALIDATORS = [
    (1, "docs", "Canonical-doc / release consistency", [f"{T}/qa/audit_release_consistency.py"]),
    (2, "species_c3", "Species / C3 ledgers + final corrections", [f"{T}/qa/validate_species_c3.py"]),
    (2, "evolution", "Evolution (Pass A)", [f"{T}/evolution/validate_evolutions.py"]),
    (3, "c1_moves", "C1 existing-move rebalance (82 edits)", [f"{T}/moves/validate_c1.py"]),
    (3, "created_moves", "Created moves 468-489", [f"{T}/qa/validate_created_moves.py"]),
    (3, "id_integrity", "Move/species/item ID integrity", [f"{T}/qa/validate_id_integrity.py"]),
    (4, "c2_tm_hm", "C2 TM/HM + HM battle + reusable TMs", [f"{T}/c2/validate_c2.py"]),
    (5, "availability", "Encounters / availability / special acquisition (manifest state)", [f"{T}/availability/validate_availability.py"]),
    (6, "trainers", "Trainers (D1)", [f"{T}/trainers/validate_trainers.py", "--no-report"]),
    (7, "economy", "Economy / EXP (D2)", [f"{T}/economy/validate_economy.py"]),
    (7, "progression", "Progression simulation integrity (D2 profiles, final source)", [f"{T}/qa/progression_report.py"]),
    (8, "pokeballs", "Poké Balls (D3)", [f"{T}/pokeballs/validate_pokeballs.py"]),
    (9, "breeding", "Breeding 2.0 (D4)", [f"{T}/validate_breeding.py"]),
    (10, "events", "Legendary/Mythical events (D5)", [f"{T}/validate_legendary_availability.py", "--no-report"]),
    (11, "postgame", "Battle Frontier / postgame (D6)", [f"{T}/postgame/validate_postgame.py"]),
    (12, "graphs", "Completion graphs (493 / evolution / events / gates), artifacts current", [f"{T}/qa/build_qa_graphs.py", "--check"]),
    (12, "runtime_matrix", "Runtime matrix integrity (no PASS without evidence)", [f"{T}/qa/validate_runtime_matrix.py"]),
    (12, "smoke", "Structural smoke (host-side, not runtime)", [f"{T}/qa/smoke_structural.py"]),
    (14, "mystery_starter", "Mystery Egg starter (D8)", [f"{T}/opening/validate_mystery_starter_script_native.py"]),
]
SUITES = [  # mutation / regression suites (run with their own directory as cwd)
    ("c1_tests", f"{T}/moves/test_validate_c1.py"), ("c2_tests", f"{T}/c2/test_validate_c2.py"),
    ("evolution_tests", f"{T}/evolution/test_validate_evolutions.py"),
    ("availability_tests", f"{T}/availability/test_validators.py"),
    ("trainer_tests", f"{T}/trainers/test_validate_trainers.py"),
    ("economy_tests", f"{T}/economy/test_validate_economy.py"), ("exp_model_tests", f"{T}/economy/test_exp_model.py"),
    ("pokeball_tests", f"{T}/pokeballs/test_pokeballs.py"), ("breeding_tests", f"{T}/breeding/test_validate_breeding.py"),
    ("event_tests", f"{T}/events/test_validate_legendary.py"), ("postgame_tests", f"{T}/postgame/test_validate_postgame.py"),
    ("qa_graph_tests", f"{T}/qa/test_qa_graphs.py"), ("qa_validator_tests", f"{T}/qa/test_qa_validators.py"),
    ("mystery_starter_tests", f"{T}/opening/test_mystery_starter_script_native.py"),
]
KEEP = re.compile(r"pass|fail|ok\b|error|warning|result|mutation|hits|reachable|integrity|checks|PASS|FAIL", re.I)


def git_dirty():
    out = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout
    return {l[3:] for l in out.splitlines()}


def run(argv, cwd=None):
    t0 = time.time()
    r = subprocess.run([PY, *argv] if not argv[0].startswith("/") else argv, cwd=cwd or ROOT, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip().splitlines()
    tail = next((l for l in reversed(out) if KEEP.search(l)), out[-1] if out else "")
    return r.returncode, tail.strip()[:150], round(time.time() - t0, 1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--skip-suites", action="store_true")
    a = ap.parse_args()
    before = git_dirty()
    results, restored = [], []
    for phase, ident, title, argv in VALIDATORS:
        rc, tail, secs = run(argv)
        results.append({"kind": "validator", "phase": phase, "id": ident, "title": title, "command": "python3 " + " ".join(argv),
                        "result": "PASS" if rc == 0 else "FAIL", "summary": tail, "seconds": secs})
        print(f"[{'PASS' if rc == 0 else 'FAIL'}] {title}: {tail}")
    if not a.skip_suites:
        for ident, rel in SUITES:
            rc, tail, secs = run([os.path.basename(rel)], cwd=os.path.join(ROOT, os.path.dirname(rel)))
            results.append({"kind": "suite", "phase": 13, "id": ident, "title": ident.replace("_", " "), "command": f"(cd {os.path.dirname(rel)} && python3 {os.path.basename(rel)})",
                            "result": "PASS" if rc == 0 else "FAIL", "summary": tail, "seconds": secs})
            print(f"[{'PASS' if rc == 0 else 'FAIL'}] suite {ident}: {tail}")
    # Some child validators rewrite their own tracked report on every run; restore any such side effect so the master run is read-only.
    for path in sorted(git_dirty() - before):
        if path.startswith("docs/overhaul/implementation/") and subprocess.run(["git", "ls-files", "--error-unmatch", path], cwd=ROOT, capture_output=True).returncode == 0:
            subprocess.run(["git", "checkout", "--", path], cwd=ROOT)
            restored.append(path)
    failed = [r for r in results if r["result"] != "PASS"]
    summary = {"schema": "pokeplatinum-overhaul/d7-master-validation/v1", "validators": sum(r["kind"] == "validator" for r in results),
               "suites": sum(r["kind"] == "suite" for r in results), "failed": [r["id"] for r in failed],
               "overall": "PASS" if not failed else "FAIL", "scope": "static validation only; NOT runtime verification",
               "child_report_side_effects_restored": restored, "results": [{k: v for k, v in r.items() if k != "seconds"} for r in results]}
    if not a.no_write:
        with open(os.path.join(ROOT, SUMMARY), "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=1, sort_keys=True)
            f.write("\n")
        rows = "\n".join(f"| {r['phase']} | {r['title']} | `{r['command']}` | **{r['result']}** | {r['summary'].replace('|', '/')} |" for r in results)
        md = f"""# Master Validation Report (D7)

Generated by `python3 tools/overhaul/validate_overhaul.py` (orchestrates the existing validators; it re-implements none of them).
Machine-readable: `docs/overhaul/qa/master_validation_summary.json`.

**Overall: {summary['overall']}** — {summary['validators']} validators + {summary['suites']} mutation/regression suites; failed: {', '.join(summary['failed']) or 'none'}.

**Scope: static validation only. A green master run is NOT runtime verification and does not make any subsystem `VERIFIED`** (see `QA_INDEX.md`).
The master run fails if any child fails. Phase numbers follow D7 Phase 5 order (1 docs, 2 species/evolution, 3 moves, 4 TM/HM, 5 encounters,
6 trainers, 7 economy/EXP, 8 balls, 9 breeding, 10 events, 11 Frontier/postgame, 12 graphs/smoke, 13 suites, 14 D8 Mystery Egg starter).

| Phase | Check | Command | Result | Child summary |
|---|---|---|---|---|
{rows}

## Reviewed warnings (accepted, documented)

* **Trainers — 16 warnings, 13 notes, 0 errors** (`implementation/trainers/TRAINER_VALIDATION_REPORT.md`): 7 evolution-stage notes on
  exact locked boss/Rival/commander teams (owner-locked species, accepted), 8 vanilla repeated-species ordinary trainers (preserved), and
  Volkner's vanilla `iv_scale 2500` on Electivire (preserved, not normalized). No change warranted.
* **Availability — 0 warnings.** Recorded wild-band drift vs. the family planning matrix for 7 families is non-blocking (all still pre-E4):
  see `qa/progression_gates.json` → `band_drift_vs_family_manifest`.
* **Progression simulation — tolerance flags are REPORTED, not gated** (model limits; see `PROGRESSION_SIMULATION_REPORT.md`).

## Child-report side effects

Child validators that rewrite their own tracked report were restored after the run: {', '.join(f'`{p}`' for p in restored) or 'none'}.
"""
        with open(os.path.join(ROOT, REPORT), "w", encoding="utf-8") as f:
            f.write(md)
    print(f"MASTER VALIDATION: {summary['overall']} ({len(results) - len(failed)}/{len(results)} children passed)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
