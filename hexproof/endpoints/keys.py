"""
* Endpoint: Keys
* This route handles management of all Key objects.
"""
# Standard Library Imports
from contextlib import suppress

# Third Party Imports
from ninja import Router
from django.http import HttpRequest

# Local Imports
from hexproof.models import APIKey
from hexproof.schemas import APIKeySchema, schema_or_error, ErrorStatus, get_error_response

# Django Ninja Objects
api = Router()

"""
* Endpoints
"""


@api.get("{name}", **schema_or_error(APIKeySchema))
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
        return k if k.active else get_error_response(
            status=ErrorStatus.Disabled,
            details=f"API key '{name}' is disabled!")

    # Key couldn't be located
    return get_error_response(
        status=ErrorStatus.NotFound,
        details=f"API key '{name}' not found!")
