---
name: QR Code Generator
status: final
updated: 2026-10-06
sources:
  - ../../epic-qr-style-options/spec-qr-style-options/spec-qr-style-options.md
  - ../../epic-qr-style-options/spec-qr-style-options/presets.md
  - ../../epic-qr-style-options/spec-qr-style-options/scope.md
  - ../../epic-qr-style-options/epic-qr-style-options.md
  - ../../brainstorm-qr-style-options/brainstorm-qr-style-options.md
  - ../../../templates/qr_generator.html
---

# QR Code Generator — Experience Spine

## Foundation

Single page, responsive web, no UI library: hand-written CSS in `templates/qr_generator.html`. A LAN-only, self-hosted tool with no accounts. `DESIGN.md` is the visual identity reference (extracted from the current page). This spine covers the style-options feature (CAP-1 to CAP-9) and the form restructure it required. The default path stays content, Generate, Download in under 30 seconds; all styling is opt-in.

CAP-9 (private platform, removal of the GET shim and tunnel notes) has no UX surface beyond the two removals recorded in Information Architecture.

**Deviation from the spec.** CAP-6 and the brainstorm say the old code stays visible but dimmed while stale. By user decision, a stale code is instead replaced by the empty state ("Configure and generate"). The spec's CAP-6 wording needs updating to match.

### CAP trace

| CAP | Where it lands |
|---|---|
| CAP-1 Shape presets | Preset strip; Flow 2 |
| CAP-2 Preset thumbnails | Preset thumbnail; Flow 2 step 3 |
| CAP-3 Color | Color mode toggle, Color field, Direction buttons, Contrast warning; Flow 2 |
| CAP-4 Logo upgrade | Logo drop zone, Logo size slider, Logo background toggle; Flow 2; Logo rejected state |
| CAP-5 Scan check | Scan warning banner; Flow 2; Scan warning rules |
| CAP-6 Generate/Download state | Generate button, Download buttons, Preview frame (empty); State Patterns |
| CAP-7 SVG print path | Download buttons; Flow 3 |
| CAP-8 Saved logo library | Saved logo strip, Saved logo tile; Flows 2 to 4 |
| CAP-9 Private platform | No UX beyond the IA removals |

## Information Architecture

One surface with two panels. Landmarks: `header`, `main` containing the form and a preview region labelled "Preview". Each form section has a real heading (`h2`) styled as the section title.

| Panel | Section | Contents | Shown for |
|---|---|---|---|
| Form (left) | Content | Format tabs, Content pills, content fields | All formats |
| Form (left) | Code Settings | Size, Margin, Error correction control; Bar Height and Show Text on barcode tabs | All formats (Error correction on QR only) |
| Form (left) | Colors | Color mode toggle, Color fields, Direction buttons, Contrast warning | QR only |
| Form (left) | Logo | Logo drop zone, Saved logo strip, Logo size slider, Logo background toggle, errors | QR only |
| Form (left) | Style | Preset strip | QR only |
| Preview (right) | Code | Preview frame, Scan warning banner, banners | All formats |
| Preview (right) | Actions | Generate button, Download buttons | All formats |

Removed from the current page: the Output Format radio (the preview is always PNG; Download picks the file format) and the Copy URL row (it showed a POST route). No section is collapsed. Style choices persist when the user switches format tabs and returns. On barcode tabs the QR-only sections are removed from the page (not just hidden visually), and a one-line hint under the Format tabs says "Colors, Logo and Style are available for QR codes only."

→ Composition reference: `mockups/key-generator-default.html` (default path, wide, and the narrow empty state with the floating Generate button) and `mockups/key-generator-styled-warning.html` (styled code with a scan warning, dark and light). The spines win on conflict with these mocks; the mocks' codes are illustrative and not scannable.

## Voice and Tone

Microcopy. Brand voice lives in `DESIGN.md`. Wording confirmed by the user unless marked otherwise.

| Do | Don't |
|---|---|
| "This code may not scan: the logo covers too much." | "Warning! Scan check failed (code 3)." |
| "Make logo smaller (20% → 15%)" on the Fix button | "Fix" or "Auto-fix" with no named change |
| "Too large: 3.1 MB, max 2 MB" | "Upload failed." |
| "Library full ({cap}). Delete one to save this logo." | "Error: limit exceeded." |
| "Delete? Yes / No" in place | A modal "Are you sure?" |
| "Generated" | "Your QR code was successfully generated!" |
| "Configure and generate" in the empty preview | Text over or on a code; a faded old code |
| "Logo set: error correction locked to H so the code still scans." | "EC level disabled." |
| "Colors, Logo and Style are available for QR codes only." | Hiding sections with no explanation |

