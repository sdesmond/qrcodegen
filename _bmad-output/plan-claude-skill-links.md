---
title: 'Share installed agent skills with Claude'
type: 'chore'
ticket: ''
created: '2026-10-06'
status: 'built'
baseline_revision: '593eab30f898d0af5ebf34209dc0903962fd749a'
route: 'oneshot'
route_source: 'auto'
risk: 'low'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context: ['C:/Users/spenc/dev/qrcodegen/CLAUDE.md']
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The user requested a script sharing `.agents/skills` with `.claude/skills`, matching Packt. The workflow was blocked by uv's `UnknownIssuer` error; the user then asked to fix that issue.

**Approach:** Persist uv's system-certificate setting for this repository and provide a dependency-free Node script linking the complete skills directory, using a Windows junction or a relative directory symlink on other platforms. Preserve existing user work and fail safely if an incompatible destination already exists.

</frozen-after-approval>

## Implementation Notes

- Use the oneshot route: fewer than 100 lines of setup code, low impact, no application behavior changes.
- Packt's `scripts/setup-dev.mjs` uses `symlinkSync` with `junction` on Windows and a relative `dir` target elsewhere.
- `uv run --system-certs --no-cache ...render_skill.py` succeeded outside the restricted environment. TLS verification remains enabled. Verify whether `[tool.uv]` is loaded for inline scripts before adding a separate config file.
- README already explains restoring skills with Node's skills CLI; add the linking command there. Ignore the generated `.claude/skills` path, keeping other Claude configuration trackable.
- The pre-existing LICENSE change, deleted skills-lock.json, and untracked BMad installation belong to the user.
- Implemented `scripts/link-skills.mjs`, documented usage in README, ignored the generated link, and enabled `[tool.uv] system-certs = true`. Project configuration is respected by inline-script execution; no separate uv.toml is necessary.
- Original renderer command succeeded with a fresh Jinja2 download outside the restricted environment and no TLS command-line override. The script created the Windows junction successfully.
- Verified all 33 skills through the junction; reran successfully from the system temp directory. Isolated fixtures checked missing source, existing directory with preserved contents, wrong junction, and dangling junction; each failed safely with exit code 1.

## Plan Change Log

## Review Triage Log

- Quick review returned no findings; no items deferred.

## Verification

- Given this repository's installed skills, when `node scripts/link-skills.mjs` runs, then `.claude/skills` resolves to `.agents/skills` and Claude can read every skill entry point.
- Given an already-correct link, when the script runs again, then it succeeds without changing the link.
- Given a conflicting destination or missing source, when the script runs, then it fails without overwriting existing data.
- Given invocation from another working directory, when the script runs by absolute path, then it still links this repository.
- Given the persistent certificate configuration, when the original renderer command runs without a TLS flag outside the restricted environment, then Jinja2 downloads successfully and the workflow renders.
- Run `node --check scripts/link-skills.mjs`, inspect the link and skill entry points, and run `git diff --check`.
