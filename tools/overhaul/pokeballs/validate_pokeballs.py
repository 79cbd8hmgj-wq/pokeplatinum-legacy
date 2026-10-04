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

    retired = set(shop.get("retired_from_progression_shops", []))
    for vendor, balls in arrays.items():
        leaked = sorted(retired.intersection(balls))
        if leaked:
            P.append(f"{vendor}: retired progression balls present {leaked}")

    repurposed = shop.get("repurposed_slots", {})
    if repurposed.get("ITEM_NEST_BALL") != "Level Ball":
        P.append("ITEM_NEST_BALL must remain the Level Ball backing slot")
    if repurposed.get("ITEM_DIVE_BALL") != "Lure Ball":
        P.append("ITEM_DIVE_BALL must remain the Lure Ball backing slot")

    if shop["common"].get("ITEM_GREAT_BALL") != 1 or shop["common"].get("ITEM_HEAL_BALL") != 1:
        P.append("Great Ball and Heal Ball must be common-stock at zero badges")
    if "ITEM_QUICK_BALL" not in arrays.get("JubilifeMartSpecialties", []):
        P.append("Quick Ball must be available in Jubilife before Badge 1")
    if "ITEM_TIMER_BALL" not in arrays.get("OreburghMartSpecialties", []):
        P.append("Timer Ball must be available in Oreburgh by Badge 1")
    eterna = arrays.get("EternaMartSpecialties", [])
    if "ITEM_NEST_BALL" not in eterna or "ITEM_DIVE_BALL" not in eterna:
        P.append("Level/Lure backing slots must be available by Eterna")
    if "ITEM_REPEAT_BALL" not in arrays.get("SolaceonMartSpecialties", []):
        P.append("Repeat Ball must be available by Solaceon")
    if shop["common"].get("ITEM_ULTRA_BALL", 0) < 4:
        P.append("Ultra Ball common-stock gate is too early")
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
