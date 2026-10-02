"""Shared helpers for the locked EXP/economy tooling."""
from __future__ import annotations

import glob
import json
import os
import re
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
BASE_COMMIT = "447833b79fa5c0456d60bcbd8ec03ec109d92c23"  # main at EXP/economy implementation start (PR #15 merged)
MANIFEST = "docs/overhaul/implementation/economy/economy_manifest.json"

SRC = {
    "battle_script": "src/battle/battle_script.c",
    "battle_context": "include/battle/battle_context.h",
    "battle_consts": "include/constants/battle.h",
    "prize": "include/data/trainer_class_prize_mul.h",
    "marts": "include/data/mart_items.h",
    "mart_ids": "generated/mart_specialties_id.txt",
    "reminder_script": "res/field/scripts/scripts_pastoria_city_east_house.s",
    "reminder_text": "res/text/pastoria_city_east_house.json",
    "tutors": "res/pokemon/move_tutors.json",
    "fight_area_script": "res/field/scripts/scripts_fight_area_mart.s",
    "vitamin_vendor_script": "res/field/scripts/scripts_veilstone_store_2f.s",
}

# Locked prices (EXP_ECONOMY_SPEC s.5/s.6).
LOCKED_PRICES = {
    "potion": 200, "super_potion": 500, "hyper_potion": 900, "max_potion": 2000, "full_restore": 2500, "revive": 1200,
    "hp_up": 4900, "protein": 4900, "iron": 4900, "calcium": 4900, "zinc": 4900, "carbos": 4900,
}
# Status medicines: derived mechanically = ceil(0.75 * vanilla / 50) * 50 (lowest clean 50-increment >= 75%).
STATUS_MEDICINES = ("antidote", "burn_heal", "ice_heal", "awakening", "parlyz_heal", "full_heal")
RARE_CANDY_PRICES = (5000, 4800)  # preferred 5000; 4800 only with documented side-effect reason
PRIZE_CHANGES = {"TRAINER_CLASS_TUBER_MALE": (1, 3), "TRAINER_CLASS_TUBER_FEMALE": (1, 3),
                 "TRAINER_CLASS_POKE_KID": (2, 4), "TRAINER_CLASS_NINJA_BOY": (2, 4)}
STONE_VENDOR_ID = "MART_SPECIALTIES_ID_VEILSTONE_2F_MID"
RARE_CANDY_VENDOR_ID = "MART_SPECIALTIES_ID_FIGHT_AREA_POSTGAME"
SHARD_FIELDS = ("redCost", "blueCost", "yellowCost", "greenCost")
# Frozen C2 TM economy sources (Game Corner / Frontier / duplicate guard): must be byte-identical to base.
C2_ECONOMY_FILES = ("src/scrcmd_game_corner_prize.c", "src/overlay007/shop_menu.c", "src/unk_020494DC.c", "src/scrcmd.c",
                    "res/field/scripts/scripts_veilstone_city_prize_exchange.s")
# Mart-unlocking shops that exist before the Elite Four (anything not listed is treated as postgame-only).
PRE_E4_VENDOR_IDS = {"MART_SPECIALTIES_ID_" + n for n in (
    "JUBILIFE OREBURGH FLOAROMA ETERNA_MART ETERNA_HOUSE HEARTHOME SOLACEON PASTORIA VEILSTONE_1F_RIGHT VEILSTONE_1F_LEFT "
    "VEILSTONE_2F_UP VEILSTONE_2F_MID VEILSTONE_3F_UP VEILSTONE_3F_DOWN VEILSTONE_B1F CELESTIC SNOWPOINT CANALAVE SUNYSHORE".split())}


def git(*args: str) -> str:
    return subprocess.check_output(("git",) + args, cwd=ROOT, text=True)


def read(rel: str) -> str:
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def base_text(rel: str) -> str:
    return git("show", f"{BASE_COMMIT}:{rel}")


def item_price_files() -> list[str]:
    return sorted(os.path.relpath(p, ROOT) for p in glob.glob(os.path.join(ROOT, "res/items/data/*.json")))


def item_prices(read_fn=read) -> dict[str, int]:
    return {os.path.basename(rel)[:-5]: json.loads(read_fn(rel))["price"] for rel in item_price_files()}


def status_target(vanilla: int) -> int:
    """Lowest clean 50-increment >= 75% of vanilla (antidote has no clean value inside 75-80% and stays 100)."""
    return -(-(vanilla * 3) // 200) * 50


def parse_prize_table(src: str) -> dict[str, int]:
    return {m.group(1): int(m.group(2)) for m in re.finditer(r"\[(TRAINER_CLASS_\w+)\]\s*=\s*(\d+),", src)}


def parse_stock_arrays(src: str) -> dict[str, list[str]]:
    return {m.group(1): re.findall(r"\bITEM_\w+", m.group(2)) for m in re.finditer(r"const u16 (\w+)\[\] = \{(.*?)\};", src, re.S)}


def parse_vendor_map(src: str) -> dict[str, str]:
    body = re.search(r"PokeMartSpecialties\[\] = \{(.*?)\};", src, re.S).group(1)
    return {m.group(1): m.group(2) for m in re.finditer(r"\[(MART_SPECIALTIES_ID_\w+)\]\s*=\s*(\w+)", body)}


def required_stones() -> list[str]:
    """Every item that an overhauled evolution edge consumes (EVO_USE_ITEM*)."""
    man = json.loads(read("docs/overhaul/implementation/evolution_manifest.json"))
    return sorted({e["edge"][1] for e in man["edges"] if "ITEM" in e["edge"][0] and isinstance(e["edge"][1], str)})


def load_live(read_fn=read) -> dict:
    live = {"src": {k: read_fn(v) for k, v in SRC.items()}, "prices": item_prices(read_fn)}
    live["tutors"] = json.loads(live["src"]["tutors"])
    live["c2_files"] = {rel: read_fn(rel) for rel in C2_ECONOMY_FILES}
    live["tm_prices"] = {k: v for k, v in live["prices"].items() if re.fullmatch(r"[th]m\d\d", k)}
    return live


def load_base() -> dict:
    return load_live(base_text)
