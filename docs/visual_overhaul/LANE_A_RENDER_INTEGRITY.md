# Lane A Render Integrity Audit

Technical evidence pass over every A_render_ready record.

Boundary: this audit does not change donor review_status. A decodable,
nonblank PNG is not automatically a visually confirmed valid_render or usable asset.

## Summary

- Lane A assets: **40559**
- Exact visual duplicate groups: **10717**
- Assets participating in exact duplicate groups: **29565**

### Technical states

| State | Assets |
|---|---:|
| blank | 176 |
| decode_error | 164 |
| verified_nonblank | 40219 |

### By source

| Source | Assets | States |
|---|---:|---|
| diamond | 1949 | verified_nonblank=1949 |
| hgss | 2804 | decode_error=164, verified_nonblank=2640 |
| ranger2 | 35806 | blank=176, verified_nonblank=35630 |

## Interpretation

- verified_nonblank: file materialized, decoded successfully, and has visible pixels.
- blank: file decoded but has no visible pixels.
- decode_error: file exists but Pillow could not decode it as an image.
- missing: queue record could not be materialized from the checked-out donor/render roots.
- Exact duplicate grouping is evidence only; it does not choose preferred/alternate assets.
