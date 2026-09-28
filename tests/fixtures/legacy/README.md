# Legacy output fixtures

Captured from `GET /api/qr` on `main` before the QR shape styles feature
(`specs/001-qr-shape-styles`, task T001). Tests use them to prove that
requests without shape params render exactly as before (SC-002).

| File | Query string |
|---|---|
| `url_png.png` | `data=https://example.com/abc` |
| `hello_svg.svg` | `data=hello&format=svg` |
| `x_800_m0_fg_H.png` | `data=x&size=800&margin=0&fg_color=%23112233&ec_level=H` |

Captured with:

- Pillow: 12.3.0
- qrcode: 8.2

PNG fixtures are compared by decoded pixels, not file bytes, because zlib
output differs between platforms. SVG fixtures are compared byte for byte.
The tests skip when the installed Pillow or qrcode version differs from the
versions above; re-capture the fixtures after upgrading either library.
