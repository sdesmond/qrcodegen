"""Unit tests for qr_shapes: whitelists, geometry primitives, and backends."""
import io
import math
import re
import xml.etree.ElementTree as ET

import pytest
from PIL import Image
from qrcode.constants import ERROR_CORRECT_M

import qr_shapes
from qr_shapes import (
    DOT_SHAPES, EYE_BORDERS, EYE_CENTERS, ShapeStyle, RRect, circle,
    get_matrix, finder_boxes, is_finder, build_primitives,
    rasterize_png, to_svg, _supersample_ppm, _path_d,
)

SVG_NS = '{http://www.w3.org/2000/svg}'
URL = 'https://example.com/abc'
NONE = (False, False, False, False)
ALL = (True, True, True, True)


def _matrix():
    return get_matrix(URL, ERROR_CORRECT_M)


def _inside(rect, x0, y0, x1, y1, eps=1e-9):
    return (rect.x >= x0 - eps and rect.y >= y0 - eps
            and rect.x + rect.w <= x1 + eps and rect.y + rect.h <= y1 + eps)


# ── Whitelists and value types ───────────────────────────────────────────────

class TestWhitelists:
    def test_dot_shapes_in_contract_order(self):
        assert DOT_SHAPES == ('square', 'rounded', 'extra_rounded', 'dots', 'classy',
                              'classy_rounded', 'horizontal_bars', 'vertical_bars',
                              'gapped_square')

    def test_eye_borders_in_contract_order(self):
        assert EYE_BORDERS == ('square', 'rounded', 'circle', 'teardrop', 'leaf')

    def test_eye_centers_in_contract_order(self):
        assert EYE_CENTERS == ('square', 'rounded', 'circle', 'teardrop', 'leaf')

    def test_lengths(self):
        assert (len(DOT_SHAPES), len(EYE_BORDERS), len(EYE_CENTERS)) == (9, 5, 5)

    def test_every_value_has_a_display_name(self):
        for kind, values in (('dot', DOT_SHAPES), ('eye_border', EYE_BORDERS),
                             ('eye_center', EYE_CENTERS)):
            for v in values:
                assert qr_shapes.display_name(kind, v)
        assert qr_shapes.display_name('eye_border', 'teardrop') == 'Teardrop'
        assert qr_shapes.display_name('dot', 'extra_rounded') == 'Extra rounded'


class TestRRect:
    def test_fields(self):
        assert RRect._fields == ('x', 'y', 'w', 'h', 'r', 'corners', 'ink')

    def test_circle_helper(self):
        c = circle(2.5, 3.5, 0.9)
        assert c == RRect(2.05, 3.05, 0.9, 0.9, 0.45, ALL, 1)
        assert circle(0, 0, 2, ink=0).ink == 0


# ── Matrix and finders ───────────────────────────────────────────────────────

class TestMatrix:
    def test_matrix_is_square_bool_grid_without_border(self):
        m = _matrix()
        n = len(m)
        assert n == 25  # version 2 for this payload at EC M
        assert all(len(row) == n for row in m)
        assert all(isinstance(v, bool) for row in m for v in row)
        # Top-left finder's outer ring starts at (0, 0) because border=0
        assert m[0][0] and m[0][6] and not m[1][1]

    def test_finder_boxes(self):
        assert finder_boxes(25) == [(0, 0), (18, 0), (0, 18)]

    def test_is_finder(self):
        assert is_finder(0, 0, 25) and is_finder(6, 6, 25)
        assert not is_finder(7, 7, 25)
        assert is_finder(24, 0, 25) and is_finder(0, 24, 25)
        assert not is_finder(24, 24, 25)


# ── build_primitives (square style) ──────────────────────────────────────────

