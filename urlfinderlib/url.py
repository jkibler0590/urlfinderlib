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


base64_pattern = re.compile(r'(((aHR0c)|(ZnRw))[a-zA-Z0-9]+)')


def build_url(scheme: str, netloc: str, path: str) -> str:
    return f'{scheme}://{netloc}{path}'


def decode_mandrillapp(url: str) -> str:
    query_dict = URL(url).query_dict
    decoded = base64.b64decode(f"{query_dict['p'][0]}===")

    try:
        outer_json = json.loads(decoded)
        inner_json = json.loads(outer_json['p'])
        possible_url = inner_json['url']
        return possible_url if URL(possible_url).is_url else ''
    except json.JSONDecodeError:
        return ''
    except UnicodeDecodeError:
        return ''


def decode_proofpoint_v2(url: str) -> str:
    query_dict = URL(url).query_dict

    try:
        query_url = query_dict['u'][0]
        possible_url = query_url.replace('-3A', ':').replace('_', '/').replace('-2D', '-')
        return possible_url if URL(possible_url).is_url else ''
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


def get_valid_urls(possible_urls: Set[str]) -> Set[str]:
    valid_urls = set()

    possible_urls = {helpers.fix_possible_url(u) for u in possible_urls if '.' in u}
    for possible_url in possible_urls:
        if URL(possible_url).is_url:
            valid_urls.add(possible_url)
        elif is_url_ascii(possible_url):
            valid_urls.add(get_ascii_url(possible_url))

    return remove_partial_urls(valid_urls)


def is_base64_ascii(value: str) -> bool:
    try:
        base64.b64decode(f'{value}===').decode('ascii')
        return True
    except:
        return False


