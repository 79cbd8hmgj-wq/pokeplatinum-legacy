# Lane A Visual Review Candidate Set

This pass collapses exact pixel duplicates after the full render-integrity audit.
It does not change donor review status or select a preferred donor.

## Summary

- Audited Lane A assets: **40559**
- Verified nonblank assets: **39722**
- Unique visual candidates after exact deduplication: **23115**
- Redundant exact-duplicate assets removed from direct visual review: **16607**
- Exact duplicate sets: **10133**
- Decode-error assets isolated: **164**
- Blank assets isolated: **673**
- Species represented among candidate records: **282**

## Candidate representatives by source

| Source | Unique visual representatives |
|---|---:|
| diamond | 1183 |
| hgss | 1982 |
| ranger2 | 19950 |

## Review boundary

- A representative is only a bookkeeping stand-in for identical pixels.
- Every duplicate member remains recorded in the JSON.
- Exact duplicates are not automatically marked alternate or reject.
- Decode errors remain separate until format-specific handling is added.
- Blank renders remain separate evidence and are not promoted.
- No Platinum resource is modified by this pass.
