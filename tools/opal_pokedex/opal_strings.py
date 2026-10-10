#!/usr/bin/env python3
"""Authoritative UI strings for the Opal Pokedex information pages.

`sync()` appends these (idempotently) to res/text/pokedex.json after the
existing messages so existing `pl_msg_pokedex_*` indices never move.
Placeholders use the game's template syntax: {STRVAR_1 <slot>, 0, 0}.

Keep every line <= ~34 characters (DS system font, 232 px content width).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gameplay_sources as gs  # noqa: E402

PREFIX = "pl_msg_pokedex_opal_"


def V(slot):
    return "{STRVAR_1 %d, 0, 0}" % slot


# id suffix -> en_US (str, or list of lines for multi-line messages)
STRINGS = [
    # --- tab / page names (sub-screen tabs are <= 8 chars) --------------------
    ("tab_overview", "Overview"),
    ("tab_abilities", "Abilities"),
    ("tab_evolution", "Evolve"),
    ("tab_learnset", "Moves"),
    ("tab_tmhm", "TM/HM"),
    ("tab_stats", "Stats"),
    ("tab_locations", "Where"),
    ("tab_forms", "Forms"),
    ("title_overview", "OVERVIEW"),
    ("title_abilities", "ABILITIES"),
    ("title_evolution", "EVOLUTION"),
    ("title_learnset", "LEVEL-UP MOVES"),
    ("title_tmhm", "TM / HM COMPATIBILITY"),
    ("title_stats", "BASE STATS"),
    ("title_locations", "LOCATIONS"),
    ("title_forms", "FORMS"),
    ("entry_button", "OPAL DATA"),
    ("arrow_up", "↑"),
    ("arrow_down", "↓"),
    ("btn_prev", "← Prev"),
    ("btn_next", "Next →"),
    ("btn_up", "↑ Up"),
    ("btn_down", "↓ Down"),
    ("sub_hint", "L/R: Pokémon  Up/Down: scroll"),
    # --- shared labels ------------------------------------------------------------
    ("dex_no", "No. " + V(0)),
    ("name_line", V(0) + "  " + V(1)),
    ("back", "Back"),
    ("page_of", V(0) + "/" + V(1)),
    ("unknown", "???"),
    ("locked_seen", ["Catch this Pokémon to", "unlock its full Opal data."]),
    ("locked_unseen", ["No data recorded yet."]),
    ("scroll_hint", "Up/Down: scroll"),
    ("none", "None"),
    ("slot0", V(0)),
    # --- overview ------------------------------------------------------------------
    ("ov_types", "Type"),
    ("ov_category", "Kind"),
    ("ov_bst", "Base stat total"),
    ("ov_ability", "Ability"),
    ("ov_hint_pages", "Tabs show Opal’s changes."),
    ("ov_form_count", V(0) + " forms"),
    ("ov_one_form", "1 form"),
    # --- abilities -----------------------------------------------------------------
    ("ab_slot1", "Ability 1"),
    ("ab_slot2", "Ability 2"),
    ("ab_single", "Ability"),
    ("ab_note", ["A Pokémon has one of these.", "Check its Summary for its own."]),
    ("ab_desc_header", "Effect"),
    # --- stats ---------------------------------------------------------------------
    ("st_note", "BASE stats (species), not your own"),
    ("st_hp", "HP"),
    ("st_atk", "Attack"),
    ("st_def", "Defense"),
    ("st_spa", "Sp. Atk"),
    ("st_spd", "Sp. Def"),
    ("st_spe", "Speed"),
    ("st_total", "Total"),
    # --- evolution -----------------------------------------------------------------
    ("ev_none", "Does not evolve."),
    ("ev_from", "From " + V(0)),
    ("ev_into", "Into " + V(0)),
    ("ev_family", "Evolution family"),
    ("ev_m_level", "Lv. " + V(0)),
    ("ev_m_level_day", "Lv. " + V(0) + ", daytime"),
    ("ev_m_level_night", "Lv. " + V(0) + ", nighttime"),
    ("ev_m_happy", "High friendship"),
    ("ev_m_happy_day", "High friendship, day"),
    ("ev_m_happy_night", "High friendship, night"),
    ("ev_m_item", "Use " + V(0)),
    ("ev_m_item_male", "Use " + V(0) + " (male)"),
    ("ev_m_item_female", "Use " + V(0) + " (female)"),
    ("ev_m_atk_gt_def", "Lv. " + V(0) + ", Atk above Def"),
    ("ev_m_atk_eq_def", "Lv. " + V(0) + ", Atk = Def"),
    ("ev_m_atk_lt_def", "Lv. " + V(0) + ", Atk below Def"),
    ("ev_m_spa_gt_atk", "Lv. " + V(0) + ", SpA above Atk"),
    ("ev_m_spa_ge_atk", "Lv. " + V(0) + ", SpA at least Atk"),
    ("ev_m_atk_gt_spa", "Lv. " + V(0) + ", Atk above SpA"),
    ("ev_m_spd_gt_def", "Lv. " + V(0) + ", SpD above Def"),
    ("ev_m_pid_low", "Lv. " + V(0) + ", personality A"),
    ("ev_m_pid_high", "Lv. " + V(0) + ", personality B"),
    ("ev_m_ninjask", "Lv. " + V(0)),
    ("ev_m_shedinja", "Lv. " + V(0) + ", spare slot + ball"),
    ("ev_m_beauty", "Beauty " + V(0) + "+"),
    ("ev_m_held_day", "Level up holding " + V(0) + " (day)"),
    ("ev_m_held_night", "Level up holding " + V(0) + " (night)"),
    ("ev_m_know_move", "Level up knowing " + V(0)),
    ("ev_m_party", "Level up with " + V(0) + " in party"),
    ("ev_m_level_male", "Lv. " + V(0) + ", male"),
    ("ev_m_level_female", "Lv. " + V(0) + ", female"),
    ("ev_m_magnetic", "Level up in a magnetic field"),
    ("ev_m_moss", "Level up near the moss rock"),
    ("ev_m_ice", "Level up near the ice rock"),
    ("ev_m_special", "Special condition"),
    # --- learnset ------------------------------------------------------------------
    ("ls_h_lv", "Lv"),
    ("ls_h_move", "Move"),
    ("ls_h_type", "Type"),
    ("ls_h_pow", "Pow"),
    ("ls_h_acc", "Acc"),
    ("ls_h_pp", "PP"),
    ("ls_class_phys", "Phys"),
    ("ls_class_spec", "Spec"),
    ("ls_class_stat", "Stat"),
    ("ls_empty", "No level-up moves."),
    ("ls_start", "Lv.1"),
    ("ls_evolve", "Evo"),
    # --- tm/hm ---------------------------------------------------------------------
    ("tm_header", "Learns by machine:"),
    ("tm_tm", "TM" + V(0)),
    ("tm_hm", "HM" + V(0)),
    ("tm_none", "Cannot learn any TM or HM."),
    ("tm_count", V(0) + " of " + V(1) + " machines"),
    # --- locations -----------------------------------------------------------------
    ("lo_land", "Grass"),
    ("lo_surf", "Surf"),
    ("lo_old_rod", "Old Rod"),
    ("lo_good_rod", "Good Rod"),
    ("lo_super_rod", "Super Rod"),
    ("lo_radar", "Poké Radar"),
    ("lo_swarm", "Swarm"),
    ("lo_static", "Static"),
    ("lo_gift", "Gift"),
    ("lo_fossil", "Fossil"),
    ("lo_ritual", "Ritual"),
    ("lo_roamer", "Roaming"),
    ("lo_breeding", "Breeding"),
    ("lo_legacy", "Rare habitat"),
    ("lo_event", "Event"),
    ("lo_fixed", "Fixed tiles"),
    ("lo_morning", "Morn"),
    ("lo_day", "Day"),
    ("lo_night", "Night"),
    ("lo_hof", "After Hall of Fame"),
    ("lo_once", "One-time"),
    ("lo_badges", V(0) + "+ badges"),
    ("lo_pct", V(0) + "%"),
    ("lo_level", "Lv." + V(0)),
    ("lo_level_range", "Lv." + V(0) + "-" + V(1)),
    ("lo_none", ["No source recorded", "for this Pokémon."]),
    ("lo_note", "Odds = slot chance per encounter."),
    ("lo_time_legend", "M=Morning  D=Day  N=Night"),
    ("lo_unnamed_where", "Special location"),
    # curated "where" strings for acquisitions without a single map header
    ("where_fossil", "Underground fossils (Oreburgh)"),
    ("where_spiritomb", "Hallowed Tower ritual (Odd Keystone)"),
    ("where_roamer", "Roams Sinnoh once awakened"),
    ("where_phione", "Breed Manaphy with Ditto"),
    ("where_feebas", "Fixed fishing tiles"),
    # --- forms ---------------------------------------------------------------------
    ("fo_none", ["This Pokémon has no", "alternate forms."]),
    ("fo_header", "Form differences"),
    ("fo_base", "Base"),
    ("fo_types", "Type"),
    ("fo_abilities", "Ability"),
    ("fo_stats", "Stats"),
    ("fo_note", "Shown from live species data."),
    ("fo_cosmetic", ["Alternate forms share this", "species’ data."]),
    ("fo_changed_note", "Gold = differs from base form"),
    ("fo_deoxys_0", "Normal"),
    ("fo_deoxys_1", "Attack"),
    ("fo_deoxys_2", "Defense"),
    ("fo_deoxys_3", "Speed"),
    ("fo_wormadam_0", "Plant Cloak"),
    ("fo_wormadam_1", "Sandy Cloak"),
    ("fo_wormadam_2", "Trash Cloak"),
    ("fo_giratina_0", "Altered"),
    ("fo_giratina_1", "Origin"),
    ("fo_shaymin_0", "Land"),
    ("fo_shaymin_1", "Sky"),
    ("fo_rotom_0", "Rotom"),
    ("fo_rotom_1", "Heat"),
    ("fo_rotom_2", "Wash"),
    ("fo_rotom_3", "Frost"),
    ("fo_rotom_4", "Fan"),
    ("fo_rotom_5", "Mow"),
    ("fo_stat_line1", "HP " + V(0) + "  Atk " + V(1) + "  Def " + V(2)),
    ("fo_stat_line2", "SpA " + V(0) + "  SpD " + V(1) + "  Spe " + V(2)),
]


def _charmap():
    import re
    chars = set()
    with open(gs.p("tools", "msgenc", "charmap.txt"), encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^([0-9A-Fa-f]{4})=(.*)$", line.rstrip("\n"))
            if m:
                chars.add(m.group(2))
    return chars


def validate():
    """Every character must exist in the game charmap (msgenc rejects the rest)."""
    import re
    chars = _charmap()
    bad = []
    for suffix, text in STRINGS:
        lines = text if isinstance(text, list) else [text]
        for line in lines:
            plain = re.sub(r"\{STRVAR_\d+ [^}]*\}", "", line)
            for c in plain:
                if c not in chars:
                    bad.append((suffix, c))
    if bad:
        raise SystemExit("unsupported characters in Opal strings: %r" % bad)


def message_entries():
    out = []
    for suffix, text in STRINGS:
        entry = {"id": PREFIX + suffix}
        entry["en_US"] = text
        out.append(entry)
    return out


def sync(check=False):
    validate()
    path = gs.p("res", "text", "pokedex.json")
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    msgs = doc["messages"]
    base = [m for m in msgs if not m["id"].startswith(PREFIX)]
    new = base + message_entries()
    if check:
        return msgs == new
    doc["messages"] = new
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return True


if __name__ == "__main__":
    check = "--check" in sys.argv
    ok = sync(check=check)
    if check and not ok:
        print("STALE: res/text/pokedex.json opal strings")
        sys.exit(1)
    print("ok", len(STRINGS), "strings")
