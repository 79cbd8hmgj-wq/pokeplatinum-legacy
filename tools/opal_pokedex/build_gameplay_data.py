#!/usr/bin/env python3
"""Generate the Opal Pokedex gameplay manifest and runtime location table.

Outputs (deterministic; `--check` verifies the checked-in copies are current):
  docs/opal/generated/pokedex_gameplay_manifest.json   audit manifest, all 493 species
  res/graphics/pokedex/opal_locations.bin               runtime location table (packed into zukan.narc)

Everything is derived from the same sources the ROM build consumes. Where a
source cannot be resolved automatically the species/entry is *omitted* rather
than guessed, and the omission is recorded in `unresolved` in the manifest.
"""
import argparse
import json
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gameplay_sources as gs  # noqa: E402

MANIFEST_PATH = gs.p("docs", "opal", "generated", "pokedex_gameplay_manifest.json")
LOCATIONS_PATH = gs.p("res", "graphics", "pokedex", "opal_locations.bin")

# ---- runtime location record (8 bytes) ------------------------------------
# u8 kind, u8 flags, u16 name, u8 min_level, u8 max_level, u8 percent, u8 aux
KIND = {
    "LAND": 0,
    "SURF": 1,
    "OLD_ROD": 2,
    "GOOD_ROD": 3,
    "SUPER_ROD": 4,
    "RADAR": 5,
    "SWARM": 6,
    "STATIC": 7,
    "GIFT": 8,
    "FOSSIL": 9,
    "RITUAL": 10,
    "ROAMER": 11,
    "BREEDING": 12,
    "LEGACY": 13,  # post-Hall-of-Fame renewable habitat roll
    "EVENT": 14,  # restored one-time story/event encounter
    "FIXED_TILE": 15,  # Feebas fixed fishing tiles
}
KIND_NAMES = {v: k for k, v in KIND.items()}

F_MORNING, F_DAY, F_NIGHT = 0x01, 0x02, 0x04
F_HOF = 0x08  # needs Hall of Fame / game completed
F_ONCE = 0x10  # one-time (until caught)
F_BADGES = 0x20  # aux holds the minimum badge count
NAME_NONE = 0xFFFF
MAX_RECORDS = 127  # per species; runtime page capacity (OPAL_MAX_ROWS) covers this with group headers

TIME_ALL = F_MORNING | F_DAY | F_NIGHT
RECORD = struct.Struct("<BBHBBBB")

# curated, source-cited "where" strings for acquisitions that have no single
# map header. Keys are message ids appended to res/text/pokedex.json.
CURATED_WHERE = {
    "fossil": "pl_msg_pokedex_opal_where_fossil",
    "spiritomb": "pl_msg_pokedex_opal_where_spiritomb",
    "roamer_sinnoh": "pl_msg_pokedex_opal_where_roamer",
    "phione": "pl_msg_pokedex_opal_where_phione",
    "feebas": "pl_msg_pokedex_opal_where_feebas",
}


def message_index(bank_json_parts, ident):
    msgs = gs.jload(*bank_json_parts)["messages"]
    for i, m in enumerate(msgs):
        if m["id"] == ident:
            return i
    return None


def _label_index(label):
    idx = gs.location_name_index().get(label)
    return None if idx is None else idx[0]


def _slot_species(const):
    return const


