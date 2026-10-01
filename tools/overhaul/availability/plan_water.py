"""Surf / Old Rod / Good Rod placements ('-' keeps the base species in that slot).

Slot rates: Surf and Old Rod 60/30/5/4/1; Good Rod 40/40/15/4/1.  Slots 3 and 4 are below the 5% floor and
are never relied on.  Super Rod is acquired only at the Battle Frontier (post Hall of Fame), so Super Rod
tables are left to P1 and no PRE_E4 requirement relies on them.
"""

E0_BASE = "magikarp magikarp magikarp magikarp magikarp"


def build(p):
    w = p.water
    # --- E1 band maps -------------------------------------------------------------------------
    w("route_204_north", "FOREST", "E1", old_rod="magikarp poliwag goldeen - -",
      good_rod="goldeen poliwag - - -")
    w("route_205_north", "FOREST", "E1", old_rod="magikarp barboach poliwag - -",
      good_rod="barboach goldeen - - -", surf="psyduck psyduck slowpoke - -")
    w("route_205_south", "FOREST", "E1", old_rod="magikarp poliwag goldeen - -")
    w("valley_windworks_outside", "FOREST", "E1", old_rod="magikarp goldeen poliwag - -")
    w("eterna_city", "FOREST", "E1", old_rod="magikarp barboach goldeen - -",
      good_rod="barboach goldeen - - -", surf="psyduck psyduck slowpoke - -")
    # --- M1 -----------------------------------------------------------------------------------
    w("route_208", "HEARTH", "M1", old_rod="magikarp goldeen poliwag - -", good_rod="goldeen barboach - - -",
      surf="psyduck psyduck slowpoke - -")
    w("route_209", "HEARTH", "M1", old_rod="magikarp poliwag goldeen - -", good_rod="goldeen poliwag - - -",
      surf="psyduck slowpoke - - -")
    w("route_210_north", "HEARTH", "M1", old_rod="magikarp barboach poliwag - -", good_rod="barboach goldeen - - -",
      surf="psyduck psyduck slowpoke - -")
    w("route_212_north", "HEARTH", "M1", old_rod="magikarp goldeen poliwag - -", good_rod="goldeen barboach corphish - -",
      surf="psyduck psyduck slowpoke - -")
    w("route_212_south", "MARSH", "M1", old_rod="magikarp barboach krabby - -")
    w("route_213", "MARSH", "M1", old_rod="magikarp krabby poliwag - -")
    w("route_214", "DRY", "M1", old_rod="magikarp poliwag barboach - -", good_rod="goldeen barboach - - -",
      surf="psyduck psyduck slowpoke - -")
    for m in ("great_marsh_1", "great_marsh_2", "great_marsh_3", "great_marsh_4", "great_marsh_5", "great_marsh_6"):
        w(m, "MARSH", "M1", old_rod="magikarp barboach goldeen - -", good_rod="carvanha corphish barboach - -")
    w("pastoria_city", "COAST", "M1", old_rod="magikarp krabby barboach - -", good_rod="remoraid carvanha krabby - -")
    w("celestic_town", "CORONET", "M1", old_rod="magikarp goldeen barboach - -",
      surf="psyduck psyduck slowpoke - -")
    # --- M2 -----------------------------------------------------------------------------------
    w("canalave_city", "COAST", "M2", old_rod="magikarp krabby shellder - -", good_rod="horsea staryu clamperl - -")
    w("iron_island", "IRON", "M2", surf="wingull tentacool lapras - -", good_rod="chinchou wailmer qwilfish - -")
    w("route_218", "COAST", "M2", good_rod="shellder finneon luvdisc - -")
    w("route_219", "COAST", "M2", surf="tentacool mantyke seel - -", good_rod="luvdisc shellder corsola - -")
    w("route_220", "COAST", "M2", surf="tentacool mantyke wingull - -", good_rod="wailmer chinchou staryu - -")
    w("route_221", "COAST", "M2", surf="tentacool mantyke wingull - -", good_rod="horsea qwilfish corsola - -")
    # --- L1 / L2 ------------------------------------------------------------------------------
    w("lake_acuity", "SNOW", "L1", surf="psyduck spheal psyduck - -", good_rod="goldeen seel spheal - -")
    w("mt_coronet_4f_rooms_1_and_2", "CORONET", "L1", good_rod="barboach magikarp dratini - -")
    w("sunyshore_city", "EAST", "L2", good_rod="remoraid luvdisc relicanth - -")
    w("route_223", "EAST", "L2", surf="tentacool mantyke mantyke - -", good_rod="remoraid luvdisc clamperl - -")
