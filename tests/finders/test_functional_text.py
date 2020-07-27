import urlfinderlib.finders


text = b'''
<http://domain.com/angle_brackets>
`http://domain.com/backticks`
[http://domain.com/brackets]
{http://domain.com/curly_brackets}
"http://domain.com/double_quotes"
(http://domain.com/parentheses)
'http://domain.com/single_quotes'
 http://domain.com/spaces 
http://domain.com/lines
'''


def test_find_urls_in_text():
    finder = urlfinderlib.finders.TextUrlFinder(text)

    expected_urls = {
        'http://domain.com/angle_brackets',
        'http://domain.com/backticks',
        'http://domain.com/brackets',
        'http://domain.com/curly_brackets',
        'http://domain.com/double_quotes',
        'http://domain.com/parentheses',
        'http://domain.com/single_quotes',
        'http://domain.com/spaces',
        'http://domain.com/lines'
    }

    assert finder.find_urls() == expected_urls
