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
    status: StatusCode
    details: str
    warnings: Optional[list[str]] = None
    data: Optional[dict[str, Any]] = None


class ErrorResponseBadRequest(ErrorResponse):
    """ErrorResponse for a 400 status code."""
    status: StatusCode = StatusCode.BadRequest
    details: str = 'Resource not found!'


class ErrorResponseForbidden(ErrorResponse):
    """ErrorResponse for a 403 status code."""
    status: StatusCode = StatusCode.Forbidden
    details: str = 'Insufficient permissions to access this resource!'


class ErrorResponseNotFound(ErrorResponse):
    """ErrorResponse for a 404 status code."""
    status: StatusCode = StatusCode.NotFound
    details: str = 'Resource not found!'


class ErrorResponseDisabled(ErrorResponse):
    """ErrorResponse for a 405 status code."""
    status: StatusCode = StatusCode.Disabled
    details: str = 'The requested method is disabled for this resource!'


class ErrorResponseGone(ErrorResponse):
    """ErrorResponse for a 410 status code."""
    status: StatusCode = StatusCode.Gone
    details: str = 'This resource was permanently retired!'


class ErrorResponseServer(ErrorResponse):
    """ErrorResponse for a 500 status code."""
    status: StatusCode = StatusCode.Server
    details: str = 'A server-side error was encountered!'


class ErrorResponseNotImplemented(ErrorResponse):
    """ErrorResponse for a 501 status code."""
    status: StatusCode = StatusCode.NotImplemented
    details: str = "The requested resource hasn't been implemented yet!"


class ErrorResponseBadGateway(ErrorResponse):
    """ErrorResponse for a 502 status code."""
    status: StatusCode = StatusCode.BadGateway
    details: str = 'An upstream server-side error was encountered!'


# Error status codes
ErrorStatuses: dict[int, type[ErrorResponse]] = {
    400: ErrorResponseBadRequest,
    403: ErrorResponseForbidden,
    404: ErrorResponseNotFound,
    405: ErrorResponseDisabled,
    410: ErrorResponseGone,
    500: ErrorResponseServer,
    501: ErrorResponseNotImplemented,
    502: ErrorResponseBadGateway
}

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
    exclude_defaults: bool = False,
    errors: list[StatusCode] | None = None
) -> SchemaOrErrorWithExclusions:
    """Creates a response that returns a schema on OK status code, or an error response on error status code.

    Args:
        schema: Schema to return on a 200 status code.
        exclude_none: Whether to exclude 'None' values from the response schema.
        exclude_unset: Whether to exclude unset values from the response schema.
        exclude_defaults: Whether to exclude default values from the response schema.
        errors: A list of error statuses that may be returned as an error response.

    Returns:
        A django-ninja response dict mapping the given schema to 200 status code, and 'ErrorResponse' to all others.
    """
    if errors is None:
        errors = []
    return SchemaOrErrorWithExclusions(
        response={200: schema, **{n: ErrorStatuses[n] for n in errors}},
        exclude_none=exclude_none,
        exclude_unset=exclude_unset,
        exclude_defaults=exclude_defaults
    )
