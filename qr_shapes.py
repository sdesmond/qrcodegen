"""Shape geometry and PNG/SVG backends for styled QR codes.

Pure module: no Flask imports. A styled QR is described as a list of
``RRect`` primitives in module units (built once by ``build_primitives``)
and drawn two ways: a supersampled Pillow mask for PNG and ``<path>`` data
for SVG. Both backends consume the same primitive lists, so PNG and SVG
output always share one geometry.

Shape constants are documented in specs/001-qr-shape-styles/research.md §5.
"""
import io
import math
from decimal import Decimal
from typing import NamedTuple, Tuple

import qrcode
from PIL import Image, ImageDraw

# ── Whitelists (order = UI display order) ────────────────────────────────────

DEFAULT = 'square'

DOT_SHAPES = ('square', 'rounded', 'extra_rounded', 'dots', 'classy', 'classy_rounded',
              'horizontal_bars', 'vertical_bars', 'gapped_square')
EYE_BORDERS = ('square', 'rounded', 'circle', 'teardrop', 'leaf', 'leaf_circle',
               'square_circle')
EYE_CENTERS = ('square', 'rounded', 'circle', 'teardrop', 'leaf')

DOT_SHAPE_SET = frozenset(DOT_SHAPES)
EYE_BORDER_SET = frozenset(EYE_BORDERS)
EYE_CENTER_SET = frozenset(EYE_CENTERS)

_DISPLAY_NAMES = {
    'dot': {
        'square': 'Square', 'rounded': 'Rounded', 'extra_rounded': 'Extra rounded',
        'dots': 'Dots', 'classy': 'Classy', 'classy_rounded': 'Classy rounded',
        'horizontal_bars': 'Horizontal bars', 'vertical_bars': 'Vertical bars',
        'gapped_square': 'Gapped square',
    },
    'eye_border': {
        'square': 'Square', 'rounded': 'Rounded', 'circle': 'Circle', 'teardrop': 'Teardrop',
        'leaf': 'Leaf', 'leaf_circle': 'Leaf, round opening',
        'square_circle': 'Square, round opening',
    },
    'eye_center': {
        'square': 'Square', 'rounded': 'Rounded', 'circle': 'Circle', 'teardrop': 'Teardrop',
        'leaf': 'Leaf',
    },
}


def display_name(kind, value):
    return _DISPLAY_NAMES[kind][value]


class ShapeStyle(NamedTuple):
    dot: str = DEFAULT
    eye_border: str = DEFAULT
    eye_center: str = DEFAULT

    @property
    def is_default(self):
        return self.dot == self.eye_border == self.eye_center == DEFAULT


# ── Geometry primitive ───────────────────────────────────────────────────────

Corners = Tuple[bool, bool, bool, bool]  # TL, TR, BR, BL
NO_CORNERS = (False, False, False, False)
ALL_CORNERS = (True, True, True, True)


class RRect(NamedTuple):
    """Rectangle in module units with optionally rounded corners.

    ``ink`` 1 paints foreground; 0 cuts an opening (eye rings).
    """
    x: float
    y: float
    w: float
    h: float
    r: float
    corners: Corners
    ink: int = 1


def circle(cx, cy, d, ink=1):
    return RRect(cx - d / 2, cy - d / 2, d, d, d / 2, ALL_CORNERS, ink)


# ── Matrix and finder patterns ───────────────────────────────────────────────

def get_matrix(data, ec):
    qr = qrcode.QRCode(error_correction=ec, border=0)
    qr.add_data(data)
    qr.make(fit=True)
    return [[bool(v) for v in row] for row in qr.get_matrix()]


def finder_boxes(n):
    """Origins (x, y) of the three 7×7 finder patterns."""
    return [(0, 0), (n - 7, 0), (0, n - 7)]


def is_finder(x, y, n):
    return (x < 7 and y < 7) or (x >= n - 7 and y < 7) or (x < 7 and y >= n - 7)


# ── Shape dispatch ───────────────────────────────────────────────────────────

