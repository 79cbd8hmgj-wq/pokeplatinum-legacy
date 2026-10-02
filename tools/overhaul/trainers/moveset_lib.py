"""Deterministic move-proposal helpers (legal, thematic, level-appropriate) built on current main data."""
from __future__ import annotations

import hashlib

from trainer_lib import bst, legal_moves, move_data, species_data

BAD_EFFECTS = {
    "BATTLE_EFFECT_RECHARGE_AFTER", "BATTLE_EFFECT_CHARGE_TURN_DEF_UP", "BATTLE_EFFECT_CHARGE_TURN_HIGH_CRIT_FLINCH",
    "BATTLE_EFFECT_SKIP_CHARGE_TURN_IN_SUN", "BATTLE_EFFECT_FLY", "BATTLE_EFFECT_DIG", "BATTLE_EFFECT_DIVE",
    "BATTLE_EFFECT_BOUNCE", "BATTLE_EFFECT_SHADOW_FORCE", "BATTLE_EFFECT_HIT_IN_3_TURNS", "BATTLE_EFFECT_CRASH_ON_MISS",
    "BATTLE_EFFECT_FAIL_IF_NOT_USED_ALL_OTHER_MOVES", "BATTLE_EFFECT_EAT_BERRY", "BATTLE_EFFECT_STRUGGLE",
    "BATTLE_EFFECT_INCREASE_PRIZE_MONEY", "BATTLE_EFFECT_LEAVE_WITH_1_HP", "BATTLE_EFFECT_CONTINUE_AND_CONFUSE_SELF",
    "BATTLE_EFFECT_DAMAGE_WHILE_ASLEEP", "BATTLE_EFFECT_RECOVER_DAMAGE_SLEEP", "BATTLE_EFFECT_UPROAR",
    "BATTLE_EFFECT_CHATTER", "BATTLE_EFFECT_SECRET_POWER", "BATTLE_EFFECT_STEAL_HELD_ITEM", "BATTLE_EFFECT_REMOVE_HELD_ITEM",
    "BATTLE_EFFECT_DOUBLE_POWER_IF_MOVING_SECOND", "BATTLE_EFFECT_HIT_LAST_WHIFF_IF_HIT", "BATTLE_EFFECT_USER_SP_ATK_DOWN_2",
    "BATTLE_EFFECT_REMOVE_PROTECT", "BATTLE_EFFECT_DECREASE_POWER_WITH_LESS_USER_HP",
}
BAD_MOVES = {"MOVE_EXPLOSION", "MOVE_SELF_DESTRUCT", "MOVE_FOCUS_PUNCH", "MOVE_FLAIL", "MOVE_REVERSAL", "MOVE_SPIT_UP",
             "MOVE_NATURE_POWER", "MOVE_FURY_CUTTER", "MOVE_ROLLOUT", "MOVE_ICE_BALL", "MOVE_FUTURE_SIGHT", "MOVE_DOOM_DESIRE",
             "MOVE_SNORE", "MOVE_LAST_RESORT", "MOVE_FLING", "MOVE_TRUMP_CARD", "MOVE_PUNISHMENT", "MOVE_WRING_OUT",
             "MOVE_CRUSH_GRIP", "MOVE_STORED_POWER", "MOVE_PAYBACK", "MOVE_BRINE", "MOVE_ASSURANCE", "MOVE_ACROBATICS"}
CUSTOM_MOVES = {  # created moves (IDs 468-489): trainers get them only when the species is a manifest recipient
    "MOVE_STATIC_STRIKE", "MOVE_FROST_RUSH", "MOVE_AURA_BURST", "MOVE_DRAGON_SWIPE", "MOVE_METAL_RAY", "MOVE_RIPTIDE_RUSH",
    "MOVE_SOUL_SIPHON", "MOVE_CURSED_STITCH", "MOVE_STAR_JAB",
}


def _h(*a) -> int:
    return int(hashlib.sha256("|".join(map(str, a)).encode()).hexdigest()[:8], 16)


def is_attack(m: str) -> bool:
    d = move_data(m)
    return bool(d) and d["power"] >= 1 and d["class"] in ("CLASS_PHYSICAL", "CLASS_SPECIAL")


def usable(m: str) -> bool:
    d = move_data(m)
    return bool(d) and m not in BAD_MOVES and m not in CUSTOM_MOVES and d["effect"]["type"] not in BAD_EFFECTS


def score(species: str, m: str) -> float:
    d = move_data(m)
    sd = species_data(species)
    st = sd["base_stats"]
    prefer = "CLASS_PHYSICAL" if st["attack"] >= st["special_attack"] else "CLASS_SPECIAL"
    s = d["power"] * (min(d["accuracy"], 100) or 100) / 100
    if d["type"] in sd["types"]:
        s *= 1.5
    if d["class"] != prefer:
        s *= 0.5
    if d["effect"]["type"] in ("BATTLE_EFFECT_HIT_TWICE",):
        s *= 1.6
    return s


def propose(species: str, level: int, seed: str = "", utility: tuple[str, ...] = (), n: int = 4) -> list[str]:
    """STAB x2 (distinct types where possible), one coverage attack, then listed utility moves."""
    leg = [m for m in legal_moves(species, level) if usable(m)]
    atk = sorted((m for m in leg if is_attack(m) and move_data(m)["accuracy"] >= 75), key=lambda m: (-score(species, m), m))
    types = species_data(species)["types"]
    out: list[str] = []
    used_types: set[str] = set()
    for m in atk:
        t = move_data(m)["type"]
        if t in types and t not in used_types:
            out.append(m)
            used_types.add(t)
        if len(out) >= 2:
            break
    for m in atk:
        t = move_data(m)["type"]
        if m not in out and t not in types and t not in used_types and move_data(m)["power"] >= 60:
            out.append(m)
            used_types.add(t)
            break
    for m in atk:
        if len(out) >= n - len(utility):
            break
        if m not in out:
            out.append(m)
    for u in utility:
        if u in leg and u not in out and len(out) < n:
            out.append(u)
    return out[:n]
