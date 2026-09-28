---

description: "Task list for QR Code Shape Styles (Dots & Eyes)"
---

# Tasks: QR Code Shape Styles (Dots & Eyes)

**Input**: Design documents from `specs/001-qr-shape-styles/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/http-params.md, contracts/generator-ui.md, quickstart.md

**Tests**: REQUIRED. Constitution Principle V says every route and shared helper needs pytest coverage, and every contract or validation change needs tests, including fallback behavior. plan.md also lists the test files. Write each story's tests first and confirm they fail before implementing.

**Organization**: Tasks are grouped by user story so each story can be built and validated on its own.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on an incomplete task)
- **[Story]**: The user story the task belongs to (US1, US2, US3)

## Path Conventions

This is a single project with files at the repo root: `qr_generator.py`, the new `qr_shapes.py`, `templates/qr_generator.html`, and `tests/`.

## Ground rules for every task

These apply to all tasks below:

- **Python 3.14.** Production runs `python:3.14-slim` (upgraded on `chore/python-3.14`, which must merge first), matching local dev. No compatibility shims are needed for older Pythons.
- **No new runtime dependencies.** `zxing-cpp` is dev-only.
- **Default render path stays exactly as it is.** When the style is all-`square`, `_make_qr_png` and `_make_qr_svg` must run their current code with no edits to that path (research §4). This is what guarantees FR-011 and SC-002.
- **Keys, values, and order.** Parameter keys are `dot_shape`, `eye_border`, `eye_center`. Allowed values and their order come from `contracts/http-params.md`, and that order is also the UI display order.
- **Geometry constants.** These live in research.md §5 (dot table, eye border table, eye center table, and the corner rule).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Tooling, baseline capture, and the empty new module.

- [ ] T001 Capture pre-feature baseline hashes per `specs/001-qr-shape-styles/quickstart.md` §1. Run the app from current `main` and save the sha256 of the three `/api/qr` requests to `/tmp/qr-baseline.txt`. Also save the raw response bytes of those requests as fixtures in `tests/fixtures/legacy/` (`url_png.png`, `hello_svg.svg`, `x_800_m0_fg_H.png`) along with a `tests/fixtures/legacy/README.md` that lists the exact query string for each file and the installed `Pillow` and `qrcode` versions the fixtures were captured with.
- [ ] T002 [P] Add `zxing-cpp` to `requirements-dev.txt`. It must not go in `requirements.txt`.
- [ ] T003 [P] Add `COPY qr_shapes.py .` next to the existing `COPY qr_generator.py .` line in `Dockerfile`.
- [ ] T004 [P] Create `qr_shapes.py` at the repo root with a module docstring saying it holds pure geometry plus the PNG/SVG backends for styled QR codes and has no Flask imports. Leave everything else empty.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The value types, parser, geometry primitive, both backends, and render dispatch. Every story depends on these. At the end of this phase a styled render works end to end with square dots and square eyes, and nothing is exposed to users yet.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

### Tests for Foundation (write first; they must fail)

- [ ] T005 [P] In `tests/test_helpers.py`, add `_parse_shape_style` tests:
  - Missing keys give `ShapeStyle('square','square','square')`.
  - Every whitelisted value for each field is accepted.
  - Differently-cased values (`Dots`, `CIRCLE`), unknown values, the empty string, and values over 32 chars all fall back to `square`, and only for that field (FR-012, FR-004).
  - It works with both a dict and a werkzeug `MultiDict`.
  - `ShapeStyle.is_default` is True only when all three fields are `square`.
- [ ] T006 [P] Create `tests/test_shapes.py` with the foundational geometry and backend units:
  - The whitelist tuples `DOT_SHAPES`, `EYE_BORDERS`, `EYE_CENTERS` have exactly the values in contract order, with lengths 9, 7, and 5.
  - `RRect` fields match data-model.md.
  - `build_primitives(matrix, ShapeStyle('square','square','square'))` gives zero dot primitives inside the three 7×7 finder boxes and exactly one 1×1 dot per other dark module.
  - Eye primitives come in the order outer (ink 1), opening (ink 0), center (ink 1) for each of the 3 finders.
  - No primitive extends outside `[0, n]²`.
  - `rasterize_png` returns a valid PNG of exactly `size×size` whose corner pixel equals `bg` when margin > 0.
  - The supersample canvas side is ≤ 4096 for version 40 (177 modules) with margin 10 at size 2000 (research §3). Expose the computed pixels-per-module through a small helper `_supersample_ppm(n_total, size)` so this can be asserted.
  - `to_svg` returns text that parses as XML (`xml.etree.ElementTree`) with an `svg` root, a `viewBox`, at least one `<path>`, no `<image>`, and an eyes path that has `fill-rule="evenodd"`.
  - `to_svg`'s `width`/`height` equal the legacy `_make_qr_svg` values (mm units) for the same data, size, and margin, e.g. `33mm` at size 300, margin 4 for a 25-module code.
  - **SVG structure matches geometry**: for a few hand-built primitive lists (a sharp rect, a fully rounded circle, a TL+BR classy rect, and an eye ring), the number of subpaths (`M` commands) in each `<path>` equals the number of primitives, each subpath starts at the expected coordinate, and a rounded corner emits an `A` command while a sharp corner does not. This catches arc and sweep-flag bugs that PNG decode tests can't see.
- [ ] T007 [P] In `tests/test_routes.py`, add legacy byte-identity tests (SC-002, FR-011, contract rule 5):
  - **Always on (same-run)**: for each T001 query, output with no `shape` argument equals output with `shape=ShapeStyle('square','square','square')`, for both `_make_qr_png` and `_make_qr_svg`.
  - **Fixture check**: output with no `shape` argument equals the T001 fixture bytes. Skip with a clear message when the installed `Pillow` or `qrcode` version differs from the versions in `tests/fixtures/legacy/README.md`, so a dependency upgrade doesn't fail the suite. Re-capture the fixtures after an upgrade.

### Implementation for Foundation

- [ ] T008 In `qr_shapes.py`, define:
  - The ordered tuples `DOT_SHAPES`, `EYE_BORDERS`, `EYE_CENTERS`, with values in contract order, plus matching `frozenset`s for lookup.
  - `DEFAULT = 'square'`.
  - `class ShapeStyle(NamedTuple)` with fields `dot`, `eye_border`, `eye_center` (all defaulting to `'square'`) and an `is_default` property.
  - A human display-name map for each value (e.g. `extra_rounded` → "Extra rounded", `leaf_circle` → "Leaf, round opening", `square_circle` → "Square, round opening"), using the names from spec FR-001 to FR-003.
- [ ] T009 In `qr_shapes.py`, define `class RRect(NamedTuple)`: `x, y, w, h, r` as floats, `corners` as a tuple of 4 bools in the order TL, TR, BR, BL, and `ink` as an int (1 paints, 0 cuts). Add a helper `circle(cx, cy, d, ink=1)` that returns an `RRect` with `r = d/2` and all corners set.
- [ ] T010 In `qr_shapes.py`, implement `get_matrix(data, ec)`. It builds `qrcode.QRCode(error_correction=ec, border=0)`, calls `add_data` and `make(fit=True)`, and returns `get_matrix()` as a list of lists of bool. Also implement `finder_boxes(n)`, which returns the three 7×7 origins `(0,0)`, `(n-7,0)`, `(0,n-7)`, and `is_finder(x, y, n)`.
- [ ] T011 In `qr_shapes.py`, implement `build_primitives(matrix, style)`, which returns `(dots, eyes)` per data-model.md "Render plan".
  - Loop over dark modules that aren't in a finder box and dispatch to `_dot_primitives(style.dot, x, y, nb)`. `nb` is a neighbour lookup for up, down, left, and right that treats finder modules and light modules as absent.
  - For each finder box, append `_eye_border_primitives(style.eye_border, ox, oy)` (outer, then opening) and `_eye_center_primitives(style.eye_center, ox, oy)`.
  - In this phase, only implement the `square` branch of each dispatcher: a 1×1 dot; a 7×7 outer at r=0 plus a 5×5 opening at (+1,+1) with ink 0; and a 3×3 center at (+2,+2). Any other value should temporarily fall through to the square geometry. US1 and US2 fill in the real branches.
- [ ] T012 In `qr_shapes.py`, implement the PNG backend `rasterize_png(dots, eyes, n, margin, size, fg, bg) -> io.BytesIO` following research §2 and §3:
  - `_supersample_ppm(N, size) = clamp(ceil(3*size/N), 1, floor(4096/N))`, where `N = n + 2*margin`.
  - Create a black `L` mask of side `N*ppm`.
  - Draw each `RRect` offset by `margin` using `_draw_rrect(draw, rect, ppm, fill)`: two cross rectangles, each skipped when degenerate, plus one `pieslice` or R×R square per corner, with `R = min(r, w/2, h/2)` in px. Round coordinates to integer px once, at the corner coordinates. **Don't use `ImageDraw.rounded_rectangle`.** Fill is 255 for ink 1 and 0 for ink 0. Draw dots first, then eyes, in list order.
  - Resize the mask to `size×size` with `Image.LANCZOS`, then `Image.composite(Image.new('RGB', …, fg), Image.new('RGB', …, bg), mask)`.
  - Save as PNG to a `BytesIO` and seek to 0.
- [ ] T013 In `qr_shapes.py`, implement the SVG backend `to_svg(dots, eyes, n, margin, size) -> io.BytesIO`.
  - The `svg` root has `xmlns`, `width` and `height` set to `size`, and `viewBox="0 0 N N"` in module units.
  - Emit one `<path d=…>` for the dots and one `<path fill-rule="evenodd" d=…>` for the eyes. The eye openings cut holes because of evenodd, so the ink-0 rects are emitted as ordinary subpaths.
  - Build each `RRect` subpath with `M`/`H`/`V` plus `A r r 0 0 1 x y` on rounded corners. Numbers use at most 3 decimals with trailing zeros stripped.
  - Keep today's SVG color and sizing behavior: black fill, no background rect, and `width`/`height` in mm computed like the legacy path: `box_size = max(1, size // (21 + 2*margin))`, then `box_size * N / 10` mm (research §2, spec Assumptions).
  - UTF-8 encode, then seek to 0.
- [ ] T014 In `qr_generator.py`:
  - `from qr_shapes import ShapeStyle, DOT_SHAPES, EYE_BORDERS, EYE_CENTERS, …`
  - Add `_parse_shape_style(src)` next to `_safe_color`. It reads `dot_shape`, `eye_border`, `eye_center` via `src.get(key, '')`, truncates each to `[:32]`, does an exact frozenset membership check, and uses `'square'` otherwise. It returns a `ShapeStyle` and never raises.
- [ ] T015 In `qr_generator.py`, extend `_parse_common(form)` to return a 7-tuple `(output_fmt, size, margin, fg, bg, ec, shape)`, where `shape = _parse_shape_style(form)`. Update the unpacking in both `generate()` and `download()` to match, without using `shape` yet, so behavior doesn't change. Update any existing `_parse_common` tests in `tests/test_helpers.py` for the new tuple length.
- [ ] T016 In `qr_generator.py`, add a keyword argument `shape=None` to `_make_qr_png(data, ec, size, margin, fg, bg, shape=None)` and `_make_qr_svg(data, ec, size, margin, shape=None)`.
  - Add a guard at the top: `if shape is None or shape.is_default:` then fall through to the **unchanged existing body**.
  - Otherwise, call `qr_shapes.get_matrix(data, ec)`, then `build_primitives(matrix, shape)`, then `rasterize_png(..., size, fg, bg)` or `to_svg(..., size)`, and return that buffer.
- [ ] T017 Run `python3 -m pytest tests/test_helpers.py tests/test_shapes.py tests/test_routes.py`. T005–T007 must pass, and all pre-existing tests must still pass.

**Checkpoint**: The parser, geometry primitive, both backends, and dispatch all work. Default output is byte-identical to before, and user stories can begin.

---

## Phase 3: User Story 1 - Choose a dot shape in the generator (Priority: P1) 🎯 MVP

**Goal**: The generator page shows a "Shape style" section with 9 dot swatches. The preview and downloads (PNG and SVG) use the chosen dot shape, and the eyes stay unchanged.

**Independent Test**: Open `/generator` in QR mode, enter a URL, pick each dot shape, and confirm the preview changes while the eyes stay square. Download PNG and SVG and scan them. Untouched options give today's output. The first 8 swatches match `assets/dot-shape-styles.png` in order, followed by Gapped square.

### Tests for User Story 1 (write first; they must fail)

- [ ] T018 [P] [US1] In `tests/test_shapes.py`, add dot geometry units against research §5, using small hand-built matrices (for example a 21×21 all-light matrix with a few dark data modules placed away from the finders):
  - **`rounded` / `extra_rounded`**: an isolated module has all 4 corners set with r = 0.25 / 0.5. In a horizontal pair, the left module's TR and BR corners are not set.
  - **`dots`**: one circle of diameter 0.9 centred in the cell, with no joining.
  - **`classy` / `classy_rounded`**: only the TL and BR corners are ever set, following the corner rule.
  - **`horizontal_bars`**: y ∈ [0.1, 0.9], r = 0.4, and the ends are rounded only where there is no left or right neighbour. An isolated module is fully rounded.
  - **`vertical_bars`**: the transpose of `horizontal_bars`.
  - **`gapped_square`**: a centred 0.8×0.8 square with r = 0.
  - **Every shape**: each dot primitive stays inside its 1×1 cell, and finder modules never produce dots.
  - **Swatches**: `swatch_svg('dot', v)` for each of the 9 values parses as XML with an `svg` root, `fill="currentColor"`, and at least one `<path>`.
- [ ] T019 [P] [US1] In `tests/test_routes.py`, add shape tests for the POST routes:
  - `POST /api/generate` with `format=qrcode` and each of the 9 `dot_shape` values returns 200 with the `{image, mime}` envelope. Non-square values give a PNG that differs from the default.
  - `output_format=svg` with `dot_shape=dots` returns a data URL whose decoded SVG contains `<path` and no `<image`.
  - `POST /api/generate/download` with `dot_shape=extra_rounded` returns an attachment with the same filename and content-type as the default.
  - `dot_shape=Dots` (wrong case) returns the same bytes as omitting it.
  - A barcode `format` (for example `code128`) with shape params returns bytes identical to the same request without them (contract rule 3, research §10).
- [ ] T020 [P] [US1] In `tests/test_routes.py`, add decode tests marked with `decode` in their names. Use `pytest.importorskip('zxingcpp')` and decode through `_make_qr_png` with `zxingcpp.read_barcodes(PIL.Image)`:
  - Each of the 9 dot shapes with square eyes decodes a representative URL at size 300.
  - Each dot shape decodes a short payload at `MIN_SIZE` (100).
  - Each dot shape decodes with custom fg `#1a237e` on bg `#fffde7`, and the pixel color at a known dark module is the fg color (FR-009).
- [ ] T021 [P] [US1] In `tests/test_routes.py`, add log-field tests (FR-015). Capture the `qrcodegen` logger (with `caplog`, or by patching `_log_event`). A successful QR `generate` and `download` event contains `dot_shape`, `eye_border`, `eye_center` with the normalized values. Raw invalid input such as `Dots` is logged as `square`. The payload `data` never appears in the event. Barcode events have no shape keys.
- [ ] T022 [P] [US1] In `tests/test_routes.py`, add a `GET /generator` test. The HTML contains a "Shape style" heading inside `#qr-options`, exactly 9 `input[name="dot_shape"]` radios whose `value`s are in contract order, `square` checked, and an inline `<svg` inside each dot option label.

### Implementation for User Story 1

- [ ] T023 [US1] In `qr_shapes.py`, implement `_dot_primitives(dot, x, y, nb)` for all 9 values per the research §5 table.
  - **Corner rule**: a corner is rounded only when both orthogonal neighbours touching it are absent. TL uses up and left, TR uses up and right, BR uses down and right, BL uses down and left.
  - `rounded` and `extra_rounded` apply the rule on all 4 corners. `classy` and `classy_rounded` apply it on TL and BR only.
  - The bar styles use the end rule from the table.
  - `dots` and `gapped_square` never join.
  - Unknown values give a 1×1 square.
- [ ] T024 [US1] In `qr_shapes.py`, implement `swatch_svg(kind, value) -> str`, returning a compact inline `<svg viewBox=… width="36" height="36" fill="currentColor" aria-hidden="true">` string. For `kind == 'dot'`, render a fixed 5×5 sample matrix drawn with that dot shape via `build_primitives` and the same path builder as `to_svg`, with no finder boxes. Use a hard-coded pattern that shows joins horizontally, vertically, and at L-corners, plus one isolated module. Reuse the path-building helper from T013; don't duplicate it. `kind in ('eye_border','eye_center')` is added in US2.
- [ ] T025 [US1] In `qr_generator.py`, pass `shape=shape` into `_make_qr_png` and `_make_qr_svg` inside the QR (`fmt == 'qrcode'`) branches of both `generate()` and `download()`. Barcode branches must not use `shape`.
- [ ] T026 [US1] In `qr_generator.py`, add `dot_shape=shape.dot, eye_border=shape.eye_border, eye_center=shape.eye_center` to the QR success `_log_event` calls in `generate()` and `download()`. Leave barcode and error events unchanged.
- [ ] T027 [US1] In `qr_generator.py`, change `generator()` to build `shape_options`, a dict mapping `'dot_shape'`, `'eye_border'`, `'eye_center'` to lists of `(value, display_name, svg)`. Iterate `DOT_SHAPES` with `swatch_svg('dot', v)`. Build only the `dot_shape` list here; the eye lists are added in T037, because `swatch_svg` has no eye kinds until T036 and this runs at import time. Compute it once at import time and cache it in a module-level constant, since the inputs are constants. Pass it to `render_template('qr_generator.html', shape_options=shape_options)`.
- [ ] T028 [US1] In `templates/qr_generator.html`, add a "Shape style" block inside `#qr-options`, after the Error Correction block (contract generator-ui.md).
  - Add a sub-group labelled "Dot shape" that renders `{% for value, name, svg in shape_options['dot_shape'] %}<label class="shape-opt" title="{{ name }}"><input type="radio" name="dot_shape" value="{{ value }}" aria-label="{{ name }}" {% if loop.first %}checked{% endif %}>{{ svg|safe }}</label>{% endfor %}`.
  - Add CSS for `.shape-opts` and `.shape-opt`, mirroring the `.ec-btn` look: a bordered tile with a hover accent. Show the checked state with `.shape-opt:has(input:checked)` or a JS-toggled `.active` class, using the same accent as `.ec-btn.active`. Visually hide the radio but keep it focusable, and show a focus ring on `:focus-visible`. Swatches use `currentColor` so they work in both themes. Tiles must wrap on narrow screens.
- [ ] T029 [US1] In the `templates/qr_generator.html` JS:
  - In `collectFormData()`, when `currentFormat === 'qrcode'`, append the checked `dot_shape`, `eye_border`, `eye_center` values, reading each with `document.querySelector('input[name="…"]:checked')?.value || 'square'`. The eye groups may not exist until US2, so this must default safely.
  - Add a delegated `change` listener on `.shape-opts` inputs that calls `generate()` when a preview is currently displayed, using the same condition the existing EC-button handler uses.
  - Add `dot_shape`, `eye_border`, `eye_center` to the `gtag('event', 'generate', …)` payload in QR mode and `null` otherwise, mirroring `ec_level`.
  - Confirm `updateApiUrl(fd)` shows the new params without further changes.
- [ ] T030 [US1] Run `python3 -m pytest`. T018–T022 must pass along with the whole suite. Then run the app (`python3 preview_app.py`), open `/generator`, and visually compare the 9 dot swatches with `specs/001-qr-shape-styles/assets/dot-shape-styles.png`: same order, recognisably the same silhouettes, Gapped square last. Tune the dot constants in `qr_shapes.py` if needed, re-run the tests, and record any tuned values in research.md §5.

**Checkpoint**: US1 is fully functional. Dot shapes work in the UI, preview, PNG and SVG downloads, and logs, and default output is unchanged. This is the MVP and can ship on its own.

If shipping at this point: the parser already accepts `eye_border`/`eye_center` values, but eye geometry still falls through to square (T011), and the UI has no eye pickers. A POST that sends eye values renders square eyes through the styled path. That's acceptable only because no UI exposes it. `/api/qr` must not be wired yet (see the deploy-ordering note in Dependencies).

---

## Phase 4: User Story 2 - Choose eye border and eye center styles (Priority: P2)

**Goal**: Two more swatch groups control the outer ring (7 styles) and the inner block (5 styles) of all three eyes. Each is independent and combinable with any dot shape.

**Independent Test**: With square dots, change only the eye border and confirm only the rings change, identically on all three corners. Then change only the center. All 315 combinations decode.

### Tests for User Story 2 (write first; they must fail)

- [ ] T031 [P] [US2] In `tests/test_shapes.py`, add eye geometry units against the research §5 tables:
  - Each of the 7 borders gives an outer `RRect` equal to the 7×7 box with the specified r and corners, followed by an opening (ink 0) inside the 5×5 box at (+1,+1) with the specified r and corners. `leaf_circle` and `square_circle` have circular openings (r = 2.5, all corners).
  - Each of the 5 centers gives a 3×3 `RRect` at (+2,+2) with the specified r and corners.
  - All three finders get identical relative geometry, not mirrored (FR-005).
  - Changing `eye_border` doesn't change the center primitives or the dot list, and vice versa (FR-004, FR-005).
  - Every eye primitive stays within `[0, n]²`, so margin=0 never clips.
  - `swatch_svg('eye_border', v)` and `swatch_svg('eye_center', v)` for every value parse as XML with an `svg` root and an evenodd `<path>`.
- [ ] T032 [P] [US2] In `tests/test_routes.py`, add the exhaustive decode test `test_decode_all_315_combinations`. Use `pytest.importorskip('zxingcpp')` and parametrize (or loop with collected failures) over `DOT_SHAPES × EYE_BORDERS × EYE_CENTERS`. Render a representative URL at size 300 via `_make_qr_png` and assert the decoded text equals the input (SC-001, FR-014). Also add:
  - A dense payload (about 300 chars, EC `H`) at size 600 for each dot shape paired with each eye border, and separately with each eye center.
  - margin=0 at size 300 for each eye border.
- [ ] T033 [P] [US2] In `tests/test_routes.py`, add route tests for eyes:
  - `POST /api/generate` with `eye_border=leaf&eye_center=circle` returns 200 and differs from the default.
  - `eye_border=nope` falls back independently: `dot_shape=dots&eye_border=nope` gives the same bytes as `dot_shape=dots` alone.
  - A `GET /generator` test checks for 7 `eye_border` radios and 5 `eye_center` radios in contract order, `square` checked, each with an inline `<svg`.

### Implementation for User Story 2

- [ ] T034 [US2] In `qr_shapes.py`, implement `_eye_border_primitives(border, ox, oy)` for all 7 values per the research §5 table. It returns `[outer RRect(ink=1), opening RRect(ink=0)]`.
  - `square` / `rounded` / `circle` / `teardrop` / `leaf` use the table's r and corner flags.
  - `leaf_circle` uses the `leaf` outer with a circle opening of r = 2.5.
  - `square_circle` uses an r=0 outer with a circle opening of r = 2.5.
  - Unknown values give `square`.
- [ ] T035 [US2] In `qr_shapes.py`, implement `_eye_center_primitives(center, ox, oy)` for all 5 values per the research §5 table, as one 3×3 `RRect` at (+2,+2). Unknown values give `square`.
- [ ] T036 [US2] In `qr_shapes.py`, extend `swatch_svg` with two kinds:
  - `kind='eye_border'` renders one 7×7 eye with that border and a square center.
  - `kind='eye_center'` renders one 7×7 eye with that center and a square border.
  - Both use the evenodd path from `to_svg`'s path builder and the same `<svg>` wrapper attributes as dot swatches.
- [ ] T037 [US2] In `qr_generator.py`, extend the cached `shape_options` from T027 so it also builds the `eye_border` list from `EYE_BORDERS` with `swatch_svg('eye_border', v)` and the `eye_center` list from `EYE_CENTERS` with `swatch_svg('eye_center', v)`.
- [ ] T038 [US2] In `templates/qr_generator.html`, add the "Eye border" and "Eye center" sub-groups to the "Shape style" block, after "Dots". Use the same `.shape-opts` / `.shape-opt` markup pattern and loop over `shape_options['eye_border']` and `shape_options['eye_center']` with radios named `eye_border` and `eye_center`, `square` checked. The JS from T029 already collects them and re-generates on change, so no new JS should be needed. Verify this.
- [ ] T039 [US2] Run `python3 -m pytest` (T031–T033 plus the full suite). Then open `/generator` and compare the 7 border swatches with `specs/001-qr-shape-styles/assets/eye-border-styles.png` in order and silhouette, and check that each center has the same orientation as its matching border (SC-006). Tune the eye constants if needed, re-run the tests, and record any changes in research.md §5.

**Checkpoint**: US1 and US2 both work independently and together. All 315 combinations decode.

---

## Phase 5: User Story 3 - Request shaped codes from the embed/API endpoints (Priority: P3)

**Goal**: `GET /api/qr` accepts `dot_shape`, `eye_border`, `eye_center` with the same response type and caching as today. The POST APIs already accept them as of US1 and US2.

**Independent Test**: A styled `/api/qr` URL returns the styled image with the same `Content-Type` and `Cache-Control`. The same URL without shape params is byte-identical to the pre-feature baseline, and invalid values fall back.

### Tests for User Story 3 (write first; they must fail)

- [ ] T040 [P] [US3] In `tests/test_routes.py`, add `/api/qr` shape tests:
  - `?data=https://example.com/abc&dot_shape=dots&eye_border=circle&eye_center=circle` returns 200, `Content-Type: image/png`, and `Cache-Control: public, max-age=86400, immutable`, with a body that differs from the unstyled request (FR-013).
  - `format=svg&dot_shape=extra_rounded&eye_border=leaf` returns `image/svg+xml` with `<path` and no `<image`.
  - The three T001 fixture queries, with no shape params, return bytes equal to `tests/fixtures/legacy/*` (SC-002).
  - The same fixture query plus `dot_shape=square&eye_border=square&eye_center=square` is byte-identical to the fixture.
  - `dot_shape=Dots&eye_border=nope` is byte-identical to the fixture (US3 scenario 3, FR-012).
  - Shape values never give a 4xx or 5xx, including 1000-char garbage values.
  - Missing `data` still returns 400.
- [ ] T041 [P] [US3] In `tests/test_routes.py`, add a `qr_embed` log test. A styled `/api/qr` success event includes the normalized `dot_shape`, `eye_border`, `eye_center` and never includes `data`.

### Implementation for User Story 3

- [ ] T042 [US3] In `qr_generator.py` `qr_image_get()`:
  - Call `shape = _parse_shape_style(args)` after the existing param parsing, and pass `shape=shape` into `_make_qr_png` and `_make_qr_svg`.
  - Add `dot_shape=shape.dot, eye_border=shape.eye_border, eye_center=shape.eye_center` to the success `_log_event(event='qr_embed', …)`.
  - Leave the `send_file` call and the `Cache-Control` header exactly as they are.
- [ ] T043 [US3] In `qr_generator.py`, extend the `qr_image_get()` docstring's "Query params" list with `dot_shape`, `eye_border`, `eye_center`, their allowed values, and the default `square`, noting the case-sensitive fallback.
- [ ] T044 [US3] Run `python3 -m pytest` (T040–T041 plus the full suite), then run quickstart.md §3 contract checks against a local server. The legacy hashes must match `/tmp/qr-baseline.txt`, and the styled embed must keep its headers.

**Checkpoint**: All three user stories work independently.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Docs (FR-016), compatibility, performance, and the final end-to-end validation.

- [ ] T045 [P] In `README.md`, add `dot_shape`, `eye_border`, `eye_center` rows to the `/api/qr` parameter table, with allowed values, the default, and the fallback rule. Add an example styled `<img src>` URL that uses `example.com`, not lnklab.us. Note that contrast between fg/bg and thin shapes (dots, bars, gapped squares) is the caller's responsibility (spec Edge Cases).
- [ ] T046 [P] In `CLAUDE.md`:
  - Add the three params to the `/api/qr` query-param sentence in "Routes".
  - Add `qr_shapes.py  # shape geometry + PNG/SVG backends for styled QR` to "Repo layout" and `test_shapes.py` to the tests line.
  - Add a Conventions bullet saying styled rendering goes through `qr_shapes.build_primitives` and that the all-square style must keep the legacy path byte-identical.
- [ ] T047 [P] In `docs/INTEGRATIONS.md`, document the shape params for embedders, with a styled example URL, a note that existing URLs render identically and stay cache-stable, and the same contrast-responsibility note as T045.
- [ ] T048 [P] Run the full test suite inside the production image: `docker compose build`, then run `pip install -r requirements-dev.txt && python -m pytest` in a `python:3.14-slim` container with the repo mounted. Confirm `qr_shapes.py` is copied into the image (T003) by starting the container and requesting a styled `/api/qr` URL.
- [ ] T049 [P] Check performance (SC-005, plan's ≤ ~50 ms goal). Time `_make_qr_png` for `extra_rounded` / `teardrop` / `leaf` at size 300 and for the worst case (a 2000-char payload, EC `H`, size 2000). Record the numbers in the PR description. Add a test `test_styled_render_perf` that asserts the median of 5 renders at size 300 is ≤ 50 ms (SC-005); if it fails, profile `_draw_rrect`.
- [ ] T050 Run all of `specs/001-qr-shape-styles/quickstart.md`: §2 the automated suite, §3 the contract checks, §4 the visual comparison, §5 the manual end-to-end including phone scans of the PNG and SVG downloads and the under-30 s timing, and §6 the log check. Note any deviations.
- [ ] T051 Final `python3 -m pytest` run. The full suite must pass before merge (Principle V).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies. **T001 must run on unmodified `main` before any change to `qr_generator.py`.**
- **Foundational (Phase 2)**: Depends on Setup. T007 needs the T001 fixtures. It blocks all user stories.
- **US1 (Phase 3)**: Depends on Foundational.
- **US2 (Phase 4)**: Depends on Foundational. The UI tasks T037 and T038 build on the `shape_options` and "Shape style" block from T027 and T028. If US2 is built before US1, those scaffolding tasks move into US2. The geometry work (T034–T036) doesn't depend on US1.
- **US3 (Phase 5)**: Depends only on Foundational. `/api/qr` wiring (T042) is independent of the UI. Its tests exercise real shapes, so to see non-square output it needs T023 (dots) and/or T034 and T035 (eyes).
- **Polish (Phase 6)**: Depends on all stories that are going to ship.
- **Prerequisite outside this feature**: `chore/python-3.14` (Dockerfile base image) must merge to `main` before this feature deploys.
- **Deploy ordering for `/api/qr`**: `/api/qr` responses are cached `immutable` for 24 h at the edge. Don't deploy T042 until all geometry (T023, T034, T035) is implemented and swatch tuning (T030, T039) is done, or cached styled URLs would change after a later deploy. US3 can be *built* after Foundational, but must *ship* after US2.

### Within Each Phase

- Foundational: T008 → T009 → T010 → T011 → T012 and T013 (same file, so sequential) → T014 → T015 → T016 → T017.
- US1: tests T018–T022 → T023 → T024 → T025 → T026 → T027 → T028 → T029 → T030.
- US2: tests T031–T033 → T034 → T035 → T036 → T037 → T038 → T039.
- US3: tests T040–T041 → T042 → T043 → T044.

### Parallel Opportunities

- Setup: T002, T003, T004 are different files.
- Foundational tests: T005 (`test_helpers.py`), T006 (`test_shapes.py`), T007 (`test_routes.py`).
- US1 tests: T018 (`test_shapes.py`) can run alongside T019–T022, but T019–T022 all touch `test_routes.py`, so run them sequentially unless you split them into separate files.
- After Foundational, geometry for US1 (T023) and US2 (T034, T035) are different functions in the same file. They can be developed in parallel on separate branches, but merge them sequentially.
- US3's T042 (in `qr_generator.py`, `qr_image_get`) can run in parallel with US2's `qr_shapes.py` work.
- Polish: T045, T046, T047, T048, T049.

---

## Parallel Example: User Story 1

```bash
# Tests first, in parallel across files:
Task: "T018 [US1] Dot geometry units in tests/test_shapes.py"
Task: "T019 [US1] POST route shape tests in tests/test_routes.py"

# Then implementation in parallel across files, once T023 is done:
Task: "T025/T026 [US1] Wire shape + log fields in qr_generator.py"
Task: "T028 [US1] Shape style markup + CSS in templates/qr_generator.html"
```

## Parallel Example: User Story 2 + User Story 3

```bash
Task: "T034/T035 [US2] Eye border + center geometry in qr_shapes.py"
Task: "T042 [US3] Wire _parse_shape_style into qr_image_get in qr_generator.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 Setup, capturing the baseline first.
2. Phase 2 Foundational (the byte-identity tests guard the legacy path).
3. Phase 3 US1 (dot shapes in the UI and POST APIs).
4. **Stop and validate**: run the suite, compare the swatches visually, and phone-scan the downloads.
5. Deploy (`git pull && docker compose up -d --build`). Embedders see no change.

### Incremental Delivery

1. Setup + Foundational: nothing changes for users.
2. US1: dot shapes. Ship the MVP.
3. US2: eye styles, with the 315-combo decode gate. Ship.
4. US3: `/api/qr` params for embedders. Ship with the Polish docs (FR-016).

---

## Notes

- [P] means different files with no incomplete dependencies. Many tasks share `qr_shapes.py` or `qr_generator.py` and are deliberately sequential.
- If a decode test fails for a combination, tune the geometry constants (research §5 allows this). Don't drop the combination: SC-001 requires all 315.
- Never modify the legacy branch in `_make_qr_png` or `_make_qr_svg`. If a byte-identity test fails, the guard in T016 is wrong.
- After deploying, if a styled URL looks wrong publicly but is correct against the container, suspect the Cloudflare edge cache (CLAUDE.md gotcha).
- Commit after each checkpoint.