def _dot_primitives(dot, x, y, nb):
    """Primitives for the dark data module at (x, y).

    ``nb(dx, dy)`` is True when the orthogonal neighbour is a dark data module.
    Corner rule: a corner is rounded only when both neighbours touching it are
    absent, so joined modules render as solid groups with rounded outer corners.
    """
    if dot == 'dots':
        return [circle(x + 0.5, y + 0.5, 0.9)]
    if dot == 'gapped_square':
        return [RRect(x + 0.1, y + 0.1, 0.8, 0.8, 0, NO_CORNERS)]
    if dot == 'horizontal_bars':
        left, right = not nb(-1, 0), not nb(1, 0)
        return [RRect(x, y + 0.1, 1, 0.8, 0.4, (left, right, right, left))]
    if dot == 'vertical_bars':
        top, bottom = not nb(0, -1), not nb(0, 1)
        return [RRect(x + 0.1, y, 0.8, 1, 0.4, (top, top, bottom, bottom))]
    if dot in ('rounded', 'extra_rounded', 'classy', 'classy_rounded'):
        up, down, left, right = not nb(0, -1), not nb(0, 1), not nb(-1, 0), not nb(1, 0)
        tl, tr, br, bl = up and left, up and right, down and right, down and left
        if dot.startswith('classy'):
            tr = bl = False
        r = 0.5 if dot in ('extra_rounded', 'classy_rounded') else 0.25
        return [RRect(x, y, 1, 1, r, (tl, tr, br, bl))]
    return [RRect(x, y, 1, 1, 0, NO_CORNERS)]


def _eye_border_primitives(border, ox, oy):
    """[outer ring (ink 1), opening (ink 0)] for the finder at (ox, oy)."""
    return [RRect(ox, oy, 7, 7, 0, NO_CORNERS, 1),
            RRect(ox + 1, oy + 1, 5, 5, 0, NO_CORNERS, 0)]


def _eye_center_primitives(center, ox, oy):
    """The solid 3×3 center for the finder at (ox, oy)."""
    return [RRect(ox + 2, oy + 2, 3, 3, 0, NO_CORNERS, 1)]


def _dots_for(matrix, dot, skip=None):
    n = len(matrix)

    def dark(x, y):
        return (0 <= x < n and 0 <= y < n and matrix[y][x]
                and not (skip and skip(x, y)))

    dots = []
    for y in range(n):
        for x in range(n):
            if dark(x, y):
                dots.extend(_dot_primitives(dot, x, y,
                                            lambda dx, dy, x=x, y=y: dark(x + dx, y + dy)))
    return dots


def build_primitives(matrix, style):
    """Return ``(dots, eyes)``: lists of RRect in module units (margin excluded)."""
    n = len(matrix)
    dots = _dots_for(matrix, style.dot, skip=lambda x, y: is_finder(x, y, n))
    eyes = []
    for ox, oy in finder_boxes(n):
        eyes.extend(_eye_border_primitives(style.eye_border, ox, oy))
        eyes.extend(_eye_center_primitives(style.eye_center, ox, oy))
    return dots, eyes


# ── PNG backend ──────────────────────────────────────────────────────────────

_MAX_CANVAS = 4096


