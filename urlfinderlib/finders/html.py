import re
import warnings

from bs4 import BeautifulSoup
from bs4.element import Comment
from itertools import chain
from typing import Set, Union
from urllib.parse import unquote, urljoin

import urlfinderlib.helpers as helpers
import urlfinderlib.tokenizer as tokenizer

from .text import TextUrlFinder
from urlfinderlib import is_url
from urlfinderlib.url import URLList

warnings.filterwarnings('ignore', category=UserWarning, module='bs4')


class HtmlUrlFinder:
    def __init__(self, blob: Union[bytes, str], base_url: str = None):
        if isinstance(blob, str):
            blob = blob.encode('utf-8', errors='ignore')

        utf8_string = blob.decode('utf-8', errors='ignore')
        unquoted_utf8_string = unquote(utf8_string, errors='ignore')

        self._base_url = base_url

        self._soups = [BeautifulSoup(utf8_string, features='html.parser')]
        if utf8_string != unquoted_utf8_string:
            self._soups.append(BeautifulSoup(unquoted_utf8_string, features='html.parser'))

    def find_urls(self) -> Set[str]:
        urls = URLList()
        for soup in self._soups:
            urls += HtmlSoupUrlFinder(soup, base_url=self._base_url).find_urls()

        return set(urls)


