import re
import warnings

from bs4 import BeautifulSoup
from bs4.element import Comment
from typing import Set, Union
from urllib.parse import unquote, urljoin

import urlfinderlib.helpers as helpers
import urlfinderlib.tokenizer as tokenizer

from .text import TextUrlFinder
from urlfinderlib import is_url
from urlfinderlib.url import get_valid_urls

warnings.filterwarnings('ignore', category=UserWarning, module='bs4')


class HtmlUrlFinder:
    def __init__(self, blob: Union[bytes, str], base_url: str = None):
        if isinstance(blob, str):
            blob = blob.encode('utf-8', errors='ignore')

        utf8_string = blob.decode('utf-8', errors='ignore')
        unquoted_utf8_string = unquote(utf8_string, errors='ignore')

        self._base_url = base_url

        self._soups = [
            BeautifulSoup(utf8_string, features='html.parser'),
            BeautifulSoup(unquoted_utf8_string, features='html.parser')
        ]

    def find_urls(self) -> Set[str]:
        urls = set()
        for soup in self._soups:
            urls |= HtmlSoupUrlFinder(soup, base_url=self._base_url).find_urls()

        return urls


class HtmlSoupUrlFinder:
    def __init__(self, soup: BeautifulSoup, base_url: str = None):
        self._soup = soup
        self._remove_obfuscating_font_tags_from_soup()
        self._base_url = self._pick_base_url(base_url)

    def find_urls(self) -> Set[str]:
        possible_urls = set()
        possible_urls |= self._get_tag_attribute_values()
        possible_urls |= {urljoin(self._base_url, u) for u in self._get_base_url_eligible_values()}
        possible_urls |= self._find_document_write_urls()
        possible_urls |= self._find_visible_urls()

        tok = tokenizer.UTF8Tokenizer(str(self._soup))
        possible_urls |= set(tok.get_tokens_between_double_quotes())
        possible_urls |= set(tok.get_tokens_between_single_quotes())

        srcset_values = self._get_srcset_values()
        possible_urls = {u for u in possible_urls if not any(srcset_value in u for srcset_value in srcset_values)}
        possible_urls |= {urljoin(self._base_url, u) for u in srcset_values}

        return get_valid_urls(possible_urls)

    def _find_document_write_urls(self) -> Set[str]:
        urls = set()

        document_writes_contents = self._get_document_write_contents()
        for content in document_writes_contents:
            new_parser = HtmlUrlFinder(content, base_url=self._base_url)
            urls |= new_parser.find_urls()

        return urls

    def _find_visible_urls(self) -> Set[str]:
        visible_text = self._get_visible_text()
        return TextUrlFinder(visible_text).find_urls(strict=True)

    def _get_action_values(self) -> Set[str]:
        return {helpers.fix_possible_value(tag['action']) for tag in self._soup.find_all(action=True)}

    def _get_background_values(self) -> Set[str]:
        return {helpers.fix_possible_value(tag['background']) for tag in self._soup.find_all(background=True)}

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
        values |= self._get_meta_refresh_values()
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
        return {helpers.fix_possible_value(tag['href']) for tag in self._soup.find_all(href=True)}

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
        return {helpers.fix_possible_value(tag['src']) for tag in self._soup.find_all(src=True)}

    def _get_srcset_values(self) -> Set[str]:
        values = set()

        srcset_values = {helpers.fix_possible_value(tag['srcset']) for tag in self._soup.find_all(srcset=True)}
        for srcset_value in srcset_values:
            splits = srcset_value.split(',')
            values |= {s.strip().split(' ')[0] for s in splits}

        return values

    def _get_tag_attribute_values(self) -> Set[str]:
        all_values = set()

        for tag in self._soup.find_all():
            for value in tag.attrs.values():
                if isinstance(value, str):
                    all_values.add(helpers.fix_possible_value(value))
                elif isinstance(value, list):
                    all_values |= {helpers.fix_possible_value(v) for v in value}

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
        return {helpers.fix_possible_value(tag['xmlns']) for tag in self._soup.find_all(xmlns=True)}

    def _pick_base_url(self, given_base_url: str) -> str:
        found_base_url = self._get_base_url_from_html()
        return found_base_url if found_base_url else given_base_url

    def _remove_obfuscating_font_tags_from_soup(self) -> None:
        font_tags = self._soup.find_all(
            lambda t: t.name == 'font' and len(t.attrs) == 1 and 'id' in t.attrs and t['id'])

        for tag in font_tags:
            tag.decompose()
