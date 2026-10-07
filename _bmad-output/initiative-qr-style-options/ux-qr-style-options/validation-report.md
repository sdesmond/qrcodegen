# Validation Report — QR Code Generator

- **DESIGN.md:** `DESIGN.md`
- **EXPERIENCE.md:** `EXPERIENCE.md`
- **Run at:** 2026-10-06 22:08

## Overall verdict

Adequate, not yet a clean contract. Tokens resolve, section order is correct and most memlog decisions are carried. The rubric found 5 high items: the SVG scan-check decision, the scan-warning dead end, component-name drift between the two files, the logo size and pad control, and the EC hint in the Logo section.

The accessibility review is more demanding: not ready to build from at WCAG 2.2 AA, with 10 high items (about 27 medium). The main themes are the stale state with no durable cue, focus and keyboard behavior, non-text contrast of unselected controls, and the live-region strategy. Most fixes are small spec additions. Two of its recommendations conflict with decisions you made: visible text for the stale state, and a grid instead of a scrolling strip for presets.

## Category verdicts
- Flow coverage — adequate
- Token completeness — adequate
- Component coverage — thin
- State coverage — adequate
- Visual reference coverage — adequate
- Bloat & overspecification — strong
- Inheritance discipline — adequate
- Shape fit — strong

## Findings by severity

### Critical (0)

### High (15)

**[Rubric: Flow coverage]** — Scan check does not say it decodes the downloaded format (incl. SVG) (§ EXPERIENCE IA, Flow 3, Scan warning)
The memlog decision is absent. Without it 'Download enabled = verified' is undefined for SVG.
Fix: State that the generate-time check decodes the render the user will download (PNG and SVG) and that both downloads are gated by it.

**[Rubric: Flow coverage]** — Scan warning dead end is undefined (§ EXPERIENCE Scan warning)
Nothing says what the banner shows when the check still fails after Fix, or when no fix remains.
Fix: State the fix order, that the banner re-evaluates after each Generate, and the terminal message with no Fix button.

**[Rubric: Component coverage]** — Component names are not identical across the two files (§ DESIGN Components vs EXPERIENCE Component Patterns)
Segmented toggle vs Solid / Gradient toggle; Saved logo thumbnail vs Saved-logo strip; Scan warning banner vs Scan warning; Stale preview vs Preview frame; and others.
Fix: Pick one canonical name per component and use it in both files.

**[Rubric: Component coverage]** — 'Logo size and background pad' has no DESIGN row and no named control type (§ EXPERIENCE Component Patterns)
The memlog says slider and toggle; the spines never do.
Fix: Add a DESIGN row and name the controls.

**[Rubric: Inheritance discipline]** — EC-locked explanation appears at the EC control only (§ EXPERIENCE Logo and EC rows)
The memlog says both the Logo section and the EC control.
Fix: Add the hint to the Logo section.

**[Accessibility]** — Stale preview has no durable state cue (§ EXPERIENCE State Patterns, Voice)
The faded code is 2.85:1 for black modules and about 1.7:1 for a brand gradient. The live-region sentence is transient, so a screen-reader user returning to the preview finds no state.
Fix: Keep the QR clean but add a persistent status line outside the code, tied to the image with aria-describedby. If visible text stays banned, use a non-opacity frame cue (dashed border) and keep the state in the DOM.

**[Accessibility]** — Floating Generate can obscure focus; zoom and short viewports unguarded (§ EXPERIENCE Responsive (2.4.11, 1.4.10))
The pill covers the bottom of the viewport; the sticky preview can exceed short viewports.
Fix: scroll-padding-bottom, page bottom padding, no float on short viewports, sticky preview released on short screens.

**[Accessibility]** — Radio-group keyboard model conflicts with the ARIA pattern; focus targets unspecified (§ EXPERIENCE Interaction Primitives)
'Arrows move, Space/Enter confirms' is not the radio pattern. Focus after Fix, Generate auto-scroll and delete confirm is undefined.
Fix: Specify roving tabindex, select-on-arrow, Home/End, and a focus target for each action.

**[Accessibility]** — Non-text contrast: unselected control borders are 1.2 to 1.5:1 (§ DESIGN Components (1.4.11))
Thumbnails, direction buttons, color fields, drop zone and logo tiles.
Fix: Require a 3:1 boundary on new interactive controls.

**[Accessibility]** — Locked EC at 0.35 opacity hides the selected level (1.9:1) (§ DESIGN Locked control note)
Fix: Keep the locked H at full contrast; dim the other three.

**[Accessibility]** — 2-second 'Generated' banner; no persistent status region (§ EXPERIENCE State Patterns (2.2.1, 4.1.3))
Fix: Put 'Generated' in a persistent role=status line.

**[Accessibility]** — Live-region strategy would announce on every keypress and clobber messages (§ EXPERIENCE Accessibility Floor)
Fix: One persistent polite region; announce stale only on the fresh-to-stale transition; merge messages.

**[Accessibility]** — Delete icon 18px (2.5.8) overlapping the selectable tile (§ DESIGN Saved logo thumbnail)
Fix: 24px minimum target, outside the tile or a single Delete button under the strip.

**[Accessibility]** — No landmarks or headings; no focus-visible or forced-colors spec (§ EXPERIENCE Accessibility Floor)
Fix: Add landmarks, real headings, outline-based cues and forced-colors fallbacks.

**[Accessibility]** — Form column, fixed preview frame and row-2 grids at 320px (§ EXPERIENCE Responsive (1.4.10))
Fix: Target 320px width; max-width on the frame; stack row-2.

### Medium (20)

**[Rubric: Flow coverage]** — CAP-9 has no non-UX note; CAP names are never mirrored (§ EXPERIENCE Foundation)
A consumer cannot trace a CAP to a flow, component or state.
Fix: Add a CAP trace table.

