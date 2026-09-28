"""Integration tests for the Flask routes."""
import base64
import io
import os
import re
from importlib import metadata

import pytest
from PIL import Image
from qrcode.constants import ERROR_CORRECT_M, ERROR_CORRECT_H

from qr_generator import _make_qr_png, _make_qr_svg
from qr_shapes import ShapeStyle

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), 'fixtures', 'legacy')

# (fixture file, /api/qr query string, kind, positional render args)
LEGACY_CASES = [
    ('url_png.png', 'data=https://example.com/abc', 'png',
     ('https://example.com/abc', ERROR_CORRECT_M, 300, 4, '#000000', '#ffffff')),
    ('hello_svg.svg', 'data=hello&format=svg', 'svg',
     ('hello', ERROR_CORRECT_M, 300, 4)),
    ('x_800_m0_fg_H.png', 'data=x&size=800&margin=0&fg_color=%23112233&ec_level=H', 'png',
     ('x', ERROR_CORRECT_H, 800, 0, '#112233', '#ffffff')),
]
LEGACY_IDS = [c[0] for c in LEGACY_CASES]


def _fixture_versions():
    with open(os.path.join(FIXTURE_DIR, 'README.md'), encoding='utf-8') as f:
        text = f.read()
    return {name: re.search(rf'- {name}: (\S+)', text).group(1) for name in ('Pillow', 'qrcode')}


def _require_fixture_versions():
    want = _fixture_versions()
    have = {'Pillow': metadata.version('Pillow'), 'qrcode': metadata.version('qrcode')}
    if want != have:
        pytest.skip(f'legacy fixtures captured with {want}, installed {have}; re-capture them')


def _read_fixture(name):
    with open(os.path.join(FIXTURE_DIR, name), 'rb') as f:
        return f.read()


def _same_image(kind, a, b):
    """PNG: compare decoded pixels (zlib output varies by platform). SVG: exact bytes."""
    if kind == 'svg':
        return a == b
    ia = Image.open(io.BytesIO(a)).convert('RGB')
    ib = Image.open(io.BytesIO(b)).convert('RGB')
    return ia.size == ib.size and ia.tobytes() == ib.tobytes()


def _render(kind, args, **kw):
    fn = _make_qr_svg if kind == 'svg' else _make_qr_png
    return fn(*args, **kw).getvalue()


# ── /generator (UI) ──────────────────────────────────────────────────────────

class TestGeneratorPage:
    def test_returns_200(self, client):
        rv = client.get('/generator')
        assert rv.status_code == 200

    def test_returns_html(self, client):
        rv = client.get('/generator')
        assert b'<!DOCTYPE html>' in rv.data
        assert b'QR Code Generator' in rv.data

    def test_has_google_analytics(self, client):
        rv = client.get('/generator')
        assert b'G-PD7DGWW92P' in rv.data

    def test_has_chrisrmiller_link(self, client):
        rv = client.get('/generator')
        assert b'chrisrmiller.com' in rv.data.lower()


# ── POST /api/generate ───────────────────────────────────────────────────────

