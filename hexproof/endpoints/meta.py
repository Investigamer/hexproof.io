"""
* Endpoint: Meta
* This route handles management of all Meta objects.
"""
# Standard Library Imports
from contextlib import suppress

# Third Party Imports
from ninja import Router
from django.http import HttpRequest, JsonResponse

# Local Imports
from hexproof.models import Meta
from hexproof.schemas import ErrorStatus, MetaSchema, schema_or_error, get_error_response

# Django Ninja Objects
api = Router()

"""
* Endpoints
"""


@api.get("", **schema_or_error(dict[str, MetaSchema]))
def get_meta_all(request: HttpRequest, pretty: bool = False):
    """Retrieve a dictionary of all resource metas.

    Args:
        request: HTTP request object.
        pretty: Whether to format the JSON response for readability.

    Returns:
        dict: A dictionary of all Meta objects, with keys as 'resource' value.
    """
    return JsonResponse(
        {n.resource: n._api_obj.dict() for n in Meta.objects.all()},
        json_dumps_params={'indent': 2}
    ) if pretty else {n.resource: n._api_obj for n in Meta.objects.all()}


@api.get("", **schema_or_error(dict[str, MetaSchema]))
def get_meta(request: HttpRequest, resource: str, pretty: bool = False):
    """Retrieve a dictionary of all resource metas.

    Args:
        request: HTTP request object.
        resource: Specific 'Meta' resource to look for.
        pretty: Whether to format the JSON response for readability.

    Returns:
        MetaSchema: A specific MetaSchema object matching a resource value.
    """
    with suppress(Exception):

        # Return found Meta resource
        obj = Meta.objects.get(resource=resource)._api_obj
        return JsonResponse(obj.dict(), json_dumps_params={'indent': 2}) if pretty else obj

    # Meta resource not found
    return get_error_response(
        status=ErrorStatus.NotFound,
        details=f"Meta info matching resource name '{resource}' not found.")
