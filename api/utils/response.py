"""
* Response Utilities
"""
# Standard Library Imports
from enum import IntEnum
from typing import Any, Optional, Union, TypedDict

# Third Party Imports
from django.http import HttpResponseBase
from ninja import Schema
from pydantic import BaseModel

"""
* Types / Enums
"""


class StatusCode(IntEnum):
    """Enumerates response status codes which indicate a successful response or a type of
        error with the request."""
    OK = 200
    BadRequest = 400
    Forbidden = 403
    NotFound = 404
    Disabled = 405
    Gone = 410
    Server = 500
    NotImplemented = 501
    BadGateway = 502


"""
* Schemas
"""


class ErrorResponse(Schema):
    """Defines the object structure of an error response."""
    object: str = 'error'
    status: StatusCode = StatusCode.NotFound
    details: str = 'Resource not found!'
    warnings: Optional[list[str]] = None
    data: Optional[dict[str, Any]] = None


# Error status codes
ErrorStatuses = {int(x): ErrorResponse for x in StatusCode if x != 200}

# Endpoint response
APIResponse = Union[type[dict], type[TypedDict], type[BaseModel], type[HttpResponseBase]]


class MessageResponse(Schema):
    """Response describing the result of an API action."""
    object: str = 'message'
    details: str
    data: Optional[dict[str, Any]]


class SchemaOrErrorWithExclusions(TypedDict):
    """Kwargs used for an API endpoint to return a schema or an error response."""
    response: dict[int, APIResponse]
    exclude_none: bool
    exclude_unset: bool
    exclude_defaults: bool


"""
* Response Util Funcs
"""


def schema_or_error(
    schema: APIResponse,
    exclude_none: bool = True,
    exclude_unset: bool = True,
    exclude_defaults: bool = False
) -> dict[str, Any]:
    """Creates a response that returns a schema on OK status code, or an error response on error status code.

    Args:
        schema: Schema to return on a 200 status code.
        exclude_none: Whether to exclude 'None' values from the response schema.
        exclude_unset: Whether to exclude unset values from the response schema.
        exclude_defaults: Whether to exclude default values from the response schema.

    Returns:
        A django-ninja response dict mapping the given schema to 200 status code, and 'ErrorResponse' to all others.
    """
    return SchemaOrErrorWithExclusions(
        response={200: schema, **ErrorStatuses},
        exclude_none=exclude_none,
        exclude_unset=exclude_unset,
        exclude_defaults=exclude_defaults
    )


def get_error_response(
    status: StatusCode = StatusCode.NotFound,
    details: str = 'Resource not found on the server!',
    warnings: Optional[list[str]] = None,
    data: Optional[dict[str, Any]] = None
) -> tuple[int, ErrorResponse]:
    """Returns a tuple containing a status code and a formatted 'ErrorResponse' schema.

    Args:
        status: A `StatusCode` integer indicating the type of error response.
        details: A string describing the details of the error.
        warnings: An optional list of specific warnings related to the error.
        data: An optional dictionary containing any relevant related to the error, usually for testing.
    """
    return status, ErrorResponse(details=details, status=status, warnings=warnings, data=data)
