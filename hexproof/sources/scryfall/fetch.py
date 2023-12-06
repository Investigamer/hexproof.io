"""
* Scryfall Request Handling
"""
# Third Party Imports
from typing import Callable

# Third Party Imports
import requests
from ratelimit import sleep_and_retry, RateLimitDecorator
from backoff import on_exception, expo

# Local Imports
from hexproof.constants import REQUEST_HEADER_DEFAULT
from hexproof.sources.scryfall.enums import SCRY_URL
from hexproof.sources.scryfall import types as SCRY

# Rate limiter to safely limit MTGJSON requests
scryfall_rate_limit = RateLimitDecorator(calls=20, period=1)
scryfall_request_header = REQUEST_HEADER_DEFAULT.copy()


"""
* Handlers
"""


def request_handler_scryfall(func) -> Callable:
    """Wrapper for a Scryfall request function to handle retries and rate limits.

    Notes:
        Scryfall recommends a 5-10 millisecond delay between requests.
        We target the floor of this recommendation: 20 requests/second.
        Might consider dropping this to 10 requests/second in the future.
        https://scryfall.com/docs/api
    """
    @sleep_and_retry
    @scryfall_rate_limit
    @on_exception(expo, requests.exceptions.RequestException, max_tries=2, max_time=1)
    def decorator(*args, **kwargs):
        return func(*args, **kwargs)
    return decorator


"""
* Request Funcs
"""


@request_handler_scryfall
def get_set(set_code: str) -> SCRY.Set:
    """Grabs a 'Set' object from Scryfall's `/set/{code}` endpoint.

    Args:
        set_code: The set to look for, e.g. MH2

    Returns:
        A Scryfall 'Set' object.
    """
    # Make the request
    res = requests.get(
        url=SCRY_URL.API_SETS / set_code.lower(),
        headers=scryfall_request_header)

    # Check for error
    if not res.status_code == 200:
        raise requests.RequestException(response=res)
    return res.json()


@request_handler_scryfall
def get_set_list() -> list[SCRY.Set]:
    """Grab a list of all Scryfall 'Set' objects from their `/sets/` endpoint.

    Returns:
        A list of every Scryfall 'Set' object.
    """
    res = requests.get(
        url=SCRY_URL.API_SETS,
        headers=scryfall_request_header)

    # Check for error
    if not res.status_code == 200:
        raise requests.RequestException(response=res)
    return res.json().get('data', [])
