import magic

from typing import Set, Union

import urlfinderlib.finders as finders

from urlfinderlib import URL
from urlfinderlib.url import get_every_url, remove_partial_urls


def find_urls(blob: Union[bytes, str], base_url: str = '', mimetype: str = '') -> Set[str]:
    if isinstance(blob, str):
        blob = blob.encode('utf-8', errors='ignore')

    if not mimetype:
        mimetype = magic.from_buffer(blob)
    mimetype = mimetype.lower()

    urls = set()

    if 'rfc 822' in mimetype or 'mail' in mimetype:
        return set()
    elif 'html' in mimetype:
        urls |= finders.HtmlUrlFinder(blob, base_url=base_url).find_urls()
    elif 'pdf' in mimetype:
        urls |= finders.PdfUrlFinder(blob).find_urls()
    elif 'xml' in mimetype:
        urls |= finders.XmlUrlFinder(blob).find_urls()
    elif 'text' in mimetype:
        if b'xmlns' in blob and b'</' in blob:
            urls |= finders.HtmlUrlFinder(blob, base_url=base_url).find_urls()
        else:
            urls |= finders.TextUrlFinder(blob).find_urls()

    urls = {URL(u) for u in urls}

    return remove_partial_urls(get_every_url(urls))
