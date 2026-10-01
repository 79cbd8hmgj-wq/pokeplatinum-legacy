"""M1, M2, L1, L2 and P0 land placements.

Conventions (see wild_plan_lib.Plan.land): core = slots 0,1,2,4,5,6,7; time3 = slot 3 (morning,day,night);
tail = slots 8-11.  "=" keeps the base-commit species in that slot (used to leave USER_DECISION families
such as Chansey exactly as they were).
"""


def build(p):
    # ---------------- M1 ----------------
    p.land("route_206", "CYCLE", "M1", "ordinary",
           "doduo sandshrew phanpy gligar machop shuckle scyther", "geodude geodude geodude",
           "doduo sandshrew phanpy machop")
    p.land("route_208", "HEARTH", "M1", "ordinary",
           "jigglypuff natu snubbull girafarig togepi smeargle ralts", "glameow glameow glameow",
           "jigglypuff natu snubbull girafarig")
    p.land("route_209", "HEARTH", "M1", "ordinary",
           "drowzee mime_jr bonsly spoink lickitung ralts bonsly", "ralts ralts ralts",
           "drowzee = mime_jr =")
    p.land("route_210_south", "HEARTH", "M1", "ordinary",
           "ponyta girafarig miltank stantler tauros kecleon scyther", "ponyta ponyta ponyta",
           "ponyta = girafarig =")
    p.land("route_210_north", "HEARTH", "M1", "ordinary",
           "swablu meditite machop bidoof chingling scyther chingling", "meditite swablu hoothoot",
           "swablu bidoof scyther chingling")
    p.land("route_211_west", "CORONET", "M1", "ordinary",
           "meditite bronzor machop zubat chingling swablu machop", "meditite meditite zubat",
           "meditite bronzor machop zubat", group="route_211")
    p.land("route_211_east", "CORONET", "M1", "ordinary",
           "bronzor meditite machop geodude chingling wynaut swablu", "meditite meditite zubat",
           "bronzor meditite geodude machop", group="route_211")
    p.land("route_212_north", "HEARTH", "M1", "ordinary",
           "budew azurill ralts pinsir volbeat bidoof azurill", "illumise illumise illumise",
           "budew azurill ralts bidoof")
    p.land("route_212_south", "MARSH", "M1", "ordinary",
           "croagunk shellos buizel gulpin skorupi wooper shellos", "grimer grimer grimer",
           "croagunk shellos buizel wooper")
    p.land("route_213", "MARSH", "M1", "ordinary",
           "chatot buizel shellos tangela wingull tangela yanma", "yanma yanma yanma",
           "chatot buizel tangela wingull")
    p.land("route_214", "DRY", "M1", "ordinary",
           "houndour rhyhorn spinda cacnea electrike baltoy numel", "numel numel numel",
           "houndour rhyhorn spinda cacnea")
    p.land("route_215", "HEARTH", "M1", "ordinary",
           "abra azurill drowzee zangoose seviper spoink abra", "azurill azurill azurill",
           "abra azurill drowzee spoink")
    p.land("wayward_cave_1f", "CYCLE", "M1", "ordinary",
           "bronzor geodude gligar onix zubat mawile sableye", "zubat zubat zubat",
           "geodude onix zubat bronzor", group="wayward_cave")
    p.land("wayward_cave_b1f", "CYCLE", "M1", "ordinary",
           "bronzor geodude gligar onix zubat gible trapinch", "geodude geodude geodude",
           "bronzor geodude onix gligar", group="wayward_cave")
    p.land("mt_coronet_1f_south", "CORONET", "M1", "ordinary",
           "bronzor swablu rhyhorn chingling wynaut lunatone solrock", "zubat zubat zubat",
           "bronzor swablu rhyhorn zubat")
    for m in ("maniac_tunnel", "ruin_maniac_cave_long", "ruin_maniac_cave_short"):
        p.land(m, "DRY", "M1", "connector",
               "geodude hippopotas onix rhyhorn geodude geodude hippopotas", "baltoy baltoy baltoy",
               "geodude hippopotas onix rhyhorn", group="maniac_caves")
    marsh_a = ["great_marsh_1", "great_marsh_2"]
    marsh_b = ["great_marsh_3", "great_marsh_4"]
    marsh_c = ["great_marsh_5", "great_marsh_6"]
    for m in marsh_a:
        p.land(m, "MARSH", "M1", "signature",
               "croagunk skorupi gulpin yanma carnivine gulpin skorupi", "tangela tangela volbeat",
               "croagunk skorupi gulpin yanma", group="great_marsh_a")
    for m in marsh_b:
        p.land(m, "MARSH", "M1", "signature",
               "croagunk grimer tangela exeggcute kangaskhan paras croagunk", "slowpoke slowpoke illumise",
               "croagunk grimer tangela exeggcute", group="great_marsh_b")
    for m in marsh_c:
        p.land(m, "MARSH", "M1", "signature",
               "croagunk slowpoke volbeat illumise tropius kecleon shroomish", "yanma yanma yanma",
               "croagunk slowpoke volbeat tropius", group="great_marsh_c")
    p.land("trophy_garden", "HEARTH", "M1", "signature",
           "meowth azurill pichu ditto plusle pikachu pichu", "minun minun minun",
           "meowth azurill pichu pikachu")
    p.land("fuego_ironworks_outside", "IRON", "M1", "signature",
           "magnemite koffing voltorb slugma magby torkoal numel", "elekid elekid elekid",
           "magnemite koffing voltorb slugma")

    # ---------------- M2 ----------------
    p.land("valor_lakefront", "MARSH", "M1", "ordinary",
           "girafarig houndour kangaskhan tropius exeggcute starly carnivine", "starly starly houndour",
           "girafarig houndour starly kangaskhan")
    p.land("route_218", "COAST", "M2", "ordinary",
           "shellos buizel chatot mime_jr ditto skarmory wingull", "chatot chatot shellos",
           "shellos buizel chatot wingull")
    p.land("route_221", "COAST", "M2", "ordinary",
           "buizel girafarig budew bonsly farfetchd wingull shellos", "budew budew buizel",
           "buizel girafarig budew bonsly")
    p.land("iron_island_1f", "IRON", "M2", "connector",
           "geodude aron zubat onix geodude mawile aron", "zubat zubat zubat",
           "geodude aron zubat onix", group="iron_island_caves")
    for m in ("iron_island_b1f_left_room", "iron_island_b1f_right_room"):
        p.land(m, "IRON", "M2", "connector",
               "aron geodude onix zubat mawile geodude aron", "zubat zubat zubat",
               "aron geodude onix zubat", group="iron_island_caves")
    for m in ("iron_island_b2f_left_room", "iron_island_b2f_right_room"):
        p.land(m, "IRON", "M2", "connector",
               "aron onix geodude zubat mawile aron onix", "zubat zubat zubat",
               "aron onix geodude zubat", group="iron_island_caves")
    p.land("iron_island_b3f", "IRON", "M2", "ordinary",
           "aron onix geodude zubat mawile beldum beldum", "zubat zubat zubat",
           "aron onix geodude zubat", group="iron_island_caves")

    # ---------------- L1 ----------------
    p.land("route_216", "SNOW", "L1", "ordinary",
           "snover sneasel swinub meditite snorunt delibird smoochum", "meditite meditite meditite",
           "snover sneasel swinub snorunt")
    p.land("route_217", "SNOW", "L1", "ordinary",
           "snover swinub sneasel snorunt spheal delibird smoochum", "sneasel sneasel snorunt",
           "snover swinub sneasel snorunt")
    p.land("acuity_lakefront", "SNOW", "L1", "ordinary",
           "snover swinub sneasel snorunt delibird smoochum absol", "snover snover snorunt",
           "snover swinub sneasel snorunt")
    p.land("lake_acuity", "SNOW", "L1", "ordinary",
           "snover psyduck sneasel snorunt spheal smoochum snover", "psyduck psyduck snorunt",
           "snover psyduck sneasel snorunt")
    for m in ("mt_coronet_outside_north", "mt_coronet_outside_south"):
        p.land(m, "CORONET", "L1", "ordinary",
               "snover meditite machop swablu chingling absol nosepass", "meditite meditite zubat",
               "snover meditite absol swablu", group="coronet_outside")
    p.land("mt_coronet_1f_north_room_2", "CORONET", "L1", "ordinary",
           "bronzor geodude meditite machop clefairy nosepass chingling", "zubat zubat zubat",
           "bronzor geodude machop meditite", group="coronet_lower_deep")
    # B1F is reached through the Waterfall route; HM07 comes from Sunyshore City (post badge 8), so band P0.
    p.land("mt_coronet_b1f", "CORONET", "P0", "ordinary",
           "bronzor geodude meditite machop clefairy nosepass chingling", "zubat zubat zubat",
           "bronzor geodude machop meditite", group="coronet_lower_deep")
    p.land("mt_coronet_1f_tunnel_room", "CORONET", "L1", "ordinary",
           "bronzor geodude meditite machop clefairy nosepass chingling", "zubat zubat zubat",
           "bronzor geodude machop meditite", group="coronet_lower_deep")
    p.land("mt_coronet_2f", "CORONET", "L1", "ordinary",
           "bronzor geodude meditite machop larvitar nosepass chingling", "zubat zubat zubat",
           "bronzor geodude machop meditite", group="coronet_upper")
    p.land("mt_coronet_3f", "CORONET", "L1", "ordinary",
           "bronzor geodude meditite machop larvitar clefairy nosepass", "zubat zubat zubat",
           "bronzor geodude machop meditite", group="coronet_upper")
    p.land("mt_coronet_4f_rooms_1_and_2", "CORONET", "L1", "ordinary",
           "bronzor geodude meditite machop larvitar nosepass chingling", "zubat zubat zubat",
           "bronzor geodude machop meditite", group="coronet_upper")
    p.land("mt_coronet_4f_room_3", "CORONET", "L1", "ordinary",
           "bronzor geodude meditite larvitar clefairy chingling nosepass", "zubat zubat zubat",
           "bronzor geodude meditite nosepass", group="coronet_upper")
    p.land("mt_coronet_5f", "DEEP", "L1", "ordinary",
           "bronzor geodude meditite machop larvitar bagon nosepass", "zubat zubat zubat",
           "bronzor geodude machop meditite", group="coronet_deep")
    p.land("mt_coronet_6f", "DEEP", "L1", "ordinary",
           "bronzor geodude meditite machop bagon larvitar chingling", "zubat zubat zubat",
           "bronzor geodude machop meditite", group="coronet_deep")

    # ---------------- L2 ----------------
    p.land("route_222", "EAST", "L2", "ordinary",
           "shinx elekid magnemite wingull chatot skitty buizel", "chatot chatot buizel",
           "shinx elekid magnemite wingull")
    p.land("lake_valor", "EAST", "L2", "ordinary",
           "psyduck bidoof starly kricketot girafarig houndour starly", "starly starly houndour",
           "psyduck bidoof starly girafarig")

    # ---------------- P0 ----------------
    p.land("victory_road_1f", "DEEP", "P0", "ordinary",
           "geodude rhyhorn onix magnemite zubat gible rhyhorn", "geodude onix zubat",
           "geodude rhyhorn onix gible", group="victory_road")
    for m in ("victory_road_1f_room_1", "victory_road_1f_room_3"):
        p.land(m, "DEEP", "P0", "ordinary",
               "geodude buizel onix zubat gible aron buizel", "geodude onix zubat",
               "geodude buizel onix gible", group="victory_road")
    p.land("victory_road_1f_room_2", "DEEP", "P0", "ordinary",
           "buizel azurill geodude zubat seel gible azurill", "geodude azurill zubat",
           "buizel azurill seel gible", group="victory_road")
    p.land("victory_road_2f", "DEEP", "P0", "ordinary",
           "magnemite onix geodude zubat gible aron onix", "geodude onix zubat",
           "magnemite onix geodude gible", group="victory_road")
    p.land("victory_road_b1f", "DEEP", "P0", "ordinary",
           "buizel azurill geodude onix gible zubat aron", "geodude azurill zubat",
           "buizel azurill onix gible", group="victory_road")
