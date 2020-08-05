import base64
import binascii
import html
import idna
import json
import re
import tld
import validators

from typing import Set, Union
from urllib.parse import parse_qs, quote, unquote, urlparse, urlsplit

import urlfinderlib.helpers as helpers


def build_url(scheme: str, netloc: str, path: str) -> str:
    return f'{scheme}://{netloc}{path}'


def decode_mandrillapp(url: str) -> str:
    query_dict = get_query_dict(url)
    decoded = base64.b64decode(f"{query_dict['p'][0]}===")

    try:
        outer_json = json.loads(decoded)
        inner_json = json.loads(outer_json['p'])
        possible_url = inner_json['url']
        return possible_url if is_url(possible_url) else ''
    except json.JSONDecodeError:
        return ''
    except UnicodeDecodeError:
        return ''


def decode_proofpoint_v2(url: str) -> str:
    query_dict = get_query_dict(url)

    try:
        query_url = query_dict['u'][0]
        possible_url = query_url.replace('-3A', ':').replace('_', '/').replace('-2D', '-')
        return possible_url if is_url(possible_url) else ''
    except KeyError:
        return ''


def get_all_parent_and_child_urls(urls: Union[Set['URL'], 'URL'], ret=None) -> Set[str]:
    if ret is None:
        ret = set()

    if isinstance(urls, URL):
        urls = {urls}

    for url in urls:
        ret.add(url.original_url)
        ret |= get_all_parent_and_child_urls(url.child_urls)

    return ret


def get_ascii_url(url: str) -> str:
    return url.encode('ascii', errors='ignore').decode()


def get_netloc_idna(url: str) -> str:
    try:
        split_url = urlsplit(url)
    except ValueError:
        return ''

    if all(ord(char) < 128 for char in split_url.netloc):
        return split_url.netloc.lower()

    try:
        return idna.encode(split_url.netloc).decode('utf-8').lower()
    except idna.core.IDNAError:
        try:
            return split_url.netloc.encode('idna').decode('utf-8', errors='ignore').lower()
        except UnicodeError:
            return ''


def get_netloc_unicode(url: str) -> str:
    try:
        split_url = urlsplit(url)
    except ValueError:
        return ''

    if any(ord(char) >= 128 for char in split_url.netloc):
        return split_url.netloc.lower()

    try:
        return idna.decode(split_url.netloc).lower()
    except idna.core.InvalidCodepoint:
        return split_url.netloc.encode('utf-8', errors='ignore').decode('idna').lower()


def get_path_all_decoded(url: str) -> str:
    return html.unescape(unquote(get_path_original(url)))


def get_path_html_decoded(url: str) -> str:
    return html.unescape(get_path_original(url))


def get_path_html_encoded(url: str) -> str:
    return html.escape(get_path_all_decoded(url))


def get_path_original(url: str) -> str:
    try:
        split_url = urlsplit(url)
    except ValueError:
        return ''

    path = split_url.path
    query = split_url.query
    fragment = split_url.fragment

    if (path or query or fragment) and not path.startswith('/'):
        path = f'/{path}'

    if query:
        path = f'{path}?{query}'

    if fragment:
        path = f'{path}#{fragment}'

    return path


def get_path_percent_decoded(url: str) -> str:
    return unquote(get_path_original(url))


def get_path_percent_encoded(url: str) -> str:
    """
    Line breaks are included in safe_chars because they should not exist in a valid URL.
    The tokenizer will frequently create tokens that would be considered valid URLs if
    these characters get %-encoded.
    """
    safe_chars = '/\n\r'

    return quote(get_path_all_decoded(url), safe=safe_chars)


def get_query_dict(url) -> dict:
    return parse_qs(urlparse(url).query)


def get_scheme(url: str) -> str:
    try:
        return urlsplit(url).scheme
    except ValueError:
        return ''


def get_valid_urls(possible_urls: Set[str]) -> Set[str]:
    valid_urls = set()

    possible_urls = {helpers.fix_possible_url(u) for u in possible_urls if '.' in u}
    for possible_url in possible_urls:
        if is_url(possible_url):
            valid_urls.add(possible_url)
        elif is_url_ascii(possible_url):
            valid_urls.add(get_ascii_url(possible_url))

    return remove_partial_urls(valid_urls)