class TestBuildPrimitivesSquare:
    def test_one_unit_dot_per_dark_data_module(self):
        m = _matrix()
        n = len(m)
        dots, _ = build_primitives(m, ShapeStyle())
        expected = {(x, y) for y in range(n) for x in range(n)
                    if m[y][x] and not is_finder(x, y, n)}
        assert {(d.x, d.y) for d in dots} == expected
        assert len(dots) == len(expected)
        for d in dots:
            assert (d.w, d.h, d.r, d.ink) == (1, 1, 0, 1)

    def test_no_dots_inside_finder_boxes(self):
        m = _matrix()
        dots, _ = build_primitives(m, ShapeStyle('dots'))
        for d in dots:
            assert not is_finder(int(d.x), int(d.y), len(m))

    def test_eye_primitive_order(self):
        m = _matrix()
        n = len(m)
        _, eyes = build_primitives(m, ShapeStyle())
        assert len(eyes) == 9
        for i, (ox, oy) in enumerate(finder_boxes(n)):
            outer, opening, center = eyes[3 * i:3 * i + 3]
            assert (outer.ink, opening.ink, center.ink) == (1, 0, 1)
            assert (outer.x, outer.y, outer.w, outer.h) == (ox, oy, 7, 7)
            assert (opening.x, opening.y, opening.w, opening.h) == (ox + 1, oy + 1, 5, 5)
            assert (center.x, center.y, center.w, center.h) == (ox + 2, oy + 2, 3, 3)

    def test_nothing_outside_symbol(self):
        m = _matrix()
        n = len(m)
        dots, eyes = build_primitives(m, ShapeStyle())
        for p in dots + eyes:
            assert _inside(p, 0, 0, n, n)


# ── PNG backend ──────────────────────────────────────────────────────────────

class TestRasterizePng:
    def _render(self, size=300, margin=4, fg='#000000', bg='#ffffff', style=ShapeStyle()):
        m = _matrix()
        dots, eyes = build_primitives(m, style)
        return rasterize_png(dots, eyes, len(m), margin, size, fg, bg)

    def test_valid_png_of_exact_size(self):
        buf = self._render(size=333)
        assert buf.tell() == 0
        img = Image.open(buf)
        assert img.format == 'PNG'
        assert img.size == (333, 333)

    def test_corner_pixel_is_background(self):
        img = Image.open(self._render(bg='#fffde7')).convert('RGB')
        assert img.getpixel((0, 0)) == (0xff, 0xfd, 0xe7)

    def test_finder_pixel_is_foreground(self):
        # Centre of the top-left eye: margin 4 + 3.5 modules of a 33-module image
        img = Image.open(self._render(size=330, fg='#1a237e')).convert('RGB')
        px = int((4 + 3.5) * 10)
        assert img.getpixel((px, px)) == (0x1a, 0x23, 0x7e)

    def test_supersample_canvas_capped(self):
        n_total = 177 + 2 * 10  # version 40 with max margin
        assert _supersample_ppm(n_total, 2000) * n_total <= 4096
        assert _supersample_ppm(n_total, 2000) >= 20

    def test_supersample_is_about_3x(self):
        assert _supersample_ppm(33, 300) == 28  # ceil(900 / 33)
        assert _supersample_ppm(33, 100) == 10

    def test_supersample_never_below_one(self):
        assert _supersample_ppm(4096, 100) == 1


# ── SVG backend ──────────────────────────────────────────────────────────────

def _svg_root(buf):
    return ET.fromstring(buf.getvalue())


