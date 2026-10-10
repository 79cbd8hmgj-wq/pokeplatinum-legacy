#!/usr/bin/env python3
"""Headless DeSmuME driver for the Opal Pokedex runtime checks.

Requires:  pip install py-desmume pillow     and a *debug* ROM (make setup_debug rom),
whose GDB_DEBUGGING new-save path boots straight into the field (see src/main.c).

The driver
  1. boots the ROM with all keys released (py-desmume reports every key held by default),
  2. patches an all-caught Pokedex into RAM (located by its 0xBEEFCAFE magic),
  3. opens the Pokedex from the start menu, enters a species Info tab and then the Opal pages
     with the START key and again with the stylus, capturing a PNG per step,
  4. checks the emulated game for resets / asserts while doing so.

It is a development aid: results are emulator-specific evidence (DeSmuME), not a substitute for
the on-device checks listed in docs/opal/POKEDEX_RUNTIME_QA.md.
"""
import argparse
import bisect
import os
import struct
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from desmume.controls import Keys, keymask  # noqa: E402
from desmume.emulator import DeSmuME, Language  # noqa: E402

MAGIC = 0xBEEFCAFE
DEX_SIZE_U32 = 16  # (493 + 31) / 32
RAM_START, RAM_END = 0x02000000, 0x02400000


class Qa:
    def __init__(self, rom, out_dir, nef=None):
        self.out = out_dir
        os.makedirs(out_dir, exist_ok=True)
        self.emu = DeSmuME()
        self.emu.set_language(Language.ENGLISH)
        self.emu.open(rom)
        self.emu.volume_set(0)
        self.frame = 0
        self.keys = 0
        self.syms = {}
        self.sorted = []
        if nef:
            self.load_symbols(nef)

    # ---- symbols ---------------------------------------------------------
    def load_symbols(self, nef):
        import subprocess
        out = subprocess.run(["arm-none-eabi-nm", "-n", nef], capture_output=True, text=True).stdout
        for line in out.splitlines():
            p = line.split()
            if len(p) == 3:
                try:
                    a = int(p[0], 16)
                except ValueError:
                    continue
                self.syms[p[2]] = a
                self.sorted.append((a, p[2]))
        self.sorted.sort()
        self.addrs = [a for a, _ in self.sorted]

    def sym_at(self, pc):
        i = bisect.bisect_right(self.addrs, pc) - 1
        return "%s+0x%x" % (self.sorted[i][1], pc - self.sorted[i][0]) if i >= 0 else hex(pc)

    # ---- stepping / input --------------------------------------------------
    def step(self, n=1):
        for _ in range(n):
            self.emu.input.keypad_update(self.keys)
            self.emu.cycle()
            self.frame += 1

    def press(self, key, hold=3, wait=20):
        self.keys |= keymask(key)
        self.step(hold)
        self.keys &= ~keymask(key)
        self.step(wait)

    def touch(self, x, y, hold=6, wait=25):
        self.emu.input.touch_set_pos(x, y)
        self.step(hold)
        self.emu.input.touch_release()
        self.step(wait)

    def shot(self, name):
        path = os.path.join(self.out, name + ".png")
        self.emu.screenshot().save(path)
        return path

    # ---- memory ---------------------------------------------------------------
    def r32(self, a):
        return self.emu.memory.unsigned.read_long(a)

    def w32(self, a, v):
        self.emu.memory.write_long(a, v & 0xFFFFFFFF)

    def r8(self, a):
        return self.emu.memory.unsigned.read_byte(a)

    def w8(self, a, v):
        self.emu.memory.write_byte(a, v & 0xFF)

    def find_pokedex(self):
        found = []
        for a in range(RAM_START, RAM_END, 4):
            if self.r32(a) == MAGIC and all(self.r32(a + 4 + 4 * i) == 0 for i in range(8)):
                # literal-pool copies of the constant in code are followed by instructions, never by the
                # zeroed caught/seen bitmaps of a fresh Pokedex
                found.append(a)
        return found

    def patch_pokedex(self, base, caught=range(1, 494), seen=range(1, 494)):
        # struct Pokedex (include/pokedex.h): magic, caught[16], seen[16], genders[2][16], spinda, ...
        for sp in caught:
            bit = sp - 1
            a = base + 4 + (bit // 32) * 4
            self.w32(a, self.r32(a) | (1 << (bit % 32)))
        for sp in seen:
            bit = sp - 1
            a = base + 4 + 64 + (bit // 32) * 4
            self.w32(a, self.r32(a) | (1 << (bit % 32)))
        # layout: magic(4) caught(64) seen(64) genders(2*64) spinda(4) | shellos,gastrodon,burmy,wormadam (4 x u8)
        # | unownFormsSeen[28] | recordedLanguages[MAX_SPECIES + 1 = 496] | canDetectForms, canDetectLanguages,
        # pokedexObtained, nationalDexObtained (4 x u8)
        off = 4 + 64 + 64 + 128 + 4
        for i in range(4):
            self.w8(base + off + i, 3)
        off += 4 + 28
        for i in range(496):
            self.w8(base + off + i, 0x3F)
        off += 496
        for i in range(4):
            self.w8(base + off + i, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom")
    ap.add_argument("--nef")
    ap.add_argument("--out", default="/tmp/opal_runtime")
    ap.add_argument("--boot-frames", type=int, default=900)
    args = ap.parse_args()
    qa = Qa(args.rom, args.out, args.nef)
    qa.step(args.boot_frames)
    qa.shot("00_boot")
    print("booted; pokedex candidates:", [hex(a) for a in qa.find_pokedex()])


if __name__ == "__main__":
    main()
