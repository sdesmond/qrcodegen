# Research: QR Code Shape Styles

**Feature**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Date**: 2026-09-27

A throwaway spike was run in a scratch venv with Pillow 12.3, qrcode, and zxing-cpp. It rendered
a URL code with extra-rounded dots, a teardrop eye border, and a leaf eye center at 300 px in
about 5 ms, and zxing-cpp decoded it correctly. The findings below come from that spike and from
the reference images in `assets/`.

---

## 1. Rendering approach

**Decision**: Build a custom renderer on top of the module matrix from `qrcode` (`QRCode(border=0)`
→ `get_matrix()`). One geometry description is drawn by two backends: a Pillow mask for PNG and
SVG `<path>` data for SVG.

**Rationale**:

- `qrcode`'s `StyledPilImage` module drawers cover only some dot shapes: square, gapped, circle,
  rounded, and the two bar styles. They have no Classy / Classy-rounded shapes and no separate
  eye border or center styling. `eye_drawer` draws the eye module-by-module, which cannot
  produce a ring with a circular or teardrop opening.
- `StyledPilImage` is PNG-only. Its SVG drawers don't share geometry with the PIL drawers, so
  keeping PNG and SVG identical (FR-007/FR-008) would mean two implementations.
- One geometry source gives one set of bugs (Principle IV) and lets the UI swatches reuse it
  (§8).

**Alternatives considered**: `StyledPilImage` plus hand-written SVG was rejected because it
can't cover the full shape set and PNG/SVG would drift apart. A new dependency (cairosvg, or
segno with plugins) was rejected because it's an unjustified runtime dependency, cairo needs
system libs, and it still wouldn't have the needed shapes.

## 2. Geometry primitive

**Decision**: Every shape is a list of `RRect(x, y, w, h, r, corners=(tl, tr, br, bl), ink)` in
**module units**. `ink` is 1 to paint and 0 to cut. A circle is an `RRect` with `r = w/2` and all
four corners on. A ring is an outer `RRect(ink=1)` followed by an opening `RRect(ink=0)`.

**Rationale**: FR-001 to FR-003 can all be written as rectangles whose corners are either sharp
or rounded with a common radius. A single primitive keeps both backends small.

**PNG backend finding**: `ImageDraw.rounded_rectangle(..., corners=...)` in Pillow 12.3 **raises
`ValueError`** for per-corner combinations such as TL+BR rounded with radius near half the side.
Clamping the radius did not help. **Do not use it.** Draw each `RRect` as follows instead:

- Two cross rectangles, `[x0+R, y0, x1−R, y1]` and `[x0, y0+R, x1, y1−R]`, each skipped when
  degenerate.
- For each corner, either a `pieslice` (rounded) or an R×R square (sharp).

The spike showed this is robust across all combinations. Integer pixel rounding is applied
once, at the corner coordinates.

**SVG backend**: Each `RRect` becomes one subpath: `M` / `H` / `V` with `A r r 0 0 1` arcs on
rounded corners. Two `<path>` elements are emitted: one for dots (default nonzero fill) and one
for eyes with `fill-rule="evenodd"`, so that openings cut holes. Coordinates are written with at
most 3 decimals.

**SVG sizing**: The legacy `qrcode` `SvgImage` writes `width`/`height` in **mm**:
`box_size × N / 10` mm, where `box_size = max(1, size // (21 + 2·margin))` and N is modules plus
2·margin (33mm at the defaults). The styled SVG uses the same formula for `width`/`height` and a
`viewBox="0 0 N N"` in module units, so picking a shape never changes the physical size of a
downloaded SVG.

**Alternatives considered**: Pillow `rounded_rectangle` was rejected because of the bug above.
Polygon approximation of arcs was rejected because it makes larger SVGs and loses true vector
curves.

## 3. PNG antialiasing and memory bound

**Decision**: Render a white-on-black `L` mask at `p` px per module, where
`p = clamp(ceil(3 · size / N), 1, floor(4096 / N))` and `N = modules + 2·margin`. Then resize the
mask to `size × size` with LANCZOS and use `Image.composite(fg, bg, mask)`.

**Rationale**:

