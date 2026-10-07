#!/usr/bin/env python3
"""Field sprite alignment: HGSS NSBTX sprite sheet -> canonical Platinum npc/player sprite target.

Identity key = sprite base name (HGSS NSBTX texture base == Platinum meson `basename`).
Targets: `fs_<category>_<stem>` for Platinum files (res/graphics/field_sprites/<category>/<stem>.png), else `fs_hgss_<base>`.
"""
from __future__ import annotations

import re

from common import *  # noqa: F401,F403

MESON = ROOT / "res/graphics/field_sprites/meson.build"


def main() -> int:
    txt = MESON.read_text()
    plat: dict[str, list[str]] = {}
    for f, b in re.findall(r"\{\s*'file':\s*'([^']+)',\s*'basename':\s*'([^']+)'", txt):
        plat.setdefault(b, []).append(f)
    cat = jload(EXT_DIR / "hgss_field_sprites" / "CATALOG.json")
    out = {}
    for a in cat["assets"]:
        base = a["variant"] or (a["source_metadata"]["base_names"] or ["?"])[0]
        files = [f for f in plat.get(base, []) if f.split("/")[0] in ("npc", "player")]
        pf = sorted(files)[0] if files else None
        if pf:
            c, stem = pf.split("/")[0], pf.split("/")[1].removesuffix(".png")
            target, method = f"fs_{c}_{stem}", "basename_match" + ("_multi" if len(files) > 1 else "")
        else:
            target, method = f"fs_hgss_{base}", "none"
        out[a["source_path"]] = {"base": base, "platinum_file": pf, "target": target, "method": method}
    doc = {"schema_version": 1, "inputs": {"platinum_meson_sha256": file_sha256(MESON),
                                            "catalog_sha256": file_sha256(EXT_DIR / "hgss_field_sprites" / "CATALOG.json")}, "hgss": out}
    jdump(SEL / "alignment" / "field_sprites.json", doc)
    import collections
    print(len(out), dict(collections.Counter(v["method"] for v in out.values())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
