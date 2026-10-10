#!/usr/bin/env bash
# Deterministic host preflight; no copyrighted ROM or firmware required.
set -euo pipefail
mkdir -p artifacts/b1-melonds
log=artifacts/b1-melonds/preflight.txt
exec > >(tee "$log") 2>&1
echo "Host: $(uname -a)"
for item in curl unzip Xvfb xdotool import; do
 command -v "$item"
done
url="https://github.com/melonDS-emu/melonDS/releases/download/1.1/melonDS-1.1-appimage-x86_64.zip"
curl -fL --retry 3 --connect-timeout 15 "$url" -o artifacts/b1-melonds/melonds.zip
sha256sum artifacts/b1-melonds/melonds.zip | tee artifacts/b1-melonds/download.sha256
mkdir -p artifacts/b1-melonds/unpacked
unzip -o -q artifacts/b1-melonds/melonds.zip -d artifacts/b1-melonds/unpacked
find artifacts/b1-melonds/unpacked -maxdepth 4 -type f -printf '%p\n'
app="$(find artifacts/b1-melonds/unpacked -type f -name '*.AppImage' | head -n 1)"
test -n "$app"
chmod +x "$app"
echo "melonDS AppImage: $app"
# Verify AppImage has a valid ELF payload and extract instead of requiring FUSE.
file "$app"
"$app" --appimage-extract >/dev/null
test -x squashfs-root/AppRun
printf 'APPIMAGE=%s\n' "$app" >artifacts/b1-melonds/emulator.env
# Start virtual X display and test input/capture utilities independently.
Xvfb :99 -screen 0 1024x768x24 -nolisten tcp >artifacts/b1-melonds/xvfb.log 2>&1 &
xvfb_pid=$!
trap 'kill "$xvfb_pid" 2>/dev/null || true' EXIT
export DISPLAY=:99
for i in $(seq 1 30); do xdpyinfo >/dev/null 2>&1 && break; sleep 0.2; done
xdpyinfo | grep dimensions
xdotool getdisplaygeometry
import -window root artifacts/b1-melonds/virtual-display.png
test -s artifacts/b1-melonds/virtual-display.png
# Validate binary can be invoked; don't assert debugger protocol without a running ROM.
set +e
timeout 8s squashfs-root/AppRun --help >artifacts/b1-melonds/emulator-help.txt 2>&1
status=$?
set -e
echo "Emulator --help exit: $status (timeout/GUI process can be normal)"
echo "PASS: installed melonDS AppImage, extracted executable, Xvfb, xdotool, screenshot capture"
echo "PENDING: launch user-supplied Opal ROM with GDB flags, handshake ARM9/ARM7 and battle scenario."
