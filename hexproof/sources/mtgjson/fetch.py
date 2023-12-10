"""
* MTGJSON Request Handling
"""
# Standard Library Imports
from typing import Callable
from pathlib import Path

# Third Party Imports
import requests
from ratelimit import sleep_and_retry, RateLimitDecorator
from backoff import on_exception, expo

# Local Imports
from hexproof.constants import REQUEST_HEADER_DEFAULT
from hexproof.sources.mtgjson.enums import MTJ_URL
from hexproof.sources.mtgjson import types as MTJ
from hexproof.apps import HexproofConfig
from hexproof.utils.archive import unpack_tar_gz

# Rate limiter to safely limit MTGJSON requests
mtgjson_rate_limit = RateLimitDecorator(calls=20, period=1)
mtgjson_gql_rate_limit = RateLimitDecorator(calls=20, period=1)
mtgjson_request_header = REQUEST_HEADER_DEFAULT.copy()


"""
* Handlers
"""


def request_handler_mtgjson(func) -> Callable:
    """Wrapper for MTGJSON request functions to handle retries and rate limits.

    Notes:
        There are no known rate limits for requesting JSON file resources.
        We include a 20-per-second rate limit just to be nice.
    """
    @sleep_and_retry
    @mtgjson_rate_limit
    @on_exception(expo, requests.exceptions.RequestException, max_tries=2, max_time=1)
    def decorator(*args, **kwargs):
        return func(*args, **kwargs)
    return decorator


def request_handler_mtgjson_gql(func) -> Callable:
    """Wrapper for MTGJSON GraphQL request functions to handle retries and rate limits.

    Notes:
        MTGJSON GraphQL requests are capped at 500 per-hour per-token at the moment.
        https://mtgjson.com/mtggraphql/#rate-limits
    """
    @sleep_and_retry
    @mtgjson_gql_rate_limit
    @on_exception(expo, requests.exceptions.RequestException, max_tries=2, max_time=1)
    def decorator(*args, **kwargs):
        return func(*args, **kwargs)
    return decorator


"""
* Request Funcs
"""


@request_handler_mtgjson
def get_meta() -> MTJ.Meta:
    """MTG.Meta: Get the current metadata resource for MTGJSON."""
    res = requests.get(
        url=MTJ_URL.API_META,
        headers=mtgjson_request_header)

    # Check for error
    if not res.status_code == 200:
        raise requests.RequestException(response=res)
    return res.json().get('data', {})


@request_handler_mtgjson
def get_set(card_set: str) -> MTJ.Set:
    """Grab available set data from MTG Json.

    Args:
        card_set: The set to look for, ex: MH2

    Returns:
        MTGJson set dict or empty dict.
    """
    res = requests.get(
        url=(MTJ_URL.API / card_set.upper()).with_suffix('.json'),
        headers=mtgjson_request_header)

    # Check for error
    if not res.status_code == 200:
        raise requests.RequestException(response=res)
    return res.json().get('data', {})


@request_handler_mtgjson
def get_set_list() -> list[MTJ.SetList]:
    """Grab the current 'SetList' MTGJSON file."""
    res = requests.get(
        url=MTJ_URL.API_SET_LIST,
        headers=mtgjson_request_header)

    # Check for error
    if not res.status_code == 200:
        raise requests.RequestException(response=res)
    return res.json().get('data', [])


@request_handler_mtgjson
def get_sets_all() -> Path:
    """Download the current JSON file archive from the 'AllSetFiles' MTGJSON endpoint."""
    path = Path(HexproofConfig.DIRS['CACHE'], 'AllSetFiles.tar.gz')
    res = requests.get(
        url=MTJ_URL.API_SET_ALL,
        headers=mtgjson_request_header)
    with open(path, 'wb') as f:
        f.write(res.content)

    # Unpack the contents
    unpack_tar_gz(path)
    return Path(path.parent) / 'AllSetFiles'
