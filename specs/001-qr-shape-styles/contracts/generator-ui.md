# Contract: Generator UI "Shape style" Section

Page: `GET /generator` (`templates/qr_generator.html`).

## Placement and visibility

- There is a new block inside the existing `#qr-options` container, after "Error Correction",
  with a section title of **"Shape style"**.
- It is visible only in QR code mode. `#qr-options` is already toggled by the format pills, so no
  new toggle logic is needed (FR-006, and the barcode edge case).

## Controls

There are three radio groups, one per parameter. Each option is a
`<label class="shape-opt"><input type="radio" name="…" value="…">…swatch…</label>`:

| Group label | `name` | Options (in order) | Initially checked |
|---|---|---|---|
| Dot shape | `dot_shape` | 9 dot values, in contract order | `square` |
| Eye border | `eye_border` | 7 border values, in contract order | `square` |
| Eye center | `eye_center` | 5 center values, in contract order | `square` |

- Each option shows a **visual swatch**: an inline SVG generated server-side from the
  production geometry (research §8). The option name goes in `title` and `aria-label`, so the
  control is not text-only but stays accessible.
- The checked state is shown visually (an outline or background like `.ec-btn.active`). The
  radios stay keyboard-operable.
- Swatches follow `currentColor`, so they work in both light and dark theme.

## Behavior

- `collectFormData()` appends `dot_shape`, `eye_border`, and `eye_center` (the checked values)
  when `currentFormat === 'qrcode'`.
- Changing any shape radio triggers `generate()` if a preview is currently displayed (FR-007).
  Downloads reuse `collectFormData()`, so they match the preview.
- The GA `generate` event includes the three values in QR mode and `null` otherwise, following
  the pattern of `ec_level`.
- The API URL display picks up the new fields automatically through `updateApiUrl(fd)`.

## Non-goals

- No per-eye styling and no eye colors (spec Assumptions).
- The state is not persisted across page loads.
