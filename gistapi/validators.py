import re
from typing import Optional, Dict

from gistapi.exceptions import BadRequest


def is_valid_username(username: Optional[str]) -> bool:
    if not username or not isinstance(username, str) or username.strip() == '':
        return False
    return True


def is_valid_pattern(pattern: Optional[str]) -> bool:
    if not pattern or not isinstance(pattern, str):
        return False
    try:
        re.compile(pattern)
        return True
    except re.error:
        return False


def clean_post_data(post_data: Optional[Dict]) -> (str, str):
    if not post_data or 'username' not in post_data or 'pattern' not in post_data:
        raise BadRequest(f'username and pattern are required')

    username = post_data.get('username')
    pattern = post_data.get('pattern')

    if not is_valid_username(username):
        raise BadRequest(f'Invalid value of user expected non empty string')

    if not is_valid_pattern(pattern):
        raise BadRequest(f'Invalid pattern of pattern value: {pattern}')

    return username, pattern
