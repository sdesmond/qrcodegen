<!--
Sync Impact Report
==================
Version change: 1.0.0 → 1.0.1 (PATCH: clarification)
Modified principles:
  - II. Stable Public Contracts — removed the `lnklab.us` example; that domain is not a
    live consumer. The rule itself is unchanged.
Consumer impact (Principle II): none; no contract changed.
Added sections: none
Removed sections: none
Templates: not modified (dependent templates read this file at runtime)
Follow-up TODOs: none (CLAUDE.md "Consumers" section removed to match)
-->

# qrcodegen Constitution

## Core Principles

### I. Stateless & Self-Contained

The service MUST run as a single stateless container with no database, no persistent
storage, and no required external service. Every response MUST be computable from the
request alone. Optional integrations (e.g., URL shortener, analytics) MUST be gated by
configuration and MUST degrade gracefully—the core generator keeps working when they are
absent or unavailable.

**Rationale**: Statelessness keeps deployment to `docker compose up -d --build`, makes
responses deterministic and edge-cacheable, and removes an entire class of data-handling risk.

### II. Stable Public Contracts

`GET /api/qr` is a public embedding contract consumed by external services. Its response shape—raw image bytes, an `image/*` content type, and
long-lived public cache headers—MUST NOT change without coordinating with consumers.
Existing query parameters MUST NOT be removed or have their meaning changed; new parameters
MUST be optional with safe defaults. The same rule applies to the JSON envelope returned by
`POST /api/generate`.

**Rationale**: Printed and embedded QR codes cannot be reissued cheaply; a silent contract
break propagates to every consumer and may be cached at the edge.

### III. Whitelist Validation & Bounded Resources

All request input MUST be validated against an explicit whitelist or clamped range
(`_safe_color`, `_safe_int`, `_safe_float`, `_HEX_COLOR_RE`, and equivalents). Invalid
optional values MUST fall back to defaults rather than error; only missing required data
may return 4xx. Hard limits (`MAX_DATA_LEN`, `MIN_SIZE`, `MAX_SIZE`) MUST bound every
rendering path, and raising them requires an explicit justification of memory impact.
Security headers MUST be applied globally via `qr_bp.after_request`; per-route overrides
require a documented reason.

**Rationale**: This is a public, unauthenticated image renderer; unbounded input is a direct
path to resource exhaustion and injection.

### IV. Single Rendering Path

All routes MUST share the same helpers (`_build_qr_data`, `_parse_common`, `_make_qr_png`,
`_make_qr_svg`, `_make_barcode_buf`). New routes or features MUST extend these helpers rather
than fork rendering logic. New parameters are added once, in the shared parsing layer.

**Rationale**: One path means one set of limits, one set of bugs, and identical output across
the UI, the JSON API, downloads, and embeds.

### V. Tested Behavior

Every route and every shared helper MUST have pytest coverage in `tests/`. Any change to a
public contract (Principle II), validation rule, or hard limit (Principle III) MUST include
tests asserting the new behavior, including fallback behavior for invalid input. The full
suite (`python3 -m pytest`) MUST pass before merge or deploy.

**Rationale**: The service is small enough that complete coverage is cheap, and consumers
depend on exact behavior.

### VI. Structured Observability

Generation, download, and embed events MUST be logged as single-line JSON via `_log_event`,
including outcome (`status`) and, on failure, the error. Logs MUST NOT contain the encoded
payload data or other user-supplied content beyond non-sensitive metadata (format, content
type, size parameters, source).

**Rationale**: Structured events feed Grafana/Loki dashboards; excluding payloads keeps
potentially personal data (Wi-Fi passwords, contact cards) out of log storage.

## Operational Constraints

- **Stack**: Python, Flask, `qrcode`, `python-barcode`, Pillow, served by
  Gunicorn. New runtime dependencies require justification in the feature plan.
- **Deployment**: One `app` service in `docker-compose.yml`, container port 8000, exposed
  through Cloudflare Tunnel at `qrcode.chrisrmiller.com`. No sidecar services
  (reverse proxies, databases) may be added without amending Principle I.
- **Caching**: Deterministic GET responses SHOULD carry long-lived `public, immutable`
  cache headers. Error responses MUST NOT be marked cacheable, since Cloudflare can cache 4xx.
- **Configuration**: Environment variable changes require
  `docker compose up -d --force-recreate app`; `restart` does not re-read `.env`.

## Development Workflow

- Features follow the Spec Kit flow (`/speckit-specify` → `/speckit-plan` → `/speckit-tasks`
  → `/speckit-implement`); each plan MUST include a Constitution Check against the
  principles above.
- Changes land on `main` via small, focused commits; the test suite
  MUST pass locally before pushing.
- Changes to public routes MUST update the route table in `CLAUDE.md` and, where relevant,
  `README.md` and `docs/INTEGRATIONS.md` in the same change.
- Deploy is `git pull && docker compose up -d --build`; after deploy, verify `/api/qr` from
  the public URL, and suspect edge cache before code if results differ from the container.

## Governance

This constitution supersedes other project practices where they conflict. `CLAUDE.md` is the
runtime development guidance file and MUST remain consistent with it.

- **Amendments**: Proposed via a commit that edits this file, updates the Sync Impact Report,
  and states the rationale. Amendments affecting Principle II MUST note consumer impact.
- **Versioning**: Semantic versioning. MAJOR for removing or redefining a principle; MINOR for
  adding a principle or section or materially expanding guidance; PATCH for clarifications and
  wording fixes.
- **Compliance**: Every feature plan and code review MUST verify compliance with the Core
  Principles. Deviations MUST be recorded with justification in the plan's Complexity Tracking
  section, or the constitution amended first.

**Version**: 1.0.1 | **Ratified**: 2026-09-27 | **Last Amended**: 2026-09-27
