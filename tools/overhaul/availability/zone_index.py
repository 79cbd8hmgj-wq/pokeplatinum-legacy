"""Map -> (zone, band, kind) for every encounter file."""
from __future__ import annotations

from zones_data import UNMODIFIED


def zone_index(wild: dict) -> dict[str, dict]:
    idx = {n: {"zone": z, "band": b, "kind": "unmodified", "authored": False} for n, (z, b, _) in UNMODIFIED.items()}
    for n, m in wild["maps"].items():
        idx[n] = {"zone": m["zone"], "band": m["band"], "kind": m["kind"], "authored": True}
    return idx
