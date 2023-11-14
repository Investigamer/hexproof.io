"""
* Main API Endpoint
"""
# Standard Library Imports
from contextlib import suppress
from enum import IntEnum
from typing import TypedDict, Literal

# Third Party Imports
from ninja import NinjaAPI
from django.http import HttpRequest

# Local Imports
from .models import Keyring
from .schemas import KeyringSchema

# Django Ninja Objects
api = NinjaAPI()


class KeyResponses(IntEnum):
    """Enumerates the potential error reasons for `get/key/`."""
    Valid = 200
    Missing = 404
    Disabled = 403


class ReturnError(TypedDict):
    """Defines the object structure of an error response."""
    object: Literal['error']
    message: str


@api.get("key/get/{name}", response={
    KeyResponses.Valid: KeyringSchema,
    KeyResponses.Missing: ReturnError,
    KeyResponses.Disabled: ReturnError
})
def get_key(_request: HttpRequest, name: str):
    """Retrieve an API key that is currently active.

    Args:
        _request (HttpRequest): Django request object.
        name (str): Name of the key to look for.

    Returns:
        dict: A key object if an active key was found, otherwise
            an error object with a reason code and readable message.
    """
    with suppress(Exception):
        k = Keyring.objects.get(name=name)
        if k.active:
            return k
        return KeyResponses.Disabled, {
            'object': 'error',
            'message': f"API key '{name}' is disabled!"}
    return KeyResponses.Missing, {
        'object': 'error',
        'message': f"API key '{name}' not found!"}