def _supersample_ppm(n_total, size):
    """Pixels per module for the supersampled mask, keeping its side ≤ 4096 px."""
    return max(1, min(math.ceil(3 * size / n_total), _MAX_CANVAS // n_total))


def _draw_rrect(draw, rect, ppm, margin, fill):
    x0 = round((rect.x + margin) * ppm)
    y0 = round((rect.y + margin) * ppm)
    x1 = round((rect.x + rect.w + margin) * ppm)  # exclusive
    y1 = round((rect.y + rect.h + margin) * ppm)
    if x1 <= x0 or y1 <= y0:
        return
    r = round(min(rect.r, rect.w / 2, rect.h / 2) * ppm)
    r = min(r, (x1 - x0) // 2, (y1 - y0) // 2)
    if r <= 0:
        draw.rectangle([x0, y0, x1 - 1, y1 - 1], fill=fill)
        return
    # Cross rectangles; each is skipped when degenerate.
    if x1 - r - 1 >= x0 + r:
        draw.rectangle([x0 + r, y0, x1 - r - 1, y1 - 1], fill=fill)
    if y1 - r - 1 >= y0 + r:
        draw.rectangle([x0, y0 + r, x1 - 1, y1 - r - 1], fill=fill)
    d = 2 * r
    tl, tr, br, bl = rect.corners
    # (rounded?, square box, pieslice box, start angle)
    for rounded, sq, pie, start in (
        (tl, [x0, y0, x0 + r - 1, y0 + r - 1], [x0, y0, x0 + d - 1, y0 + d - 1], 180),
        (tr, [x1 - r, y0, x1 - 1, y0 + r - 1], [x1 - d, y0, x1 - 1, y0 + d - 1], 270),
        (br, [x1 - r, y1 - r, x1 - 1, y1 - 1], [x1 - d, y1 - d, x1 - 1, y1 - 1], 0),
        (bl, [x0, y1 - r, x0 + r - 1, y1 - 1], [x0, y1 - d, x0 + d - 1, y1 - 1], 90),
    ):
        if rounded:
            draw.pieslice(pie, start, start + 90, fill=fill)
        else:
            draw.rectangle(sq, fill=fill)


def rasterize_png(dots, eyes, n, margin, size, fg, bg):
    n_total = n + 2 * margin
    ppm = _supersample_ppm(n_total, size)
    mask = Image.new('L', (n_total * ppm, n_total * ppm), 0)
    draw = ImageDraw.Draw(mask)
    for rect in list(dots) + list(eyes):
        _draw_rrect(draw, rect, ppm, margin, 255 if rect.ink else 0)
    mask = mask.resize((size, size), Image.LANCZOS)
    img = Image.composite(Image.new('RGB', (size, size), fg),
                          Image.new('RGB', (size, size), bg), mask)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


# ── SVG backend ──────────────────────────────────────────────────────────────

def _num(v):
    s = f'{v:.3f}'.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


def _rrect_subpath(rect, off):
    x0, y0 = rect.x + off, rect.y + off
    x1, y1 = x0 + rect.w, y0 + rect.h
    r = min(rect.r, rect.w / 2, rect.h / 2)
    tl, tr, br, bl = rect.corners if r > 0 else NO_CORNERS
    arc = f'A{_num(r)} {_num(r)} 0 0 1 '
    p = [f'M{_num(x0 + r if tl else x0)} {_num(y0)}', f'H{_num(x1 - r if tr else x1)}']
    if tr:
        p.append(f'{arc}{_num(x1)} {_num(y0 + r)}')
    p.append(f'V{_num(y1 - r if br else y1)}')
    if br:
        p.append(f'{arc}{_num(x1 - r)} {_num(y1)}')
    p.append(f'H{_num(x0 + r if bl else x0)}')
    if bl:
        p.append(f'{arc}{_num(x0)} {_num(y1 - r)}')
    if tl:
        p.append(f'V{_num(y0 + r)}')
        p.append(f'{arc}{_num(x0 + r)} {_num(y0)}')
    p.append('Z')
    return ''.join(p)


def _path_d(rects, off):
    return ''.join(_rrect_subpath(r, off) for r in rects)


def _svg_mm(size, margin, n):
    """Width/height matching the legacy qrcode SvgImage (mm, box_size / 10 per module)."""
    box_size = max(1, size // (21 + margin * 2))
    return f'{Decimal(box_size * (n + 2 * margin)) / Decimal(10)}mm'


def to_svg(dots, eyes, n, margin, size):
    n_total = n + 2 * margin
    dim = _svg_mm(size, margin, n)
    parts = ["<?xml version='1.0' encoding='UTF-8'?>\n",
             f'<svg xmlns="http://www.w3.org/2000/svg" width="{dim}" height="{dim}" '
             f'viewBox="0 0 {n_total} {n_total}">']
    if dots:
        parts.append(f'<path d="{_path_d(dots, margin)}"/>')
    if eyes:
        parts.append(f'<path fill-rule="evenodd" d="{_path_d(eyes, margin)}"/>')
    parts.append('</svg>')
    buf = io.BytesIO(''.join(parts).encode('utf-8'))
    buf.seek(0)
    return buf


# ── UI swatches ──────────────────────────────────────────────────────────────

# 5×5 dot sample: horizontal and vertical joins, L-corners and an isolated module
_SWATCH_DOTS = (
    '11101',
    '10100',
    '10011',
    '01010',
    '11001',
)


def _swatch_wrapper(view, paths):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="{0}" width="36" height="36" '
            'fill="currentColor" aria-hidden="true" focusable="false">{1}</svg>').format(view, paths)


def swatch_svg(kind, value):
    """Inline SVG preview for one picker option, drawn with the production geometry."""
    if kind == 'dot':
        matrix = [[c == '1' for c in row] for row in _SWATCH_DOTS]
        dots = _dots_for(matrix, value)
        return _swatch_wrapper('-0.5 -0.5 6 6', f'<path d="{_path_d(dots, 0)}"/>')
    return ''