class TestGenerateApi:
    def test_qr_text_png_returns_base64(self, client):
        rv = client.post('/api/generate', data={
            'format': 'qrcode', 'content_type': 'text', 'text': 'hello',
            'output_format': 'png', 'size': '300', 'margin': '4',
        })
        assert rv.status_code == 200
        body = rv.get_json()
        assert body['mime'] == 'image/png'
        assert body['image'].startswith('data:image/png;base64,')
        # Decoded payload is a real PNG (starts with PNG magic bytes)
        b64 = body['image'].split(',', 1)[1]
        png_bytes = base64.b64decode(b64)
        assert png_bytes[:8] == b'\x89PNG\r\n\x1a\n'

    def test_qr_text_svg_returns_svg(self, client):
        rv = client.post('/api/generate', data={
            'format': 'qrcode', 'content_type': 'text', 'text': 'hello',
            'output_format': 'svg',
        })
        assert rv.status_code == 200
        body = rv.get_json()
        assert body['mime'] == 'image/svg+xml'
        b64 = body['image'].split(',', 1)[1]
        svg_bytes = base64.b64decode(b64)
        assert b'<svg' in svg_bytes

    def test_qr_url_content_type(self, client):
        rv = client.post('/api/generate', data={
            'format': 'qrcode', 'content_type': 'url', 'url': 'https://example.com',
        })
        assert rv.status_code == 200

    def test_qr_wifi_content_type(self, client):
        rv = client.post('/api/generate', data={
            'format': 'qrcode', 'content_type': 'wifi',
            'wifi_ssid': 'TestNet', 'wifi_password': 'pass1234', 'wifi_auth': 'WPA',
        })
        assert rv.status_code == 200

    def test_empty_data_returns_400(self, client):
        rv = client.post('/api/generate', data={
            'format': 'qrcode', 'content_type': 'text', 'text': '',
        })
        assert rv.status_code == 400
        assert 'error' in rv.get_json()

    def test_unknown_format_returns_400(self, client):
        rv = client.post('/api/generate', data={
            'format': 'made_up_format', 'barcode_data': 'abc',
        })
        assert rv.status_code == 400

    def test_barcode_code128(self, client):
        rv = client.post('/api/generate', data={
            'format': 'code128', 'barcode_data': 'HELLO123',
            'output_format': 'png',
        })
        assert rv.status_code == 200
        body = rv.get_json()
        assert body['mime'] == 'image/png'

    def test_barcode_empty_data_returns_400(self, client):
        rv = client.post('/api/generate', data={
            'format': 'code128', 'barcode_data': '',
        })
        assert rv.status_code == 400

    # ── Security boundary tests ──────────────────────────────────────────────

    def test_malicious_color_falls_back_to_default(self, client):
        # Passing arbitrary string as fg_color should not crash;
        # _safe_color falls back to '#000000'
        rv = client.post('/api/generate', data={
            'format': 'qrcode', 'content_type': 'text', 'text': 'hi',
            'fg_color': 'red; DROP TABLE users;',
        })
        assert rv.status_code == 200

    def test_oversized_size_is_clamped(self, client):
        # Requesting 99999px should clamp to MAX_SIZE (2000), not blow up memory
        rv = client.post('/api/generate', data={
            'format': 'qrcode', 'content_type': 'text', 'text': 'hi',
            'size': '99999',
        })
        assert rv.status_code == 200

    def test_negative_size_is_clamped(self, client):
        rv = client.post('/api/generate', data={
            'format': 'qrcode', 'content_type': 'text', 'text': 'hi',
            'size': '-100',
        })
        assert rv.status_code == 200

    def test_invalid_output_format_falls_back_to_png(self, client):
        rv = client.post('/api/generate', data={
            'format': 'qrcode', 'content_type': 'text', 'text': 'hi',
            'output_format': 'evil_format',
        })
        assert rv.status_code == 200
        assert rv.get_json()['mime'] == 'image/png'

    def test_unknown_content_type_returns_400(self, client):
        rv = client.post('/api/generate', data={
            'format': 'qrcode', 'content_type': 'made_up', 'text': 'hi',
        })
        assert rv.status_code == 400


# ── POST /api/generate/download ──────────────────────────────────────────────

class TestDownloadApi:
    def test_qr_png_download_returns_attachment(self, client):
        rv = client.post('/api/generate/download', data={
            'format': 'qrcode', 'content_type': 'text', 'text': 'hello',
            'output_format': 'png',
        })
        assert rv.status_code == 200
        assert rv.mimetype == 'image/png'
        assert 'attachment' in rv.headers.get('Content-Disposition', '')
        assert rv.data[:8] == b'\x89PNG\r\n\x1a\n'

    def test_qr_svg_download(self, client):
        rv = client.post('/api/generate/download', data={
            'format': 'qrcode', 'content_type': 'text', 'text': 'hello',
            'output_format': 'svg',
        })
        assert rv.status_code == 200
        assert rv.mimetype == 'image/svg+xml'
        assert b'<svg' in rv.data

    def test_barcode_download(self, client):
        rv = client.post('/api/generate/download', data={
            'format': 'code128', 'barcode_data': 'ABC123',
            'output_format': 'png',
        })
        assert rv.status_code == 200
        assert rv.mimetype == 'image/png'

    def test_download_empty_data_returns_400(self, client):
        rv = client.post('/api/generate/download', data={
            'format': 'qrcode', 'content_type': 'text', 'text': '',
        })
        assert rv.status_code == 400


