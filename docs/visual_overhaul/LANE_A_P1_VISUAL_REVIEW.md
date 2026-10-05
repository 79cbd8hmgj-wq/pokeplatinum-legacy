# Lane A P1 Visual Review (Ranger species renders)

Visual validation only. No donor assets imported, no Platinum resources changed, no usable/alternate/preferred-donor selection made.

## Summary

- P1 candidates reviewed: **19950** (each accounted for exactly once)
- Contact sheets inspected: **369**; species: **282**
- valid_render: **129**
- reject: **19016**
- decode_issue: **0** (none newly assigned; see note)
- needs_review (ambiguous, left open): **805**
- Assets covered incl. exact-duplicate members: **35133**

## Findings

- The overwhelming majority of Ranger frames reconstruct as horizontally sliced / scrambled tile soup, consistent with the still-open reconstruction concern recorded in `DDA1J_RANGER_RENDER_VISUAL_QA.md`. These are `reject`.
- Only these slots visibly reconstruct correctly (`valid_render`):
  - `species:421:p001` slots 1-36: Cherubi body frames render as clean, recognisable sprites
  - `species:422:p001` slots 45-76: Shellos (west sea) frames render as clean, recognisable sprites
  - `species:465:p001` slots 29-80: Tangrowth frames render as clean, recognisable sprites
  - `species:465:p002` slots 1-8: Tangrowth frames render as clean, recognisable sprites
  - `species:490:p001` slots 33-33: small round icon-style frame renders cleanly (Manaphy-egg-like)
- `valid_render` means the pixels look like a correct reconstruction only. It does **not** mean usable/alternate for Platinum; no semantic/use review was done.
- Slots with alpha bbox area <= 256 px are `needs_review`: too little visible art to judge at contact-sheet scale. This is a deterministic metadata rule, not a visual verdict.
- No `decode_issue` was assigned: no decode failure occurred in this pass, and the root cause of the scrambling (stride/geometry vs. other) was not isolated here. Treating the scrambling as a reconstruction defect is a hypothesis for the renderer owner, not a conclusion of this review.

## Limits of this review

- Judgement was made on 96px contact-sheet thumbnails; the raw per-frame PNGs are CI artifacts not present in the repo. The `valid_render` slots are clear at that scale; borderline cases fall to `needs_review`, not `valid_render`.
- Species sheet slot -> `asset_id` mapping comes from `LANE_A_REVIEW_SHEETS.json`.

## Species with any valid_render

421, 422, 465, 490

## Per-species counts

