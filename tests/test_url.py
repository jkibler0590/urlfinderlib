from urlfinderlib.url import *

valid_urls = [
    'http://localhost:8080/index.php',
    'http://127.0.0.1/index.html',
    'http://localhost.localdomain',
    'http://1.1.1.255',
    'http://1.1.1.0',
    'http://1.1.1.1:8080',
    'https://www.domain.com/',
    'http://domain.com/about us/index.php',
    'http://domain.com/about%20us/index.php',
    'HTTPS://WWW.DOMAIN.COM',
    'https://www.domain.com:8080',
    'ftp://user:pass@domain.com/index.html',
    'http://faß.de',
    'http://√.com',
    'http://domain.com?test=true',
    'http://domain.com/?test=true',
    'http://xn--bcher-kva.com',
    'http://domain.coffee',
    'http://www.😉.com/😉',
    'http://উদাহরণ.বাংলা',
    'http://xn--d5b6ci4b4b3a.xn--54b7fta0cc',
    'http://domain.com/&lt;',
    b'http://domain.com'
]

invalid_urls = [
    'user@domain.com',
    'domain.com',
    'domain.com/index.html'
    'http:/domain.com',
    'http:/\\domain.com',
    'http://domain.com\\index.html',
    'http://domain.invalidtld',
    'http://some_domain.com',
    'http://domain.com&test=true',
    'http://some domain.com',
    'http://domain.com:999999',
    b'domain.com',
    ''
]

valid_url_formats = valid_urls + [
    'http://domain.invalidtld'
]

invalid_url_formats = list(set(invalid_urls) - set(valid_url_formats))


def test_build_url():
    assert build_url('http', 'domain.com', '/index.php?test') == 'http://domain.com/index.php?test'


def test_bytes_create():
    url = URL(b'http://domain.com')
    assert url.value == 'http://domain.com'


def test_child_urls():
    url = URL('https://www.domain.com/redirect?url=http%3A//domain2.com')
    assert url.child_urls == {URL('http://domain2.com')}


def test_equal_bytes():
    assert b'http://domain.com' == URL('http://domain.com')


def test_equal_other():
    assert URL('http://domain.com') != 1


def test_equal_string():
    assert 'http://domain.com' == URL('http://domain.com')


def test_equal_url():
    assert URL('http://domain.com') == URL('http://domain.com')


def test_get_all_parent_and_child_urls():
    urls = {URL('https://www.domain.com/redirect?url=http%3A//domain2.com')}
    expected_urls = {
        'http://domain2.com',
        'https://www.domain.com/redirect?url=http%3A//domain2.com'
    }
    assert get_all_parent_and_child_urls(urls) == expected_urls


def test_get_ascii_url():
    assert get_ascii_url('http://d😉o😉m😉a😉i😉n😉.😉c😉o😉m') == 'http://domain.com'


def test_get_fragment_dict():
    url = URL('http://domain.com/index.php#one=1&two=2&three=3')
    assert url._fragment_dict == {'one': ['1'], 'two': ['2'], 'three': ['3']}


def test_get_netloc_idna():
    assert get_netloc_idna('http://faß.de') == 'xn--fa-hia.de'
    assert get_netloc_idna('http://DOMAIN.COM') == 'domain.com'
    assert get_netloc_idna('http://dom[ain.com') == ''
    assert get_netloc_idna('http://domain\x8a.com') == ''


def test_get_netloc_unicode():
    assert get_netloc_unicode('http://xn--fa-hia.de') == 'faß.de'
    assert get_netloc_unicode('http://dom[ain.com') == ''


def test_get_path_all_decoded():
    assert get_path_all_decoded('http://domain.com/?index%3D1&lt;2') == '/?index=1<2'


def test_get_path_html_decoded():
    assert get_path_html_decoded('http://domain.com/?index%3D1&lt;2') == '/?index%3D1<2'


def test_get_path_html_encoded():
    assert get_path_html_encoded('http://domain.com/?index=1<2') == '/?index=1&lt;2'


