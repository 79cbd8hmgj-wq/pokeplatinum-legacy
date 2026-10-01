"""E0 (start-Oreburgh) and E1 (Oreburgh-Eterna) land placements."""


def build(p):
    # ---------------- E0 ----------------
    p.land("route_201", "START", "E0", "ordinary",
           "starly pidgey rattata sentret ledyba caterpie poochyena", "poochyena poochyena poochyena",
           "starly bidoof pidgey rattata")
    p.land("route_202", "START", "E0", "ordinary",
           "wurmple hoothoot shinx kricketot zigzagoon poochyena spinarak", "spinarak spinarak spinarak",
           "wurmple shinx starly kricketot")
    p.land("route_203", "START", "E0", "ordinary",
           "bidoof weedle spearow mankey abra shinx starly", "meditite meditite meditite",
           "bidoof spearow mankey abra")
    p.land("route_204_south", "START", "E0", "ordinary",
           "budew caterpie hoppip nidoran_f nidoran_m pachirisu budew", "taillow taillow taillow",
           "budew hoppip nidoran_f nidoran_m")
    for room in ("lake_verity", "lake_verity_low_water"):
        p.land(room, "START", "E0", "ordinary",
               "psyduck starly mareep pichu meowth bidoof psyduck", "meowth meowth hoothoot",
               "psyduck starly mareep pichu", group="lake_verity")
    p.land("ravaged_path", "ORE", "E0", "connector",
           "zubat psyduck diglett zubat psyduck geodude machop", "zubat zubat zubat",
           "zubat psyduck geodude diglett")
    p.land("oreburgh_gate_1f", "ORE", "E0", "connector",
           "zubat geodude whismur zubat geodude dunsparce whismur", "zubat zubat zubat",
           "zubat geodude zubat whismur")
    p.land("oreburgh_gate_b1f", "ORE", "E0", "ordinary",
           "psyduck zubat onix whismur geodude dunsparce onix", "zubat zubat zubat",
           "zubat psyduck geodude onix")
    p.land("oreburgh_mine_b1f", "ORE", "E0", "ordinary",
           "geodude zubat machop diglett makuhita onix machop", "zubat zubat zubat",
           "geodude zubat machop diglett")
    p.land("oreburgh_mine_b2f", "ORE", "E0", "ordinary",
           "geodude zubat machop onix diglett cubone nosepass", "zubat zubat zubat",
           "geodude zubat onix machop")

    # ---------------- E1 ----------------
    p.land("route_204_north", "FOREST", "E1", "ordinary",
           "budew combee sunkern cherubi skitty ralts glameow", "surskit surskit surskit",
           "budew combee sunkern skitty")
    p.land("route_205_south", "FOREST", "E1", "ordinary",
           "buizel wingull shellos azurill lotad pachirisu surskit", "wooper wooper wooper",
           "buizel shellos wingull lotad")
    p.land("valley_windworks_outside", "FOREST", "E1", "ordinary",
           "buizel wingull shinx seedot stunky drifloon shellos", "pachirisu pachirisu pachirisu",
           "buizel wingull shinx seedot")
    p.land("eterna_forest", "FOREST", "E1", "signature",
           "wurmple buneary paras venonat burmy slakoth shroomish", "munchlax munchlax munchlax",
           "buneary paras wurmple venonat")
    p.land("route_205_north", "FOREST", "E1", "ordinary",
           "oddish bellsprout ekans aipom pineco farfetchd heracross", "teddiursa teddiursa teddiursa",
           "oddish bellsprout ekans pineco")
    p.land("route_207", "CYCLE", "E1", "ordinary",
           "ponyta geodude stunky machop nincada growlithe vulpix", "zubat zubat zubat",
           "ponyta geodude machop stunky")
    p.land("mt_coronet_1f_north_room_1", "CORONET", "E1", "ordinary",
           "geodude zubat machop meditite clefairy nosepass clefairy", "zubat zubat zubat",
           "geodude zubat machop meditite")
    front = ["old_chateau", "old_chateau_corridor", "old_chateau_dining_area", "old_chateau_side_rooms"]
    back = ["old_chateau_back_west_room", "old_chateau_back_middle_west_room", "old_chateau_back_middle_room",
            "old_chateau_back_middle_east_room", "old_chateau_back_east_room"]
    for m in front:
        p.land(m, "FOREST", "E1", "ordinary",
               "gastly shuppet duskull murkrow misdreavus sableye gastly", "gastly gastly misdreavus",
               "gastly shuppet duskull gastly", group="old_chateau_front")
    for m in back:
        p.land(m, "FOREST", "E1", "ordinary",
               "gastly duskull shuppet misdreavus murkrow sableye shuppet", "gastly gastly murkrow",
               "gastly duskull shuppet gastly", group="old_chateau_back")
