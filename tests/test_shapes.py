"""Unit tests for qr_shapes: whitelists, geometry primitives, and backends."""
import io
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
        assert EYE_BORDERS == ('square', 'rounded', 'circle', 'teardrop', 'leaf',
                               'leaf_circle', 'square_circle')

    def test_eye_centers_in_contract_order(self):
        assert EYE_CENTERS == ('square', 'rounded', 'circle', 'teardrop', 'leaf')

    def test_lengths(self):
        assert (len(DOT_SHAPES), len(EYE_BORDERS), len(EYE_CENTERS)) == (9, 7, 5)

    def test_every_value_has_a_display_name(self):
        for kind, values in (('dot', DOT_SHAPES), ('eye_border', EYE_BORDERS),
                             ('eye_center', EYE_CENTERS)):
            for v in values:
                assert qr_shapes.display_name(kind, v)
        assert qr_shapes.display_name('eye_border', 'leaf_circle') == 'Leaf, round opening'
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
