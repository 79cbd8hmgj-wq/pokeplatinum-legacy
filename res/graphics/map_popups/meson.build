map_popup_files = files(
    'city_popup.png',
    'town_popup.png',
    'route_popup.png',
    'cave_popup.png',
    'forest_popup.png',
    'water_popup.png',
    'park_popup.png',
    'lake_popup.png',
    'indoors_popup.png',
)

map_popup_ncgrs = ncgr_gen.process(
    map_popup_files,
    extra_args: [
        '-version101',
        '-sopc',
        '-convertTo4Bpp',
        '-width', '32',
        '-num_tiles', '96',
    ]
)

# IO-PREVIEW area cards: NCGR only. They share the forest popup palette (BG palette slot 7),
# so no NCLR is generated or loaded for them. Members 18-20 of the NARC (see map_popup.order).
map_popup_card_files = files(
    'card_eterna_forest_day.png',
    'card_eterna_forest_dusk.png',
    'card_eterna_forest_night.png',
)

map_popup_card_ncgrs = ncgr_gen.process(
    map_popup_card_files,
    extra_args: [
        '-version101',
        '-sopc',
        '-convertTo4Bpp',
        '-num_tiles', '65',
    ]
)

map_popup_nclrs = nclr_gen.process(
    map_popup_files,
    extra_args: [
        '-bitdepth', '4'
    ]
)

map_popup_narc = custom_target('map_popup.narc',
    output: [
        'map_popup.narc',
    ],
    input: [
        map_popup_ncgrs,
        map_popup_nclrs,
        map_popup_card_ncgrs,
    ],
    command: [
        nitroarc_exe,
        '--create',
        '--files-from', files('map_popup.order'),
        '--file', '@OUTPUT0@',
        '@PRIVATE_DIR@',
    ],
)

nitrofs_files += map_popup_narc