class TestToSvg:
    def _render(self, style=ShapeStyle('dots'), size=300, margin=4):
        m = _matrix()
        dots, eyes = build_primitives(m, style)
        return to_svg(dots, eyes, len(m), margin, size)

    def test_parses_as_svg_with_viewbox(self):
        buf = self._render()
        assert buf.tell() == 0
        root = _svg_root(buf)
        assert root.tag == SVG_NS + 'svg'
        assert root.get('viewBox') == '0 0 33 33'

    def test_vector_paths_only(self):
        root = _svg_root(self._render())
        assert len(root.findall(SVG_NS + 'path')) >= 1
        assert root.find('.//' + SVG_NS + 'image') is None
        assert root.find('.//' + SVG_NS + 'rect') is None  # no background rect

    def test_eyes_path_is_evenodd(self):
        root = _svg_root(self._render())
        assert any(p.get('fill-rule') == 'evenodd' for p in root.findall(SVG_NS + 'path'))

    @pytest.mark.parametrize('size,margin', [(300, 4), (800, 0), (100, 10), (2000, 2)])
    def test_dimensions_match_legacy_svg(self, size, margin):
        from qr_generator import _make_qr_svg
        legacy = ET.fromstring(_make_qr_svg(URL, ERROR_CORRECT_M, size, margin).getvalue())
        root = _svg_root(self._render(size=size, margin=margin))
        assert root.get('width') == legacy.get('width')
        assert root.get('height') == legacy.get('height')

    def test_default_dimensions(self):
        root = _svg_root(self._render())
        assert root.get('width') == '33mm'


# ── SVG path structure matches geometry ──────────────────────────────────────

def _subpaths(d):
    return [s for s in re.split(r'(?=M)', d) if s.strip()]


class TestPathStructure:
    def test_sharp_rect(self):
        d = _path_d([RRect(1, 2, 1, 1, 0.25, NONE, 1)], 0)
        assert _subpaths(d) == ['M1 2H2V3H1Z']

    def test_offset_applied(self):
        d = _path_d([RRect(1, 2, 1, 1, 0, NONE, 1)], 4)
        assert d.startswith('M5 6')

    def test_circle_has_four_arcs(self):
        d = _path_d([circle(0.5, 0.5, 1)], 0)
        assert d.count('M') == 1
        assert d.count('A') == 4
        assert d.startswith('M0.5 0')

    def test_classy_rounds_only_tl_and_br(self):
        d = _path_d([RRect(0, 0, 1, 1, 0.25, (True, False, True, False), 1)], 0)
        assert d == 'M0.25 0H1V0.75A0.25 0.25 0 0 1 0.75 1H0V0.25A0.25 0.25 0 0 1 0.25 0Z'

    def test_one_subpath_per_primitive(self):
        rects = [RRect(0, 0, 7, 7, 3.5, ALL, 1), RRect(1, 1, 5, 5, 2.5, ALL, 0),
                 RRect(2, 2, 3, 3, 0, NONE, 1)]
        subs = _subpaths(_path_d(rects, 0))
        assert len(subs) == 3
        assert subs[0].startswith('M3.5 0') and subs[0].count('A') == 4
        assert subs[1].startswith('M3.5 1') and subs[1].count('A') == 4
        assert subs[2].startswith('M2 2') and 'A' not in subs[2]

    def test_radius_clamped_to_half_side(self):
        d = _path_d([RRect(0, 0, 1, 1, 5, ALL, 1)], 0)
        assert 'A0.5 0.5' in d


# ── Geometry parity ──────────────────────────────────────────────────────────

class TestGeometryParity:
    def test_both_backends_consume_build_primitives(self, monkeypatch):
        """The PNG and SVG helpers must draw exactly the primitives they are given."""
        drawn = []
        real = qr_shapes._draw_rrect

        def spy(draw, rect, ppm, margin, fill):
            drawn.append(rect)
            return real(draw, rect, ppm, margin, fill)

        monkeypatch.setattr(qr_shapes, '_draw_rrect', spy)
        m = _matrix()
        dots, eyes = build_primitives(m, ShapeStyle('rounded', 'leaf', 'circle'))
        rasterize_png(dots, eyes, len(m), 4, 300, '#000000', '#ffffff')
        assert drawn == dots + eyes

        root = ET.fromstring(to_svg(dots, eyes, len(m), 4, 300).getvalue())
        n_sub = sum(len(_subpaths(p.get('d'))) for p in root.findall(SVG_NS + 'path'))
        assert n_sub == len(dots) + len(eyes)


# ── US1: dot shape geometry (research §5) ────────────────────────────────────

