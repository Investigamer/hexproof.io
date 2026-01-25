"""
* Endpoint: Meta
* This route handles management of all Meta objects.
"""
# Third Party Imports
from ninja import Router
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from hexproof.providers.hexapi import schema as Hexproof

# Local Imports
from api.models import Meta
from api.utils.response import StatusCode, schema_or_error, ErrorResponseNotFound

# Django Ninja Objects
router = Router()

"""
* Endpoints
"""


@router.get("", **schema_or_error(dict[str, Hexproof.Meta]))
def get_meta_all(request: HttpRequest):
    """Retrieve a dictionary of all resource metas.

    Args:
        request: HTTP request object.

    Returns:
        dict: A dictionary of all Meta objects, with keys as 'resource' value.
    """
    return {n.resource: n._api_obj for n in Meta.objects.all()}


@router.get("{resource}", **schema_or_error(
    schema=Hexproof.Meta, errors=[StatusCode.NotFound]))
def get_meta(request: HttpRequest, resource: str):
    """Retrieve a dictionary of all resource metas.

    Args:
        request: HTTP request object.
        resource: Specific 'Meta' resource to look for.

    Returns:
        MetaSchema: A specific MetaSchema object matching a resource value.
    """
    try:
        _obj = Meta.objects.get(resource=resource)
        return _obj._api_obj
    except ObjectDoesNotExist:
        # Meta resource not found
        return StatusCode.NotFound, ErrorResponseNotFound(
            details=f"Metadata matching resource name '{resource}' not found.")
