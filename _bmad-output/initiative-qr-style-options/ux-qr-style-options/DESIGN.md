---
name: QR Code Generator
description: Visual identity for the self-hosted QR generator page, extracted from the existing templates/qr_generator.html and extended with style-option components. Dark by default, light theme available.
status: final
updated: 2026-10-06
sources:
  - ../../epic-qr-style-options/spec-qr-style-options/spec-qr-style-options.md
  - ../../../templates/qr_generator.html
colors:
  # Extracted from templates/qr_generator.html :root and [data-theme="light"],
  # then extended for AA contrast. Dark values are the base; -light are overrides.
  bg: '#0f1117'
  surface: '#1a1d27'
  surface-2: '#22263a'
  border: '#2e3347'
  input-bg: '#12141e'
  text: '#e8eaf6'
  text-muted: '#8b91b0'
  accent: '#6c63ff'
  accent-text: '#8b84ff'
  accent-fill: '#5b52f0'
  accent-fill-end: '#7c3aed'
  accent-fill-foreground: '#ffffff'
  accent-2: '#00d4aa'
  danger: '#ff5c7c'
  danger-foreground: '#0f1117'
  success: '#00d4aa'
  code-background: '#ffffff'
  control-border: '#8b91b0'
  focus-ring: '#e8eaf6'
  bg-light: '#f0f2f8'
  surface-light: '#ffffff'
  surface-2-light: '#f5f7ff'
  border-light: '#dde2f0'
  input-bg-light: '#f8f9ff'
  text-light: '#1a1d2e'
  text-muted-light: '#5b6270'
  accent-text-light: '#5b52f0'
  accent-2-light: '#007a63'
  danger-light: '#c4234a'
  danger-foreground-light: '#ffffff'
  control-border-light: '#5b6270'
  focus-ring-light: '#1a1d2e'
  # accent (rings, glows, slider thumbs), accent-fill, accent-fill-end,
  # accent-fill-foreground, accent-2 as a fill or border, code-background
  # and success are shared across themes.
typography:
  # Font stack: Inter, then system sans. Sizes extracted from the page CSS;
  # section-title and hint raised slightly for legibility.
  body:
    fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif'
    fontSize: 0.875rem
    fontWeight: '400'
    lineHeight: '1.5'
  label:
    fontSize: 0.78rem
    fontWeight: '500'
  section-title:
    fontSize: 0.7rem
    fontWeight: '700'
    letterSpacing: 0.1em
  button:
    fontSize: 0.82rem
    fontWeight: '600'
  hint:
    fontSize: 0.75rem
    fontWeight: '400'
  mono:
    fontFamily: monospace
    fontSize: 0.82rem
rounded:
  sm: 8px
  md: 12px
  lg: 20px
  pill: 20px
  full: 9999px
spacing:
  # Page uses rem steps rather than a numeric scale.
  field-gap: 0.9rem
  section-gap: 1.5rem
  panel-padding: 1.5rem
  control-gap: 6px
  row-gap: 12px
  strip-padding: 6px
sizing:
  target-min: 24px
  target-touch: 44px
  preset-thumbnail: 72px
  saved-logo-tile: 56px
  direction-button: 44px
  scrollbar: 12px
  preview-frame: 280px