def _grid(cells, n=21):
    m = [[False] * n for _ in range(n)]
    for x, y in cells:
        m[y][x] = True
    return m


def _dots(cells, dot):
    dots, _ = build_primitives(_grid(cells), ShapeStyle(dot))
    return {(math.floor(d.x), math.floor(d.y)): d for d in dots}


ISOLATED = [(10, 10)]
H_PAIR = [(10, 10), (11, 10)]
V_PAIR = [(10, 10), (10, 11)]
# An L-shape, a bar and an isolated module, away from the finders
PATTERN = [(9, 9), (10, 9), (11, 9), (9, 10), (9, 11), (13, 10), (13, 11), (13, 12),
           (11, 12), (15, 15)]


class TestDotGeometry:
    @pytest.mark.parametrize('dot,r', [('rounded', 0.25), ('extra_rounded', 0.5)])
    def test_rounded_isolated_module(self, dot, r):
        d = _dots(ISOLATED, dot)[(10, 10)]
        assert (d.x, d.y, d.w, d.h, d.r, d.corners) == (10, 10, 1, 1, r, ALL)

    @pytest.mark.parametrize('dot', ['rounded', 'extra_rounded'])
    def test_rounded_horizontal_pair_joins(self, dot):
        ds = _dots(H_PAIR, dot)
        assert ds[(10, 10)].corners == (True, False, False, True)
        assert ds[(11, 10)].corners == (False, True, True, False)

    @pytest.mark.parametrize('dot', ['rounded', 'extra_rounded'])
    def test_rounded_vertical_pair_joins(self, dot):
        ds = _dots(V_PAIR, dot)
        assert ds[(10, 10)].corners == (True, True, False, False)
        assert ds[(10, 11)].corners == (False, False, True, True)

    def test_rounded_l_corner(self):
        ds = _dots(PATTERN, 'rounded')
        # (9, 9) has right and down neighbours: only TL is an outer corner
        assert ds[(9, 9)].corners == (True, False, False, False)

    def test_dots_are_separate_circles(self):
        for cells in (ISOLATED, H_PAIR, V_PAIR):
            for (x, y), d in _dots(cells, 'dots').items():
                assert d == circle(x + 0.5, y + 0.5, 0.9)

    @pytest.mark.parametrize('dot,r', [('classy', 0.25), ('classy_rounded', 0.5)])
    def test_classy_isolated(self, dot, r):
        d = _dots(ISOLATED, dot)[(10, 10)]
        assert (d.w, d.h, d.r, d.corners) == (1, 1, r, (True, False, True, False))

    @pytest.mark.parametrize('dot', ['classy', 'classy_rounded'])
    def test_classy_only_tl_and_br(self, dot):
        for d in _dots(PATTERN, dot).values():
            assert not d.corners[1] and not d.corners[3]
        ds = _dots(H_PAIR, dot)
        assert ds[(10, 10)].corners == (True, False, False, False)
        assert ds[(11, 10)].corners == (False, False, True, False)

    def test_horizontal_bars(self):
        d = _dots(ISOLATED, 'horizontal_bars')[(10, 10)]
        assert (d.x, d.y, d.w, d.h, d.r, d.corners) == (10, 10.1, 1, 0.8, 0.4, ALL)
        ds = _dots(H_PAIR, 'horizontal_bars')
        assert ds[(10, 10)].corners == (True, False, False, True)
        assert ds[(11, 10)].corners == (False, True, True, False)
        # Vertical neighbours don't join horizontal bars
        for d in _dots(V_PAIR, 'horizontal_bars').values():
            assert d.corners == ALL

    def test_vertical_bars(self):
        d = _dots(ISOLATED, 'vertical_bars')[(10, 10)]
        assert (d.x, d.y, d.w, d.h, d.r, d.corners) == (10.1, 10, 0.8, 1, 0.4, ALL)
        ds = _dots(V_PAIR, 'vertical_bars')
        assert ds[(10, 10)].corners == (True, True, False, False)
        assert ds[(10, 11)].corners == (False, False, True, True)
        for d in _dots(H_PAIR, 'vertical_bars').values():
            assert d.corners == ALL

    def test_gapped_square(self):
        for (x, y), d in _dots(H_PAIR, 'gapped_square').items():
            assert d == RRect(x + 0.1, y + 0.1, 0.8, 0.8, 0, NONE, 1)

    def test_unknown_dot_is_square(self):
        d = _dots(ISOLATED, 'stars')[(10, 10)]
        assert d == RRect(10, 10, 1, 1, 0, NONE, 1)

    @pytest.mark.parametrize('dot', DOT_SHAPES)
    def test_every_dot_stays_in_its_cell_and_avoids_finders(self, dot):
        m = _matrix()
        n = len(m)
        dots, _ = build_primitives(m, ShapeStyle(dot))
        assert dots
        for d in dots:
            cx, cy = math.floor(d.x), math.floor(d.y)
            assert m[cy][cx] and not is_finder(cx, cy, n)
            assert _inside(d, cx, cy, cx + 1, cy + 1)
            assert d.ink == 1

    @pytest.mark.parametrize('dot', DOT_SHAPES)
    def test_dot_shape_does_not_change_eyes(self, dot):
        m = _matrix()
        assert build_primitives(m, ShapeStyle(dot))[1] == build_primitives(m, ShapeStyle())[1]