Messages name the problem, then the exact fix or limit. No exclamation marks, no blame. `{cap}` is the configured library cap (20 by default). [ASSUMPTION] The wording for the terminal scan message, the Fix-applied note, validation messages and the delete-fallback note is drafted in this spine and not reviewed by the user.

## Component Patterns

Behavioral. Visual specs live in `DESIGN.md.Components` under the same names.

| Component | Use | Behavioral rules |
|---|---|---|
| Format tabs | Content | Switching to a barcode tab removes Colors, Logo and Style; their choices are kept and return on the QR tab. Resets the preview to the empty state. Exposes the selected tab with `aria-pressed` (or tab semantics). |
| Content pills | Content | Choose the QR content type. Inherited as is. |
| Preset strip | Style | A radio group named "Shape preset" with all 7 presets, always showing, in one horizontally scrolling row with a visible scrollbar. Square selected by default. Selecting a preset resets the preview to the empty state. Roving tabindex: Tab enters at the selected item; arrow keys move focus and select; Home and End jump to the first and last; focus scrolls into view. No `tabindex` on the scroller itself. |
| Preset thumbnail | Style | A static crop of a demo QR (one eye plus some dots) drawn client-side from the shared preset table, in the chosen color or gradient, independent of the user's content. Each has an `aria-label` (its name) and an `aria-describedby` one-clause shape description. No `title` attribute and no visible name. |
| Color mode toggle | Colors | A radio group named "Color mode": Solid or Gradient. Gradient adds the second Color field and the Direction buttons. Switching back to Solid keeps the gradient values for return. |
| Color field | Colors | Swatch picker plus a hex text field labelled with its role ("Foreground color, hex"); the hex field is the accessible path and the swatch is supplementary. Applies to foreground, gradient second color and background. Invalid hex is flagged inline and not applied (see State Patterns). |
| Direction buttons | Colors | A radio group named "Gradient direction" with five options: horizontal, vertical, diagonal down-right, diagonal up-right, radial (first color at the center; the radial label says so). Same keyboard model as the Preset strip. |
| Contrast warning | Colors | Appears under the color fields when any chosen color (solid, or either gradient stop) falls below decodable contrast against the background. Names the offending color and offers one Fix button that adjusts that color to a passing value. Evaluates on commit (blur or color pick), not per keystroke. The offending field gets `aria-invalid` and `aria-describedby` to the warning. Clears when contrast passes. |
| Logo drop zone | Logo | A focusable control labelled "Add a logo": click or Enter opens the file picker; drag and drop is optional and never required. A client pre-check for type and size gives instant inline feedback; the server is authoritative. A rejected upload shows reason plus limit under the zone (associated with it through `aria-describedby`), never blocks the rest of the form, and leaves any previously selected logo in place. Shows an uploading state until the server accepts. |
| Saved logo strip | Logo | A radio group named "Saved logos", horizontally scrolling with a visible scrollbar, same keyboard model as the Preset strip. Selecting a tile is a single action. "Save to library" is opt-in after an upload. Instance-wide: other LAN users see and can delete the same logos. At the cap, saving shows "Library full ({cap}). Delete one to save this logo." and the logo can still be used unsaved. |
| Saved logo tile | Logo | Shows the logo; its accessible name is the stored file name. The Delete key on the focused tile starts delete, as does the tile's delete control. |
| Saved logo delete | Logo | Asks "Delete? Yes / No" in place, no modal. Focus moves to "No"; Esc cancels and returns focus to the tile; "Yes" deletes, moves focus to the next tile (or the drop zone when none remain) and announces "Logo deleted". If the deleted logo is in use, the code falls back to no logo with a note and the preview resets to the empty state. |
| Logo size slider | Logo | Native range input, 10 to 30 (% of code width), value shown beside it. Shown only while a logo is set. The soft fade is automatic and has no control. |
| Logo background toggle | Logo | A switch labelled "Background behind logo"; on by default. Shown only while a logo is set. |
| Error correction control | Code Settings | Four levels. Locked to H while a logo is set: the locked H stays at full contrast with a lock glyph, the others are disabled, and the reason "Logo set: error correction locked to H so the code still scans." appears here and in the Logo section. Restores the previous level when the logo is removed. |
| Scan warning banner | Preview | See Scan check rules below. A labelled group, not a live region; its content is announced through the Status region. |
| Preview frame | Preview | Shows the generated PNG with an accessible name stating what it encodes ("QR code for {content summary}", truncated). Receives focus (`tabindex="-1"`) after Generate on narrow screens. |
| Preview frame (empty) | Preview | The initial state, and the state the preview returns to whenever any input or preset changes after a code was generated. Text "Configure and generate". The old code is removed, so there is never a stale code on screen. |
| Generate button | Actions | Enabled when there is no current code (first load, or the inputs changed since the last generated code); disabled when the displayed code is current. Uses `aria-disabled` and stays focusable, with `aria-describedby` giving the reason ("Up to date"). Also triggered by Enter in a content field, only while enabled. At 900px and below it is the floating variant and, once generation finishes, the page scrolls to the Preview frame. |
| Download buttons | Actions | PNG and SVG. Enabled only while a current, generated code is shown. Use `aria-disabled` with a reason ("Generate first") when unavailable. Both are gated by the scan check. Stay enabled while a scan warning shows, with a decorative warning glyph and the warning in the accessible description. |
| Banner (success and error) | Preview | "Generated" appears for 5 seconds; the Status region announces it independently. Error banners persist until the next generate and name the problem. |
| Fix cue | Logo, Colors, Code Settings | When Fix changes a control, focus moves to that control and a short note beside it says what changed ("Changed from 30% to 22% by Fix"). The note stays until the next edit of that control. |
| Status region | Page | A persistent visually hidden `role="status"` (polite) region that exists on load. Announces: "Generating", then one merged message ("Generated. Download available." plus the scan warning sentence when present); "Settings changed. Press Generate." only on the transition from a current code to the empty state (once per cycle, not per keypress); the Fix-cue changes are announced by the focus move instead. |