def test_get_path_original():
    assert get_path_original('http://domain.com/?index%3D1&lt;2') == '/?index%3D1&lt;2'
    assert get_path_original('http://dom[ain.com/test') == ''


def test_get_path_percent_decoded():
    assert get_path_percent_decoded('http://domain.com/?index%3D1&lt;2') == '/?index=1&lt;2'


def test_get_path_percent_encoded():
    assert get_path_percent_encoded('http://domain.com/?index=1&lt;2') == '/%3Findex%3D1%3C2'


def test_get_query_dict():
    url = URL('http://domain.com/index.php?one=1&two=2&three=3')
    assert url.query_dict == {'one': ['1'], 'two': ['2'], 'three': ['3']}


def test_get_scheme():
    assert get_scheme('https://domain.com') == 'https'
    assert get_scheme('HTTPS://domain.com') == 'https'
    assert get_scheme('http://dom[ain.com') == ''


def test_get_valid_urls():
    assert get_valid_urls({
        'http://domain.com',
        'domain',
        'http://d😉o😉m😉a😉i😉n😉2😉.😉c😉o😉m',
        'email@domain3.com'
    }) == {'http://domain.com', 'http://domain2.com'}


def test_is_base64_ascii():
    assert is_base64_ascii('asdf') is False
    assert is_base64_ascii('faß') is False
    assert is_base64_ascii('YXNkZgo=') is True


def test_is_netloc_ipv4():
    valid_ipv4_netloc = [
        'http://1.1.1.1',
        'http://1.1.1.1:8080',
        'http://user:password@1.1.1.1:8080'
    ]

    invalid_ipv4_netloc = [
        'http://domain.com',
        'http://1.1.1',
        'http://do[main.com'
    ]

    for url in valid_ipv4_netloc:
        assert is_netloc_ipv4(url) is True

    for url in invalid_ipv4_netloc:
        assert is_netloc_ipv4(url) is False


def test_is_netloc_localhost():
    valid_localhost_netloc = [
        'http://localhost',
        'http://localhost:8080/index.html',
        'http://user:password@localhost.localdomain:8080/index.html'
    ]

    invalid_localhost_netloc = [
        'http://domain.com',
        'http://local[host'
    ]

    for url in valid_localhost_netloc:
        assert is_netloc_localhost(url) is True

    for url in invalid_localhost_netloc:
        assert is_netloc_localhost(url) is False


def test_is_netloc_valid_tld():
    valid_tld_netloc = [
        'http://domain.com',
        'http://domain.com:8080',
        'redis://user:password@domain.com'
    ]

    invalid_tld_netloc = [
        'http://1.1.1.1',
        'http://domain.invalidtld'
    ]

    for url in valid_tld_netloc:
        assert is_netloc_valid_tld(url) is True

    for url in invalid_tld_netloc:
        assert is_netloc_valid_tld(url) is False


def test_is_url():
    for url in valid_urls:
        assert is_url(url) is True

    for url in invalid_urls:
        assert is_url(url) is False


def test_is_url_ascii():
    assert is_url('http://d😉o😉m😉a😉i😉n😉.😉c😉o😉m') is False
    assert is_url_ascii('http://d😉o😉m😉a😉i😉n😉.😉c😉o😉m') is True


def test_is_valid_format():
    for url in valid_url_formats:
        assert is_valid_format(url) is True

    for url in invalid_url_formats:
        assert is_valid_format(url) is False


def test_remove_partial_urls():
    urls = {
        'http://domain.com/about us/index.php',
        'http://domain.com/about us',
        'http://domain.com'
    }

    expected_urls = {'http://domain.com/about us/index.php', 'http://domain.com'}

    assert remove_partial_urls(urls) == expected_urls


def test_repr():
    assert(repr(URL('http://domain.com'))) == 'URL: http://domain.com'


def test_string():
    assert str(URL('http://domain.com')) == 'http://domain.com'


def test_url_create():
    assert URL('http://domain.com').value == 'http://domain.com'
    assert URL('http://domain.com/').value == 'http://domain.com'
    assert URL(b'http://domain.com').value == 'http://domain.com'