class TestDotSwatches:
    @pytest.mark.parametrize('dot', DOT_SHAPES)
    def test_swatch_is_inline_svg(self, dot):
        svg = qr_shapes.swatch_svg('dot', dot)
        root = ET.fromstring(svg)
        assert root.tag == SVG_NS + 'svg'
        assert root.get('fill') == 'currentColor'
        assert root.get('aria-hidden') == 'true'
        assert len(root.findall(SVG_NS + 'path')) >= 1

    def test_swatches_differ(self):
        assert len({qr_shapes.swatch_svg('dot', d) for d in DOT_SHAPES}) == len(DOT_SHAPES)

    def test_unknown_kind_is_empty(self):
        assert qr_shapes.swatch_svg('nope', 'square') == ''


# ── US2: eye geometry (research §5) ──────────────────────────────────────────

TL, TR, BR, BL = 0, 1, 2, 3


def _flags(*on):
    return tuple(i in on for i in range(4))


# border → (outer r, outer corners, opening r, opening corners)
BORDER_TABLE = {
    'square': (0, NONE, 0, NONE),
    'rounded': (2, ALL, 1, ALL),
    'circle': (3.5, ALL, 2.5, ALL),
    'teardrop': (3.5, _flags(TR, BR, BL), 2.5, _flags(TR, BR, BL)),
    'leaf': (3.5, _flags(TR, BL), 2.5, _flags(TL, TR, BL)),
}

# center → (r, corners)
CENTER_TABLE = {
    'square': (0, NONE),
    'rounded': (0.75, ALL),
    'circle': (1.5, ALL),
    'teardrop': (1.5, _flags(TR, BR, BL)),
    'leaf': (1.5, _flags(TR, BL)),
}


def _eyes(style):
    m = _matrix()
    return len(m), build_primitives(m, style)[1]


def _norm(rect):
    """Treat corner flags as irrelevant when r == 0."""
    return rect._replace(corners=NONE) if rect.r == 0 else rect


