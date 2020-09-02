import os

import urlfinderlib
from urlfinderlib.urlfinderlib import _has_u_escaped_lowercase_bytes, _has_u_escaped_uppercase_bytes, _has_x_escaped_lowercase_bytes, _has_x_escaped_uppercase_bytes, _unescape_ascii

this_dir = os.path.dirname(os.path.realpath(__file__))
files_dir = os.path.realpath(f'{this_dir}/files')


def test_find_urls_binary():
    with open(f'{files_dir}/hello.bin', 'rb') as f:
        blob = f.read()

    expected_urls = {'http://domain.com'}

    assert urlfinderlib.find_urls(blob) == expected_urls


def test_find_urls_html():
    with open(f'{files_dir}/test.html', 'rb') as f:
        blob = f.read()

    expected_urls = {
        'http://domain.com',
        'http://domain.com/action',
        'http://domain.com/background',
        'http://domain.com/css',
        'http://domain.com/href',
        'http://domain.com/meta',
        'http://domain.com/src',
        'http://domain.com/xmlns',
        'http://domain3.com',
        'http://faß.de/re.php',
        'http://domain2.com/image-small.png',
        'http://domain2.com/image-medium.png',
        'http://domain2.com/image-large.png',
        'http://domain4.com/index.php#thing=http://domain5.com',
        'http://domain5.com'
    }

    assert urlfinderlib.find_urls(blob) == expected_urls


def test_find_urls_ooxml():
    with open(f'{files_dir}/test.ooxml', 'rb') as f:
        blob = f.read()

    assert urlfinderlib.find_urls(blob) == set()


def test_find_urls_pdf():
    with open(f'{files_dir}/test.pdfparser', 'rb') as f:
        blob = f.read()

    expected_urls = {
        'http://domain.com/(test/123'
    }

    assert urlfinderlib.find_urls(blob) == expected_urls


def test_find_urls_rfc822():
    with open(f'{files_dir}/email.rfc822', 'rb') as f:
        blob = f.read()

    assert urlfinderlib.find_urls(blob) == set()


def test_find_urls_text():
    assert urlfinderlib.find_urls('test') == set()


def test_find_urls_text_xml():
    with open(f'{files_dir}/text.xml', 'rb') as f:
        blob = f.read()

    expected_urls = {
        'http://schemas.microsoft.com/office/drawing/2010/main',
        'http://schemas.openxmlformats.org/drawingml/2006/chart',
        'http://schemas.openxmlformats.org/drawingml/2006/chartDrawing',
        'http://schemas.openxmlformats.org/drawingml/2006/main',
        'http://schemas.openxmlformats.org/markup-compatibility/2006'
    }

    assert urlfinderlib.find_urls(blob) == expected_urls


def test_find_urls_xml():
    with open(f'{files_dir}/sharedStrings.xml', 'rb') as f:
        blob = f.read()

    expected_urls = {
        'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
        'http://domain.com/test',
        'http://domain2.com',
        'http://www.w3.org/XML/1998/namespace'
    }

    assert urlfinderlib.find_urls(blob) == expected_urls


def test_get_url_permutations():
    url = 'http://faß.de/index.php?test<123/😉'

    expected_permutations = {
        'http://faß.de/index.php%3Ftest%3C123/%F0%9F%98%89',
        'http://faß.de/index.php?test&lt;123/😉',
        'http://faß.de/index.php?test<123/😉',
        'http://xn--fa-hia.de/index.php%3Ftest%3C123/%F0%9F%98%89',
        'http://xn--fa-hia.de/index.php?test&lt;123/😉',
        'http://xn--fa-hia.de/index.php?test<123/😉'
    }

    assert urlfinderlib.get_url_permutations(url) == expected_permutations


def test_has_u_escaped_lowercase_bytes():
    assert _has_u_escaped_lowercase_bytes(b'This is a test') is False
    assert _has_u_escaped_lowercase_bytes(b'This is \\u002A a test') is False
    assert _has_u_escaped_lowercase_bytes(b'This is \\u002a a test') is True


def test_has_u_escaped_uppercase_bytes():
    assert _has_u_escaped_uppercase_bytes(b'This is a test') is False
    assert _has_u_escaped_uppercase_bytes(b'This is \\u002A a test') is True
    assert _has_u_escaped_uppercase_bytes(b'This is \\u002a a test') is False


def test_has_x_escaped_lowercase_bytes():
    assert _has_x_escaped_lowercase_bytes(b'This is a test') is False
    assert _has_x_escaped_lowercase_bytes(b'This is \\x2A a test') is False
    assert _has_x_escaped_lowercase_bytes(b'This is \\x2a a test') is True


def test_has_x_escaped_uppercase_bytes():
    assert _has_x_escaped_uppercase_bytes(b'This is a test') is False
    assert _has_x_escaped_uppercase_bytes(b'This is \\x2A a test') is True
    assert _has_x_escaped_uppercase_bytes(b'This is \\x2a a test') is False


def test_unescape_ascii():
    assert _unescape_ascii(b'\\x4d') == b'M'
    assert _unescape_ascii(b'\\x4D') == b'M'
    assert _unescape_ascii(b'\\u004d') == b'M'
    assert _unescape_ascii(b'\\u004D') == b'M'
