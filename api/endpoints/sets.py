"""
* Endpoint: Sets
* This route handles management of all Set objects.
"""
# Third Party Imports
from ninja import Router
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from hexproof.providers.hexapi import schema as Hexproof
from omnitils.files import load_data_file

# Local Imports
from api.apps import HexproofConfig
from api.models import Set
from api.utils.response import StatusCode, schema_or_error, ErrorResponseNotFound

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


@router.get('{code}', **schema_or_error(
    schema=Hexproof.Set, errors=[StatusCode.NotFound]))
def get_set(request: HttpRequest, code: str):
    """Returns a data object for a specific set."""

    # Does set exist?
    try:
        obj = Set.objects.get(code=code.lower())
        return obj._api_obj
    except ObjectDoesNotExist:
        return StatusCode.NotFound, ErrorResponseNotFound(
            details=f"Set matching code '{code}' not found.")
