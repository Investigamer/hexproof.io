"""
* Key Model Schemas
"""
# Third Party Imports
from ninja import Schema


"""
* Schemas
"""


class APIKeySchema(Schema):
    """API object schema for API Keys."""
    name: str
    key: str
    active: bool
