"""Static reading of the *native* move scripts (``res/moves/<slug>/anim.s``): which Platinum particle archive and emitters a move creates,
with which callbacks and at what script frame (lower bound), what else the script already does (donor sprites, Opal cues, fades, shakes).

This resolves the DAU2 blocker "which emitters does a move create": for Platinum moves the script says so.  Frame numbers are LOWER BOUNDS
(sum of ``Delay`` before the command; ``WaitForAnimTasks`` / ``Func_*`` task durations are unknown and counted as 0), exactly like
``opal_cue_trace.py``; they are for ordering and budget reasoning, never a performance claim.
"""
from __future__ import annotations

import re
from pathlib import Path

CB_ROLE = {"EMITTER_CB_SET_POS_TO_ATTACKER": "attacker", "EMITTER_CB_SET_POS_TO_DEFENDER": "defender"}
OPAL_CUES = ("OpalSheetBegin", "OpalFx", "OpalChargeAura", "OpalProjectile", "OpalImpactBurst", "OpalResidual", "OpalCam", "OpalDim", "OpalLight",
             "OpalWeatherAccent", "OpalReact")


def read_script(path: Path) -> dict:
    """Parse one anim.s -> {spa, emitters[{index, callback, role, frame}], delays, flags...}."""
    t = 0                                       # cumulative Delay frames (lower bound)
    task_lb = 0                                 # duration of tasks whose length is an explicit argument (Func_BlinkAttacker n)
    spa, emitters, events, donor, opal, branches = None, [], [], [], [], 0
    sounds, shakes, fades, moves, loops = 0, 0, 0, 0, 0
    comments = []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if line.startswith("//"):
            comments.append(line[2:].strip())
            continue
        if not line or line.endswith(":") or line.startswith("#"):
            continue
        m = re.match(r"(\w+)\s*(.*)", line)
        if not m:
            continue
        op, args = m.group(1), [a.strip() for a in m.group(2).split("//")[0].split(",")]
        if op == "Delay":
            try:
                t += int(args[0])
            except ValueError:
                pass
        elif op == "LoadParticleResource":
            spa = args[1].replace("_spa", "") if len(args) > 1 else None
        elif op in ("CreateEmitter", "CreateEmitterEx"):
            # CreateEmitter res, index, callback  |  CreateEmitterEx res, extra_id, index, callback
            ex = op == "CreateEmitterEx"
            cb = args[3] if ex and len(args) > 3 else (args[2] if not ex and len(args) > 2 else "")
            e = {"index": int(args[2] if ex else args[1]), "callback": cb, "role": CB_ROLE.get(cb, "other"), "frame_lb": t}
            if ex:
                e["extra_id"] = int(args[1])
            emitters.append(e)
        elif op.startswith("Opal"):
            opal.append(op)
        elif op in ("InitSpriteManager", "AddSpriteWithFunc", "LoadCharResObj"):
            if op == "LoadCharResObj":
                donor.append(args[1])
        elif op.startswith("Play") and "Sound" in op:
            sounds += 1
        elif op == "Func_BlinkAttacker":
            try:
                task_lb = max(task_lb, t + int(args[0]))
            except ValueError:
                pass
        elif op == "Func_Shake":
            shakes += 1
        elif op in ("Func_FadeBattlerSprite", "Func_FadeBg"):
            fades += 1
        elif op.startswith("Func_MoveBattler"):
            moves += 1
        elif op in ("BeginLoop",):
            loops += 1
        elif op.startswith("Jump") or op == "Call":
            branches += 1
    return {"spa": spa, "emitters": emitters, "delay_total_lb": max(t, task_lb), "opal_cues": sorted(set(opal)), "sprite_resources": donor, "comments": comments,
            "sounds": sounds, "shakes": shakes, "fades": fades, "battler_moves": moves, "loops": loops, "branches": branches}


def analyse(root: Path, slug: str, spl_headers: dict | None = None) -> dict:
    """spl_headers: {emitter_index: {'emitter_life','particle_life',...}} for the script's archive (optional) -> duration lower bound."""
    p = root / "res/moves" / slug / "anim.s"
    s = read_script(p)
    end = s["delay_total_lb"]
    first_def = min((e["frame_lb"] for e in s["emitters"] if e["role"] == "defender"), default=None)
    for e in s["emitters"]:
        h = (spl_headers or {}).get(e["index"])
        if h:
            life = (h["emitter_life"] or 0) + h["start_delay"] + h["particle_life"]
            e["emitter_life"], e["particle_life"], e["start_delay"] = h["emitter_life"], h["particle_life"], h["start_delay"]
            e["ends_frame_lb"] = e["frame_lb"] + life
            end = max(end, e["ends_frame_lb"])
    s["native_duration_lb_frames"] = end
    s["first_defender_emitter_frame_lb"] = first_def
    s["script"] = f"res/moves/{slug}/anim.s"
    return s
