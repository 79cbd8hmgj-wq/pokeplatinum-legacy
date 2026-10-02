"""Reference model of the locked Poké Ball modifiers (units of 1/10; mirrors BattleScript_CalcCatchShakes)."""
from __future__ import annotations

BASIC = {"ultra": 20, "great": 15, "poke": 10, "safari": 15}


def ball_mod(ball: str, *, turns=0, target_types=(), terrain="land", time="day", caught=False,
             user_level=1, target_level=1) -> int:
    if ball in BASIC:
        return BASIC[ball]
    if ball == "net":
        return 35 if {"water", "bug"} & set(target_types) else 10
    if ball == "dive":
        return 40 if terrain == "water" else 10
    if ball == "nest":
        if user_level >= 4 * target_level:
            return 50
        if user_level >= 2 * target_level:
            return 35
        if user_level >= target_level:
            return 20
        return 10
    if ball == "repeat":
        return 35 if caught else 10
    if ball == "timer":
        return min(40, 10 + 3 * turns)
    if ball == "dusk":
        return 30 if time in ("night", "late_night") or terrain == "cave" else 10
    if ball == "quick":
        return 50 if turns < 1 else 10
    if ball == "heal":
        return 15
    return 10  # luxury, premier, master (guarantee handled elsewhere)


def catch_rate(species_rate: int, mod: int, max_hp: int, cur_hp: int, status: str = "") -> int:
    rate = (species_rate * mod // 10) * (max_hp * 3 - cur_hp * 2) // (max_hp * 3)
    if status in ("sleep", "freeze"):
        rate *= 2
    elif status in ("poison", "burn", "paralysis", "toxic"):
        rate = rate * 15 // 10
    return rate
