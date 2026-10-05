# Ranger Pokémon Render Compatibility Audit

Target comparison cell: **80x80**

Classification uses the nontransparent pixel bounding box, not the raw OAM canvas.
Palette index 0 is treated as transparent.

## Summary

| Status | Cells | Share |
|---|---:|---:|
| fits_small | 26703 | 74.58% |
| fits | 8550 | 23.88% |
| geometry_close | 335 | 0.94% |
| oversize | 44 | 0.12% |
| blank | 174 | 0.49% |

## Species with oversize cells

| Species | Oversize cells | Total cells |
|---:|---:|---:|
| 484 | 32 | 203 |
| 483 | 12 | 174 |

## Interpretation

- fits_small: occupied art is at most 40x40.
- fits: occupied art fits inside 80x80.
- geometry_close: occupied art exceeds 80x80 but is no larger than 96x96.
- oversize: occupied art exceeds the 96x96 review envelope.
- blank: no nontransparent pixels were rendered.

These are census labels, not automatic import decisions.