| Dex | valid_render | reject | needs_review |
|---:|---:|---:|---:|
| 004 | 0 | 46 | 26 |
| 005 | 0 | 64 | 0 |
| 006 | 0 | 198 | 0 |
| 007 | 0 | 56 | 0 |
| 008 | 0 | 64 | 0 |
| 009 | 0 | 74 | 0 |
| 013 | 0 | 20 | 12 |
| 015 | 0 | 64 | 0 |
| 019 | 0 | 34 | 6 |
| 020 | 0 | 40 | 4 |
| 021 | 0 | 42 | 2 |
| 022 | 0 | 56 | 4 |
| 025 | 0 | 40 | 4 |
| 026 | 0 | 46 | 2 |
| 027 | 0 | 108 | 12 |
| 028 | 0 | 130 | 4 |
| 037 | 0 | 32 | 8 |
| 038 | 0 | 70 | 0 |
| 039 | 0 | 45 | 4 |
| 040 | 0 | 42 | 6 |
| 041 | 0 | 26 | 10 |
| 042 | 0 | 58 | 2 |
| 043 | 0 | 66 | 10 |
| 044 | 0 | 44 | 8 |
| 045 | 0 | 56 | 0 |
| 056 | 0 | 110 | 2 |
| 057 | 0 | 104 | 0 |
| 058 | 0 | 58 | 2 |
| 059 | 0 | 48 | 0 |
| 063 | 0 | 73 | 2 |
| 065 | 0 | 71 | 2 |
| 066 | 0 | 62 | 2 |
| 067 | 0 | 50 | 0 |
| 068 | 0 | 50 | 0 |
| 071 | 0 | 80 | 0 |
| 073 | 0 | 56 | 0 |
| 074 | 0 | 45 | 0 |
| 075 | 0 | 69 | 0 |
| 076 | 0 | 63 | 0 |
| 077 | 0 | 64 | 0 |
| 078 | 0 | 136 | 0 |
| 081 | 0 | 28 | 0 |
| 082 | 0 | 20 | 4 |
| 084 | 0 | 44 | 0 |
| 085 | 0 | 68 | 0 |
| 089 | 0 | 60 | 0 |
| 092 | 0 | 98 | 2 |
| 093 | 0 | 84 | 7 |
| 094 | 0 | 96 | 1 |
| 096 | 0 | 86 | 2 |
| 097 | 0 | 166 | 0 |
| 100 | 0 | 38 | 6 |
| 101 | 0 | 94 | 8 |
| 109 | 0 | 24 | 2 |
| 110 | 0 | 28 | 0 |
| 111 | 0 | 56 | 0 |
| 112 | 0 | 112 | 0 |
| 115 | 0 | 158 | 0 |
| 116 | 0 | 22 | 10 |
| 117 | 0 | 56 | 0 |
| 120 | 0 | 53 | 1 |
| 121 | 0 | 124 | 0 |
| 122 | 0 | 110 | 0 |
| 123 | 0 | 64 | 0 |
| 124 | 0 | 32 | 0 |
| 125 | 0 | 80 | 0 |
| 126 | 0 | 44 | 0 |
| 127 | 0 | 44 | 0 |
| 128 | 0 | 70 | 0 |
| 133 | 0 | 44 | 12 |
| 134 | 0 | 48 | 0 |
| 135 | 0 | 34 | 2 |
| 136 | 0 | 34 | 4 |
| 138 | 0 | 24 | 18 |
| 139 | 0 | 76 | 0 |
| 142 | 0 | 40 | 0 |
| 147 | 0 | 56 | 0 |
| 148 | 0 | 52 | 0 |
| 167 | 0 | 24 | 12 |
| 168 | 0 | 40 | 0 |
| 169 | 0 | 32 | 0 |
| 170 | 0 | 46 | 2 |
| 171 | 0 | 48 | 0 |
| 172 | 0 | 60 | 4 |
| 179 | 0 | 50 | 10 |
| 180 | 0 | 60 | 0 |
| 181 | 0 | 48 | 12 |
| 182 | 0 | 43 | 9 |
| 185 | 0 | 50 | 0 |
| 190 | 0 | 44 | 2 |
| 193 | 0 | 112 | 1 |
| 196 | 0 | 70 | 0 |
| 197 | 0 | 54 | 0 |
| 198 | 0 | 144 | 0 |
| 200 | 0 | 102 | 3 |
| 203 | 0 | 44 | 0 |
| 204 | 0 | 66 | 8 |
| 205 | 0 | 104 | 0 |
| 207 | 0 | 70 | 2 |
| 211 | 0 | 34 | 6 |
| 212 | 0 | 36 | 0 |
| 215 | 0 | 38 | 2 |
| 218 | 0 | 48 | 0 |
| 219 | 0 | 48 | 0 |
| 220 | 0 | 0 | 2 |
| 221 | 0 | 50 | 2 |
| 222 | 0 | 74 | 2 |
| 225 | 0 | 35 | 0 |
| 226 | 0 | 64 | 0 |
| 227 | 0 | 44 | 0 |
| 228 | 0 | 66 | 0 |
| 229 | 0 | 80 | 0 |
| 230 | 0 | 56 | 0 |
| 236 | 0 | 68 | 2 |
| 239 | 0 | 56 | 6 |
| 240 | 0 | 44 | 2 |
| 241 | 0 | 48 | 0 |
| 246 | 0 | 46 | 2 |
| 247 | 0 | 28 | 0 |
| 248 | 0 | 60 | 0 |
| 251 | 0 | 124 | 0 |
| 252 | 0 | 66 | 4 |
| 253 | 0 | 56 | 6 |
| 254 | 0 | 56 | 0 |
| 255 | 0 | 70 | 6 |
| 256 | 0 | 42 | 10 |
| 257 | 0 | 92 | 0 |
| 258 | 0 | 40 | 0 |
| 259 | 0 | 52 | 0 |
| 260 | 0 | 44 | 0 |
| 273 | 0 | 32 | 10 |
| 274 | 0 | 30 | 0 |
| 275 | 0 | 30 | 0 |
| 276 | 0 | 46 | 10 |
| 277 | 0 | 72 | 0 |
| 278 | 0 | 50 | 2 |
| 279 | 0 | 44 | 0 |
| 280 | 0 | 12 | 30 |
| 281 | 0 | 62 | 11 |
| 282 | 0 | 230 | 1 |
| 287 | 0 | 40 | 0 |
| 291 | 0 | 12 | 0 |
| 296 | 0 | 62 | 2 |
| 297 | 0 | 80 | 0 |
| 299 | 0 | 18 | 12 |
| 302 | 0 | 44 | 0 |
| 303 | 0 | 94 | 0 |
| 304 | 0 | 28 | 8 |
| 305 | 0 | 36 | 8 |
| 306 | 0 | 88 | 0 |
| 311 | 0 | 94 | 2 |
| 312 | 0 | 92 | 4 |
| 315 | 0 | 32 | 0 |
| 319 | 0 | 24 | 0 |
| 320 | 0 | 52 | 0 |
| 322 | 0 | 40 | 0 |
| 323 | 0 | 44 | 0 |
| 324 | 0 | 196 | 0 |
| 330 | 0 | 64 | 0 |
| 331 | 0 | 15 | 11 |
| 332 | 0 | 52 | 0 |
| 334 | 0 | 52 | 0 |
| 344 | 0 | 62 | 0 |
| 353 | 0 | 44 | 11 |
| 354 | 0 | 49 | 3 |
| 355 | 0 | 54 | 15 |
| 356 | 0 | 54 | 0 |
| 359 | 0 | 62 | 1 |
| 361 | 0 | 40 | 0 |
| 362 | 0 | 32 | 0 |
| 363 | 0 | 64 | 0 |
| 364 | 0 | 44 | 0 |
| 365 | 0 | 40 | 0 |
| 367 | 0 | 32 | 0 |
| 368 | 0 | 36 | 0 |
| 371 | 0 | 36 | 18 |
| 372 | 0 | 44 | 0 |
| 373 | 0 | 132 | 0 |
| 377 | 0 | 44 | 0 |
| 378 | 0 | 84 | 0 |
| 379 | 0 | 102 | 0 |
| 387 | 0 | 46 | 2 |
| 388 | 0 | 92 | 0 |
| 389 | 0 | 81 | 0 |
| 390 | 0 | 42 | 14 |
| 391 | 0 | 74 | 2 |
| 392 | 0 | 88 | 0 |
| 393 | 0 | 0 | 6 |
| 394 | 0 | 84 | 0 |
| 395 | 0 | 121 | 0 |
| 396 | 0 | 66 | 0 |
| 397 | 0 | 76 | 0 |
| 398 | 0 | 56 | 0 |
| 399 | 0 | 26 | 8 |
| 400 | 0 | 60 | 0 |
| 401 | 0 | 88 | 10 |
| 402 | 0 | 116 | 0 |
| 403 | 0 | 72 | 2 |
| 404 | 0 | 76 | 0 |
| 405 | 0 | 76 | 0 |
| 406 | 0 | 62 | 22 |
| 407 | 0 | 77 | 1 |
| 408 | 0 | 74 | 6 |
| 409 | 0 | 100 | 0 |
| 410 | 0 | 44 | 12 |
| 411 | 0 | 72 | 0 |
| 412 | 0 | 0 | 12 |
| 413 | 0 | 12 | 0 |
| 414 | 0 | 62 | 0 |
| 415 | 0 | 44 | 2 |
| 416 | 0 | 76 | 0 |
| 417 | 0 | 88 | 6 |
| 418 | 0 | 96 | 6 |
| 419 | 0 | 176 | 0 |
| 420 | 0 | 47 | 9 |
| 421 | 36 | 54 | 6 |
| 422 | 32 | 28 | 16 |
| 423 | 0 | 63 | 0 |
| 424 | 0 | 96 | 0 |
| 425 | 0 | 49 | 0 |
| 426 | 0 | 60 | 0 |
| 427 | 0 | 55 | 1 |
| 428 | 0 | 65 | 0 |
| 429 | 0 | 120 | 0 |
| 430 | 0 | 57 | 0 |
| 431 | 0 | 84 | 0 |
| 432 | 0 | 76 | 0 |
| 433 | 0 | 70 | 30 |
| 434 | 0 | 52 | 4 |
| 435 | 0 | 48 | 0 |
| 436 | 0 | 48 | 0 |
| 437 | 0 | 56 | 0 |
| 438 | 0 | 115 | 2 |
| 439 | 0 | 48 | 22 |
| 440 | 0 | 40 | 4 |
| 441 | 0 | 56 | 0 |
| 442 | 0 | 169 | 11 |
| 443 | 0 | 60 | 6 |
| 444 | 0 | 65 | 0 |
| 445 | 0 | 84 | 0 |
| 446 | 0 | 42 | 10 |
| 447 | 0 | 208 | 0 |
| 448 | 0 | 425 | 0 |
| 449 | 0 | 56 | 0 |
| 450 | 0 | 118 | 2 |
| 451 | 0 | 44 | 8 |
| 452 | 0 | 69 | 0 |
| 453 | 0 | 70 | 2 |
| 454 | 0 | 104 | 0 |
| 455 | 0 | 86 | 0 |
| 456 | 0 | 76 | 10 |
| 457 | 0 | 92 | 0 |
| 458 | 0 | 58 | 6 |
| 459 | 0 | 68 | 0 |
| 460 | 0 | 97 | 0 |
| 461 | 0 | 46 | 6 |
| 462 | 0 | 114 | 0 |
| 463 | 0 | 74 | 0 |
| 464 | 0 | 100 | 0 |
| 465 | 60 | 28 | 0 |
| 466 | 0 | 76 | 0 |
| 467 | 0 | 82 | 0 |
| 468 | 0 | 40 | 0 |
| 469 | 0 | 75 | 0 |
| 470 | 0 | 53 | 0 |
| 471 | 0 | 56 | 4 |
| 472 | 0 | 165 | 0 |
| 473 | 0 | 107 | 0 |
| 474 | 0 | 74 | 0 |
| 475 | 0 | 80 | 0 |
| 476 | 0 | 118 | 0 |
| 477 | 0 | 84 | 0 |
| 478 | 0 | 64 | 2 |
| 483 | 0 | 154 | 0 |
| 484 | 0 | 170 | 0 |
| 485 | 0 | 115 | 0 |
| 486 | 0 | 126 | 0 |
| 488 | 0 | 108 | 0 |
| 489 | 0 | 16 | 0 |
| 490 | 1 | 32 | 0 |
| 491 | 0 | 221 | 0 |
| 492 | 0 | 12 | 44 |
