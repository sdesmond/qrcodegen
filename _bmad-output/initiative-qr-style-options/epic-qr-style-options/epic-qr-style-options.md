---
type: epic
title: "Users style their QR codes with safe, one-tap presets"
parent: initiative-qr-style-options
covers: [CAP-1, CAP-2, CAP-3, CAP-4, CAP-5, CAP-6, CAP-7, CAP-8, CAP-9]
after: []
assignee: ""
risk: medium
---

# Users style their QR codes with safe, one-tap presets

## Description

The self-hosted QR generator gains seven shape presets (dots, outer eye and inner eye as one family), independent color and gradient, a logo upgrade with soft fade, and a generate-time scan check with a one-click fix. The default path stays content, Generate, Download in under 30 seconds. The spec holds the full contract.

## Outcome

A first-time user still gets a download in under 30 seconds with nothing styled; a brand user picks a preset, color and saved logo and gets a code that decodes, or is told how to fix it. The spec's success signal is the measure.

## Requirements

The spec's capability ids are the requirement source: CAP-1 to CAP-9 in `spec-qr-style-options/spec-qr-style-options.md`, with the preset catalog in `presets.md` and scope in `scope.md`.

## Done when

1. All seven presets render and decode on both PNG and SVG, and Square output matches today's.
2. Preset thumbnails show in the chosen color; Generate and Download are strict inverses; a fresh code is required to download.
3. The scan check flags a failing code at generate time, shows a persistent warning with a one-click fix, and clears it once a regenerated code decodes.
4. A logo-bearing code decodes; rejected uploads show reason plus limit; saved logos can be reused and deleted.
5. A poster-size SVG with logo opens correctly in a vector editor.
6. `GET /api/qr` and the Cloudflare tunnel notes are gone, and the test suite passes.

## Boundaries

The Flask generator, its single UI page and the POST routes. Not frames, stress-test grades, saved presets/brands, built-in icons, the print-size helper, or transparent/inverted backgrounds (Could). Not diamond, separate eye pickers, sliders, SVG logo uploads, accounts or the GET shim (Won't). The spec's non-goals apply.

## References

- spec — _bmad-output/initiative-qr-style-options/epic-qr-style-options/spec-qr-style-options/spec-qr-style-options.md, capabilities CAP-1 to CAP-9
- spec — _bmad-output/initiative-qr-style-options/epic-qr-style-options/spec-qr-style-options/presets.md, preset table and eye-pairing rules
- spec — _bmad-output/initiative-qr-style-options/epic-qr-style-options/spec-qr-style-options/scope.md, MoSCoW and platform notes
- ux — _bmad-output/initiative-qr-style-options/ux-qr-style-options/DESIGN.md and EXPERIENCE.md
- constraint — CLAUDE.md, conventions (shared render helpers, whitelist validation, security headers, UI CSP `img-src 'self' data:`)

## Notes

- Decision: 2026-10-06 loose epic, no initiative; superseded 2026-10-07, the epic now sits under initiative-qr-style-options (user).
- Decision: 2026-10-07 re-sliced against the UX spines into 14 entries; story 1 is the tracer bullet (user).
- Decision: 2026-10-07 sequencing: 13 after 1; chains 2 -> 4 -> 5 -> 6 and 7 -> 3 -> 8 so no two stories edit the renderer or the single-file template at once; 14 before 10; 11 after 8 and 13 because 13 removes the Copy URL row that points at the route (user).
- Decision: 2026-10-07 any change replaces the old code with the empty state instead of dimming it; spec CAP-6 wording is out of date (user, from the UX spines).
- Decision: 2026-10-07 UX assumptions confirmed as written: 4:1 decodable-contrast threshold, Fix order contrast then EC then smaller logo, Download enabled while a scan warning is active (user).
- Decision: 2026-10-07 zxing-cpp enters as a dev dependency in story 1 and becomes a runtime dependency in story 7 (user).
- Assumption: the decoder is zxing-cpp; verify it decodes every styled preset before committing.
- Assumption: the "20" saved-logo cap was meant as 20 logos, not presets.
- Unknown: Fluid concave fillet radius, tuned later by the scan test.
