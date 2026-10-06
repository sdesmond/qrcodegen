---
id: SPEC-qr-style-options
companions:
  - presets.md
  - scope.md
sources:
  - ../../brainstorm-qr-style-options/brainstorm-qr-style-options.md
---

> **Canonical contract.** This SPEC and the files in `companions:` are the complete, preservation-validated contract for what to build, test, and validate. Source documents listed in frontmatter are for traceability — consult them only if you need narrative rationale or prose color this contract intentionally omits.

# QR Style Options

## Why

A vision to realize and an opportunity to capture: the self-hosted Flask QR generator offers little styling, while commercial generators offer ~20 body shapes, 14 eye frames and 16 eye balls. Users range from a home Wi-Fi sharer to an enterprise social media manager, and all share one job: "generate a QR in under 30 seconds and move on." Styling must add personality and brand fit without hurting scannability or that speed.

## Capabilities

Priority tags (Must/Should) per `scope.md`.

- **CAP-1** (Must) Shape presets
  - **intent:** A user can pick one named preset that sets dot shape, outer eye and inner eye together as one coherent family (see `presets.md`).
  - **success:** Each of the 7 presets renders a scannable code from the same table row; Square is selected by default and its output matches today's.
- **CAP-2** (Must) Preset thumbnails
  - **intent:** A user can see what every preset looks like before choosing, independent of their content, in their chosen colors.
  - **success:** The strip shows all presets at all times as upper-left crops of a demo QR, drawn client-side in JS from the shared preset table; changing color or gradient redraws them with no request tied to the user's data.
- **CAP-3** (Must) Color
  - **intent:** A user can apply a solid color or gradient independently of the chosen preset.
  - **success:** Any color setting works with any preset; a color pair that would fall below decodable contrast is clamped or flagged via CAP-5.
- **CAP-4** (Must) Logo upgrade
  - **intent:** A user can place a center logo whose neighboring dots fade softly, rendered at print-grade resolution, with clear errors when the upload is rejected.
  - **success:** A logo-bearing code still decodes; a rejected upload shows reason plus limit inline without blocking the rest of the form; a 1 ft SVG at 30% logo width is not visibly soft.
- **CAP-5** (Must) Scan check
  - **intent:** A user is told, and offered a fix, when their generated code may not scan.
  - **success:** At generate time the server decodes its own render; on failure a persistent warning appears with a one-click suggested fix (EC level, smaller logo, contrast clamp) and stays until the problem is resolved (a regenerated code decodes); the user may fix manually instead of using the suggestion.
- **CAP-6** (Must) Generate/Download state
  - **intent:** A user can only download a code that matches the current inputs and passed generation.
  - **success:** Any input or preset change enables Generate, disables Download, and dims the old code; a fresh code disables Generate and enables Download.
- **CAP-7** (Should) SVG print path
  - **intent:** A user can download an SVG suitable for large print.
  - **success:** Dots, eyes and frame stay vector; a poster-size SVG with logo opens correctly in a vector editor (release check).
- **CAP-8** (Should) Saved logo library
  - **intent:** A user can save, reuse and delete logos on the instance to speed up repeat codes.
  - **success:** A saved logo is selectable in one action after upload; delete removes it and any reference falls back to no logo with a note.
- **CAP-9** (Must) Private platform
  - **intent:** The app is a LAN-only, self-hosted service with all options on POST routes.
  - **success:** `GET /api/qr` and Cloudflare tunnel config/notes are gone; the full feature set works through POST routes.

## Constraints

- The default path (content, Generate, Download) stays unchanged and fast; all styling is opt-in, and the default preset reproduces today's output.
- Eye frames stay 1:1 aspect so the 1:1:3:1:1 finder ratio holds; the eye frame echoes how the dots end, the eye ball echoes their direction or form.
- Fluid has no square edges, including smoothed concave joins; this rule applies to Fluid only.
- Logo fade shrinks dot size, never lowers opacity, so decoders still binarize cleanly.
- One preset-table row `{dot, frame, ball}` is the single source for the renderer, thumbnail and scan-test fixture; keep it shared (JSON) with golden-image tests so implementations cannot drift.
- Logos persist only as re-encoded PNG (never the raw upload), metadata stripped, atomic write; existing `_load_logo` validation is kept; SVG uploads stay rejected.
- Rendering reuses the existing helper paths (`_render_qr` etc.); no forked pipelines. Input stays whitelist-validated.
- Existing hard limits (`MAX_DATA_LEN`, size bounds) bound memory; PNG `MAX_SIZE` stays 2000 by default but becomes a configurable variable, and raising it requires checking gunicorn workers and memory.
- The scan decoder (zxing-cpp, assumed; opencv-headless as fallback) is a new dependency added via uv and Docker; container pip must be verified against the dev machine's TLS interception.
- Saved-logo cap is 20 by default and env-configurable.

## Non-goals

- Diamond preset; separate eye frame/ball pickers; blend/intensity slider; tunable spacing or roundness sliders.
- SVG logo uploads; accounts or auth; GET `/api/qr` shim.
- Deferred (Could): frames, stress-test grades, saved presets/brands, built-in icons, print-size helper, transparent/inverted background (see `scope.md`).

## Success signal

A first-time user opens the page, types content, presses Generate and Download in under 30 seconds with no styling touched; a brand user picks a preset, color and saved logo and gets a code that decodes, or is told exactly how to fix it; and a 1 ft poster SVG with logo prints sharp.

## Assumptions

- While the scan warning persists, Download stays enabled (warn but proceed); the warning clears only when a regenerated code decodes.
- Fluid's concave corners use fixed-radius smoothed fillets tuned by the scan test.
- The logo cap of 20 was stated as "20 presets"; read as 20 saved logos, since there are 7 presets.
- zxing-cpp was chosen because the user had no preference; verify it decodes the styled presets before committing.
