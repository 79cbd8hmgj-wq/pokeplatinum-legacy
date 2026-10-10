#!/usr/bin/env python3
"""ROM-driven melonDS GDB smoke test using the toolkit's managed backend.

Requires installed nds_disassembly_toolkit from its orchestration branch.
Not a substitute for battle interaction/emulator QA.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

from nds_disassembly_toolkit.analysis.orchestration.melonds_backend import MelonDSBackend
from nds_disassembly_toolkit.analysis.runtime.model import RuntimeCpu

rom = Path(sys.argv[1]).resolve()
executable = Path(sys.argv[2]).resolve()
root = Path(sys.argv[3]).resolve()
root.mkdir(parents=True, exist_ok=True)
output = {"rom": str(rom), "emulator": str(executable), "arm9": "not_checked", "arm7": "not_checked"}
backend = MelonDSBackend()
launch = backend.build_launch_spec(executable=executable, rom=rom, cpu=RuntimeCpu.ARM9,
                                    debugger_host="127.0.0.1", debugger_port=3333,
                                    session_root=root, display=os.environ.get("DISPLAY"))
env = {**os.environ, **dict(launch.environment)}
with (root / "emulator.stdout.log").open("w") as log:
    process = subprocess.Popen(launch.argv, cwd=launch.cwd, env=env, stdout=log, stderr=subprocess.STDOUT)
    try:
        for cpu, port in ((RuntimeCpu.ARM9, 3333), (RuntimeCpu.ARM7, 3334)):
            for attempt in range(24):
                if process.poll() is not None:
                    raise RuntimeError(f"melonDS exited early: {process.returncode}")
                try:
                    session = backend.connect_debugger(cpu=cpu, host="127.0.0.1", port=port, timeout=1.0)
                    try:
                        snapshot = session.snapshot()
                        output[cpu.value] = {"status": "connected", "snapshot": str(snapshot)[:800]}
                    finally:
                        session.close()
                    break
                except Exception as exc:
                    if attempt == 23:
                        output[cpu.value] = {"status": "failed", "error": str(exc)}
                    else:
                        time.sleep(0.5)
    except Exception as exc:
        output["fatal"] = str(exc)
        output["traceback"] = traceback.format_exc()[-1500:]
    finally:
        process.terminate()
        try: process.wait(timeout=5)
        except subprocess.TimeoutExpired: process.kill()
(root / "runtime-result.json").write_text(json.dumps(output, indent=2))
print(json.dumps(output, indent=2))
if not all(isinstance(output.get(k), dict) and output[k].get("status") == "connected" for k in ("arm9", "arm7")):
    sys.exit(1)