### Scan check rules

- At generate time the server decodes the render the user will download, both PNG and SVG. A failure in either raises the warning, and both Download buttons are gated by the same check.
- The warning is one banner naming the problem plus one Fix button naming the exact change. Fix order: contrast clamp (when colors fail), error correction bump (when not already H), then smaller logo. [ASSUMPTION] The order is a draft.
- Fix applies the change to its control, cues the control (see Fix cue), resets the preview to the empty state, and the banner then reads "Applied. Press Generate to re-check." with no Fix button. The user presses Generate; the banner re-evaluates.
- When no fix remains (for example dense data or a small output), the banner shows the problem and a hint with no button: "This code may not scan, and no automatic fix is left. Try shorter content, a larger size or the Square preset." [ASSUMPTION] drafted wording.
- The warning stays until a regenerated code decodes. The user may instead change settings manually and Generate.
- The scan check applies to QR codes only; barcode tabs have no scan check.

## State Patterns

| State | Surface | Treatment |
|---|---|---|
| First load | Preview, Actions | Preview frame (empty); Generate enabled, Download disabled. |
| Current code | Preview, Actions | Code shown; Generate disabled ("Up to date"); Download enabled. |
| Inputs changed (any input or preset change) | Preview, Actions | The code is replaced by the empty state; Generate enabled; Download disabled. The Status region announces once. |
| Generating | Preview | Spinner in the preview frame; Generate disabled; the Status region says "Generating". |
| Generated | Preview | Code shown; "Generated" banner for 5 seconds; the Status region announces the merged result. |
| Scan warning active | Preview, Actions | Banner with Fix; Download stays enabled with the warning glyph; stays until a regenerated code decodes. |
| Scan warning and inputs changed | Preview, Actions | The banner stays. After a Fix its button is replaced by "Applied. Press Generate to re-check."; after a manual edit it is unchanged. The preview is empty; Download disabled. |
| Scan warning, no fix left | Preview | Banner with the terminal hint and no button. |
| Scan check could not run | Preview | Error banner "Couldn't check this code. Try again."; Download stays enabled. [ASSUMPTION] |
| Generation error | Preview | Error banner with the server message; the empty state shows; the field in error gets focus and `aria-invalid`. |
| Invalid input | Content, Code Settings | Content over the length limit, barcode data invalid for the symbology, or size and margin out of bounds: inline message naming the limit; Generate stays enabled so the server message can also surface. |
| Hex invalid | Colors | Inline message "Enter a color like #1a2b3c"; the value is not applied; announced on commit. |
| Contrast below threshold | Colors | Inline warning with Fix under the color fields. |
| Logo uploading | Logo | The drop zone shows a progress state; the rest of the form stays usable. |
| Logo rejected | Logo | Inline reason plus limit under the drop zone; the previous logo is kept. |
| Library loading or failed | Logo | A short inline message "Couldn't load saved logos" with a Retry control; upload still works. Save and delete failures show the same inline pattern. |
| Library empty | Logo | Only the drop zone, with a one-line hint. |
| Library full | Logo | Inline message on save; the logo remains usable unsaved. |
| Saved logo deleted while in use | Logo, Preview | Falls back to no logo with a note; the preview resets to the empty state. Another LAN user's delete is noticed on the next generate: the code is generated without the logo and the note is shown. |
| EC locked | Code Settings, Logo | See the Error correction control. |
| Barcode tab active | Form | Colors, Logo and Style are removed; barcode options appear in Code Settings; the hint under the Format tabs explains. |
| Download failure | Actions | Error banner "Download failed. Try again."; the code stays. |