def is_url_ascii(url: str) -> bool:
    url = url.encode('ascii', errors='ignore').decode()
    return URL(url).is_url


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

        self.value = value.rstrip('/') if value else ''
        self._value_lower = None

        self._is_url = None
        self._is_valid_format = None

        self._parse_value = None
        self._split_value = None
        self._query_dict = None
        self._fragment_dict = None

        self._netloc_idna = None
        self._netloc_original = None
        self._netloc_unicode = None
        self._netlocs = None

        self._is_netloc_ipv4 = None
        self._is_netloc_localhost = None
        self._is_netloc_valid_tld = None

        self._path_all_decoded = None
        self._path_html_decoded = None
        self._path_html_encoded = None
        self._path_original = None
        self._path_percent_decoded = None
        self._path_percent_encoded = None
        self._paths = None

        self._original_url = None

        self._is_mandrillapp = None
        self._is_proofpoint_v2 = None

        self._child_urls = None
        self._permutations = None

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

    @property
    def fragment_dict(self):
        if self._fragment_dict is None:
            self._fragment_dict = parse_qs(self.parse_value.fragment)

        return self._fragment_dict

    @property
    def is_mandrillapp(self):
        if self._is_mandrillapp is None:
            self._is_mandrillapp = 'mandrillapp.com' in self.value_lower and 'p' in self.query_dict

        return self._is_mandrillapp

    @property
    def is_netloc_ipv4(self):
        if self._is_netloc_ipv4 is None:
            if not self.split_value.hostname:
                self._is_netloc_ipv4 = False
            else:
                self._is_netloc_ipv4 = bool(validators.ipv4(self.split_value.hostname))

        return self._is_netloc_ipv4

    @property
    def is_netloc_localhost(self):
        if self._is_netloc_localhost is None:
            if not self.split_value.hostname:
                self._is_netloc_localhost = False
            else:
                self._is_netloc_localhost = self.split_value.hostname.lower() == 'localhost' or self.split_value.hostname.lower() == 'localhost.localdomain'

        return self._is_netloc_localhost

    @property
    def is_netloc_valid_tld(self):
        if self._is_netloc_valid_tld is None:
            try:
                self._is_netloc_valid_tld = bool(tld.get_tld(self.value, fail_silently=True))
            except:
                self._is_netloc_valid_tld = False

        return self._is_netloc_valid_tld

    @property
    def is_proofpoint_v2(self):
        if self._is_proofpoint_v2 is None:
            self._is_proofpoint_v2 = 'urldefense.proofpoint.com/v2' in self.value_lower and 'u' in self.query_dict

        return self._is_proofpoint_v2

    @property
    def is_url(self):
        if self._is_url is None:
            if '.' not in self.value or ':' not in self.value or '/' not in self.value:
                self._is_url = False
            else:
                self._is_url = (self.is_netloc_valid_tld or self.is_netloc_ipv4 or self.is_netloc_localhost) and self.is_valid_format

        return self._is_url

    @property
    def is_valid_format(self):
        if self._is_valid_format is None:
            if not re.match(r'^[a-zA-Z0-9\-\.\:\@]{1,255}$', self.netloc_idna):
                return False

            encoded_url = build_url(self.split_value.scheme, self.netloc_idna, self.path_percent_encoded)
            self._is_valid_format = bool(validators.url(encoded_url))

        return self._is_valid_format

    @property
    def netloc_idna(self):
        if self._netloc_idna is None:
            if all(ord(char) < 128 for char in self.split_value.netloc):
                self._netloc_idna = self.split_value.netloc.lower()
                return self._netloc_idna

            try:
                self._netloc_idna = idna.encode(self.split_value.netloc).decode('utf-8').lower()
                return self._netloc_idna
            except idna.core.IDNAError:
                try:
                    self._netloc_idna = self.split_value.netloc.encode('idna').decode('utf-8', errors='ignore').lower()
                    return self._netloc_idna
                except UnicodeError:
                    self._netloc_idna = ''

            self._netloc_idna = ''

        return self._netloc_idna

    @property
    def netloc_original(self):
        if self._netloc_original is None:
            self._netloc_original = self.split_value.netloc.lower()

        return self._netloc_original

    @property
    def netloc_unicode(self):
        if self._netloc_unicode is None:
            if any(ord(char) >= 128 for char in self.split_value.netloc):
                self._netloc_unicode = self.split_value.netloc.lower()
                return self._netloc_unicode

            try:
                self._netloc_unicode = idna.decode(self.split_value.netloc).lower()
                return self._netloc_unicode
            except idna.core.IDNAError:
                self._netloc_unicode = self.split_value.netloc.encode('utf-8', errors='ignore').decode('idna').lower()
                return self._netloc_unicode

            self._netloc_unicode = ''
            
        return self._netloc_unicode

    @property
    def netlocs(self):
        if self._netlocs is None:
            self._netlocs = {
                'idna': self.netloc_idna,
                'original': self.netloc_original,
                'unicode': self.netloc_unicode
            }

        return self._netlocs

    @property
    def original_url(self):
        if self._original_url is None:
            self._original_url = build_url(self.split_value.scheme, self.netlocs['original'], self.paths['original'])

        return self._original_url

    @property
    def parse_value(self):
        if self._parse_value is None:
            self._parse_value = urlparse(self.value)
        
        return self._parse_value

    @property
    def path_all_decoded(self):
        if self._path_all_decoded is None:
            self._path_all_decoded = html.unescape(unquote(self.path_original))

        return self._path_all_decoded

    @property
    def path_html_decoded(self):
        if self._path_html_decoded is None:
            self._path_html_decoded = html.unescape(self.path_original)

        return self._path_html_decoded

    @property
    def path_html_encoded(self):
        if self._path_html_encoded is None:
            self._path_html_encoded = html.escape(self.path_all_decoded)

        return self._path_html_encoded

    @property
    def path_original(self):
        if self._path_original is None:
            path = self.split_value.path
            query = self.split_value.query
            fragment = self.split_value.fragment

            if (path or query or fragment) and not path.startswith('/'):
                path = f'/{path}'

            if query:
                path = f'{path}?{query}'

            if fragment:
                path = f'{path}#{fragment}'

            self._path_original = path
            
        return self._path_original

    @property
    def path_percent_decoded(self):
        if self._path_percent_decoded is None:
            self._path_percent_decoded = unquote(self.path_original)

        return self._path_percent_decoded

    @property
    def path_percent_encoded(self):
        if self._path_percent_encoded is None:
            """
            Line breaks are included in safe_chars because they should not exist in a valid URL.
            The tokenizer will sometimes create tokens that would be considered valid URLs if
            these characters get %-encoded.
            """
            safe_chars = '/\n\r'
            self._path_percent_encoded = quote(self.path_all_decoded, safe=safe_chars)

        return self._path_percent_encoded

    @property
    def paths(self):
        if self._paths is None:
            self._paths = {
                'all_decoded': self.path_all_decoded,
                'original': self.path_original,
                'html_decoded': self.path_html_decoded,
                'html_encoded': self.path_html_encoded,
                'percent_decoded': self.path_percent_decoded,
                'percent_encoded': self.path_percent_encoded
            }
        
        return self._paths

    @property
    def query_dict(self):
        if self._query_dict is None:
            self._query_dict = parse_qs(self.parse_value.query)

        return self._query_dict

    @property
    def split_value(self):
        if self._split_value is None:
            try:
                self._split_value = urlsplit(self.value)
            except ValueError:
                self._split_value = urlsplit('')

        return self._split_value

    @property
    def child_urls(self) -> Set['URL']:
        if self._child_urls is None:
            self._child_urls = self.get_child_urls()

        return self._child_urls

    @property
    def permutations(self) -> Set[str]:
        if self._permutations is None:
            self._permutations = self.get_permutations()

        return self._permutations

    @property
    def value_lower(self):
        if self._value_lower is None:
            self._value_lower = self.value.lower()

        return self._value_lower

    def get_base64_urls(self) -> Set[str]:
        fixed_base64_values = {helpers.fix_possible_value(v) for v in self.get_base64_values()}
        return {u for u in fixed_base64_values if URL(u).is_url}

    def get_base64_values(self) -> Set[str]:
        values = set()

        for match in base64_pattern.findall(self.paths['original']):
            if is_base64_ascii(match[0]):
                values.add(base64.b64decode(f'{match[0]}===').decode('ascii'))

        return values

    def get_child_urls(self) -> Set['URL']:
        child_urls = self.get_query_urls()
        child_urls |= self.get_fragment_urls()
        child_urls |= self.get_base64_urls()

        if self.is_mandrillapp:
            decoded_url = decode_mandrillapp(self.value)
            if decoded_url:
                child_urls.add(decoded_url)

        if self.is_proofpoint_v2:
            child_urls.add(decode_proofpoint_v2(self.value))

        return {URL(u) for u in child_urls}

    def get_fragment_urls(self) -> Set[str]:
        return {v for v in self.get_fragment_values() if URL(v).is_url}

    def get_fragment_values(self) -> Set[str]:
        values = set()

        for url in self.permutations:
            values |= {item for sublist in URL(url).fragment_dict.values() for item in sublist}

        return values

    def get_permutations(self) -> Set[str]:
        return {
            build_url(self.split_value.scheme, netloc, path) for netloc in
            self.netlocs.values() for path in
            self.paths.values()
        }

    def get_query_urls(self) -> Set[str]:
        return {v for v in self.get_query_values() if URL(v).is_url}

    def get_query_values(self) -> Set[str]:
        values = set()

        for url in self.permutations:
            values |= {item for sublist in URL(url).query_dict.values() for item in sublist}

        return values