**[Rubric: Flow coverage]** — Behaviors with no flow or state (§ EXPERIENCE Flows)
Download-despite-warning, contrast Fix, delete, library full, barcode round trip and shared-library deletion by another LAN user.
Fix: Add Flow 4 and state the shared-library behavior.

**[Rubric: Token completeness]** — contrast-warning and scan-warning-banner bind dark danger only (§ DESIGN components)
Light theme would ship 2.97:1 warning text.
Fix: Add light variants.

**[Rubric: Token completeness]** — 'Decodable contrast' has no threshold (§ EXPERIENCE Contrast warning)
The inline warning, its Fix target and the generate-time check cannot be built consistently.
Fix: Commit a threshold or defer it to architecture explicitly.

**[Rubric: Token completeness]** — Teal text is about 1.9:1 on white in light theme (§ DESIGN Colors)
Applies to the Generated banner and content pills.
Fix: Add a darker light-theme teal for text and borders.

**[Rubric: Token completeness]** — No focus-visible token; the glow is 15% alpha (§ DESIGN Components)
The focus ring fails 3:1 and is the same glow as the Fix cue.
Fix: Define one focus-visible ring and keep the Fix cue distinct.

**[Rubric: Component coverage]** — Components with no DESIGN row (§ EXPERIENCE)
Format tabs, content pills, banners, spinner, tooltip, empty-library hint, Download warning icon.
Fix: Add a banner row and an 'inherited as-is' line.

**[Rubric: Component coverage]** — Changed-by-fix cue and locked-control note have no behavioral row (§ EXPERIENCE)
Fix: Add rows and a minimum target size.

**[Rubric: State coverage]** — No validation states (§ EXPERIENCE State Patterns)
Over-length content, invalid barcode data, size and margin bounds, invalid hex (silent today).
Fix: Add Invalid input and Hex invalid states.

**[Rubric: State coverage]** — No logo async states (§ EXPERIENCE State Patterns)
Uploading, library load failure, save and delete failure.
Fix: Add Logo uploading and Library error.

**[Rubric: State coverage]** — Scan warning combined with stale is unspecified; scan check on barcode tabs unclear (§ EXPERIENCE State Patterns)
Fix: State both.

**[Rubric: Inheritance discipline]** — Thumbnail background: prose says light, token says input-bg (§ DESIGN Components)
Fix: Pick one and tokenize the code background.

**[Rubric: Inheritance discipline]** — Background-behind-logo called 'toggle' in memlog and 'pad' in spines (§ EXPERIENCE)
Fix: Name the control type.

**[Accessibility]** — Accent contrast: white on accent 4.32:1, accent text 3.90:1, muted-light on bg-light 4.32:1, teal on white 1.91:1 (§ DESIGN Colors)
Includes the new Solid/Gradient toggle and floating Generate.
Fix: Darker fill accent, light-theme teal and muted tokens.

**[Accessibility]** — Disabled buttons leave the tab order so their reason is unreachable (§ EXPERIENCE Actions)
Fix: aria-disabled with aria-describedby.

**[Accessibility]** — Preset strip: most items off-screen with no count; scrollbars are 8px (§ EXPERIENCE Preset strip (2.5.8, 1.4.10))
7 presets need about 580px in a 372px column. A grid avoids horizontal scrolling.
Fix: Revisit grid versus strip, or add prev/next and a position count.

**[Accessibility]** — Tooltips: title duplicates aria-label; 1.4.13 behavior unspecified; names do not describe shapes (§ EXPERIENCE Preset strip)
Fix: Drop title or build a compliant tooltip; add a one-clause description per preset.

**[Accessibility]** — Scan warning role=alert plus status double-announces (§ Mocks, EXPERIENCE)
Fix: One polite status message; banner is a labelled group.

**[Accessibility]** — Contrast warning announces on every keystroke; Fix cue is a 1.5s 15% glow (§ EXPERIENCE Contrast warning, DESIGN)
Fix: Announce on commit; add a persistent 'changed by Fix' note; honour reduced motion.

**[Accessibility]** — Preview alt text, Download warning icon text, section group names, color well labelling (§ EXPERIENCE)
Fix: Specify names and descriptions.

### Low (7)

**[Rubric: Flow coverage]** — Flow 3 'sets Size larger' is meaningless for SVG; Flow 1 failure has no matching state (§ EXPERIENCE Flows 1 and 3)
Fix: Tie size to the print case; add an invalid-input state.

**[Rubric: Token completeness]** — Hard-coded values, orphan preset-strip token, sources list omits the template (§ DESIGN frontmatter)
Fix: Tokenize or reference; add the template to sources.

**[Rubric: State coverage]** — Download failure, network error, 'scan check could not run', reduced-motion rule, hard-coded '20' in the cap message (§ EXPERIENCE)
Fix: Add rows; use a cap placeholder.

**[Rubric: Visual reference coverage]** — Mocks not linked; link text still says 'to be rendered'; DESIGN has no link or spines-win line (§ EXPERIENCE IA, DESIGN)
Fix: Promote to mockups/ and link at finalize.

**[Rubric: Visual reference coverage]** — Six spine-only items rely on prose (§ EXPERIENCE)
Chosen by the user; no further mock.
Fix: None.

**[Rubric: Bloat & overspecification]** — Behavior in DESIGN Components (delete confirm swap, disabled opacities) (§ DESIGN Components)
Fix: Move to EXPERIENCE.

**[Accessibility]** — Barcode tab hides sections silently; format tabs lack selected semantics; target sizes, text spacing, small type, theme toggle name (§ EXPERIENCE)
Fix: See the review file for each.

## Reviewer files
- `review-rubric.md`
- `review-accessibility.md`
