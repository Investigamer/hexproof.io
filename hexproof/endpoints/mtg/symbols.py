"""
* Endpoint: Symbols
* This route handles management of all SVG Symbol objects.
"""
# Standard Library Imports
from contextlib import suppress
from pathlib import Path
from typing import Optional

# Third Party Imports
from ninja import Router
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest, FileResponse

# Local Imports
from hexproof.models import (
    SymbolCollectionSet,
    SymbolCollectionWatermark,
    SymbolRarity,
    Set)
from hexproof.schemas import (
    schema_or_error,
    ErrorStatus,
    get_error_response,
    SetSymbolURI,
    WatermarkSymbolURI)

# Django Ninja Objects
api = Router()

"""
* Util Funcs
"""


def get_svg(svg_file: Path) -> FileResponse:
    """Returns a file response for a given SVG file.

    Args:
        svg_file: Path to the SVG file.

    Returns:
        A 'FileResponse' object to let django render the SVG file.

    Raises:
        FileNotFoundError: If the file can't be located.
    """
    if not svg_file.is_file():
        raise FileNotFoundError(f"File '{str(svg_file)}' not found!")
    return FileResponse(open(svg_file, 'rb'), content_type='image/svg+xml')


def search_symbol_set(code: str) -> SymbolCollectionSet:
    """Searches for a 'SymbolCollectionSet' by its code or by the code of its related 'Set' object.

    Args:
        code: Code of a matching 'SymbolCollectionSet' or 'Set' object.

    Returns:
        Matching 'SymbolCollectionSet' object.

    Raises:
        ObjectDoesNotExist: If no matching 'Set' or 'SymbolCollectionSet' is found.
    """
    try:
        # Try looking for matching 'SymbolCollectionSet' code
        return SymbolCollectionSet.objects.get(code=code.upper())
    except ObjectDoesNotExist:
        # Try looking for matching 'Set' code
        return Set.objects.get(code=code.lower()).symbol


def get_symbol_set_default(rarity: Optional[str] = None):
    """Returns the default set symbol or symbol URI map.

    Args:
        rarity: Rarity to look for if provided.
    """
    # Get default symbol
    try:
        symbol = SymbolCollectionSet.objects.get(code='DEFAULT')
        if not rarity:
            return symbol.get_symbol_uri_map()
    except ObjectDoesNotExist:
        # No default symbol registered in the database
        return get_error_response(
            status=ErrorStatus.Server,
            details="No default symbol is registered in the server database!",
            warnings=[
                "If you requested an SVG symbol other than 'DEFAULT', it wasn't found."
            ])

    # Get rarity requested
    with suppress(Exception):
        matched = SymbolRarity.get_rarity(rarity)
        return get_svg(symbol.get_symbol_path(matched.code))

    # Revert to common rarity
    with suppress(Exception):
        return get_svg(symbol.get_symbol_path('C'))
    return get_error_response(
        status=ErrorStatus.Server,
        details="The default symbol does not support the rarity provided!",
        warnings=[
            "If you requested an SVG symbol other than 'DEFAULT', it wasn't found.",
            "Attempted to fallback to 'common' rarity, but the default symbol does not support it!"
        ])


"""
* Symbol Rarity API Endpoints
"""


@api.get('rarity', **schema_or_error(dict[str, str]))
def get_symbol_rarities(request: HttpRequest):
    """Return a dictionary of all set symbol rarities.

    Args:
        request: HTTP request object.

    Returns:
        A dictionary where keys are the rarity code, values are the name of the rarity.
    """
    return {n.code: n.name for n in SymbolRarity.objects.all()}


"""
* Set Symbol API Endpoints
"""


@api.get('set', **schema_or_error(dict[str, SetSymbolURI]))
def get_symbol_set_all(request: HttpRequest):
    """Return a dictionary of all set symbol collections.

    Args:
        request: HTTP request object.

    Returns:
        dict[str, SetSymbolURI]: A dictionary where keys are the symbol code, values are URI maps from
            'SymbolCollectionSet' resources.
    """
    return {n.code: n.get_symbol_uri_map() for n in SymbolCollectionSet.objects.all()}


@api.get('set/{code}', **schema_or_error(SetSymbolURI))
def get_symbol_set(request: HttpRequest, code: str):
    """Returns a URI map for a 'SymbolCollectionSet' resource.

    Args:
        request: HTTP request object.
        code: 'SymbolCollectionSet' identifier code or 'Set' identifier code.

    Returns:
        SetSymbolURI: A URI map from a 'SymbolCollectionSet' object.
    """
    with suppress(Exception):
        # Return found symbol
        return search_symbol_set(code).get_symbol_uri_map()

    # Code not recognized
    return get_error_response(
        status=ErrorStatus.NotFound,
        details=f"Symbol matching code '{code}' not found.")


