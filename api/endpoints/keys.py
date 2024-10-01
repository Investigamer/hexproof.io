"""
* Endpoint: Keys
* This route handles management of all Key objects.
"""
# Standard Library Imports
from contextlib import suppress

# Third Party Imports
from ninja import Router
from django.http import HttpRequest
from hexproof.hexapi import schema as Hexproof

# Local Imports
from api.models import APIKey
from api.utils.response import schema_or_error, StatusCode, get_error_response

# Django Ninja Objects
router = Router()

"""
* Endpoints
"""


@router.get("{name}", **schema_or_error(Hexproof.APIKey))
def get_key(request: HttpRequest, name: str):
    """Retrieve an API key that is currently active.

    Args:
        request (HttpRequest): Django request object.
        name (str): Name of the key to look for.

    Returns:
        APIKeySchema: An APIKey object if an active key was found, otherwise
            an error object with a reason code and readable message.
    """
    with suppress(Exception):

        # Key is valid or disabled
        k = APIKey.objects.get(name=name)
        if k.active:
            return k._api_obj
        return get_error_response(
            status=StatusCode.Disabled,
            details=f"API key '{name}' is disabled!")

    # Key couldn't be located
    return get_error_response(
        status=StatusCode.NotFound,
        details=f"API key '{name}' not found!")
