from typing import Set, Union

import urlfinderlib.tokenizer as tokenizer

from .text import TextUrlFinder


class DataUrlFinder:
    def __init__(self, blob: Union[bytes, str]):
        if isinstance(blob, str):
            blob = blob.encode('utf-8', errors='ignore')

        self.blob = blob

    def find_urls(self) -> Set[str]:
        tok = tokenizer.UTF8Tokenizer(self.blob)

        ascii_strings = tok.get_ascii_strings(length=8)
        unescaped_ascii_strings = {s.replace('\\', '') for s in ascii_strings}
        possible_url_strings = {s for s in unescaped_ascii_strings if '.' in s}

        urls = set()
        for possible_url_string in possible_url_strings:
            urls |= TextUrlFinder(possible_url_string).find_urls(strict=True)

        return urls