@api.get('set/{code}/{rarity}', **schema_or_error(type[FileResponse]))
def get_symbol_set_rarity(request: HttpRequest, code: str, rarity: str):
    """Returns a specific SVG set symbol asset with a given symbol or set code and rarity.

    Args:
        request: HTTP request object.
        code: Symbol code the symbol is defined by, or code the parent set is defined by.
        rarity: The rarity version of the symbol to return.

    Returns:
        FileResponse: The requested watermark SVG file asset.
    """
    # Return a default symbol if code is unrecognized
    try:
        symbol = search_symbol_set(code)
    except ObjectDoesNotExist:
        return get_symbol_set_default(rarity)

    # Return an error if the requested rarity is not recognized
    try:
        matched = SymbolRarity.get_rarity(rarity)
    except SymbolRarity.DoesNotExist:
        return get_error_response(
            status=ErrorStatus.NotFound,
            details=f"Unrecognized rarity: '{rarity}'")

    # Return an error if symbol doesn't support the rarity requested
    if matched not in symbol.supported.all():
        return get_error_response(
            status=ErrorStatus.NotImplemented,
            details=f"Symbol matching code '{code}' does not support rarity '{rarity}'.")

    # Return SVG file if it exists
    svg_file = symbol.get_symbol_path(matched.code)
    with suppress(Exception):
        return get_svg(svg_file)
    return get_error_response(
        # File resource not found
        status=ErrorStatus.NotFound,
        details=f"SVG file for code:rarity '{code}:{rarity}' could not be located.")


"""
* Watermark Symbol API Endpoints
"""


@api.get('watermark', **schema_or_error(WatermarkSymbolURI))
def get_symbol_watermark_all(request: HttpRequest):
    """Return a dictionary of all watermark symbol URI's.

    Args:
        request: HTTP request object.

    Returns:
        WatermarkSymbolURI: A dictionary containing named watermarks and set symbol watermarks.
    """
    return WatermarkSymbolURI(
        watermarks={
            n.name: n.get_symbol_uri() for n in
            SymbolCollectionWatermark.objects.filter(parent_symbol_set__isnull=True)},
        watermarks_set={
            n.parent_symbol_set.code: n.get_symbol_uri() for n in
            SymbolCollectionWatermark.objects.filter(parent_symbol_set__isnull=False)})


@api.get('watermark/set/{code}', **schema_or_error(type[FileResponse]))
def get_symbol_watermark_set(request: HttpRequest, code: str):
    """Returns a watermark 'Set' symbol with a given set symbol code or set code.

    Args:
        request: HTTP request object.
        code: Symbol code the symbol is defined by, or code the parent set is defined by.

    Returns:
        FileResponse: The requested watermark SVG file asset.
    """
    try:
        # Try finding a 'Set' watermark
        code = code.upper()
        obj = search_symbol_set(code)
        if obj.supports_watermark():
            return get_svg(obj.get_symbol_path('WM'))
        # 'Set' symbol found but watermark not supported
        return get_error_response(
            status=ErrorStatus.NotImplemented,
            details=f"Set symbol collection '{code}' doesn't support a watermark symbol.")
    except ObjectDoesNotExist:
        # No watermark found
        return get_error_response(
            status=ErrorStatus.NotFound,
            details=f"Unrecognized Set symbol code: '{code}'")
    except FileNotFoundError:
        # 'Set' symbol found, but file resource is missing
        return get_error_response(
            status=ErrorStatus.Server,
            details=f"Unable to locate SVG file for recognized Set symbol watermark: '{code}'")


@api.get('watermark/{name}', **schema_or_error(type[FileResponse]))
def get_symbol_watermark(request: HttpRequest, name: str):
    """Returns a specific SVG watermark symbol asset with a given name.

    Args:
        request: HTTP request object.
        name: Symbol name the symbol is defined by.

    Returns:
        FileResponse: The requested watermark SVG file asset.
    """
    try:
        # Try finding a regular watermark
        try:
            obj = SymbolCollectionWatermark.objects.get(name=name.lower())
            return get_svg(obj.get_symbol_path())
        except ObjectDoesNotExist:
            # Try finding a 'Set' watermark
            try:
                obj = search_symbol_set(name.upper())
                if obj.supports_watermark():
                    return get_svg(obj.get_symbol_path('WM'))
                # 'Set' symbol found but watermark not supported
                return get_error_response(
                    status=ErrorStatus.NotImplemented,
                    details=f"Recognized 'Set' code '{name}', but this set doesn't have a supported watermark symbol.")
            except ObjectDoesNotExist:
                # No watermark found
                return get_error_response(
                    status=ErrorStatus.NotFound,
                    details=f"Unrecognized watermark: '{name}'")
    except FileNotFoundError:
        # Watermark found, but file resource is missing
        return get_error_response(
            status=ErrorStatus.Server,
            details=f"Unable to locate SVG file for recognized watermark: '{name}'")
