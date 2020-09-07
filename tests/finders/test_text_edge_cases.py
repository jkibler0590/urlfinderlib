import urlfinderlib.finders


def test_backslashes():
    text = b'http:/\\domain.com'
    finder = urlfinderlib.finders.TextUrlFinder(text)
    assert finder.find_urls() == {'http://domain.com'}


def test_double_opening_characters():
    text = b'<http://domain.com/<123>'
    finder = urlfinderlib.finders.TextUrlFinder(text)
    assert finder.find_urls() == {'http://domain.com/<123', 'http://domain.com'}


def test_mailto():
    text = b'<mailto:user@domain.com> <mailto:http://domain.com>'
    finder = urlfinderlib.finders.TextUrlFinder(text)
    assert finder.find_urls() == {'http://domain.com'}


def test_missing_scheme_slash():
    text = b'http:/domain.com'
    finder = urlfinderlib.finders.TextUrlFinder(text)
    assert finder.find_urls() == {'http://domain.com'}


def test_null_characters():
    text = b'http://\x00domain.com'
    finder = urlfinderlib.finders.TextUrlFinder(text)
    assert finder.find_urls() == {'http://domain.com'}


def test_unicode():
    text = '''
http://উদাহরণ.বাংলা/😉
http://√.com
'''.encode('utf-8', errors='ignore')

    expected_urls = {
        'http://উদাহরণ.বাংলা/😉',
        'http://√.com'
    }

    finder = urlfinderlib.finders.TextUrlFinder(text)

    assert finder.find_urls() == expected_urls


def test_url_in_query_value():
    text = u'<html><body><a href="https://www.domain.com/redirect?url=http://√.com"></a></body></html>'
    finder = urlfinderlib.finders.TextUrlFinder(text.encode('utf-8'))
    assert finder.find_urls() == {'https://www.domain.com/redirect?url=http://√.com'}


def test_url_next_to_url():
    text = 'This is a test click here domain.com/test<https://protect2.fireeye.com/url?u=http://domain.com/test> test.'
    finder = urlfinderlib.finders.TextUrlFinder(text)
    assert finder.find_urls() == {'http://domain.com/test', 'https://protect2.fireeye.com/url?u=http://domain.com/test'}