# ── GET /api/qr (img-src shim) ───────────────────────────────────────────────

class TestQrImageGet:
    def test_png_returns_inline_image_bytes(self, client):
        rv = client.get('/api/qr?data=https://example.com&size=256&format=png')
        assert rv.status_code == 200
        assert rv.mimetype == 'image/png'
        # Inline, not attachment — must embed in <img src>
        assert 'attachment' not in rv.headers.get('Content-Disposition', '')
        assert rv.data[:8] == b'\x89PNG\r\n\x1a\n'

    def test_svg_returns_svg_bytes(self, client):
        rv = client.get('/api/qr?data=hello&format=svg')
        assert rv.status_code == 200
        assert rv.mimetype == 'image/svg+xml'
        assert b'<svg' in rv.data

    def test_missing_data_returns_400(self, client):
        rv = client.get('/api/qr')
        assert rv.status_code == 400
        assert 'error' in rv.get_json()

    def test_empty_data_returns_400(self, client):
        rv = client.get('/api/qr?data=')
        assert rv.status_code == 400

    def test_default_size_when_omitted(self, client):
        rv = client.get('/api/qr?data=hi')
        assert rv.status_code == 200
        assert rv.mimetype == 'image/png'

    def test_oversized_size_is_clamped(self, client):
        rv = client.get('/api/qr?data=hi&size=99999')
        assert rv.status_code == 200

    def test_invalid_format_falls_back_to_png(self, client):
        rv = client.get('/api/qr?data=hi&format=evil')
        assert rv.status_code == 200
        assert rv.mimetype == 'image/png'

    def test_cache_control_header_set(self, client):
        # CDN-cacheable — same payload always renders the same QR
        rv = client.get('/api/qr?data=https://example.com')
        cc = rv.headers.get('Cache-Control', '')
        assert 'public' in cc
        assert 'max-age' in cc

    def test_malicious_color_falls_back_to_default(self, client):
        rv = client.get('/api/qr?data=hi&fg_color=red;DROP%20TABLE')
        assert rv.status_code == 200


# ── Root redirect ────────────────────────────────────────────────────────────

class TestRoot:
    def test_root_redirects_to_generator(self, client):
        rv = client.get('/')
        assert rv.status_code in (301, 302)
        assert '/generator' in rv.headers['Location']


# ── Security headers (set via Flask after_request) ───────────────────────────

class TestSecurityHeaders:
    def test_csp_present_on_ui(self, client):
        rv = client.get('/generator')
        csp = rv.headers.get('Content-Security-Policy', '')
        assert "default-src 'self'" in csp
        assert 'frame-ancestors' in csp

    def test_csp_allows_google_analytics(self, client):
        rv = client.get('/generator')
        csp = rv.headers.get('Content-Security-Policy', '')
        assert 'googletagmanager.com' in csp
        assert 'google-analytics.com' in csp

    def test_x_frame_options(self, client):
        rv = client.get('/generator')
        assert rv.headers.get('X-Frame-Options') == 'SAMEORIGIN'

    def test_x_content_type_options(self, client):
        rv = client.get('/generator')
        assert rv.headers.get('X-Content-Type-Options') == 'nosniff'

    def test_referrer_policy(self, client):
        rv = client.get('/generator')
        assert rv.headers.get('Referrer-Policy') == 'strict-origin-when-cross-origin'

    def test_permissions_policy(self, client):
        rv = client.get('/generator')
        pp = rv.headers.get('Permissions-Policy', '')
        assert 'geolocation=()' in pp
        assert 'microphone=()' in pp
        assert 'camera=()' in pp

    def test_headers_present_on_api(self, client):
        rv = client.post('/api/generate', data={
            'format': 'qrcode', 'content_type': 'text', 'text': 'hi',
        })
        assert rv.headers.get('X-Content-Type-Options') == 'nosniff'
        assert 'Content-Security-Policy' in rv.headers


