import urlfinderlib.helpers as helpers


def test_build_url():
    assert helpers.build_url('http', 'domain.com', '/index.php?test') == 'http://domain.com/index.php?test'


def test_fix_possible_url():
    assert helpers.fix_possible_url('//domain.com\\index\u0000.html') == 'http://domain.com/index.html'


def test_fix_possible_value():
    assert helpers.fix_possible_value('"//domain.com\\index\u0000.html"') == '//domain.com/index.html'


def test_fix_slashes():
    assert helpers.fix_slashes('http:/\\domain.com') == 'http://domain.com'
    assert helpers.fix_slashes('http:/domain.com/index.html') == 'http://domain.com/index.html'


def test_is_base64_ascii():
    assert helpers.is_base64_ascii('asdf') is False
    assert helpers.is_base64_ascii('faß') is False
    assert helpers.is_base64_ascii('YXNkZgo=') is True


def test_prepend_missing_scheme():
    assert helpers.prepend_missing_scheme('domain.com') == 'domain.com'
    assert helpers.prepend_missing_scheme('domain.com/index.html') == 'http://domain.com/index.html'
    assert helpers.prepend_missing_scheme('https://domain.com') == 'https://domain.com'
    assert helpers.prepend_missing_scheme('redis://user:pass@domain.com') == 'redis://user:pass@domain.com'


def test_prepend_missing_scheme_value_error():
    assert helpers.prepend_missing_scheme('http://dom[ain.com') == 'http://dom[ain.com'


def test_remove_mailto_if_not_email_address():
    assert helpers.remove_mailto_if_not_email_address('mailto:http://domain.com') == 'http://domain.com'
    assert helpers.remove_mailto_if_not_email_address('mailto:user@domain.com') == 'mailto:user@domain.com'


def test_remove_mailto_if_not_email_address_value_error():
    assert helpers.remove_mailto_if_not_email_address('http://dom[ain.com') == 'http://dom[ain.com'


def test_remove_null_characters():
    assert helpers.remove_null_characters('http://domain\u0000.com') == 'http://domain.com'


def test_remove_surrounding_quotes():
    assert helpers.remove_surrounding_quotes('"test"') == 'test'
    assert helpers.remove_surrounding_quotes("'test'") == 'test'