components:
  section-title:
    typography: '{typography.section-title}'
    color: '{colors.text-muted}'
  preset-strip:
    gap: '{spacing.row-gap}'
    padding: '{spacing.strip-padding}'
    overflow: 'x scroll, scrollbar always visible, {sizing.scrollbar} thick'
  preset-thumbnail:
    size: '{sizing.preset-thumbnail}'
    background: '{colors.code-background}'
    border: '1px solid {colors.control-border}'
    radius: '{rounded.sm}'
    artwork: 'drawn in the user chosen colors or gradient'
  preset-thumbnail-selected:
    ring: '2px solid {colors.accent}'
    ring-offset: '2px'
  color-mode-toggle:
    background: '{colors.surface-2}'
    border: '1px solid {colors.control-border}'
    radius: '{rounded.pill}'
    active-background: '{colors.accent-fill}'
    active-foreground: '{colors.accent-fill-foreground}'
  color-field:
    background: '{colors.input-bg}'
    border: '1px solid {colors.border}'
    radius: '{rounded.sm}'
  direction-buttons:
    size: '{sizing.direction-button}'
    background: '{colors.surface-2}'
    border: '1px solid {colors.control-border}'
    radius: '{rounded.sm}'
    selected-ring: '2px solid {colors.accent}'
  contrast-warning:
    color: '{colors.danger}'
    color-light: '{colors.danger-light}'
    border: '1px solid {colors.danger}'
    border-light: '1px solid {colors.danger-light}'
    background: 'danger at 12% alpha over the surface'
    radius: '{rounded.sm}'
  fix-button:
    background: '{colors.danger}'
    foreground: '{colors.danger-foreground}'
    background-light: '{colors.danger-light}'
    foreground-light: '{colors.danger-foreground-light}'
    radius: '{rounded.sm}'
    min-height: '{sizing.target-min}'
  logo-drop-zone:
    background: '{colors.input-bg}'
    border: '1px dashed {colors.border}'
    radius: '{rounded.sm}'
  saved-logo-strip:
    gap: '{spacing.row-gap}'
    padding: '{spacing.strip-padding}'
    overflow: 'x scroll, scrollbar always visible, {sizing.scrollbar} thick'
  saved-logo-tile:
    size: '{sizing.saved-logo-tile}'
    background: '{colors.surface-2}'
    border: '1px solid {colors.control-border}'
    radius: '{rounded.sm}'
    selected-ring: '2px solid {colors.accent}'
  saved-logo-delete:
    target: '{sizing.target-min} minimum, glyph smaller than the target'
    placement: 'inside the tile corner, shown on the selected or focused tile'
  logo-size-slider:
    track: '{colors.border}'
    thumb: '{colors.accent}'
    value-text: '{colors.accent-text}'
  logo-background-toggle:
    track-on: '{colors.accent-fill}'
    track-off: '{colors.border}'
  error-correction-control:
    selected-background: 'accent at 20% alpha'
    selected-border: '{colors.accent}'
    selected-text: '{colors.accent-text}'
    locked-selected: 'full contrast, with a lock glyph'
    locked-others: 'reduced opacity (disabled)'
  preview-frame:
    size: '{sizing.preview-frame}'
    background: '{colors.code-background}'
    border: '2px solid {colors.accent}'
    radius: '{rounded.md}'
  preview-frame-empty:
    background: '{colors.surface-2}'
    border: '2px dashed {colors.border}'
    radius: '{rounded.md}'
    content: 'faded icon above the text "Configure and generate"'
  scan-warning-banner:
    color: '{colors.danger}'
    color-light: '{colors.danger-light}'
    border: '1px solid {colors.danger}'
    border-light: '1px solid {colors.danger-light}'
    background: 'danger at 12% alpha over the surface'
    radius: '{rounded.sm}'
  banner-success:
    color: '{colors.accent-2}'
    color-light: '{colors.accent-2-light}'
    border: '1px solid {colors.accent-2}'
    border-light: '1px solid {colors.accent-2-light}'
    background: 'accent-2 at 10% alpha over the surface'
  banner-error:
    color: '{colors.danger}'
    color-light: '{colors.danger-light}'
    border: '1px solid {colors.danger}'
  generate-button:
    background: 'linear-gradient(135deg, {colors.accent-fill}, {colors.accent-fill-end})'
    foreground: '{colors.accent-fill-foreground}'
    radius: '{rounded.md}'
  generate-button-floating:
    shape: '{rounded.full}'
    offset-bottom: '12px'
    shadow: '0 6px 24px rgba(0,0,0,0.5)'
  download-buttons:
    background: '{colors.surface-2}'
    border: '1px solid {colors.border}'
    foreground: '{colors.text}'
    radius: '{rounded.sm}'
  focus-ring:
    outline: '3px solid {colors.focus-ring}'
    outline-offset: '2px'
  fix-cue:
    outline: '2px solid {colors.accent}'
    duration: '1.5s, with a persistent note beside the control'
---

## Brand & Style

A compact utility tool, not a marketing page. The page reads as a calm dark workbench: a form column on the left, the code on the right, one violet accent for "this is selected or primary" and one teal accent for "confirmed". The existing look is kept as is. The style options are additions that must feel native: same pills, rings, borders and radii, no new decorative language. The page ships dark by default with a light theme behind the header toggle; both themes are in scope for every component below.

## Colors

Tokens extracted from the current page keep their values. Where the extraction failed AA contrast, a derived token is added next to it (`accent-fill`, `accent-text`, `accent-2-light`, `text-muted-light`, `control-border`); the originals stay for non-text uses. Contrast ratios below were calculated by hand and cross-checked by the accessibility review, not tool-verified; re-check in build.

