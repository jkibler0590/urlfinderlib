from itertools import chain
from typing import Set, Union

import urlfinderlib.helpers as helpers
import urlfinderlib.tokenizer as tokenizer

from urlfinderlib.url import URLList


class TextUrlFinder:
    def __init__(self, blob: Union[bytes, str]):
        if isinstance(blob, str):
            blob = blob.encode('utf-8', errors='ignore')

        self.blob = blob

    def find_urls(self, strict: bool = True) -> Set[str]:
        tok = tokenizer.UTF8Tokenizer(self.blob)

        token_iter = chain(
            tok.get_line_tokens(),
            tok.get_tokens_between_angle_brackets(strict=strict),
            tok.get_tokens_between_backticks(),
            tok.get_tokens_between_brackets(strict=strict),
            tok.get_tokens_between_curly_brackets(strict=strict),
            tok.get_tokens_between_double_quotes(),
            tok.get_tokens_between_parentheses(strict=strict),
            tok.get_tokens_between_single_quotes()
        )

        split_token_iter = tok.get_split_tokens_after_replace(['<', '>', '`', '[', ']', '{', '}', '"', "'", '(', ')'])

        tokens = {t for t in token_iter if '.' in t and '/' in t}
        tokens |= {t for t in split_token_iter if '.' in t and '/' in t}

        valid_urls = URLList()
        for token in tokens:
            valid_urls.append(helpers.fix_possible_url(token))

        return set(valid_urls)
