# Contract: Shape Style Parameters (HTTP)

This contract applies to all three QR routes. The parameters are **optional**, and when they are
absent every existing response is byte-identical to the pre-feature output (FR-011,
Principle II).

| Route | Where params go | Response shape change |
|---|---|---|
| `POST /api/generate` | form fields | none (same `{image, mime}` JSON envelope) |
| `POST /api/generate/download` | form fields | none (same attachment, same filenames) |
| `GET /api/qr` | query string | none (raw bytes, `image/png` or `image/svg+xml`, `Cache-Control: public, max-age=86400, immutable`) |

## Parameters

| Key | Allowed values | Default |
|---|---|---|
| `dot_shape` | `square` · `rounded` · `extra_rounded` · `dots` · `classy` · `classy_rounded` · `horizontal_bars` · `vertical_bars` · `gapped_square` | `square` |
| `eye_border` | `square` · `rounded` · `circle` · `teardrop` · `leaf` · `leaf_circle` · `square_circle` | `square` |
| `eye_center` | `square` · `rounded` · `circle` · `teardrop` · `leaf` | `square` |

## Rules

1. **Exact match, case-sensitive.** Any unknown, misspelled, empty, or differently-cased value
   falls back to `square` for that parameter only. The request still succeeds, with 200 and no
   error field (FR-012).
2. **Independent.** Any combination is valid (315 total, FR-004).
3. **QR only.** For `format` values other than `qrcode` on the POST routes, the shape params are
   ignored, and the output is byte-identical to the same request without them.
4. **Composition with existing params.**
   - PNG honours `size`, `margin`, `fg_color`, `bg_color`, `ec_level` (FR-009).
   - SVG honours `size`, `margin`, `ec_level`, and stays vector: `<path>` elements, no embedded
     raster (FR-008).
   - SVG color behavior is unchanged from today: black shapes, no background.
5. **All-default equals legacy.** `dot_shape=square&eye_border=square&eye_center=square` returns
   exactly the same bytes as omitting all three.
6. **No new error cases.** The only 4xx is still missing `data` (or no content, on POST).
   Shape values can never cause a 4xx or a 5xx.

## Examples

```text
GET /api/qr?data=https://example.com/abc&dot_shape=dots&eye_border=circle&eye_center=circle
→ 200 image/png, Cache-Control: public, max-age=86400, immutable

GET /api/qr?data=https://example.com/abc&dot_shape=Dots
→ 200 image/png, byte-identical to the request without dot_shape (fallback to square)

POST /api/generate   format=qrcode&content_type=url&url=https://x.io&output_format=svg&dot_shape=classy_rounded&eye_border=leaf
→ 200 {"image": "data:image/svg+xml;base64,…", "mime": "image/svg+xml"}
```

## Logging (FR-015)

On QR success, the `generate`, `download`, and `qr_embed` events gain:

```json
{"dot_shape": "dots", "eye_border": "circle", "eye_center": "circle"}
```

These are always the **normalized** values, never raw input. The encoded data is never logged.
