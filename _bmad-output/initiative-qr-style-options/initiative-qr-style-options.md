---
type: initiative
title: QR Style Options
parent: none
covers: [CAP-1, CAP-2, CAP-3, CAP-4, CAP-5, CAP-6, CAP-7, CAP-8, CAP-9]
assignee: ""
risk: medium
---

# QR Style Options

## Description

The self-hosted QR generator gains shape presets, independent color and gradient, a logo upgrade with soft fade, a generate-time scan check with a one-click fix, and a restyled accessible UI. The default path (content, Generate, Download) stays fast and unchanged. The spec owns the capabilities, constraints and non-goals; the UX spines own how the page looks and behaves.

## Outcome

A first-time user still gets a download in under 30 seconds with nothing styled; a brand user picks a preset, color and saved logo and gets a code that decodes, or is told exactly how to fix it; a 1 ft poster SVG with logo prints sharp. The spec's success signal is the measure.

## Done when

1. All seven presets render and decode on PNG and SVG, and Square output matches today's.
2. The scan check flags a failing code on both PNG and SVG, offers a one-click fix, and clears once a regenerated code decodes.
3. A logo-bearing code decodes; saved logos can be reused and deleted; rejected uploads show reason plus limit.
4. The page meets the UX spines' accessibility floor and Generate/Download behave as strict inverses.
5. `GET /api/qr` and the Cloudflare tunnel notes are gone and the test suite passes.

## Boundaries

The Flask generator, its single UI page and the POST routes, delivered as one epic by one owner (one outcome, one module). Not the Could and Won't items in the spec's `scope.md`. Tracer path: Circle preset picked in the UI, generated and decoded.

- Touch point: Docker image and compose — new decoder dependency and a volume for the logo library; owner: epic-qr-style-options

## References

- spec — _bmad-output/initiative-qr-style-options/epic-qr-style-options/spec-qr-style-options/spec-qr-style-options.md, capabilities CAP-1 to CAP-9
- ux — _bmad-output/initiative-qr-style-options/ux-qr-style-options/DESIGN.md and EXPERIENCE.md
- constraint — CLAUDE.md, conventions (shared render helpers, whitelist validation, security headers, UI CSP)
- brainstorm — _bmad-output/brainstorm-qr-style-options/brainstorm-qr-style-options.md, history only

## Notes

- Decision: 2026-10-07 — the earlier "loose epic, no initiative" decision is superseded; the epic moves under this initiative and its breakdown is re-sliced against the UX spines (user).
- Source conflict: spec CAP-6 — old code is dimmed vs EXPERIENCE.md, where any change removes the old code and shows the empty state "Configure and generate" (user decision recorded in the UX).
- Decision: 2026-10-07 the UX Open Items assumptions (4:1 contrast threshold, Fix order, Download enabled during a scan warning) are confirmed as written (user).
