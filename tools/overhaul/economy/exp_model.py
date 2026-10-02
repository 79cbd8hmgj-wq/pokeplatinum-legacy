"""Source-level model of the locked conserved team-wide EXP allocation.

Mirrors BtlCmd_CalcExpGain / BattleScript_GetExpTask in src/battle/battle_script.c:
  raw_pool    = floor(base_exp_reward * defeated_level / 7)
  battle_pool = floor(raw_pool * 60 / 100)  -> split among the battle group (participants U Exp. Share holders)
  team_pool   = raw_pool - battle_pool      -> split among all eligible party members
Remainders go to the lowest party slots first, so pre-modifier allocations sum to raw_pool.
"""
from __future__ import annotations

from dataclasses import dataclass

BATTLE_POOL_PERCENT = 60
MAX_LEVEL = 100


@dataclass(frozen=True)
class Member:
    slot: int
    level: int = 50
    hp: int = 1
    egg: bool = False
    valid: bool = True
    exp_share: bool = False
    participant: bool = False
    lucky_egg: bool = False
    traded: bool = False          # not the original trainer
    foreign: bool = False         # traded and language differs from the game's


def eligible(m: Member) -> bool:
    return m.valid and not m.egg and m.hp > 0 and m.level < MAX_LEVEL


def raw_pool(base_exp_reward: int, defeated_level: int) -> int:
    return base_exp_reward * defeated_level // 7


def allocate(raw: int, party: list[Member]) -> dict[int, int]:
    """Pre-individual-modifier allocation {slot: exp} for eligible members."""
    elig = [m for m in party if eligible(m)]
    group = [m for m in elig if m.participant or m.exp_share]  # union, each member counted once
    battle_pool = raw * BATTLE_POOL_PERCENT // 100
    team_pool = raw - battle_pool
    out = {m.slot: 0 for m in elig}
    if group:
        q, r = divmod(battle_pool, len(group))
        for i, m in enumerate(group):
            out[m.slot] += q + (1 if i < r else 0)
    if elig:
        q, r = divmod(team_pool, len(elig))
        for i, m in enumerate(elig):
            out[m.slot] += q + (1 if i < r else 0)
    for m in group:
        if out[m.slot] == 0:
            out[m.slot] = 1  # legacy minimum-1 for battle-group members (only when the total would be 0)
    return out


def final_exp(base: int, m: Member, trainer: bool) -> int:
    """Individual modifiers in engine order: Lucky Egg, trainer, traded."""
    exp = base
    if m.lucky_egg:
        exp = exp * 150 // 100
    if trainer:
        exp = exp * 150 // 100
    if m.traded:
        exp = exp * (170 if m.foreign else 150) // 100
    return exp


def ev_recipients(party: list[Member]) -> list[int]:
    """Only actual participants (that are eligible for EXP) earn EVs."""
    return [m.slot for m in party if eligible(m) and m.participant]


def payout(base_exp_reward: int, defeated_level: int, party: list[Member], trainer: bool) -> dict[int, int]:
    alloc = allocate(raw_pool(base_exp_reward, defeated_level), party)
    by = {m.slot: m for m in party}
    return {s: final_exp(v, by[s], trainer) for s, v in alloc.items()}
