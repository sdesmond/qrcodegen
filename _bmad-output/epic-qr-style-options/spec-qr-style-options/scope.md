# Scope and platform notes

## MoSCoW

- **Must:** CAP-1 presets incl. Fluid, CAP-2 thumbnails, CAP-3 color, CAP-4 logo upgrade, CAP-5 scan check, CAP-6 button state, CAP-9 platform.
- **Should:** CAP-7 SVG print path, CAP-8 saved logo library.
- **Could:** frames (calm and simple: none, thin, rounded, label bar with ~3-word CTA; default off; quiet zone protected); stress-test grades (blur/shrink, A/B/C) and data-driven preset curation; saved presets/brands; built-in icon library; print-size helper (inches + dpi to px); transparent or inverted background (graded, never default).
- **Won't:** diamond preset, separate eye pickers, blend slider, spacing/roundness sliders, SVG logo uploads, accounts/auth, GET shim.

## Platform changes

- Remove `GET /api/qr` and lnklab consumer notes; remove Cloudflare tunnel notes (edge-cache gotcha, tunnel ingress) from CLAUDE.md and docs.
- SQLite file (stdlib `sqlite3`) in a docker volume for the logo library; logos stored at up to ~1024px; 20 count cap, env-configurable; instance-wide, open to LAN users; delete confirms inline and notes references.
- Print math: 1 ft code at 2000px is ~167 dpi; 30% logo is ~540px at 150 dpi, ~1080px at 300 dpi. A 4000x4000 RGBA render is ~64 MB.
- Inline logo errors give reason plus limit (e.g. "Too large: 3.1 MB, max 2 MB"); client pre-check for feedback, server is authoritative.
