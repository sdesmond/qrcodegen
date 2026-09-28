# Data Model: QR Code Shape Styles

This feature adds no persisted data (Principle I). The "entities" below are in-memory value types
that are computed per request.

## ShapeStyle

A value object holding the three styling choices for one QR render. It is immutable and hashable
(`NamedTuple`).

| Field | Type | Allowed values (display order) | Default |
|---|---|---|---|
| `dot` | str | `square`, `rounded`, `extra_rounded`, `dots`, `classy`, `classy_rounded`, `horizontal_bars`, `vertical_bars`, `gapped_square` | `square` |
| `eye_border` | str | `square`, `rounded`, `circle`, `teardrop`, `leaf`, `leaf_circle`, `square_circle` | `square` |
| `eye_center` | str | `square`, `rounded`, `circle`, `teardrop`, `leaf` | `square` |

**Validation** (`_parse_shape_style`):

- Read `dot_shape`, `eye_border`, `eye_center` from the form or query args and truncate each
  to 32 chars.
- Accept a value only on an exact, case-sensitive match in its whitelist. Anything else, including
  a missing value, becomes `square`. This never raises and never returns 4xx (FR-012).
- Fields are independent (FR-004). One invalid field doesn't affect the others.

**Derived**:

- `is_default` is `dot == eye_border == eye_center == 'square'`. When it is true, the render
  goes through the legacy path (research §4).

**Ordering**: The whitelists are ordered tuples. Their order is the UI display order (FR-001,
FR-002, FR-003), and the swatch template iterates over them.

## RRect (geometry primitive)

This is internal to `qr_shapes.py`. It is not exposed by any API.

| Field | Type | Meaning |
|---|---|---|
| `x`, `y` | float | Top-left corner, in module units, relative to the symbol origin (margin excluded) |
| `w`, `h` | float | Size in module units, both > 0 |
| `r` | float | Corner radius in module units, clamped to `min(w, h) / 2` when drawn |
| `corners` | (bool, bool, bool, bool) | Which corners are rounded: TL, TR, BR, BL |
| `ink` | 1 or 0 | 1 paints foreground; 0 cuts an opening (eye rings) |

**Invariants**:

- Every eye primitive lies inside its 7×7 finder box.
- Every opening lies inside the 5×5 inner box.
- Every center lies inside the 3×3 box.
- Every dot primitive lies inside its own 1×1 cell.
- No primitive extends beyond `[0, n]²`, where n is the module count, so margin=0 never clips.

## Render plan

`build_primitives(matrix, style)` returns `(dots, eyes)`, two lists of `RRect`:

1. Mark the three finder boxes, 7×7 at (0,0), (0,n−7), (n−7,0), as excluded from dot drawing.
2. For each dark, non-excluded module, emit its dot primitive. Neighbours are looked up only
   among dark, non-excluded modules, using the corner rules in research §5.
3. For each finder box, emit the outer border (ink 1), the opening (ink 0), and the center
   (ink 1), in that order.

**Consumers**:

- `rasterize_png(dots, eyes, n, margin, size, fg, bg)` returns PNG bytes. It uses a supersampled
  `L` mask with the canvas capped at 4096 px, then does a LANCZOS resize and composites.
- `to_svg(dots, eyes, n, margin, size)` returns SVG text: a viewBox in module units, mm
  `width`/`height` computed like the legacy SVG (research §2), a dots `<path>`, and an eyes
  `<path fill-rule="evenodd">`.

Both consumers read the same primitive lists. The geometry-parity test depends on this.

## State transitions

None. Each request is independent and deterministic: the same inputs always produce the same
bytes, which is what lets `/api/qr` keep its `immutable` cache header.
