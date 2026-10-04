#!/usr/bin/env python3
"""G7.2B message-box frame refresh (plain frame family).

The player-selectable text frames 1-5 (``message_box_00`` .. ``message_box_04``)
are the plain white-field frames; frame 1 is the default and is therefore the
dialog and battle text box most players see.  Retail drew them with a muddy
beige/olive gradient edge and a green-black outline.  G7 keeps the exact pixel
indices, white text field and 1 px white halo, and retunes only the outline and
the three gradient entries:

  * outline (entry 14): deep navy, shared by all five frames
  * gradient (entries 11-13): clean steel/navy for frames 1-2, richer blue,
    crimson and emerald for frames 3-5 (same hue families as retail)

Entry 15 (field fill / halo) is intentionally untouched: battle and field text
windows fill their interior with the *font* palette's white, so any change to
the frame's own fill would show as a seam.  Decorative frames 6-20 are
explicit player choices and are not modified.

Palette-only: pixel indices, dimensions and the .order/meson contracts do not
change.  Idempotent.
"""

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
WINDOW_DIR = ROOT / "res" / "graphics" / "windows"

OUTLINE = (12, 20, 40)

# frame -> {palette entry: rgb}.  Gradient entries are listed per frame because
# retail ordered them dark->light as 11,12,13 for frame 1 and 13,12,11 for the
# others.
FRAMES = {
    "message_box_00.png": {11: (36, 64, 112), 12: (104, 142, 190), 13: (204, 220, 238)},
    "message_box_01.png": {13: (56, 70, 92), 12: (124, 140, 162), 11: (210, 220, 232)},
    "message_box_02.png": {13: (42, 86, 196), 12: (110, 150, 228), 11: (204, 220, 250)},
    "message_box_03.png": {13: (214, 52, 60), 12: (246, 120, 116), 11: (255, 206, 204)},
    "message_box_04.png": {13: (46, 160, 70), 12: (130, 206, 110), 11: (212, 240, 196)},
}


def apply(filename, gradient):
    path = WINDOW_DIR / filename
    image = Image.open(path)
    palette = list(image.getpalette())
    for index, rgb in {**gradient, 14: OUTLINE}.items():
        palette[index * 3:index * 3 + 3] = rgb
    image.putpalette(palette)
    image.save(path)


def main():
    for filename, gradient in FRAMES.items():
        apply(filename, gradient)


if __name__ == "__main__":
    main()
