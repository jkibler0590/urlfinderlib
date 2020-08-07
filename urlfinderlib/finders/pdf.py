from itertools import chain
from typing import Set, Union

import urlfinderlib.tokenizer as tokenizer

from .data import DataUrlFinder
from .text import TextUrlFinder

from urlfinderlib.url import get_valid_urls


class PdfUrlFinder:
    def __init__(self, blob: Union[bytes, str]):
        if isinstance(blob, str):
            blob = blob.encode('utf-8', errors='ignore')

        self.blob = blob

    def find_urls(self) -> Set[str]:
        tok = tokenizer.UTF8Tokenizer(self.blob)

        token_iter = chain(
            tok.get_tokens_between_open_and_close_sequence('/URI', '>>', strict=True),
            tok.get_tokens_between_parentheses(strict=True)
        )

        tokens = {t.replace('\\', '') for t in token_iter if (':' in t or '/' in t) and '.' in t}

        return get_valid_urls(tokens)
