"""Validate Poké Ball source against the locked rebalance spec and the manifests."""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MAN = "docs/overhaul/implementation/pokeballs/pokeball_manifest.json"
SHOP = "docs/overhaul/implementation/pokeballs/pokeball_shop_manifest.json"


def rd(p):
    with open(os.path.join(ROOT, p)) as f:
        return f.read()


def case_body(src, item):
    m = re.search(r"case %s:(.*?)(?:\n        case ITEM_|\n        \}\n    \} else)" % item, src, re.S)
    return m.group(1) if m else ""


def validate(bs: str, marts: str, prices: dict, man: dict, shop: dict) -> list[str]:
    P = []
    fn = bs[bs.index("static int BattleScript_CalcCatchShakes(BattleSystem *battleSys, BattleContext *battleCtx)\n{"):]
    fn = fn[:fn.index("\n}\n")]
    for ball, e in man["balls"].items():
        body = case_body(fn, e["item"])
        if not body:
            P.append(f"{e['item']}: case missing")
            continue
        for needle in e["source_contains"]:
            if needle not in body:
                P.append(f"{e['item']}: expected source `{needle}` missing")
    if "u32 ballMod = 10;" not in fn:
        P.append("default ballMod changed")
    for line in ("20, // ITEM_ULTRA_BALL", "15, // ITEM_GREAT_BALL", "10, // ITEM_POKE_BALL", "15, // ITEM_SAFARI_BALL"):
        if line not in bs:
            P.append(f"basic ball table changed: {line}")
    for needle in ("catchRate = catchRate * 15 / 10;", "catchRate *= 2;", "maxHP * 3 - battleCtx->battleMons[battleCtx->defender].curHP * 2",
                   "if (battleCtx->msgItemTemp == ITEM_MASTER_BALL) {\n            shakes = BALL_3_SHAKES_SUCCESS;"):
        if needle not in fn:
            P.append(f"base catch formula changed: {needle[:40]}")
    for ball, price in man["prices"].items():
        if prices.get(ball) != price:
            P.append(f"price {ball}: {prices.get(ball)} != {price}")
    # shops
    for m in re.finditer(r"\{ (ITEM_\w+_BALL), (0x\d) \}", marts):
        if shop["common"].get(m.group(1)) != int(m.group(2), 16):
            P.append(f"common mart {m.group(1)} gate {m.group(2)} != manifest {shop['common'].get(m.group(1))}")
    for k, v in shop["common"].items():
        if f"{{ {k}, 0x{v} }}" not in marts:
            P.append(f"common mart missing {k} gate {v}")
    arrays = {n: re.findall(r"\bITEM_\w+_BALL", b) for n, b in re.findall(r"const u16 (\w+Specialties)\[\] = \{(.*?)\};", marts, re.S)}
    for vendor, balls in shop["vendors"].items():
        if arrays.get(vendor) != balls:
            P.append(f"{vendor}: balls {arrays.get(vendor)} != {balls}")
    return P


def load():
    prices = {b: json.load(open(os.path.join(ROOT, "res/items/data/%s.json" % b)))["price"]
              for b in json.loads(rd(MAN))["prices"]}
    return rd("src/battle/battle_script.c"), rd("include/data/mart_items.h"), prices, json.loads(rd(MAN)), json.loads(rd(SHOP))


def main():
    P = validate(*load())
    print(f"pokeball validation: {len(P)} failure(s)")
    for p in P:
        print("FAIL:", p)
    return 1 if P else 0


if __name__ == "__main__":
    sys.exit(main())