# ── Legacy output is unchanged (SC-002, FR-011) ──────────────────────────────

class TestLegacyIdentity:
    @pytest.mark.parametrize('name,query,kind,args', LEGACY_CASES, ids=LEGACY_IDS)
    def test_explicit_all_square_equals_no_shape(self, name, query, kind, args):
        assert _render(kind, args) == _render(kind, args, shape=ShapeStyle('square', 'square', 'square'))

    @pytest.mark.parametrize('name,query,kind,args', LEGACY_CASES, ids=LEGACY_IDS)
    def test_no_shape_matches_pre_feature_fixture(self, name, query, kind, args):
        _require_fixture_versions()
        assert _same_image(kind, _render(kind, args), _read_fixture(name))


# ── Shape styles: helpers ────────────────────────────────────────────────────

from qr_shapes import DOT_SHAPES, EYE_BORDERS, EYE_CENTERS  # noqa: E402
from qr_generator import MIN_SIZE  # noqa: E402

SHAPE_URL = 'https://example.com/abc'


def _decode_image(data):
    b64 = data['image'].split(',', 1)[1]
    return base64.b64decode(b64)


def _post_qr(client, **extra):
    form = {'format': 'qrcode', 'content_type': 'url', 'url': SHAPE_URL, 'output_format': 'png'}
    form.update(extra)
    return client.post('/api/generate', data=form)


def _decodes_to(png_buf, expected):
    zxingcpp = pytest.importorskip('zxingcpp')
    results = zxingcpp.read_barcodes(Image.open(png_buf))
    return [r.text for r in results] == [expected]


# ── US1: POST routes accept dot_shape ────────────────────────────────────────

class TestDotShapeRoutes:
    @pytest.mark.parametrize('dot', DOT_SHAPES)
    def test_generate_accepts_every_dot_shape(self, client, dot):
        rv = _post_qr(client, dot_shape=dot)
        assert rv.status_code == 200
        body = rv.get_json()
        assert set(body) == {'image', 'mime'}
        assert body['mime'] == 'image/png'
        default = _decode_image(_post_qr(client).get_json())
        styled = _decode_image(body)
        assert styled[:8] == b'\x89PNG\r\n\x1a\n'
        if dot == 'square':
            assert styled == default
        else:
            assert styled != default

    def test_svg_output_is_vector(self, client):
        rv = _post_qr(client, output_format='svg', dot_shape='dots')
        assert rv.status_code == 200
        svg = _decode_image(rv.get_json())
        assert b'<path' in svg
        assert b'<image' not in svg

    def test_download_keeps_filename_and_type(self, client):
        base = {'format': 'qrcode', 'content_type': 'url', 'url': SHAPE_URL}
        for fmt, mime in (('png', 'image/png'), ('svg', 'image/svg+xml')):
            plain = client.post('/api/generate/download', data=dict(base, output_format=fmt))
            styled = client.post('/api/generate/download',
                                 data=dict(base, output_format=fmt, dot_shape='extra_rounded'))
            assert styled.status_code == 200
            assert styled.mimetype == plain.mimetype == mime
            assert styled.headers['Content-Disposition'] == plain.headers['Content-Disposition']
            assert styled.data != plain.data

    def test_wrong_case_is_ignored(self, client):
        a = _decode_image(_post_qr(client, dot_shape='Dots').get_json())
        b = _decode_image(_post_qr(client).get_json())
        assert a == b

    @pytest.mark.parametrize('route', ['/api/generate', '/api/generate/download'])
    def test_barcode_ignores_shape_params(self, client, route):
        base = {'format': 'code128', 'barcode_data': 'HELLO123', 'output_format': 'png'}
        plain = client.post(route, data=base)
        styled = client.post(route, data=dict(base, dot_shape='dots', eye_border='circle',
                                              eye_center='leaf'))
        assert plain.status_code == styled.status_code == 200
        assert plain.data == styled.data


