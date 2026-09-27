# Implementation Plan: QR Code Shape Styles (Dots & Eyes)

**Branch**: `001-qr-shape-styles` (lands on `main` per constitution) | **Date**: 2026-09-27 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-qr-shape-styles/spec.md`

## Summary

Add three independent, optional QR styling choices — **dot shape** (9 options), **eye border**
(7 options), **eye center** (5 options) — to the generator UI and to all three QR routes
(`POST /api/generate`, `POST /api/generate/download`, `GET /api/qr`).

Technical approach (see [research.md](research.md)):

- Take the module matrix from `qrcode`. Describe every styled element as one geometry primitive,
  a **rounded rectangle with per-corner flags** in module units, emitted by a new pure-Python
  module `qr_shapes.py`.
- Draw that single geometry two ways. **PNG** goes to a supersampled Pillow `L` mask, which is
  downscaled with LANCZOS and composited fg-over-bg. **SVG** goes to vector `<path>` data.
  No new runtime dependencies.
- When all three choices are `square`, which is the default, `_make_qr_png` / `_make_qr_svg`
  take the **existing code path unchanged**. That gives byte-identical output for existing
  consumers (FR-011, SC-002).
- Parse the new params once in a shared `_parse_shape_style()` whitelist helper, used by
  `_parse_common` and `/api/qr`. Unknown values fall back to `square` (FR-012).
- UI: a "Shape style" section inside `#qr-options` with swatch radio groups. The swatch SVGs are
  **generated server-side by the same geometry code**, so swatches always match output.

## Technical Context

**Language/Version**: Python 3.9 in production (`python:3.9-slim`), so code MUST stay
3.9-compatible (no `match`, no `X | Y` annotations). Local dev currently has Python 3.14.

**Primary Dependencies**: Flask, `qrcode[pil]` (matrix only on the styled path), Pillow ≥10
(`ImageDraw` rectangle/pieslice), python-barcode (unchanged). **No new runtime deps.**

**Storage**: N/A (stateless, Principle I).

**Testing**: pytest (`python3 -m pytest`). Add **dev-only** `zxing-cpp` to decode rendered PNGs
for the FR-014 / SC-001 exhaustive 315-combination decode test.

**Target Platform**: Linux container (Gunicorn), behind Cloudflare Tunnel; UI in modern browsers.

**Project Type**: Single-container web service (Flask blueprint + one Jinja template).

**Performance Goals**: Styled render ≤ ~50 ms at default size (spike: ~5 ms for a 300 px
URL code). Preview responsiveness unchanged (SC-005).

**Constraints**: The supersample canvas side is capped at 4096 px (≤16 MiB `L` mask) for every
input within `MAX_SIZE` / `MAX_DATA_LEN`. `/api/qr` response type and cache headers are
unchanged (FR-013). Styled SVG keeps today's SVG color behavior: black shapes, no background
(spec Assumptions).

**Scale/Scope**: 9 × 7 × 5 = 315 combinations. The changes touch `qr_generator.py`,
the new `qr_shapes.py`, `templates/qr_generator.html`, `Dockerfile` (COPY the new module), tests,
and docs (`README.md`, `CLAUDE.md`, `docs/INTEGRATIONS.md`).

No NEEDS CLARIFICATION items remain. All were resolved in [research.md](research.md).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Assessment | Status |
|---|---|---|
| I. Stateless & Self-Contained | Styled output is computed from request params only. No storage, no new services. | ✅ Pass |
| II. Stable Public Contracts | New params are optional with safe defaults. Absent or all-`square` values take the legacy path byte-for-byte. `/api/qr` keeps raw image bytes, `image/*`, and `Cache-Control: public, max-age=86400, immutable`. The JSON envelope is unchanged, so any embedder of `/api/qr` is unaffected. | ✅ Pass |
| III. Whitelist Validation & Bounded Resources | `_parse_shape_style` does an exact-match lookup against three frozen whitelists, falling back to `square`. Rendering memory is bounded by the 4096 px canvas cap. Existing limits are unchanged. No per-route header overrides. | ✅ Pass |
| IV. Single Rendering Path | Shapes go through the existing `_make_qr_png` / `_make_qr_svg` via a new `shape` argument. Params are parsed once in the shared layer. All three routes call the same helpers. `qr_shapes.py` is a geometry library those helpers call, not a parallel route path. | ✅ Pass |
| V. Tested Behavior | New tests cover the parser (valid, invalid, case, missing), geometry units, route acceptance on all three endpoints, legacy byte-identity, decoding all 315 combos, barcode ignoring shapes, and log fields. | ✅ Pass |
| VI. Structured Observability | `dot_shape`, `eye_border`, `eye_center` (normalized whitelist values) are added to QR `generate` / `download` / `qr_embed` success events. The payload is never logged. | ✅ Pass |
| Ops: new dependency justification | `zxing-cpp` is **dev-only** (`requirements-dev.txt`) and not installed in the image. Justification is in research.md §6. | ✅ Pass |
| Workflow: docs updated with route changes | README `/api/qr` param table, CLAUDE.md route notes and repo layout, and docs/INTEGRATIONS.md are updated in the same change. | ✅ Planned |

**Post-design re-check (after Phase 1)**: The data model, contracts, and quickstart introduce no
state, no new required params, no header changes, and no forked routes. All gates still pass.
Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/001-qr-shape-styles/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   ├── http-params.md   # Shape params on /api/generate, /api/generate/download, /api/qr
│   └── generator-ui.md  # "Shape style" UI section contract
├── assets/              # Reference images (authoritative visuals)
├── checklists/
└── tasks.md             # Phase 2 output (/speckit-tasks, not created here)
```

### Source Code (repository root)

```text
qr_generator.py          # + _parse_shape_style(), ShapeStyle wiring into _parse_common,
                         #   _make_qr_png/_make_qr_svg(shape=...), route + log changes,
                         #   generator() passes swatch SVGs to the template
qr_shapes.py             # NEW: whitelists, ShapeStyle, geometry (module matrix → primitives),
                         #   PNG mask rasterizer, SVG path emitter, swatch SVG builder
templates/
└── qr_generator.html    # + "Shape style" section in #qr-options, swatch CSS, JS form fields
Dockerfile               # + COPY qr_shapes.py
requirements-dev.txt     # + zxing-cpp (tests only)
tests/
├── test_helpers.py      # + _parse_shape_style cases
├── test_shapes.py       # NEW: geometry/corner-rule units, canvas cap, SVG validity
└── test_routes.py       # + shape params on 3 routes, legacy byte-identity, 315-combo decode,
                         #   barcode ignores shapes, log fields
README.md, CLAUDE.md, docs/INTEGRATIONS.md   # param docs (FR-016)
```

**Structure Decision**: Keep the existing single-project layout. Geometry and rasterization live
in a new module `qr_shapes.py`, because they are pure and unit-testable and would roughly double
`qr_generator.py` otherwise. Route wiring, parsing, and logging stay in `qr_generator.py`,
following the constitution's shared-helper conventions.

## Complexity Tracking

No constitution violations. Nothing to justify.