def test_url_decode_barracuda():
    url = URL('https://linkprotect.cudasvc.com/url?a=http://domain.com')
    assert url.child_urls == {URL('http://domain.com')}


def test_url_decode_base64():
    url = URL('http://domain.com/dXNlckBkb21haW4uY29tCg==#aHR0cDovL2RvbWFpbjIuY29tCg')
    assert url.child_urls == {URL('http://domain2.com')}


def test_url_decode_double_nested():
    url = URL('https://protect2.fireeye.com/url?k=225eb64e-7e024241-225e9cd6-0cc47a33347c-67785364a067dbfc&u=https://mandrillapp.com/track/click/30233568/domain.com?p=eyJzIjoiQnU1NFZhQV9RUTJyTnA0OGxZVllHdFZIdVVzIiwidiI6MSwicCI6IntcInVcIjozMDIzMzU2OCxcInZcIjoxLFwidXJsXCI6XCJodHRwOlxcXC9cXFwvZG9tYWluLmNvbVxcXC90ZXN0XCIsXCJpZFwiOlwiMjIyMjk4YmUyNGU0NDE4MzhlMDFmZjcxN2ZlNzE5YjFcIixcInVybF9pZHNcIjpbXCI5ODdjODQ1Y2ZmZGRmYTU4MjYxN2Y5NDFjZmNmNTE4NmU0MGZlNjY5XCJdfSJ9Cg==')

    assert get_all_parent_and_child_urls(url) == {
        'https://protect2.fireeye.com/url?k=225eb64e-7e024241-225e9cd6-0cc47a33347c-67785364a067dbfc&u=https://mandrillapp.com/track/click/30233568/domain.com?p=eyJzIjoiQnU1NFZhQV9RUTJyTnA0OGxZVllHdFZIdVVzIiwidiI6MSwicCI6IntcInVcIjozMDIzMzU2OCxcInZcIjoxLFwidXJsXCI6XCJodHRwOlxcXC9cXFwvZG9tYWluLmNvbVxcXC90ZXN0XCIsXCJpZFwiOlwiMjIyMjk4YmUyNGU0NDE4MzhlMDFmZjcxN2ZlNzE5YjFcIixcInVybF9pZHNcIjpbXCI5ODdjODQ1Y2ZmZGRmYTU4MjYxN2Y5NDFjZmNmNTE4NmU0MGZlNjY5XCJdfSJ9Cg==',
        'https://mandrillapp.com/track/click/30233568/domain.com?p=eyJzIjoiQnU1NFZhQV9RUTJyTnA0OGxZVllHdFZIdVVzIiwidiI6MSwicCI6IntcInVcIjozMDIzMzU2OCxcInZcIjoxLFwidXJsXCI6XCJodHRwOlxcXC9cXFwvZG9tYWluLmNvbVxcXC90ZXN0XCIsXCJpZFwiOlwiMjIyMjk4YmUyNGU0NDE4MzhlMDFmZjcxN2ZlNzE5YjFcIixcInVybF9pZHNcIjpbXCI5ODdjODQ1Y2ZmZGRmYTU4MjYxN2Y5NDFjZmNmNTE4NmU0MGZlNjY5XCJdfSJ9Cg==',
        'http://domain.com/test'
    }

    assert url.child_urls == {URL('https://mandrillapp.com/track/click/30233568/domain.com?p=eyJzIjoiQnU1NFZhQV9RUTJyTnA0OGxZVllHdFZIdVVzIiwidiI6MSwicCI6IntcInVcIjozMDIzMzU2OCxcInZcIjoxLFwidXJsXCI6XCJodHRwOlxcXC9cXFwvZG9tYWluLmNvbVxcXC90ZXN0XCIsXCJpZFwiOlwiMjIyMjk4YmUyNGU0NDE4MzhlMDFmZjcxN2ZlNzE5YjFcIixcInVybF9pZHNcIjpbXCI5ODdjODQ1Y2ZmZGRmYTU4MjYxN2Y5NDFjZmNmNTE4NmU0MGZlNjY5XCJdfSJ9Cg=='),}
    assert url.child_urls.pop().child_urls == {URL('http://domain.com/test')}


