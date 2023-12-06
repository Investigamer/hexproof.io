"""
* Endpoint: Keys
* This route handles management of all Key objects.
"""
from contextlib import suppress
from pathlib import Path
from typing import Optional

# Third Party Imports
from ninja import Router
from django.http import HttpRequest, FileResponse, JsonResponse

# Local Imports
from hexproof.models import SymbolCollectionSet, SymbolRarity

# Django Ninja Objects
api = Router()


# Rarity names mapped
RARITY_MAP = {
    'watermark': 'WM',
    'common': 'C',
    'uncommon': 'U',
    'rare': 'R',
    'mythic': 'M',
    'special': 'S',
    'timeshifted': 'T',
    'timeshift': 'T',
    'bonus': 'B',
    '80': '80'
}


"""
* Util Funcs
"""


def get_svg(svg_file: Path) -> FileResponse:
    """Returns a file response for a given SVG file.

    Args:
        svg_file: Path to the SVG file.

    Returns:
        A 'FileResponse' object to let django render the SVG file.
    """
    return FileResponse(open(svg_file, 'rb'), content_type='image/svg+xml')


def get_symbol_set_default(rarity: Optional[str] = None, pretty: bool = False):
    """Returns the default set symbol or symbol URI map.

    Args:
        rarity: Rarity to look for if provided.
        pretty: If returning a URI map, whether to return formatted JSON or raw.
    """
    # Get default symbol
    symbol = SymbolCollectionSet.objects.get(code='DEFAULT')
    if not rarity:
        obj = symbol.get_symbol_uri_map()
        return JsonResponse(obj, json_dumps_params={'indent': 2}) if pretty else obj

    # Get rarity requested
    rarity_mapped = RARITY_MAP.get(rarity.lower()) or rarity.upper()
    with suppress(Exception):
        matched = SymbolRarity.objects.get(code=rarity_mapped)
        svg_file = symbol.get_symbol_path(matched.code)
        if svg_file.is_file():
            return get_svg(svg_file)

    # Rarity not recognized
    common = SymbolRarity.objects.get(code='C')
    svg_file = symbol.get_symbol_path(common)
    return get_svg(svg_file)


"""
* API Endpoints
"""


@api.get('set')
def get_symbol_set_all(request: HttpRequest, pretty: bool = False):
    """Return a dictionary of all set symbol collections.

    Args:
        request: Object containing HTTP request information.
        pretty: Whether to format the JSON response for readability.

    Returns:
        A dictionary where keys are the symbol code, values are the collection of symbol resources.
    """
    obj = {n.code: n.get_symbol_uri_map() for n in SymbolCollectionSet.objects.all()}
    return JsonResponse(obj, json_dumps_params={'indent': 2}) if pretty else obj


@api.get('set/{code}')
def get_symbol_set(request: HttpRequest, code: str, pretty: bool = False):
    with suppress(Exception):
        symbol = SymbolCollectionSet.objects.get(code=code.upper())
        obj = symbol.get_symbol_uri_map()
        return JsonResponse(obj, json_dumps_params={'indent': 2}) if pretty else obj
    # Code not recognized
    return {
        'object': 'error',
        'message': f"Symbol matching code '{code}' not found.",
        'status': 404
    }


@api.get('set/{code}/{rarity}')
def get_symbol_set_rarity(request: HttpRequest, code: str, rarity: str):
    """Returns a specific SVG set symbol asset with a given code and rarity.

    Args:
        request: HTTP request object.
        code: Symbol code the symbol is defined by.
        rarity: The rarity version of the symbol to return.
    """
    # Return a default symbol if code is unrecognized
    try:
        symbol = SymbolCollectionSet.objects.get(code=code.upper())
    except SymbolCollectionSet.DoesNotExist:
        return get_symbol_set_default(rarity)

    # Return an error if the requested rarity is not recognized
    rarity_mapped = RARITY_MAP.get(rarity.lower()) or rarity.upper()
    try:
        matched = SymbolRarity.objects.get(code=rarity_mapped)
    except SymbolRarity.DoesNotExist:
        return {
            'object': 'error',
            'message': f"Unrecognized rarity: '{rarity}'",
            'status': 404
        }

    # Return an error if symbol doesn't support the rarity requested
    if matched not in symbol.supported.all():
        return {
            'object': 'error',
            'message': f"Symbol matching code '{code}' does not support rarity '{rarity}'.",
            'status': 502
        }

    # Return SVG file if it exists
    svg_file = symbol.get_symbol_path(matched.code)
    return get_svg(svg_file) if svg_file.is_file else {
        'object': 'error',
        'message': f"SVG asset for code:rarity '{code}:{rarity}' could not be located.",
        'status': 404
    }