# ── US1: dot shapes decode (FR-014, FR-009) ──────────────────────────────────

class TestDotShapeDecode:
    @pytest.mark.parametrize('dot', DOT_SHAPES)
    def test_decode_dot_shape_default_size(self, dot):
        buf = _make_qr_png(SHAPE_URL, ERROR_CORRECT_M, 300, 4, '#000000', '#ffffff',
                           shape=ShapeStyle(dot))
        assert _decodes_to(buf, SHAPE_URL)

    @pytest.mark.parametrize('dot', DOT_SHAPES)
    def test_decode_dot_shape_min_size(self, dot):
        buf = _make_qr_png('hi there', ERROR_CORRECT_M, MIN_SIZE, 4, '#000000', '#ffffff',
                           shape=ShapeStyle(dot))
        assert _decodes_to(buf, 'hi there')

    @pytest.mark.parametrize('dot', DOT_SHAPES)
    def test_decode_dot_shape_custom_colors(self, dot):
        buf = _make_qr_png(SHAPE_URL, ERROR_CORRECT_M, 330, 4, '#1a237e', '#fffde7',
                           shape=ShapeStyle(dot))
        img = Image.open(buf).convert('RGB')
        # Centre of the top-left eye (always dark) is exactly fg; the corner is bg
        assert img.getpixel((75, 75)) == (0x1a, 0x23, 0x7e)
        assert img.getpixel((0, 0)) == (0xff, 0xfd, 0xe7)
        buf.seek(0)
        assert _decodes_to(buf, SHAPE_URL)


# ── US1: shape options are logged (FR-015) ───────────────────────────────────

@pytest.fixture
def events(monkeypatch):
    import qr_generator
    captured = []
    monkeypatch.setattr(qr_generator, '_log_event', lambda **kw: captured.append(kw))
    return captured


class TestShapeLogging:
    @pytest.mark.parametrize('route', ['/api/generate', '/api/generate/download'])
    def test_success_event_has_normalized_shapes(self, client, events, route):
        secret = 'https://example.com/private-token-123'
        client.post(route, data={'format': 'qrcode', 'content_type': 'url', 'url': secret,
                                 'dot_shape': 'Dots', 'eye_border': 'circle'})
        ev = events[-1]
        assert ev['status'] == 'success'
        assert (ev['dot_shape'], ev['eye_border'], ev['eye_center']) == ('square', 'circle', 'square')
        assert secret not in repr(ev)

    @pytest.mark.parametrize('route', ['/api/generate', '/api/generate/download'])
    def test_barcode_event_has_no_shape_keys(self, client, events, route):
        client.post(route, data={'format': 'code128', 'barcode_data': 'ABC', 'dot_shape': 'dots'})
        ev = events[-1]
        assert ev['status'] == 'success'
        assert not {'dot_shape', 'eye_border', 'eye_center'} & set(ev)


# ── Generator page shape pickers ─────────────────────────────────────────────

def _qr_options_html(client):
    html = client.get('/generator').get_data(as_text=True)
    start = html.index('<div id="qr-options">')
    end = html.index('<!-- ══ 1D Barcode options ══ -->', start)
    return html[start:end]


def _radios(section, name):
    pattern = r'<input type="radio" name="' + name + r'" value="([a-z_]+)"([^>]*)>'
    return re.findall(pattern, section)


def _option_labels(section, name):
    labels = re.findall(r'<label class="shape-opt"[^>]*>(.*?)</label>', section, re.S)
    return [lab for lab in labels if 'name="' + name + '"' in lab]


class TestGeneratorShapeStyle:
    def test_shape_style_section_inside_qr_options(self, client):
        assert 'Shape style' in _qr_options_html(client)

    def test_dot_shape_radios(self, client):
        radios = _radios(_qr_options_html(client), 'dot_shape')
        assert [v for v, _ in radios] == list(DOT_SHAPES)
        assert [v for v, attrs in radios if 'checked' in attrs] == ['square']

    def test_each_dot_option_has_inline_svg(self, client):
        labels = _option_labels(_qr_options_html(client), 'dot_shape')
        assert len(labels) == len(DOT_SHAPES)
        assert all('<svg' in lab for lab in labels)


