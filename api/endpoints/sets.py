"""
* Endpoint: Sets
* This route handles management of all Set objects.
"""
# Standard Library Imports
from contextlib import suppress

# Third Party Imports
from ninja import Router
from django.http import HttpRequest
from hexproof.hexapi import schema as Hexproof
from omnitils.files import load_data_file

# Local Imports
from api.apps import HexproofConfig
from api.models import Set
from api.utils.response import StatusCode, schema_or_error, get_error_response

# Django Ninja Objects
router = Router()

"""
* API Endpoints
"""


@router.get('', **schema_or_error(dict[str, Hexproof.Set]))
def all_sets(request: HttpRequest):
    """Returns a dictionary of data objects for all sets by code."""

    path = HexproofConfig.PATH.CACHE / 'sets.json'
    if path.is_file():
        return load_data_file(path)

    return {d.code: d._api_obj for d in Set.objects.all()}


@router.get('{code}', **schema_or_error(Hexproof.Set))
def get_set(request: HttpRequest, code: str):
    """Returns a data object for a specific set."""
    with suppress(Exception):

        # Return found set
        obj = Set.objects.get(code=code.lower())
        return obj._api_obj

    # Set couldn't be located
    return get_error_response(
        status=StatusCode.NotFound,
        details=f"Set matching code '{code}' not found.")
