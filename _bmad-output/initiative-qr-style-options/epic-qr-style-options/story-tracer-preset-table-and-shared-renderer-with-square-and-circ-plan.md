---
title: 'Tracer: preset table and shared renderer with Square and Circle end to end'
type: 'feature'
ticket: '1'
created: '2026-10-07'
status: 'built'
baseline_revision: 'aef1ae0f4511cc4f23e3501a23555fe78b716625'
route: 'full'
route_source: 'auto'
risk: 'medium'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/initiative-qr-style-options/epic-qr-style-options/spec-qr-style-options/presets.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The generator draws only square modules (CAP-1). Every later preset, thumbnail and scan test needs one shared preset table and one shared per-module renderer, and nothing proves that a styled code still decodes.

**Approach:** Add `presets.json` (rows `{dot, frame, ball}`) and one renderer that draws a module matrix as PNG or SVG per row. Wire a `preset` param through both POST routes and a minimal picker (Square, Circle). Add zxing-cpp as a dev dependency and a decode test helper.

## Boundaries & Constraints

**Always:** Square is the default and its PNG output stays byte-identical to today's. `preset` is whitelist-validated against the table keys; unknown values fall back to `square`. Reuse `_render_qr`, `_load_logo` and the logo geometry helpers; no forked pipeline. Eye frames stay 1:1 so the 1:1:3:1:1 ratio holds. The preset JSON is shared and read, not duplicated, so later stories can serve it to the thumbnail JS. SVG stays vector. Update the Dockerfile so `presets.json` ships in the image.

**Never:** The other five presets, thumbnails, color or gradient, the scan check, logo fade or any logo change, `/api/qr` changes (story 11 removes it), runtime zxing-cpp (story 7), UI restructure (story 13).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Default | no `preset` | Square; PNG bytes equal today's | No error expected |
| Circle PNG/SVG | `preset=circle` | Circular dots and circular eyes; decodes to the input | No error expected |
| Unknown preset | `preset=diamond` | Falls back to Square | No 4xx |
| Circle with logo | `preset=circle` plus `logo` | Renders, logo centered, still decodes | `LogoError` as today |
| GET shim | `/api/qr` | Unchanged, Square | Unchanged |

</frozen-after-approval>

## Code Map

- `qr_generator.py` -- `_parse_common` (L214) returns a 6-tuple used by both POST handlers; add `preset` here. `_make_qr_png` (L303) and `_make_qr_svg` (L331) use qrcode's own images; `_render_qr` (L370) is the shared entry; `_logo_geometry`, `_snap_pad_rect`, `_fit_logo` are reusable as-is. `/api/qr` (L451) calls the two makers directly: keep it Square and untouched.
- `presets.json` (new, repo root) -- `{square: {dot, frame, ball}, circle: {...}}` plus display `name`; loaded once at import.
- `templates/qr_generator.html` -- picker goes before "Output Format" (L928); `collectFormData` (L1112) appends `preset`. Single file, no build step.
- `tests/conftest.py`, `tests/test_helpers.py`, `tests/test_routes.py` -- add a decode helper (zxing-cpp, `zxingcpp.read_barcodes` on a PIL image; for SVG, rasterise first) and tests.
- `Dockerfile` (L15-18) -- add `COPY presets.json .`.
- `pyproject.toml` / `uv.lock` -- `uv add --dev zxing-cpp`. Container pip fails behind the dev machine's TLS interception, so the dev dependency does not affect `--no-dev` image builds.
- Do not change: `_load_logo`, `_security_headers`, limits, `/api/qr`.

## Tasks & Acceptance

**Execution:**
- [ ] `pyproject.toml`, `uv.lock` -- `uv add --dev zxing-cpp` -- decoder for tests
- [ ] `presets.json` -- Square and Circle rows -- single source of truth
- [ ] `qr_generator.py` -- load table; `_safe_preset`; thread `preset` through `_parse_common`, both handlers and `_render_qr`; one module-matrix renderer for PNG and SVG; Square keeps the existing code path so bytes match -- shared renderer
- [ ] `templates/qr_generator.html` -- two-option radio picker, sent as `preset` -- minimal UI
- [ ] `Dockerfile` -- copy `presets.json` -- ships the table
- [ ] `tests/` -- decode helper; Square golden-bytes check against the baseline; Circle decodes on PNG and SVG, with a logo, and at several data lengths; unknown preset falls back; matrix rows above -- coverage

**Acceptance Criteria:**
- Given no `preset`, when generating PNG, then the bytes equal the baseline Square output.
- Given `preset=circle`, when generating PNG or SVG, then the code decodes to the input and the SVG has no raster image except an uploaded logo.
- Given Circle selected in the UI, when Generate is pressed, then the preview shows round dots and round eyes.
- Given `uv run pytest`, then the whole suite passes.

## Implementation Notes

## Plan Change Log

## Review Triage Log

Pass 1 (quick): high 0, medium 0, low 4, false 1, unverified-AC 1.

| Finding | Verdict | Route | Evidence |
|---|---|---|---|
| Logo overlay copied into styled PNG/SVG makers | low | rejected | About 10 duplicated lines; the plan named the geometry helpers as the reuse set. Story 8 reworks logo rendering and story 12 is the refactor sweep. |
| `preset` appended to the `_parse_common` tuple, not "at the top" | false | rejected | CLAUDE.md's "top of `_parse_common`" is about where the parsing goes; the return shape is internal and both callers are updated. |
| Styled SVG honors `fg`, Square SVG does not; pad rect shows on transparent bg | false | rejected | Square SVG behavior is pre-existing and unchanged; colour is out of scope for this story. |
| Style picker shown in barcode mode | low | patch | Other QR-only sections hide via the format toggle (L1010-1015). Fixed: wrapped in `#preset-options`, toggled with `color-options`. |
| CLAUDE.md omits `presets.json` and the `preset` param | low | defer | The fix edits an agent-context file. Recorded in `deferred-work.md`. |
| UI acceptance criterion untested | n/a | not a defect | No browser check was run; listed as a manual check at presentation. |

## Design Notes

Eye detection comes from the finder positions (three 7x7 corner blocks), drawn as frame (ring) and ball (3x3 center) per the row; all other modules are dots. A per-module draw means one code path serves every later preset; Circle PNG draws at a supersampled scale and downsizes.

## Verification

**Commands:**
- `uv run pytest` -- expected: all pass, including the new decode tests

**Manual checks (if no CLI):**
- Run the app, select Circle, Generate on PNG and SVG; the code shows circular dots and eyes. Scan it with a phone.