class TestEyeGeometry:
    def test_tables_cover_whitelists(self):
        assert tuple(BORDER_TABLE) == EYE_BORDERS
        assert tuple(CENTER_TABLE) == EYE_CENTERS

    @pytest.mark.parametrize('border', EYE_BORDERS)
    def test_border_outer_and_opening(self, border):
        n, eyes = _eyes(ShapeStyle(eye_border=border))
        r_out, c_out, r_open, c_open = BORDER_TABLE[border]
        for i, (ox, oy) in enumerate(finder_boxes(n)):
            outer, opening = eyes[3 * i], eyes[3 * i + 1]
            assert _norm(outer) == _norm(RRect(ox, oy, 7, 7, r_out, c_out, 1))
            assert _norm(opening) == _norm(RRect(ox + 1, oy + 1, 5, 5, r_open, c_open, 0))

    def test_circle_opening_is_a_circle(self):
        _, eyes = _eyes(ShapeStyle(eye_border='circle'))
        assert eyes[1] == circle(3.5, 3.5, 5, ink=0)

    @pytest.mark.parametrize('dropped', ['leaf_circle', 'square_circle'])
    def test_dropped_borders_render_as_square(self, dropped):
        assert dropped not in EYE_BORDERS
        assert _eyes(ShapeStyle(eye_border=dropped)) == _eyes(ShapeStyle())

    @pytest.mark.parametrize('center', EYE_CENTERS)
    def test_center(self, center):
        n, eyes = _eyes(ShapeStyle(eye_center=center))
        r, corners = CENTER_TABLE[center]
        for i, (ox, oy) in enumerate(finder_boxes(n)):
            assert _norm(eyes[3 * i + 2]) == _norm(RRect(ox + 2, oy + 2, 3, 3, r, corners, 1))

    @pytest.mark.parametrize('border', EYE_BORDERS)
    @pytest.mark.parametrize('center', EYE_CENTERS)
    def test_all_three_eyes_identical_not_mirrored(self, border, center):
        n, eyes = _eyes(ShapeStyle('square', border, center))
        rel = []
        for i, (ox, oy) in enumerate(finder_boxes(n)):
            rel.append([p._replace(x=p.x - ox, y=p.y - oy) for p in eyes[3 * i:3 * i + 3]])
        assert rel[0] == rel[1] == rel[2]

    def test_border_and_center_are_independent(self):
        m = _matrix()
        base_dots, base = build_primitives(m, ShapeStyle())
        for border in EYE_BORDERS:
            dots, eyes = build_primitives(m, ShapeStyle(eye_border=border))
            assert dots == base_dots
            assert [eyes[i] for i in (2, 5, 8)] == [base[i] for i in (2, 5, 8)]
        for center in EYE_CENTERS:
            dots, eyes = build_primitives(m, ShapeStyle(eye_center=center))
            assert dots == base_dots
            assert [e for i, e in enumerate(eyes) if i % 3 != 2] == \
                   [e for i, e in enumerate(base) if i % 3 != 2]

    @pytest.mark.parametrize('border', EYE_BORDERS)
    @pytest.mark.parametrize('center', EYE_CENTERS)
    def test_eyes_stay_in_their_boxes(self, border, center):
        n, eyes = _eyes(ShapeStyle('square', border, center))
        for i, (ox, oy) in enumerate(finder_boxes(n)):
            outer, opening, ctr = eyes[3 * i:3 * i + 3]
            assert _inside(outer, ox, oy, ox + 7, oy + 7)
            assert _inside(opening, ox + 1, oy + 1, ox + 6, oy + 6)
            assert _inside(ctr, ox + 2, oy + 2, ox + 5, oy + 5)
            assert _inside(outer, 0, 0, n, n)

    def test_unknown_values_are_square(self):
        _, eyes = _eyes(ShapeStyle(eye_border='nope', eye_center='nope'))
        _, square = _eyes(ShapeStyle())
        assert eyes == square


class TestEyeSwatches:
    @pytest.mark.parametrize('kind,values', [('eye_border', EYE_BORDERS),
                                             ('eye_center', EYE_CENTERS)])
    def test_swatches_are_inline_evenodd_svg(self, kind, values):
        svgs = [qr_shapes.swatch_svg(kind, v) for v in values]
        assert len(set(svgs)) == len(values)
        for svg in svgs:
            root = ET.fromstring(svg)
            assert root.tag == SVG_NS + 'svg'
            assert root.get('fill') == 'currentColor'
            paths = root.findall(SVG_NS + 'path')
            assert paths and all(p.get('fill-rule') == 'evenodd' for p in paths)
