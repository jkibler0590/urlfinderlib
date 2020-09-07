import base64
import validators

from urllib.parse import urlsplit


def build_url(scheme: str, netloc: str, path: str) -> str:
    return f'{scheme}://{netloc}{path}'


def fix_possible_url(value: str) -> str:
    value = fix_possible_value(value)
    return value if validators.email(value) else prepend_missing_scheme(value)


def fix_possible_value(value: str) -> str:
    value = value.strip()
    value = fix_slashes(value)
    value = remove_mailto_if_not_email_address(value)
    value = remove_null_characters(value)
    value = remove_surrounding_quotes(value)
    return value


def fix_slashes(value: str) -> str:
    value = value.replace('\\', '/')

    if '://' not in value:
        return value.replace(':/', '://')

    return value


def get_ascii_url(url: str) -> str:
    return url.encode('ascii', errors='ignore').decode()


def is_base64_ascii(value: str) -> bool:
    try:
        base64.b64decode(f'{value}===').decode('ascii')
        return True
    except:
        return False


def prepend_missing_scheme(value: str) -> str:
    value = value.lstrip(':/')

    try:
        split_value = urlsplit(value)
    except ValueError:
        return value

    if not split_value.scheme and '/' in value:
        value = f'http://{value}'

    return value


def remove_surrounding_quotes(value: str) -> str:
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]

    return value


def remove_mailto_if_not_email_address(value: str) -> str:
    try:
        split_value = urlsplit(value)
    except ValueError:
        return value

    if split_value.scheme == 'mailto' and not validators.email(split_value.path):
        return value[7:]

    return value


def remove_null_characters(value: str) -> str:
    return value.replace('\u0000', '')