class HtmlSoupUrlFinder:
    def __init__(self, soup: BeautifulSoup, base_url: str = None):
        self._soup = soup
        self._soup_string = str(soup)
        self._remove_obfuscating_font_tags_from_soup()
        self._given_base_url = base_url
        self._base_url = None

    @property
    def base_url(self):
        if self._base_url is None:
            self._base_url = self._pick_base_url(self._given_base_url)

        return self._base_url

    def find_urls(self) -> Set[str]:
        valid_urls = URLList()

        for document_write_url in self._find_document_write_urls():
            valid_urls.append(document_write_url)

        for visible_url in self._find_visible_urls():
            valid_urls.append(visible_url)

        for meta_refresh_value in self._get_meta_refresh_values():
            valid_urls.append(meta_refresh_value)

        possible_urls = set()
        if self.base_url:
            possible_urls |= {urljoin(self.base_url, u) for u in self._get_base_url_eligible_values()}

        srcset_values = self._get_srcset_values()
        possible_urls = {u for u in possible_urls if not any(srcset_value in u for srcset_value in srcset_values)}
        possible_urls |= {urljoin(self.base_url, u) for u in srcset_values}

        possible_urls |= self._get_tag_attribute_values()

        for possible_url in possible_urls:
            valid_urls.append(helpers.fix_possible_url(possible_url))

        tok = tokenizer.UTF8Tokenizer(str(self._soup))

        # TODO: itertools.product(*zip(string.lower(), string.upper()))
        token_iter = chain(
            tok.get_tokens_between_open_and_close_sequence('"http', '"', strict=True),
            tok.get_tokens_between_open_and_close_sequence('"ftp', '"', strict=True),

            tok.get_tokens_between_open_and_close_sequence("'http", "'", strict=True),
            tok.get_tokens_between_open_and_close_sequence("'ftp", "'", strict=True),

            tok.get_tokens_between_open_and_close_sequence('"HTTP', '"', strict=True),
            tok.get_tokens_between_open_and_close_sequence('"FTP', '"', strict=True),

            tok.get_tokens_between_open_and_close_sequence("'HTTP", "'", strict=True),
            tok.get_tokens_between_open_and_close_sequence("'FTP", "'", strict=True)
        )

        for token in token_iter:
            valid_urls.append(token)

        return set(valid_urls)

    def _find_document_write_urls(self) -> Set[str]:
        urls = URLList()

        document_writes_contents = self._get_document_write_contents()
        for content in document_writes_contents:
            new_parser = HtmlUrlFinder(content, base_url=self.base_url)
            urls += new_parser.find_urls()

        return set(urls)

    def _find_visible_urls(self) -> Set[str]:
        visible_text = self._get_visible_text()
        possible_urls = [line for line in visible_text.splitlines() if '.' in line and '/' in line]

        urls = URLList()
        for possible_url in possible_urls:
            urls += TextUrlFinder(possible_url).find_urls(strict=True)

        return set(urls)

    def _get_action_values(self) -> Set[str]:
        tags = self._soup.find_all(action=True)
        values = {helpers.fix_possible_value(tag['action']) for tag in tags}
        for tag in tags:
            tag['action'] = ''

        return values

    def _get_background_values(self) -> Set[str]:
        tags = self._soup.find_all(background=True)
        values = {helpers.fix_possible_value(tag['background']) for tag in tags}
        for tag in tags:
            tag['background'] = ''

        return values

    def _get_base_url_from_html(self) -> str:
        base_tag = self._soup.find('base', attrs={'href': True})
        base_url = helpers.fix_possible_url(base_tag['href']) if base_tag else None
        return base_url if is_url(base_url) else ''

    def _get_base_url_eligible_values(self) -> Set[str]:
        values = set()
        values |= self._get_action_values()
        values |= self._get_background_values()
        values |= self._get_css_url_values()
        values |= self._get_href_values()
        values |= self._get_src_values()
        values |= self._get_xmlns_values()

        return values

    def _get_css_url_values(self) -> Set[str]:
        return {match for match in
                re.findall(r"url\s*\(\s*[\'\"]?(.*?)[\'\"]?\s*\)", str(self._soup), flags=re.IGNORECASE)}

    def _get_document_writes(self) -> Set[str]:
        return {match for match in re.findall(r"document\.write\s*\(.*?\)\s*;", str(self._soup), flags=re.IGNORECASE)}

    def _get_document_write_contents(self) -> Set[str]:
        document_writes = self._get_document_writes()
        document_writes_contents = set()

        for document_write in document_writes:
            write_begin_index = document_write.rfind('(')
            write_end_index = document_write.find(')')
            write_content = document_write[write_begin_index + 1:write_end_index]
            document_writes_contents.add(helpers.fix_possible_value(write_content))

        return document_writes_contents

    def _get_href_values(self) -> Set[str]:
        tags = self._soup.find_all(href=True)
        values = {helpers.fix_possible_value(tag['href']) for tag in tags}
        for tag in tags:
            tag['href'] = ''

        return values

    def _get_meta_refresh_values(self) -> Set[str]:
        values = set()

        tags = self._soup.find_all('meta',
                                   attrs={'http-equiv': re.compile(r"refresh", flags=re.IGNORECASE),
                                          'content': re.compile(r"url\s*=", flags=re.IGNORECASE)})
        for tag in tags:
            value = tag['content'].partition('=')[2].strip()
            value = helpers.fix_possible_value(value)
            values.add(value)

        return values

    def _get_src_values(self) -> Set[str]:
        tags = self._soup.find_all(src=True)
        values = {helpers.fix_possible_value(tag['src']) for tag in tags}
        for tag in tags:
            tag['src'] = ''

        return values

    def _get_srcset_values(self) -> Set[str]:
        tags = self._soup.find_all(srcset=True)

        values = set()
        srcset_values = {helpers.fix_possible_value(tag['srcset']) for tag in tags}
        for srcset_value in srcset_values:
            splits = srcset_value.split(',')
            values |= {s.strip().split(' ')[0] for s in splits}

        for tag in tags:
            tag['srcset'] = ''

        return values

    def _get_tag_attribute_values(self) -> Set[str]:
        all_values = set()

        """
        for tag in self._soup.find_all():
            for value in tag.attrs.values():
                if isinstance(value, str):
                    all_values.add(helpers.fix_possible_value(value))
                elif isinstance(value, list):
                    all_values |= {helpers.fix_possible_value(v) for v in value}
        """

        for tag in self._soup.find_all():
            for attr in tag.attrs:
                if isinstance(tag[attr], str):
                    all_values.add(helpers.fix_possible_value(tag[attr]))
                elif isinstance(tag[attr], list):
                    all_values |= {helpers.fix_possible_value(v) for v in tag[attr]}

                tag[attr] = ''

        return all_values

    def _get_visible_text(self) -> str:
        def _is_tag_visible(tag):
            if tag.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
                return False
            return not isinstance(tag, Comment)

        text_tags = self._soup.find_all(text=True)
        visible_text_tags = filter(_is_tag_visible, text_tags)
        return ''.join(t for t in visible_text_tags).strip()

    def _get_xmlns_values(self) -> Set[str]:
        tags = self._soup.find_all(xmlns=True)
        values = {helpers.fix_possible_value(tag['xmlns']) for tag in tags}
        for tag in tags:
            tag['xmlns'] = ''

        return values

    def _pick_base_url(self, given_base_url: str) -> str:
        found_base_url = self._get_base_url_from_html()
        return found_base_url if found_base_url else given_base_url

    def _remove_obfuscating_font_tags_from_soup(self) -> None:
        font_tags = self._soup.find_all(
            lambda t: t.name == 'font' and len(t.attrs) == 1 and 'id' in t.attrs and t['id'])

        for tag in font_tags:
            tag.decompose()