# ── US2: combinations decode (SC-001, FR-014) ────────────────────────────────

DENSE = ('https://example.com/a/very/long/path?' + '&'.join(
    f'k{i}=value{i}' for i in range(30)))[:300]

# Eye pairs that zxing-based scanners detect with every dot shape (research §6).
# Other pairs render correctly but can fail zxing's diagonal finder check; they
# are verified by phone scan (SC-004) and reported here as non-strict xfails.
DECODER_SAFE_EYES = frozenset(
    [(b, c) for b in ('square', 'rounded') for c in EYE_CENTERS]
    + [('circle', c) for c in ('rounded', 'circle', 'teardrop')])

ALL_COMBOS = [(d, b, c) for d in DOT_SHAPES for b in EYE_BORDERS for c in EYE_CENTERS]
SAFE_COMBOS = [k for k in ALL_COMBOS if k[1:] in DECODER_SAFE_EYES]
_MARGINAL = pytest.mark.xfail(strict=False, reason='eye pair outside the zxing decoder-safe set')


def _combo_params(combos):
    return [pytest.param(*k, id='-'.join(k),
                         marks=() if k[1:] in DECODER_SAFE_EYES else _MARGINAL) for k in combos]


def _padded(buf, pad=30):
    """zxing needs a light quiet zone, so pad margin-0 renders before decoding."""
    img = Image.open(buf).convert('RGB')
    out = Image.new('RGB', (img.width + 2 * pad, img.height + 2 * pad), '#ffffff')
    out.paste(img, (pad, pad))
    b = io.BytesIO()
    out.save(b, format='PNG')
    b.seek(0)
    return b


class TestShapeCombinationDecode:
    def test_combination_counts(self):
        assert len(ALL_COMBOS) == 225
        assert len(SAFE_COMBOS) == 117

    @pytest.mark.parametrize('dot,border,center', _combo_params(ALL_COMBOS))
    def test_decode_combination(self, dot, border, center):
        buf = _make_qr_png(SHAPE_URL, ERROR_CORRECT_M, 300, 4, '#000000', '#ffffff',
                           shape=ShapeStyle(dot, border, center))
        assert _decodes_to(buf, SHAPE_URL)

    @pytest.mark.parametrize('dot,border,center', _combo_params(SAFE_COMBOS))
    def test_decode_dense_payload(self, dot, border, center):
        buf = _make_qr_png(DENSE, ERROR_CORRECT_H, 600, 4, '#000000', '#ffffff',
                           shape=ShapeStyle(dot, border, center))
        assert _decodes_to(buf, DENSE)

    @pytest.mark.parametrize('dot,border,center', _combo_params(SAFE_COMBOS))
    def test_decode_min_size(self, dot, border, center):
        buf = _make_qr_png('hi there', ERROR_CORRECT_M, MIN_SIZE, 4, '#000000', '#ffffff',
                           shape=ShapeStyle(dot, border, center))
        assert _decodes_to(buf, 'hi there')

    @pytest.mark.parametrize('dot,border,center', _combo_params(SAFE_COMBOS))
    def test_decode_margin_zero(self, dot, border, center):
        buf = _make_qr_png(SHAPE_URL, ERROR_CORRECT_M, 300, 0, '#000000', '#ffffff',
                           shape=ShapeStyle(dot, border, center))
        assert _decodes_to(_padded(buf), SHAPE_URL)

    def test_dense_payload_is_dense(self):
        assert len(DENSE) == 300


# ── US2: eye params on routes ────────────────────────────────────────────────

