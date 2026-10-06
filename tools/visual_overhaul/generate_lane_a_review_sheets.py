#!/usr/bin/env python3
"""Generate persistent Lane A visual-review contact sheets and an index.

Candidates are already exact-pixel deduplicated. This tool groups them by species
when species metadata exists, otherwise by source/group, and renders bounded
contact sheets for manual/visual review. It does not change review_status.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RANGER_ID_RE = re.compile(
    r"^ranger2:pokemon:(?P<species>\d{3}):(?P<variant>\d{2}):"
    r"(?P<group>[^:]+):(?P<frame>[^:]+)$"
)


def locate(row: dict, roots: dict[str, Path], ranger_render_root: Path, platinum_root: Path) -> Path:
    source = str(row.get("source_id") or "")
    if source == "ranger2" and row.get("asset_type") == "pokemon_sprite_frame":
        m = RANGER_ID_RE.match(str(row.get("asset_id") or ""))
        if not m:
            raise FileNotFoundError(f"Unparseable Ranger asset id: {row.get('asset_id')}")
        return (
            ranger_render_root
            / m.group("species")
            / m.group("variant")
            / m.group("group")
            / f"{m.group('frame')}.png"
        )

    root = roots.get(source)
    source_path = row.get("source_path")
    render_path = row.get("render_path")
    candidates = []
    if root and source_path:
        candidates.append(root / str(source_path))
    if root and render_path and render_path != source_path:
        candidates.append(root / str(render_path))
    if render_path:
        rp = Path(str(render_path))
        if not rp.is_absolute():
            candidates.append(platinum_root / rp)
    for path in candidates:
        if path.is_file():
            return path
    raise FileNotFoundError(f"No materialized image for {row.get('asset_id')}")


def safe_name(value: str) -> str:
    out = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    return out.strip("_") or "group"


def fit_thumb(im: Image.Image, box: int) -> Image.Image:
    rgba = im.convert("RGBA")
    rgba.thumbnail((box, box), Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", (box, box), (255, 255, 255, 0))
    x = (box - rgba.width) // 2
    y = (box - rgba.height) // 2
    canvas.alpha_composite(rgba, (x, y))
    return canvas


def group_key(candidate: dict) -> tuple[str, str]:
    species = candidate.get("representative_species_dex")
    source = str(candidate.get("representative_source_id") or "unknown")
    group = str(candidate.get("representative_group") or "ungrouped")
    if species is not None:
        return ("species", f"{int(species):03d}")
    return ("source_group", f"{source}__{safe_name(group)}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--review-set", required=True, type=Path)
    p.add_argument("--integrity", required=True, type=Path)
    p.add_argument("--platinum-root", required=True, type=Path)
    p.add_argument("--ranger-render-root", required=True, type=Path)
    p.add_argument("--ranger-root", required=True, type=Path)
    p.add_argument("--hgss-root", type=Path, default=Path("/nonexistent/hgss"))
    p.add_argument("--diamond-root", type=Path, default=Path("/nonexistent/diamond"))
    p.add_argument("--pmd-sky-root", type=Path, default=Path("/nonexistent/pmd-sky"))
    p.add_argument(
        "--only-kind",
        action="append",
        default=[],
        help="Regenerate only sheets of this kind (e.g. species). Other kinds are kept "
        "from the existing --write-index-json and their PNGs are left untouched.",
    )
    p.add_argument("--output-dir", required=True, type=Path)
    p.add_argument("--write-index-json", required=True, type=Path)
    p.add_argument("--write-index-md", required=True, type=Path)
    p.add_argument("--per-sheet", type=int, default=80)
    p.add_argument("--columns", type=int, default=8)
    p.add_argument("--thumb-size", type=int, default=96)
    args = p.parse_args()

    review = json.loads(args.review_set.read_text())
    integrity = json.loads(args.integrity.read_text())
    integrity_by_id = {r["asset_id"]: r for r in integrity.get("records", [])}
    roots = {
        "ranger2": args.ranger_root.resolve(),
        "hgss": args.hgss_root.resolve(),
        "diamond": args.diamond_root.resolve(),
        "pmd_sky": args.pmd_sky_root.resolve(),
    }

    out = args.output_dir
    only = set(args.only_kind)
    kept_sheets: list[dict] = []
    if only:
        previous = json.loads(args.write_index_json.read_text())
        kept_sheets = [s for s in previous["sheets"] if s["kind"] not in only]
        for kind in only:
            if (out / kind).exists():
                shutil.rmtree(out / kind)
    else:
        if out.exists():
            shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for candidate in review.get("candidates", []):
        key = group_key(candidate)
        if only and key[0] not in only:
            continue
        grouped[key].append(candidate)

    font = ImageFont.load_default()
    cell_w = args.thumb_size + 20
    cell_h = args.thumb_size + 34
    sheets = []
    candidate_count = 0

    for (kind, key), candidates in sorted(grouped.items()):
        candidates.sort(key=lambda c: (
            str(c.get("representative_source_id") or ""),
            str(c.get("representative_asset_id") or ""),
        ))
        for part_no, start in enumerate(range(0, len(candidates), args.per_sheet), 1):
            part = candidates[start:start + args.per_sheet]
            rows_n = math.ceil(len(part) / args.columns)
            header_h = 34
            sheet = Image.new("RGB", (args.columns * cell_w, header_h + rows_n * cell_h), "white")
            draw = ImageDraw.Draw(sheet)
            title = f"{kind}:{key} part {part_no} — {len(part)} candidates"
            draw.text((6, 6), title, fill="black", font=font)

            entries = []
            for local_i, candidate in enumerate(part, 1):
                asset_id = candidate["representative_asset_id"]
                row = integrity_by_id.get(asset_id)
                if not row:
                    raise RuntimeError(f"Representative missing from integrity report: {asset_id}")
                path = locate(
                    row,
                    roots,
                    args.ranger_render_root.resolve(),
                    args.platinum_root.resolve(),
                )
                if not path.is_file():
                    raise FileNotFoundError(path)
                with Image.open(path) as im:
                    thumb = fit_thumb(im, args.thumb_size)
                col = (local_i - 1) % args.columns
                rr = (local_i - 1) // args.columns
                x = col * cell_w + 10
                y = header_h + rr * cell_h
                checker = Image.new("RGBA", (args.thumb_size, args.thumb_size), "white")
                cd = ImageDraw.Draw(checker)
                step = 12
                for yy in range(0, args.thumb_size, step):
                    for xx in range(0, args.thumb_size, step):
                        if ((xx // step) + (yy // step)) % 2:
                            cd.rectangle((xx, yy, xx + step - 1, yy + step - 1), fill=(224, 224, 224, 255))
                checker.alpha_composite(thumb)
                sheet.paste(checker.convert("RGB"), (x, y))
                label = f"{local_i:02d} {row.get('source_id','')}"
                draw.text((x, y + args.thumb_size + 2), label, fill="black", font=font)
                entries.append({
                    "slot": local_i,
                    "asset_id": asset_id,
                    "source_id": row.get("source_id"),
                    "species_dex": row.get("species_dex"),
                    "group": row.get("group"),
                    "source_path": row.get("source_path"),
                    "render_path": row.get("render_path"),
                    "width": candidate.get("width"),
                    "height": candidate.get("height"),
                    "duplicate_count": candidate.get("duplicate_count"),
                })

            rel_dir = Path(kind)
            filename = f"{key}__p{part_no:03d}.png"
            target = out / rel_dir / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            sheet.save(target, optimize=True)
            sheets.append({
                "sheet_id": f"{kind}:{key}:p{part_no:03d}",
                "kind": kind,
                "group_key": key,
                "part": part_no,
                "count": len(part),
                "path": str(target),
                "entries": entries,
            })
            candidate_count += len(part)

    if only:
        sheets = sorted(
            [*kept_sheets, *sheets], key=lambda s: (s["kind"], s["group_key"], s["part"])
        )
        candidate_count = sum(s["count"] for s in sheets)
    if candidate_count != review["unique_visual_candidates"]:
        raise RuntimeError(
            f"Sheet coverage mismatch: {candidate_count} != {review['unique_visual_candidates']}"
        )

    payload = {
        "schema_version": 1,
        "source_review_set": str(args.review_set),
        "candidate_count": candidate_count,
        "sheet_count": len(sheets),
        "per_sheet": args.per_sheet,
        "columns": args.columns,
        "thumb_size": args.thumb_size,
        "kind_counts": dict(sorted(Counter(s["kind"] for s in sheets).items())),
        "sheets": sheets,
    }
    args.write_index_json.parent.mkdir(parents=True, exist_ok=True)
    args.write_index_json.write_text(json.dumps(payload, indent=2) + "\n")

    lines = [
        "# Lane A Visual Review Sheets",
        "",
        "Persistent contact sheets for every unique Lane A visual candidate.",
        "These sheets are review material only and do not change donor review status.",
        "",
        f"- Unique visual candidates covered: **{candidate_count}**",
        f"- Contact sheets: **{len(sheets)}**",
        f"- Maximum candidates per sheet: **{args.per_sheet}**",
        "",
        "## Sheet groups",
        "",
        "| Kind | Sheets |",
        "|---|---:|",
    ]
    for kind, count in sorted(Counter(s["kind"] for s in sheets).items()):
        lines.append(f"| {kind} | {count} |")
    lines += [
        "",
        "## Review workflow",
        "",
        "- Species-backed candidates are grouped by National Dex number.",
        "- Non-species render-ready assets are grouped by donor source and catalog group.",
        "- Each sheet slot maps back to a stable asset_id in the JSON index.",
        "- Exact duplicates were already collapsed before sheet generation.",
        "- No candidate is promoted or rejected automatically.",
    ]
    args.write_index_md.write_text("\n".join(lines) + "\n")

    print("Candidates covered:", candidate_count)
    print("Sheets generated:", len(sheets))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