def test_url_decode_google_redirect():
    url = URL('https://www.google.com/url?sa=t&source=web&rct=j&url=http://domain.com')
    assert url.child_urls == {URL('http://domain.com')}


def test_url_decode_mandrillapp():
    url = URL('https://mandrillapp.com/track/click/30233568/domain.com?p=eyJzIjoiQnU1NFZhQV9RUTJyTnA0OGxZVllHdFZIdVVzIiwidiI6MSwicCI6IntcInVcIjozMDIzMzU2OCxcInZcIjoxLFwidXJsXCI6XCJodHRwOlxcXC9cXFwvZG9tYWluLmNvbVxcXC90ZXN0XCIsXCJpZFwiOlwiMjIyMjk4YmUyNGU0NDE4MzhlMDFmZjcxN2ZlNzE5YjFcIixcInVybF9pZHNcIjpbXCI5ODdjODQ1Y2ZmZGRmYTU4MjYxN2Y5NDFjZmNmNTE4NmU0MGZlNjY5XCJdfSJ9Cg==')
    assert url._is_mandrillapp is True
    assert url.child_urls == {URL('http://domain.com/test')}

    json_decode_error_url = 'https://mandrillapp.com/track/click/30233568/domain.com?p=eyJzIjoiQnU1NFZhQV9RUTJyTnA0OGxZVllHdFZIdVVzIiwidiI6MSwicCI6IntcInVcIjozMDIzMzU2OCxcInZcIjoxLFwidXJsXCI6XCJodHRwOlxcXC9cXFwvZG9tYWluLmNvbVxcXC90ZXN0XCIsXCJpZFwiOlwiMjIyMjk4YmUyNGU0NDE4MzhlMDFmZjcxN2ZlNzE5YjFcIixcInVybF9pZHNcIjpbXCI5ODdjODQ1Y2ZmZGRmYTU4MjYxN2Y5NDFjZmNmNTE4NmU0MGZlNjY5XCJdCg=='
    assert decode_mandrillapp(json_decode_error_url) == ''

    unicode_decode_error_url = 'https://mandrillapp.com/track/click/30233568/domain.com?p=eyJzasdf'
    assert decode_mandrillapp(unicode_decode_error_url) == ''


def test_url_decode_outlook_safelink():
    url = URL('https://na01.safelinks.protection.outlook.com/?url=http%3A%2F%2Fdomain.com')
    assert {URL('http://domain.com')} == url.child_urls


def test_url_decode_proofpoint_v2():
    url = URL('https://urldefense.proofpoint.com/v2/url?u=http-3A__domain.com')
    assert url._is_proofpoint_v2 is True
    assert {URL('http://domain.com')} == url.child_urls

    keyerror_url = 'https://urldefense.proofpoint.com/v2/url'
    assert decode_proofpoint_v2(keyerror_url) == ''


def test_url_get_fragment_values():
    url = URL('https://domain.com/index.php#a=1&b=2&c=3')
    assert url.get_fragment_values() == {'1', '2', '3'}


def test_url_get_query_values():
    url = URL('https://domain.com/index.php?a=1&b=2&c=3')
    assert url.get_query_values() == {'1', '2', '3'}


def test_url_netlocs():
    idna_url = URL('http://xn--n28h.com')
    assert idna_url._netlocs['idna'] == 'xn--n28h.com'
    assert idna_url._netlocs['original'] == 'xn--n28h.com'
    assert idna_url._netlocs['unicode'] == '😉.com'

    unicode_url = URL('http://😉.com')
    assert unicode_url._netlocs['idna'] == 'xn--n28h.com'
    assert unicode_url._netlocs['original'] == '😉.com'
    assert unicode_url._netlocs['unicode'] == '😉.com'

    url = URL('http://DOMAIN.COM')
    assert url._netlocs['idna'] == 'domain.com'
    assert url._netlocs['original'] == 'domain.com'
    assert url._netlocs['unicode'] == 'domain.com'


