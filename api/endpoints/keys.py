"""
* Endpoint: Keys
* This route handles management of all Key objects.
"""
# Third Party Imports
from ninja import Router
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from hexproof.providers.hexapi import schema as Hexproof

# Local Imports
from api.models import APIKey
from api.utils.response import schema_or_error, StatusCode, ErrorResponseDisabled, ErrorResponseNotFound

# Django Ninja Objects
router = Router()

"""
* Endpoints
"""


@router.get("{name}", **schema_or_error(
    schema=Hexproof.APIKey, errors=[StatusCode.NotFound, StatusCode.Disabled]))
def get_key(request: HttpRequest, name: str):
    """Retrieve an API key that is currently active.

    Args:
        request (HttpRequest): Django request object.
        name (str): Name of the key to look for.

    Returns:
        APIKeySchema: An APIKey object if an active key was found, otherwise
            an error object with a reason code and readable message.
    """
    # Does the key exist?
    try:
        k = APIKey.objects.get(name=name)
    except ObjectDoesNotExist:
        return StatusCode.NotFound, ErrorResponseNotFound(
            details=f"API key '{name}' not found!")

    # Is the key enabled?
    if k.active:
        return k._api_obj
    return StatusCode.Disabled, ErrorResponseDisabled(
        details=f"API key '{name}' is disabled!")
