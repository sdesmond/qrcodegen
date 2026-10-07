import re
import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import zxingcpp
from PIL import Image, ImageChops, ImageDraw

from preview_app import app as flask_app


@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


# ── Decode helpers (zxing-cpp is a dev-only dependency) ─────────────────────

def decode_image(img):
    """Decode a PIL image; return the list of decoded texts."""
    return [r.text for r in zxingcpp.read_barcodes(img.convert('L'))]


def rasterize_svg(svg_bytes, px_per_unit=12):
    """Rasterise our own styled-SVG output (one evenodd <path> plus optional
    pad <rect>; an embedded <image> logo is skipped, the pad hole stays)."""
    svg = svg_bytes.decode('utf-8')
    units = float(re.search(r'viewBox="0 0 ([0-9.]+) ', svg).group(1))
    side = int(round(units * px_per_unit))
    mask = Image.new('1', (side, side), 0)
    d = re.search(r'<path[^>]* d="([^"]+)"', svg).group(1)
    for sub in filter(None, (s.strip() for s in d.split('z'))):
        layer = Image.new('1', (side, side), 0)
        draw = ImageDraw.Draw(layer)
        m = re.match(r'M([-0-9.e]+) ([-0-9.e]+)(.*)', sub)
        x, y, rest = float(m.group(1)), float(m.group(2)), m.group(3)
        if rest.startswith('a'):      # circle: left-most point, radius r
            r = float(re.match(r'a([-0-9.e]+)', rest).group(1))
            draw.ellipse([x * px_per_unit, (y - r) * px_per_unit,
                          (x + 2 * r) * px_per_unit, (y + r) * px_per_unit], fill=1)
        else:                         # square: h s v s h -s
            s = float(re.match(r'h([-0-9.e]+)', rest).group(1))
            draw.rectangle([x * px_per_unit, y * px_per_unit,
                            (x + s) * px_per_unit - 1, (y + s) * px_per_unit - 1], fill=1)
        mask = ImageChops.logical_xor(mask, layer)
    img = Image.new('RGB', (side, side), '#ffffff')
    img.paste('#000000', mask=mask)
    draw = ImageDraw.Draw(img)
    for m in re.finditer(r'<rect x="([0-9.]+)" y="([0-9.]+)" width="([0-9.]+)" height="([0-9.]+)" fill="([^"]+)"', svg):
        x, y, w, h = (float(v) * px_per_unit for v in m.groups()[:4])
        draw.rectangle([x, y, x + w - 1, y + h - 1], fill=m.group(5))
    return img
