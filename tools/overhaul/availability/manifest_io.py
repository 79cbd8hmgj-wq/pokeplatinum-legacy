"""Compact, diff-friendly JSON writer: every list element of 'entries'-style arrays is one line."""
from __future__ import annotations

import json


def dumps_compact(obj, line_arrays=("entries", "slots", "families_index")) -> str:
    """Indent=2 JSON where arrays named in line_arrays place each element on a single line."""
    def enc(o, indent, key=None):
        pad = "  " * indent
        if isinstance(o, dict):
            if not o:
                return "{}"
            items = [f'{pad}  {json.dumps(k, ensure_ascii=False)}: {enc(v, indent + 1, k)}' for k, v in o.items()]
            return "{\n" + ",\n".join(items) + f"\n{pad}}}"
        if isinstance(o, list):
            if not o:
                return "[]"
            if key in line_arrays:
                items = [f"{pad}  {json.dumps(v, ensure_ascii=False)}" for v in o]
                return "[\n" + ",\n".join(items) + f"\n{pad}]"
            return json.dumps(o, ensure_ascii=False) if all(not isinstance(v, (dict, list)) for v in o) \
                else "[\n" + ",\n".join(f"{pad}  {enc(v, indent + 1)}" for v in o) + f"\n{pad}]"
        return json.dumps(o, ensure_ascii=False)
    return enc(obj, 0) + "\n"
