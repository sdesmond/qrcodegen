import hashlib
import io

import pytest
from PIL import Image
from qrcode.constants import ERROR_CORRECT_M

import qr_generator as qg
from tests.conftest import decode_image, rasterize_svg

# sha256 of the pre-preset Square PNG output, captured at baseline aef1ae0.
GOLDEN = {
    ('https://example.com/hello', 300): '551c6e5f95691e3a0f6a713ca31116949d29b1b6f7e654786a635eccb6958740',
    ('hello world', 512): 'fdff2f78733df732533c88298287d4c2c2a60deb66f9c89a67a6fec95a8cab0a',
}

LENGTHS = [5, 40, 200, 600]


def _text(n):
    return ('Hello-%d-' % n + 'abcdefghij' * 100)[:n]


def _post(client, **kw):
    form = {'format': 'qrcode', 'content_type': 'text', 'size': '400'}
    form.update(kw)
    return client.post('/api/generate/download', data=form, content_type='multipart/form-data')


def _png(resp):
    return Image.open(io.BytesIO(resp.get_data()))


def _logo_file():
    buf = io.BytesIO()
    Image.new('RGBA', (80, 80), (200, 30, 30, 255)).save(buf, 'PNG')
    buf.seek(0)
    return (buf, 'logo.png')


def test_table_has_square_and_circle():
    assert qg.PRESETS['square']['dot'] == 'square'
    assert qg.PRESETS['circle'] == {'name': 'Circle', 'dot': 'circle', 'frame': 'circle', 'ball': 'circle'}


def test_safe_preset():
    assert qg._safe_preset('circle') == 'circle'
    for bad in (None, '', 'diamond', 'CIRCLE', 5):
        assert qg._safe_preset(bad) == 'square'


@pytest.mark.parametrize('key', list(GOLDEN))
def test_square_bytes_match_baseline(key):
    data, size = key
    out = qg._make_qr_png(data, ERROR_CORRECT_M, size, 4, '#000000', '#ffffff')
    assert hashlib.sha256(out.getvalue()).hexdigest() == GOLDEN[key]


def test_default_route_is_baseline_square(client):
    a = _post(client, text='hello world', size='512').get_data()
    b = _post(client, text='hello world', size='512', preset='square').get_data()
    assert a == b
    assert hashlib.sha256(a).hexdigest() == GOLDEN[('hello world', 512)]


def test_unknown_preset_falls_back_to_square(client):
    r = _post(client, text='hello world', size='512', preset='diamond')
    assert r.status_code == 200
    assert hashlib.sha256(r.get_data()).hexdigest() == GOLDEN[('hello world', 512)]


@pytest.mark.parametrize('n', LENGTHS)
@pytest.mark.parametrize('preset', ['square', 'circle'])
def test_png_decodes(client, preset, n):
    r = _post(client, text=_text(n), preset=preset)
    assert r.status_code == 200
    assert decode_image(_png(r)) == [_text(n)]


@pytest.mark.parametrize('n', LENGTHS)
def test_circle_svg_decodes_and_is_vector(client, n):
    r = _post(client, text=_text(n), preset='circle', output_format='svg')
    assert r.status_code == 200
    assert r.mimetype == 'image/svg+xml'
    assert b'<image' not in r.get_data()
    assert decode_image(rasterize_svg(r.get_data())) == [_text(n)]


def test_circle_pixels_are_round():
    out = qg._make_styled_png('hello', ERROR_CORRECT_M, 290, 4, '#000000', '#ffffff', 'circle')
    img = Image.open(out).convert('L')
    unit = 10.0
    # Outer corner of the top-left eye frame is rounded away; ball centre is ink.
    assert img.getpixel((int(4 * unit + 1), int(4 * unit + 1))) > 200
    assert img.getpixel((int(7.5 * unit), int(7.5 * unit))) < 50


def test_circle_with_logo_png(client):
    r = client.post('/api/generate', data={
        'format': 'qrcode', 'content_type': 'text', 'text': 'https://example.com/logo',
        'size': '500', 'preset': 'circle', 'logo': _logo_file()},
        content_type='multipart/form-data')
    assert r.status_code == 200
    import base64
    img = Image.open(io.BytesIO(base64.b64decode(r.get_json()['image'].split(',', 1)[1]))).convert('RGB')
    px = img.getpixel((250, 250))
    assert px[0] > 150 and px[1] < 80          # logo centred
    assert decode_image(img) == ['https://example.com/logo']


def test_circle_with_logo_svg(client):
    r = client.post('/api/generate/download', data={
        'format': 'qrcode', 'content_type': 'text', 'text': 'https://example.com/logo',
        'size': '500', 'preset': 'circle', 'output_format': 'svg', 'logo': _logo_file()},
        content_type='multipart/form-data')
    assert r.status_code == 200
    body = r.get_data()
    assert body.count(b'<image') == 1
    assert decode_image(rasterize_svg(body)) == ['https://example.com/logo']


def test_eye_parts_are_1_to_1():
    modules, n = qg._qr_matrix('hello', ERROR_CORRECT_M)
    parts = [(p, span) for p, _k, _x, _y, span in qg._style_parts(modules, n, qg.PRESETS['circle'])
             if p != 'dot']
    assert parts.count(('frame', 7)) == 3 and parts.count(('ball', 3)) == 3


def test_api_qr_unchanged_square(client):
    r = client.get('/api/qr', query_string={'data': 'hello world', 'size': '512'})
    assert r.status_code == 200
    assert hashlib.sha256(r.get_data()).hexdigest() == GOLDEN[('hello world', 512)]
