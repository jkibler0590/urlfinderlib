import magic
import string

from typing import Set, Union

import urlfinderlib.finders as finders

from urlfinderlib import URL
from urlfinderlib.url import get_all_parent_and_child_urls, remove_partial_urls


def get_url_permutations(url: str) -> Set[str]:
    return URL(url).permutations


def find_urls(blob: Union[bytes, str], base_url: str = '', mimetype: str = '') -> Set[str]:
    if isinstance(blob, str):
        blob = blob.encode('utf-8', errors='ignore')

    blob = unescape_ascii(blob)

    if not mimetype:
        mimetype = magic.from_buffer(blob)
    mimetype = mimetype.lower()

    urls = set()

    if 'rfc 822' in mimetype or 'mail' in mimetype:
        return set()
    elif 'html' in mimetype:
        urls |= finders.HtmlUrlFinder(blob, base_url=base_url).find_urls()
    elif 'xml' in mimetype:
        urls |= finders.XmlUrlFinder(blob).find_urls()
    elif b'%PDF-' in blob[:1024]:
        urls |= finders.PdfUrlFinder(blob).find_urls()
    elif 'text' in mimetype:
        if b'xmlns' in blob and b'</' in blob:
            urls |= finders.XmlUrlFinder(blob).find_urls()
        else:
            urls |= finders.TextUrlFinder(blob).find_urls(strict=True)
    else:
        urls |= finders.DataUrlFinder(blob).find_urls()

    urls = {URL(u) for u in urls}

    return remove_partial_urls(get_all_parent_and_child_urls(urls))


def unescape_ascii(blob: bytes) -> bytes:
    ascii_chars = string.ascii_letters + string.digits + string.punctuation

    for char in ascii_chars:
        hex_string_lowercase = f'\\x{format(ord(char), "x")}'.encode('utf-8')
        blob = blob.replace(hex_string_lowercase, hex_string_lowercase.decode('unicode_escape').encode('utf-8'))

        hex_string_uppercase = f'\\x{format(ord(char), "X")}'.encode('utf-8')
        blob = blob.replace(hex_string_uppercase, hex_string_uppercase.decode('unicode_escape').encode('utf-8'))

    return blob
