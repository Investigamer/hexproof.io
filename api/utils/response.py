"""
* Response Utilities
"""
# Standard Library Imports
from enum import IntEnum
from typing import Any, Optional, Union
from typing_extensions import TypedDict

# Third Party Imports
from ninja import Schema
from django.http import HttpResponse


"""
* Schemas
"""


class ErrorStatus(IntEnum):
    """Enumerates the potential error reasons for `get/key/`."""
    BadRequest = 400
    Forbidden = 403
    NotFound = 404
    Disabled = 405
    Gone = 410
    Server = 500
    NotImplemented = 501
    BadGateway = 502


class ErrorResponse(Schema):
    """Defines the object structure of an error response."""
    object: str = 'error'
    status: ErrorStatus = ErrorStatus.NotFound
    details: str = 'Resource not found!'
    warnings: Optional[list[str]] = None
    data: Optional[dict[str, Any]] = None


class MessageResponse(Schema):
    """Response describing the result of an API action."""
    object: str = 'message'
    details: str
    data: Optional[dict[str, Any]]


class SchemaOrErrorWithExclusions(TypedDict):
    """Kwargs used for an API endpoint to return a schema or an error response."""
    response: dict[int, Union[type[TypedDict], type[Schema], type[HttpResponse]]]
    exclude_none: bool
    exclude_unset: bool
    exclude_defaults: bool


"""
* Response Util Funcs
"""


def schema_or_error(
    schema: Union[type[TypedDict], type[Schema], type[HttpResponse]],
    exclude_none: bool = True,
    exclude_unset: bool = True,
    exclude_defaults: bool = False
) -> SchemaOrErrorWithExclusions:
    """Creates a response that returns a schema on OK status code, otherwise an ErrorStatus.

    Args:
        schema: Schema to return on a 200 status code.
        exclude_none: Whether to exclude 'None' values from the response schema.
        exclude_unset: Whether to exclude unset values from the response schema.
        exclude_defaults: Whether to exclude default values from the response schema.

    Returns:
        A django-ninja response dict mapping the given schema to 200 status code, and 'ErrorResponse' to all others.
    """
    return {
        'response': {200: schema, ErrorStatus: ErrorResponse},
        'exclude_none': exclude_none,
        'exclude_unset': exclude_unset,
        'exclude_defaults': exclude_defaults
    }


def get_error_response(
        status: ErrorStatus = ErrorStatus.NotFound,
        details: str = 'Resource not found on the server!',
        warnings: Optional[list[str]] = None,
        data: Optional[dict[str, Any]] = None
) -> tuple[int, ErrorResponse]:
    """Returns a tuple containing a status code and a formatted 'ErrorResponse' schema.

    Args:
        status: A status code integer (usually from ErrorStatus enum).
        details: A string describing the details of the error.
        warnings: An optional list of specific warnings related to the error.
        data: An optional dictionary containing any relevant related to the error, usually for testing.
    """
    return status, ErrorResponse(details=details, status=status, warnings=warnings, data=data)
