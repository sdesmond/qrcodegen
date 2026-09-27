# Quickstart: Validating QR Shape Styles

These are runnable checks that show the feature works end to end. For parameter semantics, see
[contracts/http-params.md](contracts/http-params.md) and
[contracts/generator-ui.md](contracts/generator-ui.md). For geometry, see
[data-model.md](data-model.md).

## 0. Prerequisites

Local Python currently has no project dependencies installed, so create a venv first:

```bash
python3 -m venv .venv
. .venv/Scripts/activate        # Windows Git Bash; use .venv/bin/activate on Linux/macOS
pip install -r requirements-dev.txt   # includes zxing-cpp after this feature
```

## 1. Capture baseline hashes (before implementing, on current `main`)

```bash
PORT=8000 python3 preview_app.py &
for q in "data=https://example.com/abc" "data=hello&format=svg" "data=x&size=800&margin=0&fg_color=%23112233&ec_level=H"; do
  curl -s "http://localhost:8000/api/qr?$q" | sha256sum
done > /tmp/qr-baseline.txt
```

## 2. Automated suite

```bash
python3 -m pytest                        # full suite must pass (Principle V)
python3 -m pytest -k shape -q            # parser, geometry, routes
python3 -m pytest -k decode -q           # 315-combination zxing decode (SC-001), a few seconds
```

Expected: everything passes. The decode test reports 315 successful combos plus the
dense / min-size / margin-0 cases.

## 3. Contract checks (after implementing)

```bash
# Legacy byte-identity (SC-002): must match /tmp/qr-baseline.txt line for line
for q in "data=https://example.com/abc" "data=hello&format=svg" "data=x&size=800&margin=0&fg_color=%23112233&ec_level=H"; do
  curl -s "http://localhost:8000/api/qr?$q" | sha256sum
done | diff - /tmp/qr-baseline.txt && echo "no regression"

# Explicit all-square and invalid values are identical to baseline too
curl -s "http://localhost:8000/api/qr?data=https://example.com/abc&dot_shape=square&eye_border=square&eye_center=square" | sha256sum
curl -s "http://localhost:8000/api/qr?data=https://example.com/abc&dot_shape=Dots&eye_border=nope" | sha256sum

# Styled embed keeps headers (FR-013)
curl -sI "http://localhost:8000/api/qr?data=https://example.com/abc&dot_shape=dots&eye_border=circle&eye_center=circle" \
  | grep -iE "content-type|cache-control"
# → Content-Type: image/png ; Cache-Control: public, max-age=86400, immutable

# SVG stays vector (FR-008)
curl -s "http://localhost:8000/api/qr?data=hi&format=svg&dot_shape=extra_rounded&eye_border=leaf" | grep -c "<path"
```

## 4. Visual check against the reference images (SC-006, US1-4, US2-5)

1. Open `http://localhost:8000/generator` in QR mode and confirm the "Shape style" section shows
   9 dot, 7 border, and 5 center swatches.
2. Compare the swatches side by side with `assets/dot-shape-styles.png` (options 1–8, then
   Gapped square) and `assets/eye-border-styles.png`. Check that they appear in the same order
   with recognisably the same silhouettes, and that each eye center has the same orientation as
   the matching border.
3. Switch to a barcode format and confirm the section is hidden.

## 5. Manual end-to-end (US1–US3, SC-003, SC-004)

1. Enter a URL, click Generate, then pick "Dots". The preview should update, with the eyes
   unchanged.
2. Pick the "Leaf" border and "Circle" center. Only the eyes should change, on all three
   corners, with identical orientation.
3. Set custom fg/bg colors. Shapes should use them in PNG.
4. Download the PNG and the SVG. Both should match the preview, and both should scan with a
   phone camera.
5. Time it from landing on the page to finishing the download. It should take under 30 s.

## 6. Logging (FR-015)

With the app running, request a styled `/api/qr` and check stdout for a single-line JSON
`qr_embed` event containing `dot_shape`, `eye_border`, and `eye_center`, and **no** `data`
value.