## Interaction Primitives

- **Mouse and touch:** click or tap to select a preset, direction, logo or toggle. The preset and logo strips scroll horizontally with a visible scrollbar.
- **Radio groups** (Preset strip, Color mode toggle, Direction buttons, Saved logo strip): one Tab stop per group, entering at the selected item. Arrow keys move focus and select in the same step; Home and End jump to the ends; focus wraps. Focus scrolls the item into view.
- **Keyboard elsewhere:** Tab reaches every control in reading order, which matches the visual order (Content, Code Settings, Colors, Logo, Style, then Preview, banner, Generate, Download). Enter in a content field triggers Generate when enabled; when disabled it does nothing and says nothing.
- **Focus management:**
  - After Fix, focus moves to the changed control.
  - After Generate on narrow screens, the page scrolls to the Preview frame and focus moves to it. The scroll is instant when the user prefers reduced motion.
  - After delete confirm, see Saved logo delete.
  - After a validation error, focus moves to the first field in error.
- **Drag and drop:** logo drop zone only, never required.
- **Banned:** hover-only affordances for anything essential, modals for delete confirm, auto-regenerating after Fix, silent state changes, per-keystroke announcements.

## Accessibility Floor

Behavioral. Visual contrast lives in `DESIGN.md`.

- WCAG 2.2 AA target for the page.
- Landmarks and headings as in Information Architecture; the five form sections are real headings.
- Names: every preset thumbnail, direction button and saved-logo tile has an accessible name; each radio group has a group name. Preset descriptions are short shape descriptions. The Preview frame names what it encodes.
- Selection is a ring (a shape cue), never color alone, and is drawn with `outline` so it survives forced-colors modes. Focus is a separate, higher-contrast ring (see `DESIGN.md.Components`).
- The empty and current states differ by content (the placeholder text versus a code) and by border style (dashed versus solid), so they survive forced colors and low vision.
- Status messages go through the single persistent Status region; the scan warning banner is a labelled group and does not announce on its own, so nothing is announced twice. Transient banners never carry information that is not also in the Status region or the page.
- Targets are at least 24px, 44px on coarse pointers where space allows. The delete control and the Fix button meet the 24px minimum.
- Tooltips are not used for names. If a tooltip is added later it must be hoverable, dismissible with Esc and persistent.
- Reduced motion: no smooth scroll, no spinner animation beyond a static "Generating" text, and the Fix outline is not animated.
- Forced-colors: cues use outlines and borders only.
- Warning text and the Fix button use the theme-specific danger tokens so they hold AA contrast in both themes. Disabled controls are exempt from contrast but keep their reason text reachable.
- The theme toggle has an accessible name and exposes its state.
- Reflow to 320 CSS px with no horizontal page scroll (the two strips are the only horizontal scrollers). The floating Generate button must never cover the focused element.

## Responsive & Platform

| Breakpoint or condition | Behavior |
|---|---|
| `> 900px` | Two columns: scrolling form on the left, preview and actions on the right. The preview is sticky only when it fits the viewport height; otherwise it scrolls with the page. Generate stays in the preview card, which is not crowded. |
| `≤ 900px` | One column; Preview, scan warning, Download sit below the form. Generate is a floating pill pinned to the bottom of the viewport, reachable from any section. Pressing it scrolls to the Preview. |
| Floating Generate | The document reserves bottom padding equal to the pill's height plus margin and sets `scroll-padding-bottom` so focused elements scroll clear of it. On short viewports (under about 500px tall) and at high zoom the pill is not floating and sits inline above Download. |
| `320px` wide | Two-column rows stack; the Preview frame is at most the available width; no horizontal page scroll. |