def wild_entries():
    """species const -> {(location_label, kind) -> record dict} from map encounter files.

    Odds are computed per encounter file and per time band from the real slot
    tables (see src/overlay006/wild_encounters.c), then merged across files that
    share a place name by taking the best odds and the union of level ranges
    (percentages from different areas are never added together).
    """
    headers = gs.map_headers()
    files = gs.encounter_files()
    file_labels = {}
    for mh, h in headers.items():
        if h["enc"]:
            file_labels.setdefault(h["enc"], [])
            if h["label"] not in file_labels[h["enc"]]:
                file_labels[h["enc"]].append(h["label"])

    out = {}
    unresolved = []

    for fname, enc in sorted(files.items()):
        labels = file_labels.get(fname)
        if not labels:
            unresolved.append({"encounter_file": fname, "reason": "no map header references this file"})
            continue
        per = {}  # (species, kind) -> {band -> pct}, plus level span

        def add(species, kind, minlv, maxlv, pct, band):
            if species in (None, "SPECIES_NONE") or species not in gs.SPECIES_ID:
                return
            d = per.setdefault((species, kind), {"bands": {}, "min": 255, "max": 0})
            d["bands"][band] = d["bands"].get(band, 0.0) + pct
            d["min"] = min(d["min"], minlv)
            d["max"] = max(d["max"], maxlv)

        land = enc.get("land_encounters", [])
        day = enc.get("day", [])
        night = enc.get("night", [])
        if land and enc.get("land_rate", 0):
            for band in (F_MORNING, F_DAY, F_NIGHT):
                for slot, e in enumerate(land[:12]):
                    sp = e["species"]
                    if slot in (2, 3):
                        if band == F_DAY and len(day) > slot - 2:
                            sp = day[slot - 2]
                        elif band == F_NIGHT and len(night) > slot - 2:
                            sp = night[slot - 2]
                    add(sp, "LAND", e["level"], e["level"], gs.GROUND_SLOT_PCT[slot], band)
            for i, sp in enumerate(enc.get("swarms", [])[:2]):
                lv = land[i]["level"] if i < len(land) else 0
                add(sp, "SWARM", lv, lv, gs.GROUND_SLOT_PCT[i], TIME_ALL)
            for i, sp in zip((4, 5, 10, 11), enc.get("radar", [])[:4]):
                lv = land[i]["level"] if i < len(land) else 0
                add(sp, "RADAR", lv, lv, gs.GROUND_SLOT_PCT[i], TIME_ALL)
        for key, kind, pcts in (
            ("surf", "SURF", gs.SURF_SLOT_PCT),
            ("old_rod", "OLD_ROD", gs.OLD_ROD_SLOT_PCT),
            ("good_rod", "GOOD_ROD", gs.GOOD_ROD_SLOT_PCT),
            ("super_rod", "SUPER_ROD", gs.SUPER_ROD_SLOT_PCT),
        ):
            if enc.get(key + "_rate", 0) == 0:
                continue
            for slot, e in enumerate(enc.get(key + "_encounters", [])[:5]):
                add(e["species"], kind, e["level_min"], e["level_max"], pcts[slot], TIME_ALL)

        for (species, kind), d in per.items():
            flags = 0
            for band in d["bands"]:
                flags |= band
            pct = max(d["bands"].values())
            for label in labels:
                m = out.setdefault(species, {}).setdefault((label, kind), {
                    "min": 255, "max": 0, "pct": 0.0, "flags": 0})
                m["min"] = min(m["min"], d["min"])
                m["max"] = max(m["max"], d["max"])
                m["pct"] = max(m["pct"], pct)
                m["flags"] |= flags
    return out, unresolved


def _resolve_script_header(path):
    import re
    headers = gs.map_headers()
    b = os.path.basename(path)
    b = re.sub(r"^(scripts_|events_)", "", b)
    b = re.sub(r"\.(s|json)$", "", b)
    c = "MAP_HEADER_" + b.upper()
    return c if c in headers else None


def _label_for_header(mh):
    if not mh:
        return None
    return gs.map_headers()[mh]["label"]


