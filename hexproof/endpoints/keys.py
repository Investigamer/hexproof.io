"""
* Endpoint: Keys
* This route handles management of all Key objects.
"""
# Standard Library Imports
from contextlib import suppress
from enum import IntEnum
from typing import TypedDict, Literal

# Third Party Imports
from ninja import Router
from django.http import HttpRequest

# Local Imports
from hexproof.models import APIKey
from hexproof.schemas import APIKeySchema

# Django Ninja Objects
api = Router()


"""
* Response Types
"""


class KeyResponses(IntEnum):
    """Enumerates the potential error reasons for `get/key/`."""
    Valid = 200
    Missing = 404
    Disabled = 403


class ReturnError(TypedDict):
    """Defines the object structure of an error response."""
    object: Literal['error']
    message: str


"""
* Endpoints
"""


@api.get("get/{name}", response={
    KeyResponses.Valid: APIKeySchema,
    KeyResponses.Missing: ReturnError,
    KeyResponses.Disabled: ReturnError
})
def get_key(request: HttpRequest, name: str):
    """Retrieve an API key that is currently active.

    Args:
        request (HttpRequest): Django request object.
        name (str): Name of the key to look for.

    Returns:
        dict: A key object if an active key was found, otherwise
            an error object with a reason code and readable message.
    """
    with suppress(Exception):
        k = APIKey.objects.get(name=name)
        if k.active:
            return k
        return KeyResponses.Disabled, {
            'object': 'error',
            'message': f"API key '{name}' is disabled!"}
    return KeyResponses.Missing, {
        'object': 'error',
        'message': f"API key '{name}' not found!"}