- **`{colors.bg}` / `{colors.surface}` / `{colors.surface-2}`** layer the page: page background, panels and cards, then raised controls and unselected buttons.
- **`{colors.accent}` (violet)** marks selection as a non-text cue: rings, slider thumbs, the Fix cue outline. It is never used for warnings.
- **`{colors.accent-fill}`** (about 5.4:1 with white) is the fill behind white text: active tab, active color mode, logo background toggle, the Generate gradient start. The Generate gradient ends at `{colors.accent-fill-end}` (about 5.7:1 with white). The original `{colors.accent}` with white text is about 4.3:1 and is no longer used for filled text.
- **`{colors.accent-text}`** (dark, about 5.5:1 on surface) and `{colors.accent-text-light}` (light) are for accent-colored text: selected EC level, slider values.
- **`{colors.accent-2}` (teal)** marks confirmation: the Generated banner and content pills. In light theme `{colors.accent-2-light}` (about 5.3:1 on white) replaces it for text and borders; the bright teal is about 1.9:1 on white.
- **`{colors.danger}`** marks problems the user must act on: the scan warning, the contrast warning, delete confirm, errors. Nothing else. Dark: about 5.7:1 on surface for text; the Fix button uses `{colors.danger-foreground}` text on it (about 6.4:1) because white on that fill is about 3:1. Light: `{colors.danger-light}` (about 5.7:1 on white) with `{colors.danger-foreground-light}` text on the fill. Banner text is checked on its own 12% tint (about 4.8:1 dark, 4.7:1 light), which has little margin; keep the tint at or below 12%.
- **`{colors.text-muted}`** for labels, hints and section titles. Light theme uses `{colors.text-muted-light}` (about 5.4:1 on `{colors.bg-light}`); the extracted `#6b7280` is about 4.3:1 there.
- **`{colors.control-border}`** (the muted text color, about 5.4:1 on surface) outlines new interactive controls so each meets the 3:1 non-text boundary. The extracted `{colors.border}` is about 1.3 to 1.5:1 and stays for panels, cards, inputs and dividers.
- **`{colors.code-background}`** is white: the background of every rendered code and every preset thumbnail, regardless of theme.
- **`{colors.focus-ring}`** is the high-contrast focus indicator in each theme.

The generated code's own colors (foreground, gradient stops, background) are user data and never theme the page.

[ASSUMPTION] "Decodable contrast" for the contrast warning is a luminance contrast of at least 4:1 between every module color (each gradient stop) and the background, with modules darker than the background. The real threshold comes from the scan test and is set in architecture; this value is a starting point, not a user decision.

## Typography

Inter, then system sans. Section titles are small uppercase tracked labels (`{typography.section-title}`, raised from 0.65rem to 0.7rem); field labels `{typography.label}`; buttons `{typography.button}`; hex values and URLs in `{typography.mono}`. Hints under controls use `{typography.hint}` (raised to 0.75rem). No display type. Text-bearing controls use `min-height`, never a fixed height, so they survive user text-spacing overrides.

## Layout & Spacing

Two-column grid: a 420px form panel on the left and the preview panel on the right, 1400px max width. The form panel scrolls; the preview panel is sticky below the 60px header on wide, tall viewports and is static below 900px and on short viewports. Below 900px it becomes one column with the preview under the form. The layout must hold at 320 CSS px wide: the preview frame is `max-width: 100%` of `{sizing.preview-frame}`, and two-column field rows stack. Sections are separated by `{spacing.section-gap}` with a section title above each; fields use `{spacing.field-gap}`; tight control groups use `{spacing.control-gap}`.

Section order within each column is defined in EXPERIENCE.md, Information Architecture.

Interactive targets are at least `{sizing.target-min}` square, and `{sizing.target-touch}` on coarse pointers where space allows.

## Elevation & Depth

Depth comes from tone, not shadow: `{colors.bg}` to `{colors.surface}` to `{colors.surface-2}`. The only shadows are the preview card's soft drop shadow and the floating Generate button's. Selection is shown with a ring, not elevation.

## Shapes

`{rounded.sm}` (8px) for inputs, thumbnails and small buttons; `{rounded.md}` (12px) for the Generate button and the preview frame; `{rounded.lg}` (20px) for the preview card; pills (`{rounded.pill}`) for format tabs, content pills and the color mode toggle; `{rounded.full}` for the floating Generate button. Preset thumbnails are square crops with `{rounded.sm}`.

## Components

Visual specs only; behavior lives in EXPERIENCE.md. Component names are identical in both files. Components inherited unchanged from the current page: Format tabs, Content pills, Content fields, Size and Margin sliders, the theme toggle, the header, the spinner, and the Preview card chrome.

