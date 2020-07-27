from typing import Set, Union

import urlfinderlib.finders as finders
import urlfinderlib.tokenizer as tokenizer


class PdfUrlFinder:
    def __init__(self, blob: Union[bytes, str]):
        if isinstance(blob, str):
            blob = blob.encode('utf-8', errors='ignore')

        self.blob = blob

    def find_urls(self) -> Set[str]:
        tok = tokenizer.UTF8Tokenizer(self.blob)

        matches = set()

        matches |= set(tok.get_tokens_between_open_and_close_sequence('/URI', '>>', strict=True))
        matches |= set(tok.get_tokens_between_open_and_close_sequence('(', ')', strict=True))

        matches = {m.replace('\\', '') for m in matches}

        blob = '\n'.join(matches).encode('utf-8', errors='ignore')

        return finders.TextUrlFinder(blob).find_urls()
