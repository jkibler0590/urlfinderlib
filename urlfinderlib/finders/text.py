from typing import Set, Union

import urlfinderlib.tokenizer as tokenizer

from urlfinderlib.url import get_valid_urls


class TextUrlFinder:
    def __init__(self, blob: Union[bytes, str]):
        if isinstance(blob, str):
            blob = blob.encode('utf-8', errors='ignore')

        self.blob = blob

    def find_urls(self, strict: bool = True) -> Set[str]:
        tok = tokenizer.UTF8Tokenizer(self.blob)

        tokens = {t for t in tok.get_all_tokens(strict=strict) if '.' in t}

        return get_valid_urls(tokens)
