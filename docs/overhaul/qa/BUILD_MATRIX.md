# Clean Build Matrix (D7 Phase 11)

Builds are produced by CI only (`.github/workflows/build.yml`: `make configure ROM_REVISION=N` then `make rom ROM_REVISION=N` on a fresh `ubuntu-24.04` checkout with Metroskrew); the
authoring environment has no ARM/Metroskrew toolchain or base ROM, so **no local build was run**. No manual or local-only binary patching is involved in either build.
The D7 PR adds a `continue-on-error` provenance step that prints the output ROM SHA-256 and toolchain versions into the job log/step summary (the ROM is never uploaded).

## Baseline: `main` @ `19cbadaaa296b7ae1c51e2be2e99226fe3d42813` (PR #21 merge)

| Revision | CI run | Job | Result |
|---|---|---|---|
| US Rev 0 | [37081807517](https://github.com/79cbd8hmgj-wq/pokeplatinum-legacy/actions/runs/37081807517) | `build (US rev 0)` | success |
| US Rev 1 | [37081807517](https://github.com/79cbd8hmgj-wq/pokeplatinum-legacy/actions/runs/37081807517) | `build (US rev 1)` | success |

(No output checksum was recorded for the baseline run: the provenance step did not exist yet.)

## D7 PR head

PENDING — recorded from the PR's CI run once complete (see the PR description / next section).