- 3× supersampling gives smooth curves.
- Compositing keeps fg/bg colors exact (FR-009) instead of antialiasing through color.
- The 4096 px cap bounds the mask at ≤16 MiB for every allowed input. The worst case is v40
  (177 modules) plus a 10-module margin: N = 197, p ≥ 20, which is still well sampled.
- The legacy path also finishes with a LANCZOS resize, so edge quality looks similar.

**Alternatives considered**: Drawing directly at `size` was rejected because it leaves jagged
edges. Rendering RGB at supersample scale was rejected because it uses 3× the memory for no
benefit.

## 4. Default path preservation (FR-011, SC-002)

**Decision**: If `dot_shape == eye_border == eye_center == 'square'`, `_make_qr_png` and
`_make_qr_svg` run their **current code unchanged**. The styled renderer runs only when at least
one choice is not the default.

**Rationale**: This guarantees byte-identical output for every existing `/api/qr` URL, so there
is nothing new to cache-bust at the edge and nothing changes for any external embedder. Trying to make the
new renderer reproduce the legacy pixels exactly would be fragile.

**Consequence**: `dot_shape=square` combined with a non-square eye goes through the styled
renderer. That is acceptable, because no existing request can produce it.

**Testing the guarantee**: Legacy bytes depend on the installed Pillow/qrcode/zlib versions, so
committed fixtures alone would break on any dependency upgrade. The always-on tests compare
outputs within one run (no shape params vs. explicit all-`square` vs. invalid values). The
committed fixtures additionally catch edits to the legacy path; they record the library versions
they were captured with and skip when the installed versions differ.

## 5. Shape definitions (constants tuned against `assets/`)

The corner rule for joined dot styles: a module's corner is rounded only when **both** of its
orthogonal neighbours touching that corner are light. Neighbours are data modules only; the
three 7×7 finder regions count as light. Joined modules therefore render as solid groups with
rounded outer corners.

Zooming into `assets/dot-shape-styles.png` settled the choices below: Classy rounds TL and BR,
bars are thinner than a module, and an isolated bar module is a circle.

| Dot shape | Per-module geometry |
|---|---|
| `square` | 1×1, r=0 |
| `rounded` | 1×1, r=0.25, corner rule on all 4 corners |
| `extra_rounded` | 1×1, r=0.5, corner rule on all 4 corners |
| `dots` | circle, diameter 0.9, centred; no joining |
| `classy` | 1×1, r=0.25, corner rule on **TL and BR only** |
| `classy_rounded` | 1×1, r=0.5, corner rule on **TL and BR only** |
| `horizontal_bars` | x∈[0,1], y∈[0.1,0.9], r=0.4; TL/BL rounded if no left neighbour, TR/BR if no right |
| `vertical_bars` | x∈[0.1,0.9], y∈[0,1], r=0.4; TL/TR rounded if no top neighbour, BL/BR if no bottom |
| `gapped_square` | 0.8×0.8, centred, r=0; no joining |

Eye geometry uses the 7×7 finder box. Every ring opening fits inside the 5×5 box and every
center inside the 3×3 box, so the light separator ring is never covered. That keeps finder
detection intact, and nothing extends past the symbol, so **margin=0 never clips** (edge case).
"Thick" rings (Leaf and the round-opening styles) come from a rounded opening inside a
sharper outline, not from shrinking the opening.

| Eye border | Outer (7×7) | Opening (5×5 at +1,+1) |
|---|---|---|
| `square` | r=0 | r=0 |
| `rounded` | r=2, all | r=1, all |
| `circle` | r=3.5, all | r=2.5, all |
| `teardrop` | r=3.5, TR/BR/BL (TL sharp) | r=2.5, TR/BR/BL |
| `leaf` | r=3.5, TR/BL (TL, BR sharp) | r=2.5, TL/TR/BL (BR sharp) |
| `leaf_circle` | as `leaf` | circle r=2.5 |
| `square_circle` | r=0 | circle r=2.5 |

| Eye center | 3×3 at +2,+2 |
|---|---|
| `square` | r=0 |
| `rounded` | r=0.75, all |
| `circle` | r=1.5, all |
| `teardrop` | r=1.5, TR/BR/BL |
| `leaf` | r=1.5, TR/BL |

