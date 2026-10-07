# Spine Pair Review — QR Code Generator

## Overall verdict
Adequate, not yet a clean contract. Tokens resolve, section order is correct, and most memlog decisions land in the spines. Three things stop a consumer from extracting cleanly. The scan-check-covers-SVG decision is missing. The "decodable contrast" threshold is never defined. Component names and coverage drift between DESIGN and EXPERIENCE, so a consumer cannot join them or build every component from the spines alone. Fix the 5 high items and align component names, and this is strong.

## 1. Flow coverage — adequate
**What was checked:** CAP-1..CAP-9 and the spec/scope requirements against the three flows, State Patterns and Component Patterns. Each flow was checked for protagonist, numbered steps, climax and failure path.

Coverage:
- CAP-1, 2, 3, 4, 5, 6: Flow 2 (Flow 1 for CAP-6 and the Square default).
- CAP-7: Flow 3.
- CAP-8: save and select in Flows 2 and 3; delete and library-full only in states and components.
- CAP-9: no note anywhere.

All three flows have a named protagonist, numbered steps, a bolded climax and a failure line.

### Findings
- **[high]** Memlog decision "scan check must decode the downloaded format incl. SVG render" (paired with removing the Output Format radio) is absent from both spines. EXPERIENCE only says "preview is always PNG; Download picks the file format". It never says what the scan check decodes, so "Download enabled = verified" is undefined for SVG, and Flow 3 (SVG) rests on it. (EXPERIENCE IA, Flow 3, Component Patterns "Scan warning"). *Fix:* add one rule that the generate-time check decodes the render the user will download (PNG and SVG), and that Download SVG is gated by the same check.
- **[high]** The Scan warning dead end is not defined. The memlog says "re-check after each fix; one banner, one most-effective fix". The spine does not say what the banner shows when the check still fails after Fix and Generate: the next fix, or, when none remains (dense data, small output, EC already H), a message with no Fix button. (EXPERIENCE "Scan warning"; spec CAP-5 lists EC level, smaller logo and contrast clamp). *Fix:* state the fix order, that the banner re-evaluates after each Generate, and the terminal message.
- **[medium]** CAP-9 has no explicit non-UX note. The Foundation claims "CAP-1 to CAP-9", but only the Copy URL and Output Format removals touch the UI. *Fix:* add one Foundation line: CAP-9 has no UX surface beyond the removals in IA.
- **[medium]** Several behaviors have no flow or state, only a component rule or nothing at all. These are Download-despite-warning (the spec's "warn but proceed"), the contrast-warning Fix, delete or library-full, the barcode-tab round trip, and the instance-wide library being shared by LAN users (another user may delete the logo in use). *Fix:* extend Flow 2 or add a short Flow 4, and state the shared-library behavior.
- **[low]** Flow 3 step 3 "sets Size larger" is meaningless for an SVG, and the PNG MAX_SIZE is 2000. *Fix:* drop it, or tie it to the 1 ft print case.
- **[low]** Flow 1's failure path ("required field missing → error banner names it") has no matching State Patterns row ("Generation error" is the closest). *Fix:* add a validation state or point to the existing one.

## 2. Token completeness — adequate
**What was checked:** Every `{...}` reference in the frontmatter and prose was resolved against the frontmatter (all resolve). Hex values were checked against `templates/qr_generator.html` `:root` and `[data-theme=light]` (they match). Light/dark pairs and the stated contrast numbers were recomputed.

Contrast results:
- White on accent: 4.31:1.
- Danger on surface: 5.7:1.
- Danger on white: 2.97:1.
- danger-light on white: 5.69:1.
- White on danger: 2.97:1.
- `#0f1117` on danger: 6.4:1.

All the stated figures are correct.

### Findings
- **[medium]** Component tokens contradict the Colors prose. `contrast-warning` and `scan-warning-banner` bind `{colors.danger}` with no light variant, while Colors says light theme uses `danger-light` for warning text and borders. Only `fix-button` carries light variants. A token-only consumer ships a 2.97:1 warning in light theme. (DESIGN components.contrast-warning, scan-warning-banner vs Colors). *Fix:* add light variants (color, border, alpha background) to both.
- **[medium]** Teal `accent-2` is shared across themes (stated). It is used for the "Generated" banner and content pills, and it is about 1.9:1 on `surface-light` (#ffffff). The spec states danger contrast but not this combination. *Fix:* limit teal to fills and borders in light theme, or add `accent-2-light`.
- **[medium]** "Decodable contrast", the trigger for the inline contrast warning, has no numeric threshold or method in either spine. The component, the Fix target ("passing value") and the generate-time check cannot be built consistently. (EXPERIENCE "Contrast warning"; DESIGN). *Fix:* commit a threshold, or defer it to architecture explicitly.
- **[medium]** The focus ring is the 15% alpha glow `0 0 0 3px` (DESIGN "Changed-by-fix cue"). It likely fails 3:1 non-text contrast, and it is the same glow as the fix cue. No focus-visible token or contrast target is stated, and there are no ring-contrast targets for selected states. *Fix:* add a focus-visible ring token with a contrast target, and keep the fix cue distinct.
- **[low]** Hard-coded values bypass tokens: `#8b5cf6` (gradient end), `#ffffff` active-foreground, `'danger at 12% alpha'`, the 0.5/0.4/0.35 opacities and the shadow (the template has `--shadow`). The `preset-strip` token is orphaned (never referenced), and `pill` and `lg` duplicate 20px. *Fix:* tokenize or reference them.
- **[low]** The `sources:` list omits `templates/qr_generator.html`, which is the extraction source. *Fix:* add it.
- **[low]** Hover and disabled states have no component tokens (the Download teal hover border and the disabled opacities are prose only).

## 3. Component coverage — thin
**What was checked:** Every component name used in either file was collected and matched in both DESIGN Components and EXPERIENCE Component Patterns, with the naming compared.

### Findings
- **[high]** Component names are not identical across the files, so the pair is not mechanically joinable. The DESIGN name comes first below. "Segmented toggle (Solid | Gradient)" vs "Solid / Gradient toggle". "Saved logo thumbnail" vs "Saved-logo strip". "Scan warning banner" vs "Scan warning". "Stale preview" vs "Preview frame". "Locked control note" vs "Error correction". "Generate / Download" vs "Generate" and "Download PNG / SVG". "Preset thumbnail" has no EXPERIENCE row (it is covered under Preset strip). *Fix:* pick one canonical name per component and use it in both files and in the frontmatter keys.
- **[high]** "Logo size and background pad" has a behavioral row but no DESIGN row or tokens. The memlog calls it a "size slider 10-30% and background-behind-logo toggle", and the spines never say whether each is a slider, a toggle or a number input. A consumer cannot build it. (EXPERIENCE "Logo size and background pad"; memlog). *Fix:* add a DESIGN row with anatomy, and name the control types in EXPERIENCE.
- **[medium]** Components used in EXPERIENCE with no DESIGN row or tokens: Format tabs and content pills ("as today" is not stated), the Generated banner, the Generation error banner, the Logo error message, the spinner overlay, the tooltip, the empty-library hint and the warning icon on Download. *Fix:* add a "Banner (success/error)" row and an "inherited as-is from the current page" line for the rest.
- **[medium]** "Changed-by-fix cue" and "Locked control note" have DESIGN rows but no distinct behavioral row (the behavior is spread across the Scan warning row and Accessibility). The delete icon on a 56px thumbnail has no hit-area rule. *Fix:* add rows and a minimum target size.
- **[low]** `direction-button` at 36px meets the WCAG 2.2 AA 24px minimum, but no target-size rule is stated.

## 4. State coverage — adequate
**What was checked:** Every IA surface (Content, Code Settings, Colors, Logo, Style, Preview, Actions) was walked against State Patterns, Component Patterns and the Accessibility Floor.

Covered: first load, fresh, stale, generating, generated, scan warning, generation error, logo rejected, library full, deleted while in use, contrast, EC locked, barcode tab, empty library.

### Findings
- **[medium]** Content and settings validation states are missing. Content over `MAX_DATA_LEN` (2000), barcode data invalid for the chosen symbology, and Size/Margin bounds have no state. Invalid hex is "not applied" with no visible or announced treatment, which conflicts with the banned "silent state changes". (EXPERIENCE Color field, State Patterns). *Fix:* add "Invalid input" and "Hex invalid" rows.
- **[medium]** Logo async states are missing: uploading (up to the 2 MB cap and the 3 MB 413), saved-library loading or failure (SQLite), save failure and delete failure. *Fix:* add "Logo uploading" and "Library error" states.
- **[medium]** The combination "scan warning + stale" (after Fix or any edit) is not specified. The spec says the warning stays until a regenerated code decodes, but Download is disabled when stale. It is unclear whether the banner stays, dims or changes its button. It is also unclear whether the scan check applies to barcode tabs (the Preview surface says "all formats"). *Fix:* state both.
- **[low]** Missing: Download in progress or failure, a network or timeout error distinct from a generation error, the "scan check could not run" case, the focus destination after Fix, a prefers-reduced-motion rule for the spinner and glow, and a light-theme note for the Generated banner.
- **[low]** The "Saved logo deleted" note wording is not in Voice. The library-full copy hardcodes "20" while the cap is env-configurable (scope.md). *Fix:* use a `{cap}` placeholder.

## 5. Visual reference coverage — adequate
**What was checked:** Inline links and the "spine wins" statement in both files. The mocks in `.working/` (`key-generator-default.html`, `key-generator-styled-warning.html`) were inspected for consistency. The `imports/` folder is empty.

### Findings
- **[low]** EXPERIENCE links `mockups/generator-default.html` and `mockups/generator-styled-warning.html` "(to be rendered)". The mocks are already rendered and named `key-generator-*.html`, and the spines do not link them (promotion to `mockups/` is pending). The link text is stale and the filenames will differ unless renamed at promotion. *Fix:* at finalize, rename or relink and drop "(to be rendered)".
- **[low]** DESIGN.md has no mock link and no "spines win on conflict" line. EXPERIENCE has one.
- **[low]** The mocks cover default fresh, narrow stale with floating Generate, and styled warning (dark plus a light right panel). The memlog decision is to skip mocks for the contrast warning, logo error, delete confirm, barcode tab, generation error and library full. These spine-only items therefore rely entirely on prose, which is why the gaps in sections 3 and 4 matter.

## 6. Bloat and overspecification — strong
**What was checked:** Spec-level detail the spines restate versus detail that is decision-bearing.

### Findings
- **[low]** DESIGN Components carries some behavior ("confirming swaps it in place for Delete? Yes / No", "Disabled uses the existing 0.5 / 0.4 opacity"), and Layout lists panel order a second time. Both are small leaks across the DESIGN/EXPERIENCE boundary.
- **[low]** The Inspiration & Anti-patterns "Rejected" bullets restate the spec's non-goals. They are short and useful to AI consumers, so leave them.

No real overspecification found.

## 7. Inheritance discipline — adequate
**What was checked:** Frontmatter sources resolve (all five paths do), CAP names are mirrored, component names are identical across both files, token references resolve.

### Findings
- **[high]** Memlog decision "EC-locked-to-H explanation appears both in the Logo section and at the locked EC control" is only half carried. The spines place the hint at EC only, and the Voice string has no location. (Component Patterns "Error correction" and Logo rows). *Fix:* add the hint to the Logo section rows.
- **[medium]** CAP names are never mirrored. EXPERIENCE says "CAP-1 to CAP-9" once and never names or maps them. A consumer cannot trace a CAP to a flow, component or state. (Foundation). *Fix:* add a short CAP-to-flow/component trace table or inline CAP tags.
- **[medium]** The memlog calls the background-behind-logo a "toggle". The spines call it "pad". (EXPERIENCE). *Fix:* name the control type (see section 3).
- **[medium]** DESIGN Components says the preset thumbnails are drawn "on a light code background", but the `preset-thumbnail` token background is `{colors.input-bg}` (dark in dark theme). The memlog says thumbnails follow the chosen colors exactly. *Fix:* pick one and tokenize the thumbnail's code background.
- **[low]** `scope.md` says "delete confirms inline and notes references". EXPERIENCE covers the in-use fallback but not the "notes references" wording.

Component name drift (section 3) and the memlog gaps in sections 1 and 3 also count here. No spine statement contradicts a memlog decision except the thumbnail background above.

## 8. Shape fit — strong
**What was checked:** DESIGN.md frontmatter and body order against `design-md-spec.md` and the design examples. EXPERIENCE.md sections against the experience examples.

### Findings
- **[low]** DESIGN body order matches the locked order exactly (Brand & Style through Do's and Don'ts), and the frontmatter keys follow the spec. `rounded.pill` is non-standard but acceptable. The `-light` suffix pairing with dark as the base is acceptable per the spec's "separate tokens" pattern.
- **[low]** EXPERIENCE has every required section in the example order, plus `Open Items` (an invented section). It earns its place for the reviewer gate and will be empty once validation is done.

## Mechanical notes
- Token references: 0 unresolved. Orphan token: `components.preset-strip`.
- Hex values match the template; the template's `--shadow` and `--transition` are not tokenized.
- Stated contrast ratios were recomputed and are correct.
- About 40 memlog decisions were checked. Missing or partial: the SVG scan check, re-check after each fix, the EC hint in Logo, and the logo toggle vs pad naming. The one contradiction is the thumbnail background.
- The mocks are not linked. The filenames differ from the spine's (`key-generator-*` vs `generator-*`).
- Spine files were not edited.

## Finding counts
- critical: 0
- high: 5
- medium: 14
- low: 16
