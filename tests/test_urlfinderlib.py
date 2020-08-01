import os

import urlfinderlib

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
        'http://xn--fa-hia.de/re.php',
        'http://domain2.com/image-small.png',
        'http://domain2.com/image-medium.png',
        'http://domain2.com/image-large.png'
    }

    assert urlfinderlib.find_urls(blob) == expected_urls


def test_find_urls_pdf():
    with open(f'{files_dir}/test.pdfparser', 'rb') as f:
        blob = f.read()

    expected_urls = {
        'http://domain.com/%28test/123',
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
        'http://domain2.com'
    }

    assert urlfinderlib.find_urls(blob) == expected_urls
