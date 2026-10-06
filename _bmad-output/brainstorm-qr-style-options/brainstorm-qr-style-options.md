# QR Style Options: Intent

## Goal & context

Match the style depth of commercial QR generators (reference: ~20 body shapes, 14 eye frames, 16 eye balls) in the existing self-hosted Flask QR generator, without hurting the core job.

- **Job to be done:** "When I need a quick QR, I want to generate one in under 30 seconds so I can move on."
- **Personas:** home wifi sharer (stops at the default or a preset) through enterprise social media manager (styles with color and logo).
- **Constraint:** styling is opt-in. The default path is unchanged: content, Generate, Download. Default preset is Square, which matches today's output.
- **Real print case:** 6x3 ft poster, QR at least 1 ft square.

## Core decisions

**Shape presets** replace separate dot, eye frame and eye ball pickers. One preset is one coherent family. There are no mismatched eyes, and no blend or intensity slider. Tunable spacing and roundness sliders are dropped entirely.

| Preset | Dots | Eye frame | Eye ball |
|---|---|---|---|
| Square (default) | square | square | square |
| Circle | circular | circular | circular |
| Rounded | rounded, not merged | rounded | rounded |
| Horizontal | horizontal pills | rounded | horizontal pill stack |
| Vertical | vertical pills | rounded | vertical pill stack |
| Bubble | small gapped circles | rounded | multi-dot grid |
| Fluid | merged blobs, rounded convex and concave corners | rounded square | rounded blob |

- **Eye-pairing rule:** the eye frame echoes the dot END treatment (rounded ends mean a rounded frame). The ball echoes the dot DIRECTION or form. Frames stay square-aspect so the 1:1:3:1:1 finder ratio holds.
- "Always rounded, no square edges" applies to Fluid only. Square stays square.
- One preset-table row {dot, frame, ball} drives the renderer, the thumbnail and the scan-test fixture.
- **Color is separate:** solid or gradient, an independent axis applied on top of any preset.
- **Preset thumbnails** are static, always available and independent of user data. Each is a zoomed upper-left crop of a demo QR (eye plus some dots). They are client-side inline SVG from the shared preset table and follow the currently chosen color or gradient.
- **Logo upgrade:** the existing POST logo support stays. It gains soft fade (dot size shrinks with distance from the logo edge, not opacity, so decoders still binarize cleanly), storage and rendering at ~1024px, and clear inline errors (reason plus limit, never blocking the rest of the form). The existing `_load_logo` validation is kept.
- **Scan check (Must):** the server decodes its own render at generate time (not live per keystroke). A persistent warning calls for action and offers a one-click suggested fix (EC bump, smaller logo, contrast clamp). The user can also fix manually or dismiss. It covers the residual risks that presets do not: color contrast, logo size and fade, dense data, small output.
- **Inverse buttons:** a manual Generate button is kept. Input change enables Generate and disables Download. A fresh code disables Generate and enables Download. So "Download enabled" means a verified, fresh code. The old QR stays visible but dimmed while stale or regenerating. Picking a preset marks the code stale.
- **Print path:** SVG is the poster path, with vector dots and eyes. The embedded logo is raster, so its stored resolution (~1024px) is the limit. At 1 ft and 30% logo, that is ~540px at 150dpi or ~1080px at 300dpi. PNG is bounded by MAX_SIZE (2000, possibly raised modestly to ~4000, which is ~64MB RGBA per render). A vector-editor check of a poster-size SVG with logo is a release check.

## MoSCoW

**Must**
- Shape presets including Fluid
- Static, color-aware preset thumbnails
- Separate solid/gradient color
- Logo upgrade (fade, ~1024px, clear errors)
- Inverse Generate/Download buttons
- Scan check (generate-time decode, persistent warning, one-click fix)
- Drop `/api/qr`

**Should**
- Server-side saved logos with delete (SQLite)
- SVG print path plus vector-editor release check

**Could**
- Frames (simple, calm, default off, minimal CTA text)
- Stress-test grades and data-driven preset curation
- Saved presets and brands
- Built-in icon library
- Print-size helper
- Transparent or inverted background

**Won't**
- Diamond preset
- Separate eye pickers
- Blend/intensity slider
- Tunable spacing/roundness sliders
- SVG logo uploads
- Accounts or auth
- GET shim

## Platform changes

- Drop `GET /api/qr` and the lnklab consumer notes. All options go through POST.
- Remove the Cloudflare tunnel. The app is LAN/private only, so abuse and rate-limit concerns go away. Remove the public-edge notes (CF 4xx cache gotcha, tunnel ingress) from CLAUDE.md and docs.
- SQLite file in a docker volume (stdlib `sqlite3`) for saved logos and presets. Logos are stored as re-encoded PNG only (never the raw upload), with metadata stripped, an atomic write, and a modest count and size cap (~24 logos, env-configurable). The library is instance-wide and open to LAN users. The picker offers delete with inline confirm, and a deleted logo that is referenced falls back to no logo with a note.
- New decoder dependency (zxing-cpp or opencv, pick small wheels) via uv and Docker. Pre-check the Mobicip TLS interception issue with container pip.
- Check gunicorn worker count and memory if MAX_SIZE is raised.

## Open questions

- Fluid concave corners: smoothed fillets (implied by "no square edges") with a fixed radius tuned by scan test. Needs confirmation.
- Thumbnail rendering: a JS renderer duplicates the shape logic. Mitigate with a shared preset JSON table and golden-image tests, or serve server SVG with color params. Decision pending.
- Saved-logo cap: is ~24 right for a self-hosted team?
- Raise PNG MAX_SIZE (2000 to ~4000), or rely on SVG for print?
- Scan warning semantics: persists until resolved or explicitly dismissed per style. Confirm.
- Which decoder: zxing-cpp or opencv.

## Key insights

- Presets move safety to design time: shapes are vetted offline by the scan test, and the runtime check covers only residual risks (color contrast, logo size, dense data).
- One preset-table row is the single source of truth for renderer, thumbnail and scan-test fixture.
- Inverse buttons plus a generate-time scan mean "Download enabled" equals "verified scannable". The UI state machine carries the safety guarantee.
- Dropping the public tunnel and GET shim unlocked server storage, larger renders and persistent libraries.
- What matters most: presets, safety checks, and keeping the 30-second path simple.
