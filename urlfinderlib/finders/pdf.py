from itertools import chain
from typing import Set, Union

import urlfinderlib.tokenizer as tokenizer

from .text import TextUrlFinder
from urlfinderlib.url import URLList


class PdfUrlFinder:
    def __init__(self, blob: Union[bytes, str]):
        if isinstance(blob, str):
            blob = blob.encode('utf-8', errors='ignore')

        self.blob = blob

    def find_urls(self) -> Set[str]:
        tok = tokenizer.UTF8Tokenizer(self.blob)

        # TODO: itertools.product(*zip(string.lower(), string.upper()))
        token_iter = chain(
            tok.get_tokens_between_open_and_close_sequence('/URI', '>>', strict=True),

            tok.get_tokens_between_open_and_close_sequence('(http', ')', strict=True),
            tok.get_tokens_between_open_and_close_sequence('(ftp', ')', strict=True),

            tok.get_tokens_between_open_and_close_sequence('<http', '>', strict=True),
            tok.get_tokens_between_open_and_close_sequence('<ftp', '>', strict=True),

            tok.get_tokens_between_open_and_close_sequence('"http', '"', strict=True),
            tok.get_tokens_between_open_and_close_sequence('"ftp', '"', strict=True),

            tok.get_tokens_between_open_and_close_sequence("'http", "'", strict=True),
            tok.get_tokens_between_open_and_close_sequence("'ftp", "'", strict=True),

            tok.get_tokens_between_open_and_close_sequence('(HTTP', ')', strict=True),
            tok.get_tokens_between_open_and_close_sequence('(FTP', ')', strict=True),

            tok.get_tokens_between_open_and_close_sequence('<HTTP', '>', strict=True),
            tok.get_tokens_between_open_and_close_sequence('<FTP', '>', strict=True),

            tok.get_tokens_between_open_and_close_sequence('"HTTP', '"', strict=True),
            tok.get_tokens_between_open_and_close_sequence('"FTP', '"', strict=True),

            tok.get_tokens_between_open_and_close_sequence("'HTTP", "'", strict=True),
            tok.get_tokens_between_open_and_close_sequence("'FTP", "'", strict=True)
        )

        urls = URLList()
        for token in token_iter:
            token = token.replace('\\', '')
            urls += TextUrlFinder(token).find_urls()

        return set(urls)
