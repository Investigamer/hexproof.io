# Third Party Imports
from typing import Any, Optional

# Third Party Imports
from ninja import Schema

# Local Imports
from hexproof.schemas.keys import APIKeySchema
from hexproof.schemas.mtg.sets import SetSchema, SetFlagsSchema, SetURIScryfallSchema


class ErrorResponse(Schema):
    """Defines the object structure of an error response."""
    object: str = 'error'
    message: str
    status: int


class MessageResponse(Schema):
    """Response describing the result of an API action."""
    object: str = 'message'
    message: str
    details: Optional[dict[str, Any]]
