"""
* Key Model Schemas
"""
# Third Party Imports
from ninja import Schema


"""
* Schemas
"""


class MetaSchema(Schema):
    """API object schema for Meta resources."""
    resource: str
    version: str
    date: str
    uri: str
