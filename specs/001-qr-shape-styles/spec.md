# Feature Specification: QR Code Shape Styles (Dots & Eyes)

**Feature Branch**: `001-qr-shape-styles` (git branch: `feat/add-qr-shapes`)

**Created**: 2026-09-27

**Status**: Draft

**Input**: User description: "I want to add the ability to modify the shape of the eyes and the dots."

## Clarifications

### Session 2026-09-27

- Directive: Remove references to external sites; eye border and eye center styles must match the reference image `assets/eye-border-styles.png`.
- Q: Which shapes should be offered for the eye center? → A: Five solid shapes mirroring the border outlines: Square, Rounded, Circle, Teardrop, Leaf.
- Directive: Dot shapes must include at least the eight options in the reference image `assets/dot-shape-styles.png`, in its order.
- Q: Should "Gapped square" remain as a ninth dot shape beyond the reference image's eight? → A: Yes — keep it as the ninth option, listed last.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Choose a dot shape in the generator (Priority: P1)

A person creating a QR code on the generator page wants it to look less "default" — for example with round dots instead of hard squares — so it fits their brand or flyer. Under a "Shape style" section they pick a dot shape from a small visual set of options, the preview updates, and the downloaded image uses that shape.

**Why this priority**: Dot shape is the most visible styling change and delivers the core value of the feature on its own.

**Independent Test**: Open the generator, enter a URL, select each dot shape in turn, confirm the preview changes accordingly, download PNG and SVG, and scan each with a phone camera.

**Acceptance Scenarios**:

1. **Given** the generator with QR code mode selected, **When** the user picks the "Dots" dot shape, **Then** the preview shows the data modules drawn as separate circles while the three corner eyes remain unchanged.
2. **Given** a dot shape other than the default is selected, **When** the user downloads the code as PNG or SVG, **Then** the downloaded file shows the same dot shape as the preview.
3. **Given** the user has not touched the shape options, **When** they generate a code, **Then** the result looks exactly as it does today (square dots, square eyes).
4. **Given** the dot shape picker, **When** it is displayed, **Then** its first eight options appear in the same order and with the same silhouettes as the reference image `assets/dot-shape-styles.png`, followed by Gapped square.

---

### User Story 2 - Choose eye border and eye center styles (Priority: P2)

The same person wants the three large corner markers ("eyes") to match their style. They can choose the style of the eye border (the outer ring) and, separately, the style of the eye center (the solid inner block), mixing and matching with the chosen dot shape.

**Why this priority**: Eye styling completes the shape-style experience, but the feature is still useful with dot shapes alone.

**Independent Test**: With default dots, change only the eye border style, then only the eye center style, and confirm each change affects only its part of all three eyes and the result scans.

**Acceptance Scenarios**:

1. **Given** the generator, **When** the user selects the "Rounded" eye border, **Then** the outer ring of all three corner eyes is drawn with rounded corners and nothing else changes.
2. **Given** the generator, **When** the user selects a non-default eye center style, **Then** the inner center of all three eyes takes that shape and nothing else changes.
3. **Given** a non-default dot shape, eye border, and eye center are all selected, **When** the code is generated, **Then** all three choices are applied together and the code scans successfully.
4. **Given** custom foreground/background colors are set, **When** any shape combination is selected, **Then** the eyes and dots use the chosen foreground color on the chosen background.
5. **Given** the eye border style picker, **When** it is displayed, **Then** its seven options appear in the same order and with the same silhouettes as the reference image, and the eye center picker shows the five solid shapes defined in FR-003.

---

### User Story 3 - Request shaped codes from the embed/API endpoints (Priority: P3)

An integrating service (e.g., a URL shortener embedding QR images) wants to request a styled QR code directly via the image URL or the API, without going through the generator page.

**Why this priority**: Extends the feature to programmatic consumers; valuable but not required for the human-facing experience.

**Independent Test**: Request an embed image URL with shape parameters added and confirm the returned image uses those shapes; request it without them and confirm the output is identical to today's.

**Acceptance Scenarios**:

1. **Given** an embed image request that includes dot, eye border, and eye center style options, **When** it is fetched, **Then** the returned image uses those shapes and keeps the same response type and caching behavior as today.
2. **Given** an existing embed image request with no shape options, **When** it is fetched after this feature ships, **Then** the returned image is unchanged from before the feature.
3. **Given** a request with an unrecognized shape value, **When** it is fetched, **Then** the default shape is used for that part and the request still succeeds.

---

### Edge Cases

- Unknown, misspelled, or differently-cased shape values → fall back to the default (square) for that part; never an error.
- Very small output sizes or very dense codes (long data, high error correction) with rounded, dot, or bar shapes → code must still render. It must decode at the minimum size (100 px) for short payloads (up to ~20 characters), and at 600 px for dense payloads (~300 characters, error correction H). Larger payloads at smaller sizes have too few pixels per module to scan reliably even unstyled, and are not guaranteed.
- Margin of 0 → shaped eyes must not be clipped at the image edge.
- Barcode (non-QR) formats → shape options are hidden in the UI and ignored by the API.
- Low-contrast color choices combined with thin shapes (e.g., dots, bars, or gapped squares) → no special handling beyond existing color behavior; the embed documentation notes that contrast is the user's responsibility.
- SVG output → shapes must be preserved as vector shapes, not a rasterized image.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Users MUST be able to choose a **dot shape** for QR data modules. The options, in display order, MUST be the eight shapes in the reference image `assets/dot-shape-styles.png` (options 1–8) followed by Gapped square:
  1. **Square** (default) — plain square modules; adjacent modules join into solid blocks.
  2. **Rounded** — adjacent modules join; the outer corners of each joined group are slightly rounded.
  3. **Extra rounded** — adjacent modules join; the outer corners of each joined group are fully rounded, giving soft blob-like shapes.
  4. **Dots** — each module is a separate circle; modules never join.
  5. **Classy** — adjacent modules join; groups keep mostly sharp corners, with rounding only on two diagonally opposite outer corners.
  6. **Classy rounded** — like Classy, but the two diagonal corners are fully rounded, giving slanted leaf-like shapes.
  7. **Horizontal bars** — horizontally adjacent modules join into pill-shaped bars with rounded ends.
  8. **Vertical bars** — vertically adjacent modules join into pill-shaped bars with rounded ends.
  9. **Gapped square** — each module is a slightly smaller square with a visible gap around it; modules never join. (Not in the reference image; listed after its eight options.)
