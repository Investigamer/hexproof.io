"""
* Key Model Schemas
"""
# Third Party Imports
from ninja import Schema


"""
* Schemas
"""


class APIKeySchema(Schema):
    name: str
    key: str
    active: bool
