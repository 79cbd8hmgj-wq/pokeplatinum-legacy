#!/usr/bin/env python3
"""Runtime validation harness for Pass G4 environment work.

This is intentionally a thin game-specific consumer of NDS Disassembly Toolkit.
It attaches to an already-running melonDS ARM9 GDB stub and validates the
runtime paths that source/build-only CI cannot prove.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from nds_disassembly_toolkit.analysis.runtime import MelonDSSession, RuntimeCpu


@dataclass(frozen=True)
class Scenario:
    expected_light_id: int
    warp_request: int | None = None
    before_light_symbols: tuple[str, ...] = ()
    after_light_symbols: tuple[str, ...] = ("AreaLightManager_UpdateActiveTemplate",)
    require_special_fog: bool = False


SCENARIOS: dict[str, Scenario] = {
    "eterna": Scenario(
        expected_light_id=10,
        warp_request=1,
        before_light_symbols=("ForestAmbienceRenderer_New",),
        after_light_symbols=(
            "AreaLightManager_UpdateActiveTemplate",
            "ForestAmbienceRenderer_Task",
        ),
    ),
    "snow": Scenario(expected_light_id=11, warp_request=2),
    "distortion": Scenario(expected_light_id=9, require_special_fog=True),
    "spear": Scenario(expected_light_id=12, warp_request=3, require_special_fog=True),
    "lakes": Scenario(expected_light_id=13, warp_request=4),
    "turnback": Scenario(expected_light_id=14, warp_request=5),
    "galactic": Scenario(expected_light_id=6, warp_request=6),
    "coronet-control": Scenario(expected_light_id=7, warp_request=7, require_special_fog=True),
}

REQUIRED_SYMBOLS = {
    "AreaLightManager_New",
    "AreaLightManager_UpdateActiveTemplate",
    "FieldMap_ApplySpecialAreaFog",
    "FogManager_ApplyParameters",
    "ForestAmbienceRenderer_New",
    "ForestAmbienceRenderer_Task",
    "gG4RuntimeQAControl",
}


def _parse_int(value: str) -> int:
    return int(value, 0)


def _load_overrides(values: Iterable[str]) -> dict[str, int]:
    result: dict[str, int] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"invalid --address override: {value!r}")
        name, raw = value.split("=", 1)
        name = name.strip()
        if not name:
            raise ValueError(f"invalid --address override: {value!r}")
        result[name] = _parse_int(raw.strip())
    return result


def _symbol_candidates(text: str, symbol: str) -> list[int]:
    candidates: list[int] = []
    escaped = re.escape(symbol)
    for line in text.splitlines():
        if not re.search(rf"(?<![A-Za-z0-9_]){escaped}(?![A-Za-z0-9_])", line):
            continue
        for token in re.findall(r"(?:0x)?[0-9A-Fa-f]{8}", line):
            value = int(token, 16)
            if 0x02000000 <= value <= 0x02FFFFFF:
                candidates.append(value)
    return candidates


def _resolve_symbols(symbol_file: Path, overrides: dict[str, int]) -> dict[str, int]:
    resolved = dict(overrides)
    text = symbol_file.read_text(encoding="utf-8", errors="replace")
    for symbol in sorted(REQUIRED_SYMBOLS):
        if symbol in resolved:
            continue
        candidates = _symbol_candidates(text, symbol)
        unique = sorted(set(candidates))
        if len(unique) == 1:
            resolved[symbol] = unique[0]
        elif len(unique) > 1:
            raise RuntimeError(
                f"ambiguous symbol {symbol}: "
                + ", ".join(f"0x{value:08x}" for value in unique)
                + "; pass --address SYMBOL=ADDRESS"
            )
    return resolved


def _scenario_symbol_names(scenario: Scenario) -> tuple[str, ...]:
    names = [
        *scenario.before_light_symbols,
        "AreaLightManager_New",
        *(
            ("FieldMap_ApplySpecialAreaFog", "FogManager_ApplyParameters")
            if scenario.require_special_fog
            else ()
        ),
        *scenario.after_light_symbols,
    ]
    return tuple(dict.fromkeys(names))


def _need(symbols: dict[str, int], name: str) -> int:
    if name not in symbols:
        raise RuntimeError(
            f"could not resolve {name}; provide a debug symbol/map file or "
            f"--address {name}=0x..."
        )
    return symbols[name]


def _request_debug_warp(
    session: MelonDSSession,
    symbols: dict[str, int],
    scenario: Scenario,
) -> dict[str, object]:
    if scenario.warp_request is None:
        raise RuntimeError(
            "this scenario requires a prepared checkpoint; no debug autowarp is defined"
        )

    address = _need(symbols, "gG4RuntimeQAControl")
    payload = (
        scenario.warp_request.to_bytes(4, "little")
        + (0).to_bytes(4, "little")
        + (0).to_bytes(4, "little")
    )
    session.write_memory(address, payload)
    observed = session.read_memory(address, len(payload))
    if observed != payload:
        raise RuntimeError("debug warp control verification failed after runtime write")

    return {
        "address": f"0x{address:08x}",
        "request": scenario.warp_request,
        "status": 0,
        "loaded_map_header": 0,
    }


def _read_debug_warp_control(
    session: MelonDSSession,
    symbols: dict[str, int],
) -> dict[str, object]:
    address = _need(symbols, "gG4RuntimeQAControl")
    raw = session.read_memory(address, 12)
    request = int.from_bytes(raw[0:4], "little")
    status = int.from_bytes(raw[4:8], "little")
    loaded_map_header = int.from_bytes(raw[8:12], "little")
    return {
        "address": f"0x{address:08x}",
        "request": request,
        "status": status,
        "loaded_map_header": loaded_map_header,
    }


def _hit(session: MelonDSSession, symbols: dict[str, int], name: str) -> dict[str, object]:
    address = _need(symbols, name)
    snapshot = session.run_until_breakpoint(address)
    return {
        "symbol": name,
        "address": f"0x{address:08x}",
        "pc": f"0x{snapshot.pc:08x}",
        "r0": f"0x{(snapshot.registers.value('r0') or 0):08x}",
        "r1": f"0x{(snapshot.registers.value('r1') or 0):08x}",
        "stop": snapshot.stop.kind.value,
    }


def run(args: argparse.Namespace) -> int:
    scenario = SCENARIOS[args.scenario]
    overrides = _load_overrides(args.address)
    symbols = _resolve_symbols(args.symbols, overrides)
    results: list[dict[str, object]] = []
    warp_control: dict[str, object] | None = None

    if args.validate_symbols_only:
        needed = _scenario_symbol_names(scenario)
        missing = [name for name in needed if name not in symbols]
        if missing:
            raise RuntimeError(
                f"{args.scenario}: unresolved runtime symbols: " + ", ".join(missing)
            )
        report = {
            "scenario": args.scenario,
            "symbols": {
                name: f"0x{symbols[name]:08x}"
                for name in needed
            },
            "status": "PASS",
        }
        rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        print(rendered, end="")
        return 0

    with MelonDSSession.connect(
        cpu=RuntimeCpu.ARM9,
        host=args.host,
        port=args.port,
        timeout=args.timeout,
    ) as session:
        if args.request_warp:
            warp_control = _request_debug_warp(session, symbols, scenario)

        for symbol in scenario.before_light_symbols:
            results.append(_hit(session, symbols, symbol))

        light_hit = _hit(session, symbols, "AreaLightManager_New")
        archive_id = int(str(light_hit["r1"]), 16) & 0xFF
        light_hit["archive_id"] = archive_id
        light_hit["expected_archive_id"] = scenario.expected_light_id
        light_hit["pass"] = archive_id == scenario.expected_light_id
        results.append(light_hit)
        if archive_id != scenario.expected_light_id:
            raise RuntimeError(
                f"{args.scenario}: AreaLightManager_New received lighting ID "
                f"{archive_id}, expected {scenario.expected_light_id}"
            )

        if scenario.require_special_fog:
            results.append(_hit(session, symbols, "FieldMap_ApplySpecialAreaFog"))
            results.append(_hit(session, symbols, "FogManager_ApplyParameters"))

        for symbol in scenario.after_light_symbols:
            results.append(_hit(session, symbols, symbol))

        if args.request_warp:
            warp_control = _read_debug_warp_control(session, symbols)
            if warp_control["status"] != 2:
                raise RuntimeError(
                    f"{args.scenario}: debug warp did not reach LOADED status; "
                    f"control={warp_control}"
                )

    report = {
        "scenario": args.scenario,
        "expected_light_id": scenario.expected_light_id,
        "host": args.host,
        "port": args.port,
        "checks": results,
        "warp_control": warp_control,
        "status": "PASS",
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("scenario", choices=sorted(SCENARIOS))
    p.add_argument(
        "--symbols",
        type=Path,
        default=Path("build/runtime_symbols.map"),
        help="nm-style debug symbol map used to resolve runtime addresses",
    )
    p.add_argument(
        "--address",
        action="append",
        default=[],
        metavar="SYMBOL=ADDRESS",
        help="override one unresolved/ambiguous symbol address",
    )
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=3333)
    p.add_argument("--timeout", type=float, default=30.0)
    p.add_argument(
        "--request-warp",
        action="store_true",
        help="use the GDB_DEBUGGING-only control block to warp to this scenario before probing",
    )
    p.add_argument(
        "--validate-symbols-only",
        action="store_true",
        help="resolve all symbols required by the selected scenario without connecting to an emulator",
    )
    p.add_argument("--output", type=Path)
    return p


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
