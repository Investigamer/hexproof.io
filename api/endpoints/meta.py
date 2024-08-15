"""
* Endpoint: Meta
* This route handles management of all Meta objects.
"""
# Standard Library Imports
from contextlib import suppress

# Third Party Imports
from ninja import Router
from django.http import HttpRequest
from hexproof.hexapi import schema as Hexproof

# Local Imports
from api.models import Meta
from api.utils.response import ErrorStatus, schema_or_error, get_error_response

# Django Ninja Objects
api = Router()

"""
* Endpoints
"""


@api.get("", **schema_or_error(dict[str, Hexproof.Meta]))
def get_meta_all(request: HttpRequest):
    """Retrieve a dictionary of all resource metas.

    Args:
        request: HTTP request object.

    Returns:
        dict: A dictionary of all Meta objects, with keys as 'resource' value.
    """
    return {n.resource: n._api_obj for n in Meta.objects.all()}


@api.get("{resource}", **schema_or_error(Hexproof.Meta))
def get_meta(request: HttpRequest, resource: str):
    """Retrieve a dictionary of all resource metas.

    Args:
        request: HTTP request object.
        resource: Specific 'Meta' resource to look for.

    Returns:
        MetaSchema: A specific MetaSchema object matching a resource value.
    """
    with suppress(Exception):

        # Return found Meta resource
        return Meta.objects.get(resource=resource)._api_obj

    # Meta resource not found
    return get_error_response(
        status=ErrorStatus.NotFound,
        details=f"Metadata matching resource name '{resource}' not found.")
