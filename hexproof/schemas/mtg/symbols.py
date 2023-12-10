"""
* Symbol Model Schemas
"""
# Standard Library Imports
from typing_extensions import TypedDict, NotRequired

# Third Party Imports
from ninja import Schema

# Local Imports
from hexproof.apps import HexproofConfig
from django.apps import apps


"""
* Schemas
"""


# TODO: Figure out how to load these dynamically from the 'SymbolRarity' model
SetSymbolURI = TypedDict('SetSymbolURI', {
    '80': NotRequired[str],
    'B': NotRequired[str],
    'C': NotRequired[str],
    'H': NotRequired[str],
    'M': NotRequired[str],
    'R': NotRequired[str],
    'S': NotRequired[str],
    'T': NotRequired[str],
    'U': NotRequired[str],
    'WM': NotRequired[str]
})
SetSymbolURI.__doc__ = "Endpoint URI's for 'Set' Symbol SVG assets."


class WatermarkSymbolURI(Schema):
    """Endpoint URI's for all 'SymbolCollectionWatermark' objects.
    Watermarks divided into 'watermarks' and 'watermarks_set'."""
    watermarks: dict[str, str]
    watermarks_set: dict[str, str]
