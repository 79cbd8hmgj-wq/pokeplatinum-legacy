"""Static verification of special (non-wild) acquisitions against repository source.

Every USER_DECISION family resolved by the special-acquisition pass has an entry in
docs/overhaul/implementation/special_acquisitions.json.  The analyzers below read the *actual* scripts / C source
(under SRC_ROOT, default = repo root) and prove, per family, that the acquisition path is

  S1  present in source (the give/battle/table entry exists),
  S2  retry-safe (party-full guard before the give, flag set only after a successful give, recovery for failures),
  S3  gated no later than PRE_E4 (badge gate / location band),
  S4  free of external dependencies (trade, link, Wi-Fi, Mystery Gift, National Dex, daily/random rotation, Trainer ID),
  S5  not a mutually exclusive one-time choice (independent flag per starter; chosen starter excluded only for itself).

Failure codes are returned as 'S<n>' strings; validate_availability.py prints them as FAIL lines.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from common import BANDS, IMPL_DIR, PRE_E4_BANDS, ROOT

SRC_ROOT = Path(os.environ["AVAIL_SRC_ROOT"]) if os.environ.get("AVAIL_SRC_ROOT") else ROOT

# script commands / flags that make an acquisition depend on something outside the single-player save
FORBIDDEN_SCRIPT_TOKENS = [
    "StartBattleClient", "StartBattleServer", "StartLinkBattle", "InitCommFieldCmd", "EndCommunication",
    "FieldCommEnterBattleRoom", "OpenPartyMenuForTrade", "SelectPokemonToTrade", "InitNPCTrade", "StartNPCTrade",
    "FinishNPCTrade", "MysteryGiftGive", "LoadMysteryGift", "GiveMysteryGift", "CheckAvailableMysteryGift",
    "CheckCanReceiveMysteryGift", "CheckDistributionEvent", "ShowUnionRoomMenu", "DoUnionRoomGreeting",
    "CheckHasWiFiListValidLogin", "GetNationalDexEnabled", "GetNationalDexCaughtCount", "GetDayOfWeek",
    "GetDailyRandomLevel", "GetRandom", "FLAG_DAILY_", "ITEM_GBA", "CheckIsMysteryGiftPhrase",
]
BADGE_BAND = {0: "E0", 1: "E1", 2: "M1", 3: "M1", 4: "M1", 5: "M2", 6: "L1", 7: "L2", 8: "P0"}


def read(rel: str) -> str:
    p = SRC_ROOT / rel
    if not p.exists():
        raise FileNotFoundError(rel)
    return p.read_text()


# ---------------------------------------------------------------------------------------------- script parsing
class Script:
    def __init__(self, rel: str):
        self.rel = rel
        self.labels: dict[str, list[str]] = {}
        order, cur = [], None
        for raw in read(rel).splitlines():
            line = raw.split("@")[0].rstrip()
            m = re.match(r"^(\w+):\s*$", line)
            if m:
                cur = m.group(1)
                self.labels[cur] = []
                order.append(cur)
            elif cur is not None and line.strip():
                self.labels[cur].append(line.strip())
        self.order = order
        self.entries = [l.split()[1] for l in read(rel).splitlines() if l.strip().startswith("ScriptEntry ")
                        and len(l.split()) > 1]

    def targets(self, label: str) -> set[str]:
        out = set()
        body = self.labels.get(label, [])
        for ln in body:
            tok = ln.replace(",", " ").split()
            if tok and tok[0].startswith(("GoTo", "Call")) and not tok[0].startswith("CallCommon"):
                if tok[-1] in self.labels:
                    out.add(tok[-1])
        # fallthrough into the next label when the body does not terminate
        terminal = bool(body) and re.match(r"^(End\b|Return\b|GoTo\s)", body[-1])
        i = self.order.index(label)
        if not terminal and i + 1 < len(self.order):
            out.add(self.order[i + 1])
        return out

    def ancestors(self, label: str) -> set[str]:
        rev: dict[str, set[str]] = {l: set() for l in self.labels}
        for l in self.labels:
            for t in self.targets(l):
                rev[t].add(l)
        seen, stack = {label}, [label]
        while stack:
            x = stack.pop()
            for p in rev.get(x, ()):
                if p not in seen:
                    seen.add(p)
                    stack.append(p)
        return seen

    def text(self, labels) -> str:
        return "\n".join(ln for l in labels for ln in self.labels.get(l, []))


def _has_party_guard(lines: list[str]) -> bool:
    for i, ln in enumerate(lines):
        if ln.startswith("GetPartyCount"):
            nxt = " ".join(lines[i + 1:i + 3])
            if re.search(r"GoToIfEq VAR_RESULT, (6|MAX_PARTY_SIZE),", nxt) or re.search(r"GoToIfGe VAR_RESULT, (6|MAX_PARTY_SIZE),", nxt):
                return True
    return False


def _index(lines, pred):
    for i, ln in enumerate(lines):
        if pred(ln):
            return i
    return -1


# ---------------------------------------------------------------------------------------------- analyzers
def check_gift(fid: str, a: dict, band_of: dict) -> list[str]:
    """Pokemon / Egg gift scripts (starters, Tyrogue, Happiny, Castform, Eevee, Porygon, Riolu)."""
    f = []
    try:
        sc = Script(a["file"])
    except FileNotFoundError:
        return [f"S1 {fid}: script file {a['file']} missing"]
    entry = a["entry_label"]
    if entry not in sc.labels or entry not in sc.entries:
        f.append(f"S1 {fid}: entry label {entry} is not a ScriptEntry of {a['file']}")
    cmd = a.get("give_command", "GivePokemon")
    if a["give"]["mode"] == "table":                       # offer label sets a species var, shared give routine
        off, give_label, var = a["give"]["offer_label"], a["give"]["give_label"], a["give"]["var"]
        if off not in sc.labels or give_label not in sc.labels:
            return f + [f"S1 {fid}: offer/give label missing"]
        ot = sc.labels[off]
        if f"SetVar {var}, {a['species']}" not in ot:
            f.append(f"S1 {fid}: {off} does not select {a['species']}")
        if not any(l.startswith("Call") and l.endswith(give_label) for l in ot):
            f.append(f"S1 {fid}: {off} does not call {give_label}")
        ci = _index(ot, lambda l: l.startswith("Call") and l.endswith(give_label))
        si = _index(ot, lambda l: l == f"SetFlag {a['flag']}")
        if si < 0 or si < ci:
            f.append(f"S2 {fid}: completion flag {a['flag']} must be set after the give call")
        gl = sc.labels[give_label]
        gi = _index(gl, lambda l: l.startswith(f"{cmd} {var},"))
        if gi < 0:
            f.append(f"S1 {fid}: {give_label} has no {cmd} {var}")
        if not _has_party_guard(gl[:gi if gi >= 0 else len(gl)]):
            f.append(f"S2 {fid}: no party-full guard before the give in {give_label}")
        if any(l.startswith("SetFlag") for l in gl):
            f.append(f"S2 {fid}: give routine sets a flag before success is known")
        anc_target = off
    else:                                                  # direct give in one label
        lab = a["give"]["label"]
        if lab not in sc.labels:
            return f + [f"S1 {fid}: give label {lab} missing"]
        body = sc.labels[lab]
        gi = _index(body, lambda l: l.startswith(f"{cmd} {a['species']}"))
        if gi < 0:
            f.append(f"S1 {fid}: {lab} has no {cmd} {a['species']}")
        if not _has_party_guard(body[:gi if gi >= 0 else len(body)]):
            f.append(f"S2 {fid}: no party-full guard before the give in {lab}")
        # flag: set after the give, either in this label or in the same-file label that completes the gift
        flag = a["flag"]
        fi = _index(body, lambda l: l == f"SetFlag {flag}")
        if fi >= 0 and gi >= 0 and fi < gi:
            f.append(f"S2 {fid}: completion flag {flag} set before the give")
        if fi < 0 and not any(l == f"SetFlag {flag}" for l in sc.labels[a.get("flag_label", lab)]):
            f.append(f"S2 {fid}: completion flag {flag} never set after the give")
        if a.get("recovery_flag"):                          # Riolu: failure flag keeps the offer alive
            rf = a["recovery_flag"]
            all_lines = sc.text(sc.labels)
            if f"SetFlag {rf}" not in all_lines or f"GoToIfSet {rf}" not in all_lines or f"ClearFlag {rf}" not in all_lines:
                f.append(f"S2 {fid}: recovery flag {rf} must be set on failure, checked at the entry and cleared on success")
        anc_target = lab
    # gate must not be later than PRE_E4
    if a.get("min_badges", 0) > 8:
        f.append(f"S3 {fid}: gate requires more than 8 badges")
    if a.get("min_badges", 0) > 0:
        anc_text = sc.text(sc.ancestors(anc_target))
        if not re.search(rf"GoToIfLt VAR_\w+, {a['min_badges']},", anc_text):
            f.append(f"S3 {fid}: badge gate {a['min_badges']} not found in {a['file']}")
    band = band_of(a)
    if band not in PRE_E4_BANDS:
        f.append(f"S3 {fid}: acquisition band {band} is not PRE_E4")
    # forbidden dependencies on the path to the give
    anc = sc.ancestors(anc_target if a["give"]["mode"] == "table" else a["give"]["label"])
    text = sc.text(anc)
    for tok in FORBIDDEN_SCRIPT_TOKENS:
        if tok in text:
            f.append(f"S4 {fid}: forbidden dependency '{tok}' on the path to the give")
    if re.search(r"\b(TakePokemon|RemovePokemon|RemoveItem|ReleasePokemon)\b", text):
        f.append(f"S5 {fid}: gift consumes a Pokemon/item (mutually exclusive choice)")
    return f


def check_starters(manifest: dict) -> list[str]:
    f = []
    starters = [a for a in manifest["acquisitions"].values() if a["decision_key"] == "STARTER_DISTRIBUTION"]
    flags = [a["gift"]["flag"] for a in starters]
    if len(set(flags)) != len(flags):
        f.append("S5 starters: two starters share a completion flag (mutually exclusive)")
    file = starters[0]["gift"]["file"]
    sc = Script(file)
    text = "\n".join(sc.text(sc.labels).splitlines())
    if "GetPlayerStarterSpecies" not in text:
        f.append("S5 starters: the chosen Sinnoh starter is never read, so it could be offered twice")
    for a in starters:
        if a["region"] == "SINNOH" and not re.search(rf"GoToIfEq VAR_0x8000, {a['gift']['species']},", text):
            f.append(f"S5 starters: Sinnoh {a['gift']['species']} is not skipped when it is the chosen starter")
    species = {a["gift"]["species"] for a in starters}
    expected = {f"SPECIES_{x}" for x in ["BULBASAUR", "CHARMANDER", "SQUIRTLE", "CHIKORITA", "CYNDAQUIL", "TOTODILE",
                                          "TREECKO", "TORCHIC", "MUDKIP", "TURTWIG", "CHIMCHAR", "PIPLUP"]}
    if species != expected:
        f.append(f"S5 starters: offered species {sorted(expected - species)} missing")
    return f


def check_static(fid: str, a: dict) -> list[str]:
    f = []
    sc = Script(a["file"])
    lab = a["entry_label"]
    if lab not in sc.labels or lab not in sc.entries:
        return [f"S1 {fid}: static entry {lab} missing"]
    anc_text = sc.text(sc.ancestors(lab))
    all_text = sc.text(sc.labels)
    if f"StartWildBattle {a['species']}," not in all_text:
        f.append(f"S1 {fid}: no static battle with {a['species']}")
    for tok in a.get("forbidden_gate_tokens", []):
        if tok in all_text:
            f.append(f"S4 {fid}: gate token '{tok}' still present (daily/random rotation)")
    for tok in FORBIDDEN_SCRIPT_TOKENS:
        if tok in all_text:
            f.append(f"S4 {fid}: forbidden dependency '{tok}'")
    # retry: a battle that ends without a capture must not set the caught flag
    body = all_text.splitlines()
    bi = _index(body, lambda l: l.startswith("StartWildBattle"))
    seq = "\n".join(body[bi:])
    if not re.search(r"CheckDidNotCapture VAR_RESULT\s*\nGoToIfEq VAR_RESULT, TRUE,", seq):
        f.append(f"S2 {fid}: a battle without capture is not recoverable (CheckDidNotCapture branch missing)")
    if a["caught_flag"] not in seq or "CheckDidNotCapture" not in seq or \
            seq.index(a["caught_flag"]) < seq.index("CheckDidNotCapture"):
        f.append(f"S2 {fid}: caught flag must be set only after the capture check")
    sk = a.get("secret_key")
    if sk:
        if f"SetVar VAR_0x8004, {sk['item']}" not in all_text or "Common_GiveItemQuantity" not in all_text:
            f.append(f"S1 {fid}: capture does not grant the Secret Key / form-room unlock")
        # D5: the form-room unlock is the Secret Key alone; no script may still gate on the distribution magic number
        for rel in list(sk.get("form_room_files", [])) + [a["file"]]:
            if "DISTRIBUTION_EVENT_ROTOM" in read(rel):
                f.append(f"S1 {fid}: {rel} still gates the form room on DISTRIBUTION_EVENT_ROTOM")
    if a["band"] not in PRE_E4_BANDS:
        f.append(f"S3 {fid}: band {a['band']} is not PRE_E4")
    return f


def check_fossil(fid: str, a: dict, manifest: dict) -> list[str]:
    f = []
    src = read("src/underground/mining.c")
    rows = re.findall(r"\.itemID = MINING_TREASURE_(\w+), \.oddTIDWeight = (\d+), \.evenTIDWeight = (\d+), "
                      r"\.oddTIDNatDexWeight = (\d+), \.evenTIDNatDexWeight = (\d+),", src)
    mine = [(n, tuple(map(int, w))) for n, *w in rows if n == a["mining_item"]]
    if not mine:
        return [f"S1 {fid}: {a['mining_item']} missing from the Underground mining table"]
    for n, w in mine:
        if len(set(w)) != 1:
            f.append(f"S4 {fid}: {n} weight depends on Trainer ID / National Dex {w}")
        if min(w) <= 0:
            f.append(f"S1 {fid}: {n} can never be mined for some save ({w})")
    # revival mapping
    fos = read("src/scrcmd_fossil.c")
    if not re.search(rf"\.item = {a['revival_item']}, \.species = {a['species']}", fos):
        f.append(f"S1 {fid}: fossil revival table does not map {a['revival_item']} to {a['species']}")
    sh = manifest["shared"]["fossil_revival"]
    sc = Script(sh["file"])
    lab = sc.labels.get(sh["revival_label"], [])
    gi = _index(lab, lambda l: l.startswith("GivePokemon VAR_REVIVED_POKEMON_SPECIES"))
    if gi < 0 or not _has_party_guard(lab[:gi]):
        f.append(f"S2 {fid}: revival has no party-full guard before the give")
    if gi >= 0 and not any(l == "SetVar VAR_REVIVED_POKEMON_SPECIES, 0" for l in lab[gi:]):
        f.append(f"S2 {fid}: revived species is not cleared after the give")
    if "SetVar VAR_0x8004, ITEM_EXPLORER_KIT" not in read(sh["explorer_kit_file"]):
        f.append(f"S3 {fid}: Explorer Kit (Underground access) is no longer given in {sh['explorer_kit_file']}")
    if a["band"] not in PRE_E4_BANDS:
        f.append(f"S3 {fid}: band {a['band']} is not PRE_E4")
    return f


def check_spiritomb(fid: str, a: dict) -> list[str]:
    f = []
    mining = read("src/underground/mining.c")
    if "SystemVars_SetSpiritombCounter" not in mining:
        f.append(f"S4 {fid}: Spiritomb counter has no single-player (Underground mining) source; requires multiplayer talk")
    sc = Script(a["file"])
    txt = sc.text(sc.labels).splitlines()
    bi = _index(txt, lambda l: l.startswith("StartWildBattle SPECIES_SPIRITOMB"))
    seq = "\n".join(txt[bi:]) if bi >= 0 else ""
    if bi < 0:
        f.append(f"S1 {fid}: no Spiritomb battle in {a['file']}")
    elif not re.search(r"CheckDidNotCapture VAR_RESULT\s*\nGoToIfEq VAR_RESULT, TRUE,", seq):
        f.append(f"S2 {fid}: an uncaught Spiritomb consumes the ritual (no retry)")
    elif "ClearSpiritombCounter" in seq and seq.index("ClearSpiritombCounter") < seq.index("CheckDidNotCapture"):
        f.append(f"S2 {fid}: ritual reset happens before the capture check")
    hidden = read("include/data/field/hidden_items.h")
    if "HIDDEN_ITEM_ENTRY(ITEM_ODD_KEYSTONE" not in hidden:
        f.append(f"S1 {fid}: Odd Keystone has no deterministic source")
    if "GetSpiritombCounter" not in sc.text(sc.labels) or "ITEM_ODD_KEYSTONE" not in sc.text(sc.labels):
        f.append(f"S1 {fid}: Hallowed Tower script lost its Keystone/counter logic")
    for tok in FORBIDDEN_SCRIPT_TOKENS:
        if tok in sc.text(sc.labels):
            f.append(f"S4 {fid}: forbidden dependency '{tok}'")
    if a["band"] not in PRE_E4_BANDS:
        f.append(f"S3 {fid}: band {a['band']} is not PRE_E4")
    return f


def check_feebas(fid: str, a: dict) -> list[str]:
    f = []
    src = read("src/overlay006/feebas_fishing.c")
    if re.search(r"RecordMixedRNG_GetRand\s*\(", src):
        f.append(f"S4 {fid}: Feebas tiles still come from the mixed-record RNG (random tiles)")
    m = re.search(r"#define FEEBAS_FIXED_TILE_SEED (0x[0-9A-Fa-f]+)", src)
    if not m:
        return f + [f"S4 {fid}: no fixed Feebas tile seed"]
    if "rand = FEEBAS_FIXED_TILE_SEED;" not in src:
        f.append(f"S4 {fid}: tile selection does not use the fixed seed")
    seed = int(m.group(1), 16)
    enc = json.loads(read("res/field/encounters/encounters_mt_coronet_b1f.json"))["elusive_rod_encounter"]
    tiles = enc["tiles"]
    g = len(tiles) // 4
    bytes_ = [(seed >> 24) & 0xFF, (seed >> 16) & 0xFF, (seed >> 8) & 0xFF, seed & 0xFF]
    coords = [tiles[g * i + bytes_[i] % g] for i in range(4)]
    xz = [[c % 32, c // 32] for c in coords]
    if xz != a["fixed_tiles_xz"]:
        f.append(f"S1 {fid}: fixed tiles {xz} differ from the documented {a['fixed_tiles_xz']}")
    if a["band"] not in PRE_E4_BANDS:
        f.append(f"S3 {fid}: band {a['band']} is not PRE_E4")
    return f


# ---------------------------------------------------------------------------------------------- driver
def verify(manifest: dict, families: list[dict]) -> tuple[list[str], int]:
    """Returns (failures, number of families verified)."""
    fails: list[str] = []
    fam = {f["family_id"]: f for f in families}
    specials = {f["family_id"] for f in families if f.get("availability_status") == "SPECIAL_ACQUISITION"}
    got = set(manifest["acquisitions"])
    if specials != got:
        fails.append(f"S1 special acquisitions manifest covers {sorted(got ^ specials)} inconsistently with the family manifest")

    def band_of(a):
        g = a.get("min_badges", 0)
        b1 = BADGE_BAND.get(g, "P1")
        b2 = a.get("location_band", "E0")
        return b1 if BANDS.index(b1) >= BANDS.index(b2) else b2

    ok = set()
    for fid, a in manifest["acquisitions"].items():
        before = len(fails)
        kind = a["kind"]
        try:
            if kind == "GIFT":
                fails += check_gift(fid, {**a["gift"], "min_badges": a["gift"].get("min_badges", 0),
                                          "location_band": a.get("band", "E0")}, band_of)
            elif kind == "STATIC_ENCOUNTER":
                fails += check_static(fid, a["static"] | {"band": a["band"]})
            elif kind == "FOSSIL":
                fails += check_fossil(fid, a["fossil"] | {"band": a["band"], "species": a["fossil"]["species"]}, manifest)
            elif kind == "SPIRITOMB_RITUAL":
                fails += check_spiritomb(fid, a["ritual"] | {"band": a["band"]})
            elif kind == "FISHING_FIXED_TILES":
                fails += check_feebas(fid, a["fishing"] | {"band": a["band"]})
            else:
                fails.append(f"S1 {fid}: unknown acquisition kind {kind}")
        except FileNotFoundError as e:
            fails.append(f"S1 {fid}: source file {e} missing")
        if a["band"] not in PRE_E4_BANDS:
            fails.append(f"S3 {fid}: band {a['band']} is post-E4")
        if len(fails) == before:
            ok.add(fid)
    if any(a["decision_key"] == "STARTER_DISTRIBUTION" for a in manifest["acquisitions"].values()):
        fails += check_starters(manifest)
    return fails, len(ok)


def load_manifest() -> dict:
    return json.loads((IMPL_DIR / "special_acquisitions.json").read_text())
