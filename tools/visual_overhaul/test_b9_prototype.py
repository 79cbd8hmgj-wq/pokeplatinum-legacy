#!/usr/bin/env python3
"""Static lifecycle/cadence regression gates for the B9 Metal Claw proof.

These tests do not replace ROM compilation, emulator testing or VRAM measurement.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
METAL_CLAW = ROOT / "res/moves/metal_claw/anim.s"


def commands(source):
    """Strip comments and blank lines without altering command ordering."""
    return [line.strip() for line in source.splitlines()
            if line.strip() and not line.lstrip().startswith(("//", "#"))]


class B9MetalClaw(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cmd = commands(METAL_CLAW.read_text(encoding="utf-8"))

    def test_native_sprite_manager_lifecycle_is_unchanged(self):
        c = self.cmd
        self.assertEqual(c.count("InitPokemonSpriteManager"), 1)
        self.assertEqual(c.count("FreePokemonSpriteManager"), 1)
        self.assertEqual(c.count("InitSpriteManager 0, 4, 1, 1, 1, 1, 0, 0"), 1)
        self.assertEqual(c.count("FreeSpriteManager 0"), 1)
        self.assertLess(c.index("FreePokemonSpriteManager"), c.index("InitSpriteManager 0, 4, 1, 1, 1, 1, 0, 0"))
        self.assertLess(c.index("WaitForAnimTasks", c.index("EndLoop")), c.index("FreeSpriteManager 0"))
        self.assertEqual(c[-2:], ["FreeSpriteManager 0", "End"])
        self.assertFalse(any(x.startswith(("LoadParticleResource", "CreateEmitter", "OpalSheetBegin", "OpalSheetEnd")) for x in c))

    def test_two_native_hit_beats_receive_one_finishing_glint(self):
        c = self.cmd
        begin = c.index("BeginLoop 2")
        end = c.index("EndLoop", begin)
        loop = c[begin + 1:end]
        self.assertEqual(loop.count("PlaySoundEffectR SEQ_SE_DP_W013"), 1)
        self.assertEqual(loop.count("Func_Shake 1, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER"), 1)
        self.assertEqual([x for x in loop if x.startswith("Delay ")], ["Delay 2", "Delay 2", "Delay 4"])
        self.assertFalse(any(x.startswith("Func_FadeBattlerSprite") for x in loop),
                         "the hit loop must not overlap two fade tasks on the defender")
        fade = "Func_FadeBattlerSprite BATTLE_ANIM_DEFENDER, 0, 1, BATTLE_COLOR_WHITE, 6, 0"
        self.assertEqual([x for x in c if x.startswith("Func_FadeBattlerSprite")], [fade])
        self.assertEqual(c[end + 1], fade)
        self.assertEqual(c[end + 2], "WaitForAnimTasks")
        self.assertEqual(c.count("BeginLoop 2"), 1)
        self.assertEqual(c.count("EndLoop"), 1)


if __name__ == "__main__":
    unittest.main()
