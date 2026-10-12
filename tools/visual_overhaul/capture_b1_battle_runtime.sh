#!/usr/bin/env bash
# Run only after melonDS has loaded the intended Opal ROM and GDB stub is active.
set -euo pipefail
if ! command -v nds-toolkit >/dev/null 2>&1; then
  echo "ERROR: install NDS Disassembly Toolkit (nds-toolkit CLI) first" >&2
  exit 2
fi
if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <battle-state-label> <output-dir>" >&2
  echo "Requires melonDS ARM9 GDB RSP on localhost:3333 (JIT disabled)." >&2
  exit 2
fi
label="$1"
out="$2"
if [[ ! "$label" =~ ^[a-zA-Z0-9_-]+$ ]]; then
  echo "ERROR: label must use letters/digits/_/-" >&2
  exit 2
fi
mkdir -p "$out"
# Probe first so failure is explicit; the toolkit does not start the emulator.
nds-toolkit runtime probe --cpu arm9 >"$out/${label}.probe.json"
nds-toolkit runtime snapshot --cpu arm9 >"$out/${label}.snapshot.json"
nds-toolkit runtime trace capture --cpu arm9 --steps 2000 --output "$out/${label}.ndstrace"
nds-toolkit runtime trace inspect "$out/${label}.ndstrace" >"$out/${label}.inspect.json"
echo "Capture complete: $out/${label}.ndstrace"
echo "Capture does not itself prove a move animation is correct. Attach emulator screenshots and state notes."
