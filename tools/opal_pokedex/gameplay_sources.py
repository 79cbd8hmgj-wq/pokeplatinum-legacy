#!/usr/bin/env python3
"""Loaders for the gameplay sources the Opal Pokedex reads.

Everything here reads the *same* repository files the ROM build compiles
(res/pokemon/*/data.json, res/moves/*/data.json, res/items/data/*.json,
res/field/encounters/*.json, include/data/map_headers.h, ...). Nothing is
hand-copied. The loaders are shared by the manifest generator and the parity
validator so both see identical facts.
"""
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def p(*parts):
    return os.path.join(ROOT, *parts)


def jload(*parts):
    with open(p(*parts), encoding="utf-8") as f:
        return json.load(f)


def read_lines(*parts):
    with open(p(*parts), encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]


# --------------------------------------------------------------------------
# Species
# --------------------------------------------------------------------------
SPECIES = read_lines("generated", "species.txt")  # index == species id
SPECIES_ID = {name: i for i, name in enumerate(SPECIES)}
MAX_NATIONAL = 493

# directory name exceptions (species constant -> res/pokemon directory)
_DIR_EXCEPTIONS = {
    "SPECIES_NIDORAN_F": "nidoran_f",
    "SPECIES_NIDORAN_M": "nidoran_m",
    "SPECIES_MR_MIME": "mr_mime",
    "SPECIES_MIME_JR": "mime_jr",
    "SPECIES_HO_OH": "ho_oh",
    "SPECIES_PORYGON_Z": "porygon_z",
}


def species_dir(const):
    if const in _DIR_EXCEPTIONS:
        return _DIR_EXCEPTIONS[const]
    return const[len("SPECIES_"):].lower()


_species_cache = {}


def species_data(sid):
    """data.json for the base form of species id `sid` (1..493)."""
    if sid not in _species_cache:
        d = species_dir(SPECIES[sid])
        path = p("res", "pokemon", d, "data.json")
        if not os.path.exists(path):
            path = p("res", "pokemon", d, "forms", "base", "data.json")
        _species_cache[sid] = jload(os.path.relpath(path, ROOT))
    return _species_cache[sid]


def species_forms(sid):
    """Return {form_name: data.json dict} for species with alternate-form data files."""
    d = species_dir(SPECIES[sid])
    forms_dir = p("res", "pokemon", d, "forms")
    out = {}
    if os.path.isdir(forms_dir):
        for name in sorted(os.listdir(forms_dir)):
            fp = os.path.join(forms_dir, name, "data.json")
            if os.path.exists(fp):
                with open(fp, encoding="utf-8") as f:
                    out[name] = json.load(f)
    return out


def species_name(sid):
    return species_data(sid)["pokedex_data"]["en"]["name"]


# --------------------------------------------------------------------------
# Moves / TMs / abilities
# --------------------------------------------------------------------------
MOVES = read_lines("generated", "moves.txt")
MOVE_ID = {n: i for i, n in enumerate(MOVES)}
ABILITIES = read_lines("generated", "abilities.txt")


def move_dir(const):
    return const[len("MOVE_"):].lower()


_move_cache = {}


def move_data(const):
    if const not in _move_cache:
        _move_cache[const] = jload("res", "moves", move_dir(const), "data.json")
    return _move_cache[const]


def tm_table():
    """{'TM01': 'MOVE_FOCUS_PUNCH', ..., 'HM08': ...} from res/items/data/{tm,hm}NN.json."""
    out = {}
    base = p("res", "items", "data")
    for name in sorted(os.listdir(base)):
        m = re.match(r"^(tm|hm)(\d\d)\.json$", name)
        if m:
            with open(os.path.join(base, name), encoding="utf-8") as f:
                j = json.load(f)
            out[m.group(1).upper() + m.group(2)] = j["teachesMove"]
    return out


def _message_table(*parts):
    j = jload(*parts)
    return j["messages"]


def _flatten(msg):
    en = msg.get("en_US")
    if isinstance(en, list):
        return "".join(en)
    return en or ""


def ability_names():
    return [_flatten(m) for m in _message_table("res", "text", "ability_names.json")]


def ability_descriptions():
    return [_flatten(m) for m in _message_table("res", "text", "ability_descriptions.json")]


def location_name_index():
    """LocationNames_Text_* id -> (index, en_US string)."""
    out = {}
    for i, m in enumerate(_message_table("res", "text", "location_names.json")):
        out[m["id"]] = (i, _flatten(m))
    return out


# --------------------------------------------------------------------------
# Map headers + wild encounters
# --------------------------------------------------------------------------
def map_headers():
    """Parse include/data/map_headers.h: {MAP_HEADER_X: {'enc': file|None, 'label': LocationNames_Text_X}}."""
    text = open(p("include", "data", "map_headers.h"), encoding="utf-8").read()
    out = {}
    for m in re.finditer(r"\[(MAP_HEADER_\w+)\]\s*=\s*\{(.*?)\n    \},", text, re.S):
        body = m.group(2)
        enc = re.search(r"\.wildEncountersArchiveID\s*=\s*(\w+)", body)
        lab = re.search(r"\.mapLabelTextID\s*=\s*(\w+)", body)
        e = enc.group(1) if enc else None
        out[m.group(1)] = {
            "enc": None if e in (None, "ENCOUNTERS_NONE") else e,
            "label": lab.group(1) if lab else None,
        }
    return out


def encounter_files():
    """{encounter_file_stem: dict} for res/field/encounters/encounters_*.json."""
    base = p("res", "field", "encounters")
    out = {}
    for name in sorted(os.listdir(base)):
        if name.startswith("encounters_") and name.endswith(".json"):
            with open(os.path.join(base, name), encoding="utf-8") as f:
                out[name[:-5]] = json.load(f)
    return out


# slot probabilities straight from src/overlay006/wild_encounters.c
GROUND_SLOT_PCT = [20, 20, 10, 10, 10, 10, 5, 5, 4, 4, 1, 1]
SURF_SLOT_PCT = [60, 30, 5, 4, 1]
OLD_ROD_SLOT_PCT = [60, 30, 5, 4, 1]
GOOD_ROD_SLOT_PCT = [40, 40, 15, 4, 1]
SUPER_ROD_SLOT_PCT = [40, 40, 15, 4, 1]