def special_entries():
    """Special acquisitions with provenance: {species_const: [entry,...]}."""
    out = {}
    unresolved = []

    def add(species, entry):
        out.setdefault(species, []).append(entry)

    # --- special acquisitions (starters, gifts, fossils, ritual, fixed tiles)
    sa = gs.jload("docs", "overhaul", "implementation", "special_acquisitions.json")["acquisitions"]
    for key, v in sorted(sa.items()):
        sp = "SPECIES_" + key.upper()
        if sp not in gs.SPECIES_ID:
            unresolved.append({"key": key, "reason": "species constant not found"})
            continue
        kind = v["kind"]
        label = None
        gift = v.get("gift") or {}
        flags = F_ONCE if kind in ("GIFT",) else 0
        aux = 0
        if kind == "GIFT":
            mh = _resolve_script_header(gift.get("file", ""))
            label = _label_for_header(mh)
            if gift.get("min_badges"):
                flags |= F_BADGES
                aux = gift["min_badges"]
            add(sp, {"kind": "GIFT", "label": label, "flags": flags, "aux": aux,
                     "source": v.get("overhaul_method", ""), "provenance": "special_acquisitions.json"})
        elif kind == "FOSSIL":
            add(sp, {"kind": "FOSSIL", "label": None, "where": CURATED_WHERE["fossil"], "flags": 0, "aux": 0,
                     "source": v.get("overhaul_method", ""), "provenance": "special_acquisitions.json"})
        elif kind == "SPIRITOMB_RITUAL":
            add(sp, {"kind": "RITUAL", "label": None, "where": CURATED_WHERE["spiritomb"], "flags": 0, "aux": 0,
                     "source": v.get("overhaul_method", ""), "provenance": "special_acquisitions.json"})
        elif kind == "STATIC_ENCOUNTER":
            mh = _resolve_script_header((v.get("static") or v.get("encounter") or {}).get("file", "")) or \
                _first_header_in(v)
            add(sp, {"kind": "STATIC", "label": _label_for_header(mh), "flags": 0, "aux": 0,
                     "source": v.get("overhaul_method", ""), "provenance": "special_acquisitions.json"})
        elif kind == "FISHING_FIXED_TILES":
            add(sp, {"kind": "FIXED_TILE", "label": None, "where": CURATED_WHERE["feebas"], "flags": 0, "aux": 0,
                     "source": v.get("overhaul_method", ""), "provenance": "special_acquisitions.json"})
        else:
            unresolved.append({"key": key, "reason": "unknown kind " + kind})

    # --- legendary / mythical events
    ev = gs.jload("docs", "overhaul", "implementation", "events", "native_legendary_events.json")["events"]
    st = gs.jload("docs", "overhaul", "implementation", "events", "mythical_statics.json")["statics"]
    for e in ev + st:
        cls = e["acquisition_class"]
        sp = e["species"]
        mh = _resolve_script_header(e.get("script", {}).get("file", "")) if e.get("script") else None
        flags = 0
        if e.get("hall_of_fame_required"):
            flags |= F_HOF
        if e.get("one_time_vs_renewable", "").startswith("ONE_TIME"):
            flags |= F_ONCE
        lv = _first_int(e.get("level", "0"))
        entry = {"label": _label_for_header(mh), "flags": flags, "aux": 0, "min": lv, "max": _last_int(e.get("level", "0")),
                 "source": e.get("map_system", ""), "provenance": "events/*.json:" + cls}
        if cls in ("NATIVE_STATIC", "NATIVE_RUIN", "HIDDEN_MYTHICAL_STATIC"):
            entry["kind"] = "STATIC"
        elif cls == "NATIVE_ROAMER":
            entry["kind"] = "ROAMER"
            entry["label"] = None
            entry["where"] = CURATED_WHERE["roamer_sinnoh"]
        elif cls == "RESTORED_EVENT":
            entry["kind"] = "EVENT"
        elif cls == "BREEDING_ONLY":
            entry["kind"] = "BREEDING"
            entry["label"] = None
            entry["where"] = CURATED_WHERE["phione"]
        else:
            unresolved.append({"species": sp, "reason": "unmapped class " + cls})
            continue
        add(sp, entry)

    # --- post-Hall-of-Fame renewable habitats
    lg = gs.jload("docs", "overhaul", "implementation", "events", "legacy_legendary_encounters.json")["encounters"]
    for e in lg:
        for row in e.get("rows", []):
            mh = row["map_header"]
            hdr = gs.map_headers().get(mh)
            if not hdr:
                unresolved.append({"species": e["species"], "reason": "unknown map header " + mh})
                continue
            add(e["species"], {
                "kind": "LEGACY", "label": hdr["label"], "flags": F_HOF, "aux": 0,
                "min": e["min_level"], "max": e["max_level"], "pct": e["percent"],
                "source": e.get("map_system", ""), "provenance": "events/legacy_legendary_encounters.json",
                "method": row.get("encounter_type"),
            })
    return out, unresolved


def _first_header_in(v):
    for sub in v.values():
        if isinstance(sub, dict) and "file" in sub:
            h = _resolve_script_header(sub["file"])
            if h:
                return h
    return None


def _first_int(s):
    import re
    m = re.findall(r"\d+", str(s))
    return int(m[0]) if m else 0


def _last_int(s):
    import re
    m = re.findall(r"\d+", str(s))
    return int(m[-1]) if m else 0


def build_locations():
    wild, un1 = wild_entries()
    special, un2 = special_entries()
    where_idx = {k: message_index(("res", "text", "pokedex.json"), v) for k, v in CURATED_WHERE.items()}
    per_species = {}
    for sid in range(1, gs.MAX_NATIONAL + 1):
        const = gs.SPECIES[sid]
        recs = []
        for (label, kind), d in sorted(wild.get(const, {}).items(), key=lambda kv: (KIND[kv[0][1]], kv[0][0])):
            idx = _label_index(label)
            if idx is None:
                continue
            pct = int(round(min(d["pct"], 100)))
            recs.append({"kind": kind, "label": label, "name": idx, "min": d["min"], "max": d["max"],
                         "pct": max(pct, 1), "flags": d["flags"], "aux": 0, "provenance": "res/field/encounters"})
        for e in special.get(const, []):
            if e.get("label"):
                name = _label_index(e["label"])
                name_src = 0
            else:
                name = where_idx.get(next((k for k, v in CURATED_WHERE.items() if v == e.get("where")), ""), None)
                name_src = 1
            if name is None:
                continue
            recs.append({"kind": e["kind"], "label": e.get("label") or e.get("where"), "name": name, "name_src": name_src,
                         "min": e.get("min", 0), "max": e.get("max", 0), "pct": e.get("pct", 0),
                         "flags": e["flags"], "aux": e["aux"], "provenance": e["provenance"]})
        per_species[sid] = recs
    return per_species, un1 + un2