- **FR-002**: Users MUST be able to choose an **eye border style** (outer ring of the three corner markers). The options, in display order, MUST match the reference image `assets/eye-border-styles.png`:
  1. **Square** (default) — thin square ring with sharp corners.
  2. **Rounded** — thin square ring with all four corners rounded.
  3. **Circle** — thin circular ring.
  4. **Teardrop** — thin ring with a sharp top-left corner and the other three corners fully rounded.
  5. **Leaf** — thick ring whose outline has sharp top-left and bottom-right corners and rounded top-right and bottom-left corners; the opening is teardrop-shaped (sharp only at the bottom-right).
  6. **Leaf, round opening** — same outer outline as Leaf, with a circular opening.
  7. **Square, round opening** — thick square outline with sharp corners and a circular opening.
- **FR-003**: Users MUST be able to choose an **eye center style** (solid inner block of the three corner markers). The options are solid versions of the distinct eye border outlines, in this display order:
  1. **Square** (default) — solid square with sharp corners.
  2. **Rounded** — solid square with all four corners rounded.
  3. **Circle** — solid circle.
  4. **Teardrop** — solid shape with a sharp top-left corner and the other three corners fully rounded.
  5. **Leaf** — solid shape with sharp top-left and bottom-right corners and rounded top-right and bottom-left corners.
- **FR-004**: Dot, eye border, and eye center choices MUST be independent of one another and combinable freely.
- **FR-005**: Eye style choices MUST apply identically to all three corner eyes, keeping each style's orientation as shown in the reference image (not mirrored per corner); dot shape MUST NOT alter the eyes.
- **FR-006**: The generator page MUST present these choices in a "Shape style" section, visible only when QR code mode is selected, with each option shown as a small visual swatch (not text only) resembling the reference image.
- **FR-007**: The live preview MUST reflect the selected shapes, and downloads MUST match the preview.
- **FR-008**: Shape choices MUST apply to both PNG and SVG outputs, with SVG output remaining vector.
- **FR-009**: Shape choices MUST respect the existing foreground/background colors, size, margin, and error-correction settings in PNG output.
- **FR-010**: The generate API, the download API, and the embed image endpoint MUST each accept optional dot shape, eye border style, and eye center style parameters.
- **FR-011**: When shape parameters are absent, output MUST be visually identical to the current output (square dots, square eyes), preserving existing consumers.
- **FR-012**: Invalid shape values MUST fall back to the default for that part rather than producing an error.
- **FR-013**: Adding shape parameters MUST NOT change the embed endpoint's response type or cache behavior.
- **FR-014**: Every supported shape combination MUST produce a code that decodes to the original data.
- **FR-015**: Usage logging MUST record which shape options were used (as non-sensitive metadata) without recording the encoded data.
- **FR-016**: Shape parameters MUST be documented alongside the existing embed endpoint parameters in project documentation.

### Key Entities

- **Shape Style**: The trio of choices applied to a QR code — dot shape, eye border style, eye center style — each drawn from a fixed, named set with Square as the default.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of supported dot × eye border × eye center combinations (9 × 7 × 5 = 315 total) produce codes that decode correctly to the input data at the default size.
- **SC-002**: Existing embed requests without shape options return images identical to pre-feature output (0 visual regressions for existing consumers).
- **SC-003**: A user can change a QR code's dot and eye shapes and download the result in under 30 seconds from landing on the generator.
- **SC-004**: Styled codes scan on first attempt with a typical phone camera at the default size for at least 95% of combinations tested. The phone-tested sample is each of the 9 dot shapes (with square eyes), each of the 7 eye borders, and each of the 5 eye centers (with square dots): 21 codes, one phone.
- **SC-005**: Generating a styled code feels as responsive as generating a plain code today (no user-noticeable slowdown in the preview): server-side rendering of a styled PNG at the default size (300 px) takes at most 50 ms.
- **SC-006**: Each eye border option, rendered in a generated code, is recognizable as the corresponding silhouette in the reference image when compared side by side, and each eye center option has the same orientation as the matching border outline.

## Assumptions

- The reference images `assets/dot-shape-styles.png` and `assets/eye-border-styles.png` are the authoritative visual sources for dot shapes and eye border styles; the written descriptions in FR-001 and FR-002 summarize them.
- Decorative/logo-style dot shapes (stars, hearts) and per-eye different shapes are out of scope for this version.
- Separate eye colors (different from the foreground color) are out of scope.
- Error-correction level is not automatically raised when a stylized shape is selected; the user keeps control of it.
- Existing SVG color and sizing behavior is unchanged by this feature: styled SVGs use the same black fill, no background, and the same physical dimensions (mm units) as unstyled SVGs. Aligning SVG colors with PNG is a separate concern.
- The feature adds no stored state; every styled image is computed from the request alone, consistent with the service's stateless design.
