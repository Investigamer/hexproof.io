"""
* Endpoint: Keys
* This route handles management of all Key objects.
"""
# Standard Library Imports
from contextlib import suppress

# Third Party Imports
from ninja import Router
from django.http import HttpRequest, JsonResponse

# Local Imports
from hexproof.models import Set
from hexproof.schemas import SetSchema

# Django Ninja Objects
api = Router()

"""
* API Endpoints
"""


@api.get("", response=dict[str, SetSchema])
def all_sets(request: HttpRequest, pretty: bool = False):
    """Returns a dictionary of data objects for all sets by code."""
    obj = {d.code: d._api_obj for d in Set.objects.all()}
    return JsonResponse(obj, json_dumps_params={'indent': 2}) if pretty else obj


@api.get("{code}", response=SetSchema)
def get_set(request: HttpRequest, code: str, pretty: bool = False):
    """Returns a data object for a specific set."""
    with suppress():
        obj = Set.objects.get(code=code.lower())
        return JsonResponse(
            data=obj._api_obj,
            json_dumps_params={'indent': 2}
        ) if pretty else obj._api_obj
    return {
        'object': 'error',
        'message': f"Set matching code '{code}' not found.",
        'status': 404
    }