- **Preset strip** — one row of Preset thumbnails with `{spacing.row-gap}` between them, in a container that scrolls horizontally with a visible, `{sizing.scrollbar}`-thick scrollbar.
- **Preset thumbnail** — `{components.preset-thumbnail}`: a `{sizing.preset-thumbnail}` square, always on a `{colors.code-background}` tile, with the artwork drawn in the user's chosen colors or gradient.
- **Preset thumbnail (selected)** — `{components.preset-thumbnail-selected}`: a 2px `{colors.accent}` ring with a 2px gap. The ring is a shape cue and carries the selection; the color is secondary. Rings use `outline` so they survive forced-colors modes. The strip's padding (`{spacing.strip-padding}`) is at least the ring width plus offset so the ring is never clipped.
- **Color mode toggle (Solid | Gradient)** — pill container, `{components.color-mode-toggle}`; the active option fills with `{colors.accent-fill}` and white text.
- **Color field** — swatch plus monospace hex, as today. Gradient mode shows two of them, first and second color, plus the background field.
- **Direction buttons** — five icon buttons (horizontal, vertical, diagonal down-right, diagonal up-right, radial), `{components.direction-buttons}`; the selected one gets the ring.
- **Contrast warning** — `{components.contrast-warning}`, directly under the color fields: a small icon, a plain-language message naming the offending color, and a Fix button. Text uses the theme's danger color.
- **Logo drop zone** — as today, `{components.logo-drop-zone}`.
- **Saved logo strip** and **Saved logo tile** — `{components.saved-logo-strip}` holding `{components.saved-logo-tile}` items; the selected tile gets the same ring. The logo's name is shown in the drop zone summary for the selected logo.
- **Saved logo delete** — `{components.saved-logo-delete}`: a delete glyph inside the tile corner, shown on the selected or focused tile. Its hit area is at least `{sizing.target-min}`. Confirming swaps it in place for "Delete? Yes / No" buttons, each at least `{sizing.target-min}`.
- **Logo size slider** — a native range input, 10 to 30, with the value shown at the right in `{colors.accent-text}` as today.
- **Logo background toggle** — the switch used elsewhere on the page.
- **Error correction control** — four buttons as today. When locked, the locked H keeps full contrast and shows a lock glyph; the other three drop to a disabled opacity. A hint line in `{typography.hint}` gives the reason.
- **Preview frame** — `{components.preview-frame}`: the generated PNG on `{colors.code-background}`, with the accent border when a code is shown.
- **Preview frame (empty)** — `{components.preview-frame-empty}`: the initial state, shown on first load and again whenever the inputs change after a code was generated. A faded icon over the text "Configure and generate" on `{colors.surface-2}`, with a dashed border. The old code is not shown.
- **Scan warning banner** — `{components.scan-warning-banner}`: icon, message, and a Fix button. Sits between the code area and Generate. When no fix remains, the banner has no button.
- **Banner (success and error)** — `{components.banner-success}` for "Generated"; `{components.banner-error}` for generation and validation errors, both as today but with theme-aware text colors.
- **Generate button** — `{components.generate-button}`, full width. Disabled uses the existing 0.5 opacity.
- **Generate button (floating)** — at 900px and below, a full-width pill, `{components.generate-button-floating}`, pinned 12px above the bottom of the viewport. Same fill and disabled treatment.
- **Download buttons** — `{components.download-buttons}`, two side by side. Disabled uses 0.4 opacity. When a scan warning is active each carries a warning glyph (decorative; the warning is conveyed in text).
- **Focus ring** — `{components.focus-ring}` on every interactive element, drawn with `outline`, never a box-shadow glow. This replaces the extracted 15%-alpha glow for focus; the old glow is not a valid focus indicator.
- **Fix cue** — `{components.fix-cue}`: when Fix changes a control, that control gets a brief outline and a persistent note beside it. The outline is decoration; the note is the cue.

Forced-colors mode: selection, focus and state cues use `outline` and borders, and the empty and filled preview frames differ by border style (dashed versus solid).

→ Visual reference: `mockups/key-generator-default.html` (default path, wide; narrow empty state with the floating Generate) and `mockups/key-generator-styled-warning.html` (Fluid, gradient, saved logo and scan warning, dark and light). The mocks illustrate; this spine wins on conflict. Their codes are not scannable.

## Do's and Don'ts

| Do | Don't |
|---|---|
| Show selection with a ring plus color | Show selection with color alone |
| Reuse existing pills, tabs, borders and radii | Introduce new corner styles or new accent colors |
| Reserve `{colors.danger}` for things the user must act on | Use danger for decoration or hover |
| Draw preset thumbnails in the user's chosen colors on a white tile | Override the user's colors with a "safe" pair |
| Keep the scrollbar visible on the preset and logo strips | Hide scrollbars or use fade-only scroll hints |
| Give new interactive controls a `{colors.control-border}` boundary | Rely on the 1.3:1 panel border to identify a control |
| Draw focus and selection with `outline` | Use a translucent box-shadow glow as the only indicator |
| Design every component for dark and light themes | Hard-code a theme-specific value into a component |
