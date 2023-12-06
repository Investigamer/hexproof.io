"""
* Fetch Utils
"""
# Standard Library Imports
from contextlib import suppress
from typing import Optional

# Third Party Imports
import requests

# Local Imports
from hexproof.constants import REQUEST_HEADER_DEFAULT


def supports_json(url: str, params: Optional[dict] = None) -> tuple[bool, dict]:
    """Check if a URL resource supports JSON request header.

    Args:
        url: URL endpoint of the resource.
        params: Parameters to pass for the request.

    Returns:
        The success or fail state as bool, and a json object if successful (otherwise empty dict).
    """
    try:
        res = requests.get(
            url, headers=REQUEST_HEADER_DEFAULT.copy().update({
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }), params=params)
    except requests.RequestException:
        return False, {}

    # Check apparent status code
    success = True if res.status_code == 200 else False

    # Check JSON
    with suppress(Exception):
        return success, res.json()
    return False, {}