def pack_locations(per_species):
    """Binary layout:
      u16 species_count (494)
      u16 offsets[494+1]   byte offset of each species block from file start (block 0 = SPECIES_NONE)
      blocks: u8 count, then count * 8-byte records.
    `flags` bit 6/7 are unused; name_src is encoded in aux bit 7 for records whose name is a curated pokedex message.
    """
    count = gs.MAX_NATIONAL + 1
    blocks = []
    for sid in range(count):
        recs = per_species.get(sid, [])[:MAX_RECORDS]
        b = bytearray([len(recs)])
        for r in recs:
            aux = r["aux"] & 0x7F
            if r.get("name_src"):
                aux |= 0x80
            b += RECORD.pack(KIND[r["kind"]], r["flags"], r["name"], r["min"] & 0xFF, r["max"] & 0xFF,
                             min(r["pct"], 100), aux)
        blocks.append(bytes(b))
    header_size = 2 + 2 * (count + 1)
    offsets = []
    pos = header_size
    for b in blocks:
        offsets.append(pos)
        pos += len(b)
    offsets.append(pos)
    out = struct.pack("<H", count) + struct.pack("<%dH" % (count + 1), *offsets) + b"".join(blocks)
    return out


# ---- manifest --------------------------------------------------------------
def evolution_edges(sid):
    return [list(e) for e in gs.species_data(sid)["evolutions"]]


def build_manifest():
    tms = gs.tm_table()
    per_species_loc, unresolved = build_locations()
    species = []
    for sid in range(1, gs.MAX_NATIONAL + 1):
        d = gs.species_data(sid)
        ls = d["learnset"]
        entry = {
            "id": sid,
            "const": gs.SPECIES[sid],
            "name": gs.species_name(sid),
            "types": d["types"],
            "abilities": d["abilities"],
            "base_stats": d["base_stats"],
            "base_stat_total": sum(d["base_stats"].values()),
            "evolutions": evolution_edges(sid),
            "level_up": ls["by_level"],
            "tm_hm": [{"slot": t, "move": tms[t]} for t in ls["by_tm"]],
            "tutor": ls["by_tutor"],
            "forms": {n: {"types": f["types"], "abilities": f["abilities"], "base_stats": f["base_stats"]}
                      for n, f in gs.species_forms(sid).items() if "types" in f},
            "locations": [{k: v for k, v in r.items()} for r in per_species_loc[sid]],
        }
        species.append(entry)
    return {
        "schema": "opal_pokedex_gameplay_manifest/1",
        "generated_by": "tools/opal_pokedex/build_gameplay_data.py",
        "sources": [
            "res/pokemon/*/data.json", "res/moves/*/data.json", "res/items/data/{tm,hm}*.json",
            "res/field/encounters/*.json", "include/data/map_headers.h",
            "docs/overhaul/implementation/special_acquisitions.json",
            "docs/overhaul/implementation/events/*.json",
        ],
        "unresolved": unresolved,
        "species": species,
    }


def serialize_manifest(m):
    return json.dumps(m, indent=1, sort_keys=False) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="fail if checked-in outputs are stale")
    args = ap.parse_args()

    manifest = build_manifest()
    per_species_loc, _ = build_locations()
    manifest_text = serialize_manifest(manifest)
    loc_bin = pack_locations(per_species_loc)

    if args.check:
        ok = True
        for path, data in ((MANIFEST_PATH, manifest_text.encode()), (LOCATIONS_PATH, loc_bin)):
            cur = open(path, "rb").read() if os.path.exists(path) else None
            if cur != data:
                print("STALE:", os.path.relpath(path, gs.ROOT))
                ok = False
        sys.exit(0 if ok else 1)

    os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        f.write(manifest_text)
    with open(LOCATIONS_PATH, "wb") as f:
        f.write(loc_bin)
    n_rec = sum(len(v) for v in per_species_loc.values())
    print(f"wrote {os.path.relpath(MANIFEST_PATH, gs.ROOT)} ({len(manifest_text)} bytes)")
    print(f"wrote {os.path.relpath(LOCATIONS_PATH, gs.ROOT)} ({len(loc_bin)} bytes, {n_rec} records)")
    print(f"unresolved: {len(manifest['unresolved'])}")


if __name__ == "__main__":
    main()
