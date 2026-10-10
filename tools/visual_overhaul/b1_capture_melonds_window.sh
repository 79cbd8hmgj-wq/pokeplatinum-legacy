#!/usr/bin/env bash
# Capture an existing melonDS window in X11, with optional DS button key presses.
# Requires Xvfb/display, xdotool and ImageMagick; does not send network requests.
set -euo pipefail
if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <window-id> <output-directory> [key ...]" >&2
  echo "Example: $0 123456 /tmp/opal-qa z x Return" >&2
  exit 2
fi
window="$1"; out="$2"; shift 2
[[ "$window" =~ ^[0-9]+$ ]] || { echo "Window ID must be numeric" >&2; exit 2; }
command -v xdotool >/dev/null
command -v import >/dev/null
mkdir -p "$out"
xdotool getwindowname "$window" > "$out/window-title.txt"
import -window "$window" "$out/before.png"
for key in "$@"; do
  xdotool key --window "$window" --clearmodifiers "$key"
  sleep 0.25
done
import -window "$window" "$out/after.png"
test -s "$out/before.png" && test -s "$out/after.png"
echo "PASS: captured two emulator window frames in $out"
echo "Caution: key names are HOST mappings; verify melonDS mappings before treating input as DS buttons."