def test_url_paths():
    decoded_url = URL('http://domain.com/test_path?test_query=1<2#😉')
    assert decoded_url._paths['all_decoded'] == '/test_path?test_query=1<2#😉'
    assert decoded_url._paths['html_decoded'] == '/test_path?test_query=1<2#😉'
    assert decoded_url._paths['html_encoded'] == '/test_path?test_query=1&lt;2#😉'
    assert decoded_url._paths['original'] == '/test_path?test_query=1<2#😉'
    assert decoded_url._paths['percent_decoded'] == '/test_path?test_query=1<2#😉'
    assert decoded_url._paths['percent_encoded'] == '/test_path%3Ftest_query%3D1%3C2%23%F0%9F%98%89'

    html_encoded_url = URL('http://domain.com/test_path?test_query=1&lt;2#😉')
    assert html_encoded_url._paths['all_decoded'] == '/test_path?test_query=1<2#😉'
    assert html_encoded_url._paths['html_decoded'] == '/test_path?test_query=1<2#😉'
    assert html_encoded_url._paths['html_encoded'] == '/test_path?test_query=1&lt;2#😉'
    assert html_encoded_url._paths['original'] == '/test_path?test_query=1&lt;2#😉'
    assert html_encoded_url._paths['percent_decoded'] == '/test_path?test_query=1&lt;2#😉'
    assert html_encoded_url._paths['percent_encoded'] == '/test_path%3Ftest_query%3D1%3C2%23%F0%9F%98%89'

    percent_encoded_url = URL('http://domain.com/test_path%3Ftest_query%3D1%3C2%23%F0%9F%98%89')
    assert percent_encoded_url._paths['all_decoded'] == '/test_path?test_query=1<2#😉'
    assert percent_encoded_url._paths['html_decoded'] == '/test_path%3Ftest_query%3D1%3C2%23%F0%9F%98%89'
    assert percent_encoded_url._paths['html_encoded'] == '/test_path?test_query=1&lt;2#😉'
    assert percent_encoded_url._paths['original'] == '/test_path%3Ftest_query%3D1%3C2%23%F0%9F%98%89'
    assert percent_encoded_url._paths['percent_decoded'] == '/test_path?test_query=1<2#😉'
    assert percent_encoded_url._paths['percent_encoded'] == '/test_path%3Ftest_query%3D1%3C2%23%F0%9F%98%89'

    mixed_encoded_url = URL('http://domain.com/test_path%3Ftest_query%3D1&lt;2%23%F0%9F%98%89')
    assert mixed_encoded_url._paths['all_decoded'] == '/test_path?test_query=1<2#😉'
    assert mixed_encoded_url._paths['html_decoded'] == '/test_path%3Ftest_query%3D1<2%23%F0%9F%98%89'
    assert mixed_encoded_url._paths['html_encoded'] == '/test_path?test_query=1&lt;2#😉'
    assert mixed_encoded_url._paths['original'] == '/test_path%3Ftest_query%3D1&lt;2%23%F0%9F%98%89'
    assert mixed_encoded_url._paths['percent_decoded'] == '/test_path?test_query=1&lt;2#😉'
    assert mixed_encoded_url._paths['percent_encoded'] == '/test_path%3Ftest_query%3D1%3C2%23%F0%9F%98%89'


def test_url_permutations():
    url = URL('http://faß.de/test_path?test_query=1<2#😉')
    expected_permutations = {
        'http://faß.de/test_path?test_query=1<2#😉',
        'http://faß.de/test_path?test_query=1&lt;2#😉',
        'http://faß.de/test_path%3Ftest_query%3D1%3C2%23%F0%9F%98%89',
        'http://xn--fa-hia.de/test_path?test_query=1<2#😉',
        'http://xn--fa-hia.de/test_path?test_query=1&lt;2#😉',
        'http://xn--fa-hia.de/test_path%3Ftest_query%3D1%3C2%23%F0%9F%98%89'
    }
    assert url.permutations == expected_permutations


def test_url_split_value():
    assert URL('http://domain.com')._split_value == urlsplit('http://domain.com')