All three eyes use identical, non-mirrored geometry (FR-005). These constants are the starting
point. SC-006 is checked by rendering the swatches side by side with the reference images
during implementation (see quickstart §4), and constants may be tuned there without changing
any contract.

## 6. Decode verification (FR-014, SC-001, SC-004)

**Decision**: Add **`zxing-cpp`** (pip `zxing-cpp`, module `zxingcpp`) to `requirements-dev.txt`
only. The test suite renders all 315 combinations as PNG at size 300 for a representative URL
payload and asserts that `zxingcpp.read_barcodes(img)[0].text == data`.

Additional parametrized cases:

- Dense payload (~300 chars, EC `H`) at size 600, for every dot shape paired with each eye
  style.
- Short payload at `MIN_SIZE` (100) for every dot shape.
- margin=0 for all eye borders.
- Custom fg/bg with sufficient contrast.

**Rationale**: zxing-cpp ships self-contained wheels for Windows, Linux, and macOS with no
system libraries. It is a robust, widely used decoder, it's fast (spike: <10 ms per decode, so
the 315-combo run takes a few seconds), and it accepts PIL images directly. It is dev-only, so
the image and runtime surface are unchanged.

**Alternatives considered**: `pyzbar` was rejected because it needs the system `libzbar` on
Linux and is a weaker decoder. `opencv-python-headless` was rejected because it's around 50 MB
and its QR detector is less tolerant of stylized modules.

**SVG decode**: SVG is not rasterized in tests, because that would need cairo. SVG correctness is
covered structurally: the output parses as XML, contains `<path>` elements, and has no `<image>`
(FR-008 vector). Correctness also follows from sharing geometry with the PNG path, and a
geometry-parity unit test compares the primitive lists both backends consume.

## 7. Parameter naming and validation

**Decision**: Use the query/form keys `dot_shape`, `eye_border`, `eye_center`, which are the same
on all three routes. Values are lowercase snake_case identifiers (see
[contracts/http-params.md](contracts/http-params.md)). Validation is an **exact, case-sensitive**
dict/frozenset lookup, and anything else becomes `square`. That covers the spec edge case where
differently-cased values fall back, and it also keeps one canonical URL per image for edge
caching.

The helper is `_parse_shape_style(src) -> ShapeStyle`. `_parse_common` calls it and appends it to
its return tuple, and `/api/qr` calls it directly, since `/api/qr` doesn't use `_parse_common`
today. The params are added once, in the shared layer (Principle IV). Values are also truncated
to 32 chars before lookup.

## 8. UI swatches

**Decision**: `generator()` passes the template a dict of swatch SVG strings built by
`qr_shapes.swatch_svg(kind, value)`.

- **Dots**: a fixed 5×5 sample pattern drawn with that dot shape.
- **Eyes**: one 7×7 eye with that border, or that center plus a square border.

They are rendered inline (`|safe`, since the input is internal constants only) inside
`<label><input type="radio">` swatch buttons. Inline SVG is allowed by the current CSP
(no `img-src` or `script-src` changes needed).

**Rationale**: FR-006 asks for swatches that resemble the reference images. Generating them from
the production geometry means they can't drift from the output. Hand-drawn icons were considered
and rejected because they would duplicate the geometry.

Changing a swatch re-runs `generate()` when a preview is already shown, so the preview updates
immediately (FR-007). The three values are appended in `collectFormData()` only when
`currentFormat === 'qrcode'`, and the whole section lives inside `#qr-options`, which is already
hidden for barcodes (edge case). The GA `generate` event gains the three fields, mirroring the
existing `ec_level` handling.

## 9. Logging (FR-015)

**Decision**: Add `dot_shape`, `eye_border`, `eye_center` (the normalized whitelist values,
never raw input) to the QR success events for `generate`, `download`, and `qr_embed`. Barcode
events are unchanged.

## 10. Barcodes

**Decision**: Barcode branches never read shape params. Tests assert that a barcode request
with shape params returns bytes identical to the same request without them.