class TestEyeShapeRoutes:
    def test_eye_styles_change_output(self, client):
        rv = _post_qr(client, eye_border='leaf', eye_center='circle')
        assert rv.status_code == 200
        assert _decode_image(rv.get_json()) != _decode_image(_post_qr(client).get_json())

    def test_invalid_eye_border_falls_back_independently(self, client):
        a = _decode_image(_post_qr(client, dot_shape='dots', eye_border='nope').get_json())
        b = _decode_image(_post_qr(client, dot_shape='dots').get_json())
        assert a == b

    @pytest.mark.parametrize('name,values', [('eye_border', EYE_BORDERS),
                                             ('eye_center', EYE_CENTERS)])
    def test_generator_eye_radios(self, client, name, values):
        section = _qr_options_html(client)
        radios = _radios(section, name)
        assert [v for v, _ in radios] == list(values)
        assert [v for v, attrs in radios if 'checked' in attrs] == ['square']
        labels = _option_labels(section, name)
        assert len(labels) == len(values)
        assert all('<svg' in lab for lab in labels)


# ── US3: GET /api/qr shape params (FR-010, FR-013) ───────────────────────────

CACHE = 'public, max-age=86400, immutable'


class TestQrEmbedShapes:
    def test_styled_png_keeps_type_and_cache(self, client):
        plain = client.get('/api/qr?data=https://example.com/abc')
        rv = client.get('/api/qr?data=https://example.com/abc'
                        '&dot_shape=dots&eye_border=circle&eye_center=circle')
        assert rv.status_code == 200
        assert rv.headers['Content-Type'] == 'image/png'
        assert rv.headers['Cache-Control'] == CACHE
        assert 'attachment' not in rv.headers.get('Content-Disposition', '')
        assert rv.data != plain.data

    def test_styled_svg_is_vector(self, client):
        rv = client.get('/api/qr?data=hi&format=svg&dot_shape=extra_rounded&eye_border=leaf')
        assert rv.status_code == 200
        assert rv.mimetype == 'image/svg+xml'
        assert rv.headers['Cache-Control'] == CACHE
        assert b'<path' in rv.data
        assert b'<image' not in rv.data

    @pytest.mark.parametrize('name,query,kind,args', LEGACY_CASES, ids=LEGACY_IDS)
    def test_unstyled_matches_pre_feature_fixture(self, client, name, query, kind, args):
        _require_fixture_versions()
        rv = client.get('/api/qr?' + query)
        assert _same_image(kind, rv.data, _read_fixture(name))

    @pytest.mark.parametrize('name,query,kind,args', LEGACY_CASES, ids=LEGACY_IDS)
    @pytest.mark.parametrize('shape_qs', [
        '&dot_shape=square&eye_border=square&eye_center=square',
        '&dot_shape=Dots&eye_border=nope',
        '&eye_border=leaf_circle&eye_center=square_circle',
    ])
    def test_default_or_invalid_shapes_are_byte_identical(self, client, name, query, kind,
                                                          args, shape_qs):
        plain = client.get('/api/qr?' + query)
        rv = client.get('/api/qr?' + query + shape_qs)
        assert rv.status_code == 200
        assert rv.data == plain.data

    def test_garbage_shape_values_never_error(self, client):
        junk = 'x' * 1000
        for key in ('dot_shape', 'eye_border', 'eye_center'):
            rv = client.get(f'/api/qr?data=hi&{key}={junk}')
            assert rv.status_code == 200
            assert rv.headers['Cache-Control'] == CACHE

    def test_missing_data_still_400(self, client):
        rv = client.get('/api/qr?dot_shape=dots')
        assert rv.status_code == 400
        assert 'Cache-Control' not in rv.headers or 'immutable' not in rv.headers['Cache-Control']


class TestQrEmbedLogging:
    def test_embed_event_has_normalized_shapes(self, client, events):
        client.get('/api/qr?data=https://example.com/secret-token-9'
                   '&dot_shape=classy&eye_border=Circle&eye_center=leaf')
        ev = events[-1]
        assert ev['event'] == 'qr_embed'
        assert ev['status'] == 'success'
        assert (ev['dot_shape'], ev['eye_border'], ev['eye_center']) == ('classy', 'square', 'leaf')
        assert 'secret-token-9' not in repr(ev)
