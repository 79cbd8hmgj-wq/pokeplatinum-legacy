"""Tiny control-flow model of pokeplatinum field-script assembly (`res/field/scripts/*.s`).

Only what the D5 validator needs: labels, their statement lists, and call/goto edges.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

LABEL_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):\s*$")
BRANCH_RE = re.compile(r"^(GoTo|GoToIf\w+|Call|CallIf\w+)\s+(.*)$")


@dataclass
class Stmt:
    label: str
    index: int
    text: str

    @property
    def op(self) -> str:
        return self.text.split(None, 1)[0] if self.text else ""

    @property
    def args(self) -> list[str]:
        parts = self.text.split(None, 1)
        return [a.strip() for a in parts[1].split(",")] if len(parts) > 1 else []


@dataclass
class Script:
    path: Path
    labels: dict[str, list[Stmt]] = field(default_factory=dict)
    order: list[str] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> "Script":
        s = cls(path)
        cur = None
        for raw in path.read_text().splitlines():
            line = raw.split("//", 1)[0].strip()
            if not line:
                continue
            m = LABEL_RE.match(line)
            if m:
                cur = m.group(1)
                s.labels[cur] = []
                s.order.append(cur)
                continue
            if cur is None or line.startswith((".", "#")):
                continue
            s.labels[cur].append(Stmt(cur, len(s.labels[cur]), line))
        return s

    # -- control flow -----------------------------------------------------------------------------
    def next_label(self, label: str) -> str | None:
        i = self.order.index(label)
        return self.order[i + 1] if i + 1 < len(self.order) else None

    def edges(self, st: Stmt, include_calls: bool = True) -> tuple[list[str], bool]:
        """(branch target labels, falls_through)."""
        m = BRANCH_RE.match(st.text)
        targets: list[str] = []
        falls = True
        if m:
            op = m.group(1)
            tgt = m.group(2).split(",")[-1].strip()
            if tgt in self.labels:
                if op.startswith("Call") and not include_calls:
                    pass
                else:
                    targets.append(tgt)
            if op == "GoTo":
                falls = False
        elif st.op in ("End", "Return", "EndMovement"):
            falls = False
        return targets, falls

    def reach(self, start: str, start_index: int = 0, skip: set[tuple[str, int]] | None = None) -> list[Stmt]:
        """All statements reachable from labels[start][start_index] (follows goto/call edges and fall-through)."""
        seen: set[tuple[str, int]] = set()
        out: list[Stmt] = []
        stack = [(start, start_index)]
        skip = skip or set()
        while stack:
            lab, idx = stack.pop()
            while True:
                if (lab, idx) in seen or (lab, idx) in skip:
                    break
                body = self.labels.get(lab)
                if body is None:
                    break
                if idx >= len(body):
                    nxt = self.next_label(lab)
                    if nxt is None:
                        break
                    lab, idx = nxt, 0
                    continue
                seen.add((lab, idx))
                st = body[idx]
                out.append(st)
                targets, falls = self.edges(st)
                for t in targets:
                    stack.append((t, 0))
                if not falls:
                    break
                idx += 1
        return out

    def find(self, text_prefix: str, within: list[Stmt] | None = None) -> list[Stmt]:
        pool = within if within is not None else [s for lab in self.order for s in self.labels[lab]]
        return [s for s in pool if s.text.startswith(text_prefix)]

    def label_text(self, label: str) -> str:
        return "\n".join(s.text for s in self.labels.get(label, []))
