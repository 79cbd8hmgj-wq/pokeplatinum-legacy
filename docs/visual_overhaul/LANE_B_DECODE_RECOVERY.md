# Lane B Decode Recovery Audit

Recovery-route audit for every Lane B decode_issue record.
No curation states or Platinum resources are modified.

- Decode issues audited: **7183**

## Recovery routes

| Route | Assets |
|---|---:|
| container_unpack_then_decode | 1350 |
| format_context_unknown | 9 |
| nitro_2d_decode | 719 |
| pmd_format_decode | 557 |
| ranger_embedded_decode | 4472 |
| source_png_equivalent | 76 |

## By source

| Source | Route | Assets |
|---|---|---:|
| diamond | format_context_unknown | 6 |
| diamond | nitro_2d_decode | 717 |
| hgss | container_unpack_then_decode | 5 |
| hgss | format_context_unknown | 3 |
| hgss | nitro_2d_decode | 2 |
| hgss | source_png_equivalent | 76 |
| pmd_sky | pmd_format_decode | 557 |
| ranger2 | container_unpack_then_decode | 1345 |
| ranger2 | ranger_embedded_decode | 4472 |

## Recovery policy

- source_png_equivalent: verify equivalence and inherit/merge visual curation evidence.
- nitro_2d_decode: pair NCGR/NCLR/NCER/NANR and render deterministically.
- container_unpack_then_decode: unpack NARC/package first, then classify internal resources.
- pmd_format_decode: use or add PMD WAN/WTE/WTU/WAT/WBA decoder.
- ranger_embedded_decode: use Ranger package/resource reconstruction tooling.
- unknown routes remain decode_issue until format/context is resolved.
