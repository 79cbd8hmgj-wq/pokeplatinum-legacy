# Opal Pokédex local QA harness (not built by default)

`opal_qa_harness.c` is a **development-only** boot shim: after the new-game save is created it enqueues
the Pokédex application directly instead of the field, so the Opal pages can be driven in an emulator
without playing through the intro. It is never part of a normal build and must not be committed into
`src/`, `src/meson.build`, `platinum.us/main.lsf` or `src/game_start.c`
(`validate_opal_integration.py` fails if any of those reference it).

To use locally:

1. copy `opal_qa_harness.c` to `src/`;
2. `git apply tools/opal_pokedex/qa_harness/qa_harness_local.patch` (adds the file to `src/meson.build` and
   redirects `GameStartNewSave_Exit` in `src/game_start.c`);
3. add `Object main.nef.p/src_opal_qa_harness.c.o` to the `Static main` block of `platinum.us/main.lsf`;
4. build, then drive with `tools/opal_pokedex/runtime_qa.py` (py-desmume, headless);
5. revert all four edits before committing.
