"""
* Endpoint: Sets
* This route handles management of all Set objects.
"""
# Standard Library Imports
from contextlib import suppress

# Third Party Imports
from ninja import Router
from django.http import HttpRequest

# Local Imports
from hexproof.models import Set
from hexproof.schemas import SetSchema, schema_or_error, get_error_response, ErrorStatus

# Django Ninja Objects
api = Router()

"""
* API Endpoints
"""


@api.get('', **schema_or_error(dict[str, SetSchema]))
def all_sets(request: HttpRequest):
    """Returns a dictionary of data objects for all sets by code."""
    return {d.code: d._api_obj for d in Set.objects.all()}


@api.get('{code}', **schema_or_error(SetSchema))
def get_set(request: HttpRequest, code: str):
    """Returns a data object for a specific set."""
    with suppress(Exception):

        # Return found set
        obj = Set.objects.get(code=code.lower())
        return obj._api_obj

    # Set couldn't be located
    return get_error_response(
        status=ErrorStatus.NotFound,
        details=f"Set matching code '{code}' not found.")
