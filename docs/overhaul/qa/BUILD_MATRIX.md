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

## D7 PR head `0f28b0b71d1da17915fe49f9d5c8ae334655b9b3` (PR #22)

CI run [37084418500](https://github.com/79cbd8hmgj-wq/pokeplatinum-legacy/actions/runs/37084418500). CI builds the PR *merge* commit `78866ea068e76b1257f36c380ad912135a40a86b`
(PR head merged into `main` @ `19cbadaa`). Later commits on the PR are documentation-only (`*.md`), which the workflow ignores.

| Revision | Job | Result | Output ROM SHA-256 (`pokeplatinum.us.nds`) | Size |
|---|---|---|---|---|
| US Rev 0 | `build (US rev 0)` | success | `081d53b22c67734a651f5b7ae1fcff4064c751cfe775363dbfbd50831b645b39` | 134217728 |
| US Rev 1 | `build (US rev 1)` | success | `e965b6aae8ecb443ef8b42566b1f18b8b7c3460607cdcb4d1cf7f40af450e37c` | 134217728 |

Toolchain (from the job logs): `arm-none-eabi-gcc (15:13.2.rel1-2) 13.2.1 20231009`, ninja 1.13.2, Python 3.12.3, runner `ubuntu-24.04`. Metroskrew (mwccarm) is installed by
`make skrew`; its version was not printed (the `tools/cw` listing in the provenance step came back empty), so it is not recorded here.

These are build-output checksums of unreleased test builds, recorded for provenance only; no ROM or patch is distributed.
