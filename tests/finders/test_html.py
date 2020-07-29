from bs4 import BeautifulSoup

import urlfinderlib.finders as finders


html = b'''
<html xmlns="xmlns">
    <head>
        <base href="http://domain.com">
        <meta HTTP-EQUIV="REFRESH" content=0;url="meta">
        <meta HTTP-EQUIV="REFRESH" CONTENT="0; URL=meta2">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
    </head>

    <body background="background">
        <script>
            document.write (unescape('<meta HTTP-EQUIV="REFRESH" CONTENT="0; url=http://domain.com/js.php">') ) ;
        </script>
        <script>
            document.write (unescape('<meta HTTP-EQUIV="REFRESH" CONTENT="0; url=http://domain.com/js2.php">') ) ;
        </script>
        
        <style>
            #obf{
                color: transparent;
                display: none;
                height: 0;
                max-height: 0;
                max-width: 0;
                opacity: 0;
                overflow: hidden;
                mso-hide: all;
                visibility: ;
            }
        </style>
        
        <font id="obf">asdf</font>v<font id="obf">asdf</font>i<font id="obf">asdf</font>s
        
        <form action="action"></form>
        <form action="action2"></form>
        
        <div style="background-image: url('css');">
        <div style="background-image: url('css2');">
        
        <a href="href" class="body strikeout"></a>
        <a href="href2"></a>

        <img src="src">
        <img src="src2">
        
        <div id="id"></div>
        <div id="id2"></div>
    </body>
</html>'''


soup = BeautifulSoup(html, features='html.parser')


def test_create_text():
    assert finders.HtmlUrlFinder('test')


def test_get_action_values():
    finder = finders.HtmlSoupUrlFinder(soup)
    assert finder._get_action_values() == {'action', 'action2'}


def test_get_background_values():
    finder = finders.HtmlSoupUrlFinder(soup)
    assert finder._get_background_values() == {'background'}


def test_get_base_url_from_html():
    finder = finders.HtmlSoupUrlFinder(soup)
    assert finder._get_base_url_from_html() == "http://domain.com"


def test_get_base_url_eligible_values():
    finder = finders.HtmlSoupUrlFinder(soup)
    expected = {
        'http://domain.com',
        'action',
        'action2',
        'background',
        'css',
        'css2',
        'href',
        'href2',
        'meta',
        'meta2',
        'src',
        'src2',
        'xmlns'
    }
    assert finder._get_base_url_eligible_values() == expected


def test_get_css_url_values():
    finder = finders.HtmlSoupUrlFinder(soup)
    assert finder._get_css_url_values() == {'css', 'css2'}


def test_get_document_writes():
    finder = finders.HtmlSoupUrlFinder(soup)
    expected = {
        '''document.write (unescape('<meta HTTP-EQUIV="REFRESH" CONTENT="0; url=http://domain.com/js.php">') ) ;''',
        '''document.write (unescape('<meta HTTP-EQUIV="REFRESH" CONTENT="0; url=http://domain.com/js2.php">') ) ;'''
    }
    assert finder._get_document_writes() == expected


def test_get_document_write_contents():
    finder = finders.HtmlSoupUrlFinder(soup)
    expected = {
        '<meta HTTP-EQUIV="REFRESH" CONTENT="0; url=http://domain.com/js.php">',
        '<meta HTTP-EQUIV="REFRESH" CONTENT="0; url=http://domain.com/js2.php">'
    }
    assert finder._get_document_write_contents() == expected


def test_get_href_values():
    finder = finders.HtmlSoupUrlFinder(soup)
    assert finder._get_href_values() == {'http://domain.com', 'href', 'href2'}


def test_get_meta_refresh_values():
    finder = finders.HtmlSoupUrlFinder(soup)
    expected = {'meta', 'meta2'}
    assert finder._get_meta_refresh_values() == expected


def test_get_src_values():
    finder = finders.HtmlSoupUrlFinder(soup)
    assert finder._get_src_values() == {'src', 'src2'}


def test_get_srcset_values():
    html = """
<img src="http://domain2.com/image-small.png"
    srcset="http://domain2.com/image-small.png 320w,
        http://domain2.com/image-medium.png 800w,
        http://domain2.com/image-large.png 1200w"
    sizes="80vw"
    alt="Image description">
"""

    this_soup = BeautifulSoup(html, features='html.parser')
    finder = finders.HtmlSoupUrlFinder(this_soup)
    assert finder._get_srcset_values() == {
        'http://domain2.com/image-small.png',
        'http://domain2.com/image-medium.png',
        'http://domain2.com/image-large.png'
    }


def test_get_tag_attribute_values():
    finder = finders.HtmlSoupUrlFinder(soup)
    expected = {
        'xmlns',
        'http://domain.com',
        'REFRESH',
        '0;url="meta"',
        '0; URL=meta2',
        'X-UA-Compatible',
        'IE=edge',
        'background',
        'action',
        'action2',
        "background-image: url('css');",
        "background-image: url('css2');",
        'href',
        'body',
        'strikeout',
        'href2',
        'src',
        'src2',
        'id',
        'id2'
    }
    assert finder._get_tag_attribute_values() == expected


def test_get_visible_text():
    finder = finders.HtmlSoupUrlFinder(soup)
    expected = 'vis'
    assert finder._get_visible_text() == expected


def test_get_xmlns_values():
    finder = finders.HtmlSoupUrlFinder(soup)
    assert finder._get_xmlns_values() == {'xmlns'}


def test_pick_base_url():
    finder = finders.HtmlSoupUrlFinder(soup, base_url='http://domain2.com')
    assert finder._base_url == 'http://domain.com'
