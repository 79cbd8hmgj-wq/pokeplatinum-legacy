tiles = files(
    'page.png',
    'panel.png',
    'art_dusk.png',
    'art_heal.png',
    'art_quick.png',
    'art_dive.png',
)

palettes = files(
    'page.png',
    'panel.png',
    'panel_active.png',
    'art_dusk.png',
    'art_heal.png',
    'art_quick.png',
    'art_dive.png',
)

still_card_ncgrs = ncgr_gen.process(tiles,
    extra_args: [
        '-sopc',
        '-version101',
    ]
)

still_card_nclrs = nclr_gen.process(palettes,
    extra_args: [
        '-bitdepth', '4',
    ]
)

still_card_narc = custom_target('still_card.narc',
    output: [
        'still_card.narc',
        'still_card.naix',
    ],
    input: [
        still_card_ncgrs,
        still_card_nclrs,
    ],
    command: [
        nitroarc_exe,
        '--create',
        '--index',
        '--files-from', files('still_card.order'),
        '--file', '@OUTPUT0@',
        '@PRIVATE_DIR@',
    ],
)

nitrofs_files += still_card_narc
naix_headers += still_card_narc[1]
