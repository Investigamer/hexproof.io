"""
* GitHub Request Handling
"""
from pathlib import Path
# Third Party Imports
from typing import Callable, Union

# Third Party Imports
import yarl
import requests
from ratelimit import sleep_and_retry, RateLimitDecorator
from backoff import on_exception, expo

from hexproof.constants import REQUEST_HEADER_DEFAULT

# Rate limiter to safely limit MTGJSON requests
github_rate_limit = RateLimitDecorator(calls=60, period=3600)
github_request_header = REQUEST_HEADER_DEFAULT.copy()


"""
* Handlers
"""


def request_handler_github(func) -> Callable:
    """Wrapper for a GitHub request function to handle retries and rate limits.

    Notes:
        Unauthenticated requests limited to 60 per hour.
        https://docs.github.com/en/rest/overview/rate-limits-for-the-rest-api

    Todo:
        Add optional authentication support?
    """
    @sleep_and_retry
    @github_rate_limit
    @on_exception(expo, requests.exceptions.RequestException, max_tries=2, max_time=1)
    def decorator(*args, **kwargs):
        return func(*args, **kwargs)
    return decorator


"""
* Request Funcs
"""


@request_handler_github
def get_manifest_data(url: Union[str, yarl.URL]) -> dict:
    """Request a manifest file and return its JSON loaded data.

    Args:
        url: URL to the data file resource hosted on GitHub.

    Raises:
        RequestException if resource could not be returned.
    """
    with requests.get(url, headers=github_request_header) as res:
        if res.status_code != 200:
            raise requests.RequestException(response=res)
        return res.json()


@request_handler_github
def get_archive_zip(url: Union[str, yarl.URL], path: Path) -> Path:
    """Request a zip archive file and save it to a given path location.

    Args:
        url: URL to the archive hosted on GitHub.
        path: Path to save the archive to.

    Raises:
        RequestException: If resource could not be returned.
    """
    # Download the zip package
    with requests.get(url, headers=REQUEST_HEADER_DEFAULT) as res:
        if res.status_code != 200:
            raise requests.RequestException(response=res)
        with open(path, 'wb') as f:
            f.write(res.content)
    return path