def is_netloc_ipv4(url: str) -> bool:
    try:
        split_url = urlsplit(url)
    except ValueError:
        return False

    return bool(validators.ipv4(split_url.netloc.split(':')[0]))


def is_netloc_valid_tld(url: str) -> bool:
    return bool(tld.get_tld(url, fail_silently=True))


def is_url(url: str) -> bool:
    if not url:
        return False
    elif isinstance(url, bytes):
        url = url.decode('utf-8', errors='ignore')

    return is_valid_format(url) and (is_netloc_valid_tld(url) or is_netloc_ipv4(url))


def is_url_ascii(url: str) -> bool:
    url = url.encode('ascii', errors='ignore').decode()
    return is_url(url)


def is_valid_format(url: str) -> bool:
    if not url:
        return False
    elif isinstance(url, bytes):
        url = url.decode('utf-8', errors='ignore')

    encoded_url = build_url(get_scheme(url), get_netloc_idna(url), get_path_percent_encoded(url))
    return bool(validators.url(encoded_url))


def remove_partial_urls(urls: Set[str]) -> Set[str]:
    return {
        url for url in urls if
        not any(u.startswith(url) and u != url for u in urls) or
        not urlsplit(url).path
    }


class URL:
    def __init__(self, value: Union[bytes, str]):
        if isinstance(value, bytes):
            value = value.decode('utf-8', errors='ignore')

        self.value = value.rstrip('/')
        self._value_lower = self.value.lower()
        self._split_value = urlsplit(self.value)
        self._query_dict = get_query_dict(self.value)

        self._netlocs = {
            'idna': get_netloc_idna(self.value),
            'original': self._split_value.netloc.lower(),
            'unicode': get_netloc_unicode(self.value)
        }

        self._paths = {
            'all_decoded': get_path_all_decoded(self.value),
            'original': get_path_original(self.value),
            'html_decoded': get_path_html_decoded(self.value),
            'html_encoded': get_path_html_encoded(self.value),
            'percent_decoded': get_path_percent_decoded(self.value),
            'percent_encoded': get_path_percent_encoded(self.value)
        }

        self.original_url = build_url(self._split_value.scheme, self._netlocs['original'], self._paths['original'])

        self._is_mandrillapp = 'mandrillapp.com' in self._value_lower and 'p' in self._query_dict
        self._is_proofpoint_v2 = 'urldefense.proofpoint.com/v2' in self._value_lower and 'u' in self._query_dict

        self.permutations = self.get_permutations()
        self.child_urls = self.get_child_urls()

    def __eq__(self, other):
        if isinstance(other, str):
            return other in self.permutations

        elif isinstance(other, URL):
            return self.value in other.permutations

        elif isinstance(other, bytes):
            return other.decode('utf-8', errors='ignore') in self.permutations

        return False

    def __hash__(self):
        return hash(self.value)

    def __repr__(self):
        return f'URL: {self.value}'

    def __str__(self):
        return self.value

    def get_base64_urls(self) -> Set[str]:
        fixed_base64_values = {helpers.fix_possible_value(v) for v in self.get_base64_values()}
        return {u for u in fixed_base64_values if is_url(u)}

    def get_base64_values(self) -> Set[str]:
        base64_pattern = re.compile(r'[A-Za-z0-9]+')
        values = set()

        for path in self._paths.values():
            for match in base64_pattern.findall(path):
                try:
                    values.add(base64.b64decode(f'{match}===').decode('utf-8', errors='ignore'))
                except binascii.Error:
                    pass

        return values

    def get_child_urls(self) -> Set['URL']:
        child_urls = self.get_query_urls()
        child_urls |= self.get_base64_urls()

        if self._is_mandrillapp:
            decoded_url = decode_mandrillapp(self.value)
            if decoded_url:
                child_urls.add(decoded_url)

        if self._is_proofpoint_v2:
            child_urls.add(decode_proofpoint_v2(self.value))

        return {URL(u) for u in child_urls}

    def get_permutations(self) -> Set[str]:
        return {
            build_url(self._split_value.scheme, netloc, path) for netloc in
            self._netlocs.values() for path in
            self._paths.values()
        }

    def get_query_urls(self) -> Set[str]:
        return {v for v in self.get_query_values() if is_url(v)}

    def get_query_values(self) -> Set[str]:
        values = set()

        for url in self.get_permutations():
            query_dict = get_query_dict(url)
            values |= {item for sublist in query_dict.values() for item in sublist}

        return values