## Inspiration & Anti-patterns

- **Reference (scope, not look):** commercial generators with about 20 body shapes, 14 eye frames and 16 eye balls. This feature deliberately offers 7 coherent presets instead.
- **Rejected — separate dot, eye frame and eye ball pickers:** mismatched eyes and combinatorial scan risk; presets move safety to design time.
- **Rejected — blend or intensity slider, spacing and roundness sliders:** unvetted shapes cannot be scan-tested.
- **Rejected — live scan check on every keystroke:** the check runs at generate time.
- **Rejected — modal confirmations and auto-regeneration after Fix:** the user stays in control of each regenerate.
- **Rejected — a faded old code, and text over any code:** a stale code is removed and the empty state shown instead.
- **Rejected — a preset grid and visible preset names:** a single scrolling strip with a visible scrollbar, names through `aria-label`.

## Key Flows

### Flow 1 — Default path (Priya, home Wi-Fi sharer, guests arriving in ten minutes)

1. Priya opens the generator. Content is first; Format is QR Code with Plain Text selected; the preview shows "Configure and generate".
2. She picks the Wi-Fi pill and fills in the network name and password.
3. She presses Generate. The code appears; Generate disables and Download enables.
4. **Climax:** She presses Download PNG and has a plain black-on-white code, never having scrolled to Colors, Logo or Style. Total under 30 seconds.

Failure: a required field is missing → the error banner names it and focus moves to the field; Generate stays enabled.

### Flow 2 — Branded code with a scan fix (Marcus, social media manager, campaign launch)

1. Marcus enters the campaign URL in Content.
2. In Style he scrolls the Preset strip and selects Fluid.
3. In Colors he switches to Gradient, picks his two brand colors and the diagonal direction. The Preset thumbnails redraw in the gradient.
4. In Logo he uploads the brand mark, chooses Save to library, and sets the size to 30%. Error correction locks to H with a reason in both places.
5. He presses Generate. A scan warning appears: "This code may not scan: the logo covers too much." with the button "Make logo smaller (30% → 22%)".
6. He presses Fix. The size slider changes and takes focus with a note, the preview returns to "Configure and generate", and the banner reads "Applied. Press Generate to re-check."
7. **Climax:** He presses Generate again. The warning clears, Download enables with no warning glyph, and he downloads a branded, verified code.

Failure: the logo upload is rejected ("Too large: 3.1 MB, max 2 MB") → the message sits under the drop zone and he continues styling the rest. Alternate: he downloads despite the warning; Download stays enabled, with a warning glyph, by design.

### Flow 3 — Poster print (Dana, designer, 6×3 ft poster)

1. Dana enters the poster URL and selects Circle.
2. In Logo she selects her saved logo from the Saved logo strip in one action.
3. She presses Generate; no warning appears.
4. She presses Download SVG.
5. **Climax:** She opens the SVG in her vector editor at poster size; the dots and eyes are vector and the logo is sharp.

Failure: the code fails the scan check at generate time (in either the PNG or the SVG render) → the same warning and Fix path as Flow 2. If no fix remains, the banner shows the terminal hint and Dana shortens the URL.

### Flow 4 — Shared library cleanup (Tomas, brand team lead, after a rebrand)

1. Tomas opens the Logo section and sees the saved logos the whole team uses.
2. He focuses the old logo tile and presses Delete. The tile asks "Delete? Yes / No" in place, with focus on "No".
3. He moves to "Yes" and confirms. Focus moves to the next tile and the Status region says "Logo deleted".
4. **Climax:** The library shows only current logos. A teammate who had that logo selected generates next and gets a code without it plus a note saying so, instead of a failed request.

Failure: delete fails → an inline "Couldn't delete this logo. Try again." and the tile stays.

## Open Items

1. **Assumptions to confirm or defer to architecture.** The decodable-contrast threshold (4:1 in `DESIGN.md`), the Fix order, the terminal scan message, the "scan check could not run" state, and the drafted wording noted in Voice and Tone.
2. **Scan banner beside an empty preview.** After a Fix the banner stays on screen while the frame is empty; confirm this reads well in the build.
3. **Spec update (outside UX).** CAP-6 and the brainstorm still describe a dimmed old code; see the deviation note in Foundation.
