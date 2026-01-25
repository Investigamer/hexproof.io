"""
* Endpoint: Symbols
* This route handles management of all SVG Symbol objects.
"""
# Standard Library Imports
from pathlib import Path
from typing import Optional

# Third Party Imports
from ninja import Router
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest, FileResponse, HttpResponseRedirect
from omnitils.files import load_data_file
from api.models import Meta
from hexproof.providers.hexapi import schema as Hexproof
from hexproof.providers.vectors.enums import SymbolRarity
from hexproof.providers.vectors import schema as Vectors

# Local Imports
from api.apps import HexproofConfig
from api.models.sets import Set
from api.models.symbols import get_symbol_rarity, SymbolSet, SymbolWatermark
from api.utils.response import (
    ErrorResponseServer,
    ErrorResponseNotFound,
    ErrorResponseNotImplemented,
    ErrorResponseBadRequest,
    StatusCode,
    schema_or_error)

# Django Ninja Objects
router = Router()

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


def get_zip(zip_file: Path) -> FileResponse:
    """Returns a file response for a given ZIP file.

    Args:
        zip_file: Path to the ZIP file.

    Returns:
        A 'FileResponse' object to let django render the ZIP file.

    Raises:
        FileNotFoundError: If the file can't be located.
    """
    if not zip_file.is_file():
        raise FileNotFoundError(f"File '{str(zip_file)}' not found!")
    return FileResponse(open(zip_file, 'rb'), content_type='application/zip')


def get_json(json_file: Path) -> FileResponse:
    """Returns a file response for a given JSON file.

    Args:
        json_file: Path to the JSON file.

    Returns:
        A 'FileResponse' object to let django render the JSON file.

    Raises:
        FileNotFoundError: If the file can't be located.
    """
    if not json_file.is_file():
        raise FileNotFoundError(f"File '{str(json_file)}' not found!")
    return FileResponse(open(json_file, 'rb'), content_type='application/json')


def search_symbol_set(code: str) -> SymbolSet:
    """Searches for a 'SymbolSet' by its code or by the code of its related 'Set' object.

    Args:
        code: Code of a matching 'SymbolSet' or 'Set' object.

    Returns:
        Matching 'SymbolSet' object.

    Raises:
        ObjectDoesNotExist: If no matching 'Set' or 'SymbolSet' is found.
    """
    try:
        # Try looking for matching 'SymbolSet' code
        return SymbolSet.objects.get(code=code.upper())
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
        symbol = SymbolSet.objects.get(code='DEFAULT')
        if not rarity:
            return symbol.get_symbol_uri_map()
    except ObjectDoesNotExist:
        # No default symbol registered in the database
        return StatusCode.Server, ErrorResponseServer(
            details="No default symbol is registered in the server database!",
            warnings=["If you requested a SVG symbol other than 'DEFAULT', it wasn't found."])

    # Get rarity requested
    if matched := get_symbol_rarity(rarity):
        try:
            return get_svg(symbol.get_symbol_path(matched))
        except FileNotFoundError:
            pass

    # Revert to common rarity
    try:
        return get_svg(symbol.get_symbol_path(SymbolRarity.C))
    except FileNotFoundError:
        # Unable to find common rarity
        return StatusCode.Server, ErrorResponseServer(
            details=f"The default symbol does not support the rarity provided: '{rarity}'",
            warnings=[
                "If you requested an SVG symbol other than 'DEFAULT', it wasn't found.",
                "Attempted to fallback to 'common' rarity, but the default symbol does not support it!"
            ])


"""
* Symbol Rarity API Endpoints
"""


@router.get('rarity/', **schema_or_error(dict[str, str], errors=[]))
def get_symbol_rarities(request: HttpRequest):
    """Return a dictionary of all set symbol rarities.

    Args:
        request: HTTP request object.

    Returns:
        A dictionary where keys are the rarity code, values are the name of the rarity.
    """
    return {k: v for k, v in SymbolRarity.items()}


"""
* Set Symbol API Endpoints
"""


@router.get('set/', **schema_or_error(dict[str, dict[SymbolRarity, str]], errors=[]))
def get_symbol_set_all(request: HttpRequest):
    """Return a dictionary of all set symbol collections.

    Args:
        request: HTTP request object.

    Returns:
        dict[str, SetSymbolURI]: A dictionary where keys are the symbol code, values are URI maps from
            'SymbolSet' resources.
    """
    return {n.code: n.get_symbol_uri_map() for n in SymbolSet.objects.all()}


@router.get('set/{code}', **schema_or_error(
    schema=dict[SymbolRarity, str], errors=[StatusCode.NotFound]))
def get_symbol_set(request: HttpRequest, code: str):
    """Returns a URI map for a 'SymbolSet' resource.

    Args:
        request: HTTP request object.
        code: 'SymbolSet' identifier code or 'Set' identifier code.

    Returns:
        SetSymbolURI: A URI map from a 'SymbolSet' object.
    """
    try:
        return search_symbol_set(code).get_symbol_uri_map()
    except ObjectDoesNotExist:
        # Code not recognized
        return StatusCode.NotFound, ErrorResponseNotFound(
            details=f"Symbol matching code '{code}' not found.")


@router.get('set/{code}/{rarity}', **schema_or_error(
    schema=type[FileResponse], errors=[StatusCode.NotFound, StatusCode.NotImplemented, StatusCode.Server]))
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
    matched = get_symbol_rarity(rarity)

    # Ensure requested rarity is valid
    if not matched:
        # Rarity requested not found
        return StatusCode.NotFound, ErrorResponseNotFound(
            details=f"Unrecognized rarity: '{rarity}'")
    if matched not in symbol.supported:
        # Symbol doesn't support the rarity requested
        return StatusCode.NotImplemented, ErrorResponseNotImplemented(
            details=f"Symbol matching code '{code}' does not support rarity '{rarity}'.")

    # Return SVG file if it exists
    svg_file = symbol.get_symbol_path(matched)
    try:
        return get_svg(svg_file)
    except FileNotFoundError:
        # File resource not found
        return StatusCode.NotFound, ErrorResponseNotFound(
            details=f"SVG file for code:rarity '{code}:{rarity}' could not be located.")


"""
* Watermark Symbol API Endpoints
"""


@router.get('watermark/', **schema_or_error(Hexproof.WatermarkSymbolURI))
def get_symbol_watermark_all(request: HttpRequest):
    """Return a dictionary of all watermark symbol URI's.

    Args:
        request: HTTP request object.

    Returns:
        WatermarkSymbolURI: A dictionary containing named watermarks and set symbol watermarks.
    """
    return Hexproof.WatermarkSymbolURI(
        watermarks={
            n.name: n.get_symbol_uri()
            for n in SymbolWatermark.objects.filter(parent_symbol_set__isnull=True).order_by('name')},
        watermarks_set={
            n.code: n.get_symbol_uri(rarity=SymbolRarity.WM)
            for n in SymbolSet.objects.filter(supported__contains=[SymbolRarity.WM]).order_by('code')}
    )


@router.get('watermark/set/{code}', **schema_or_error(
    schema=type[FileResponse], errors=[StatusCode.NotFound, StatusCode.NotImplemented, StatusCode.Server]))
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
        return StatusCode.NotImplemented, ErrorResponseNotImplemented(
            details=f"Set symbol collection '{code}' doesn't support a watermark symbol.")
    except ObjectDoesNotExist:
        # No watermark found
        return StatusCode.NotFound, ErrorResponseNotFound(
            details=f"Unrecognized Set symbol code: '{code}'")
    except FileNotFoundError:
        # 'Set' symbol found, but file resource is missing
        return StatusCode.Server, ErrorResponseServer(
            details=f"Unable to locate SVG file for recognized Set symbol watermark: '{code}'")


@router.get('watermark/{name}', **schema_or_error(
    schema=type[FileResponse], errors=[StatusCode.NotFound, StatusCode.NotImplemented, StatusCode.Server]))
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
            obj = SymbolWatermark.objects.get(name=name.lower())
            return get_svg(obj.get_symbol_path())
        except ObjectDoesNotExist:
            # Try finding a 'Set' watermark
            try:
                obj = search_symbol_set(name.upper())
                if obj.supports_watermark():
                    return get_svg(obj.get_symbol_path('WM'))
                # 'Set' symbol found but watermark not supported
                return StatusCode.NotImplemented, ErrorResponseNotImplemented(
                    details=f"Recognized 'Set' code '{name}', but this set doesn't have a supported watermark symbol.")
            except ObjectDoesNotExist:
                # No watermark found
                return StatusCode.NotFound, ErrorResponseNotFound(
                    details=f"Unrecognized watermark: '{name}'")
    except FileNotFoundError:
        # Watermark found, but file resource is missing
        return StatusCode.Server, ErrorResponseServer(
            details=f"Unable to locate SVG file for recognized watermark: '{name}'")


"""
* MTG Vectors Repository Resources
"""


@router.get('package/')
def get_symbol_package_default(request: HttpRequest):
    """Return the default symbol package from the `mtg-vectors` repository.

    Args:
        request: HTTP request object.
    """
    return HttpResponseRedirect('/symbols/package/optimized')


@router.get('package/{name}', **schema_or_error(
    schema=type[HttpResponseRedirect], errors=[StatusCode.BadRequest]))
def get_symbol_package(request: HttpRequest, name: str):
    """Return a specified symbol package from the `mtg-vectors` repository.

    Args:
        request: HTTP request object.
        name: Name of the symbol package, options are "all" and "optimized".
    """
    try:
        obj = Meta.objects.get(resource=f'mtg-vectors[{name}]')
        return HttpResponseRedirect(obj.uri)
    except ObjectDoesNotExist:
        # Unrecognized 'Meta' resource
        err_data = {}
        if options := Meta.objects.filter(resource__contains='mtg-vectors['):
            options = [n.resource.split('[')[1][:-1] for n in options]
            err_data['data'] = dict(
                options={
                    n: request.build_absolute_uri(f"/symbols/package/{n}") for n in options
                }
            )
        return StatusCode.BadRequest, ErrorResponseBadRequest(
            details=f"Unrecognized mtg-vectors package: '{name}'. Please provide a recognized package name.",
            **err_data
        )


@router.get('manifest/', **schema_or_error(
    schema=Vectors.Manifest, errors=[StatusCode.Server]))
def get_symbol_manifest(request: HttpRequest):
    """Return the current symbol manifest from the `mtg-vectors` repository.

    Args:
        request: HTTP request object.
    """
    try:
        return load_data_file(HexproofConfig.PATH.VECTORS_MANIFEST)
    except (FileNotFoundError, ValueError, OSError):
        return StatusCode.Server, ErrorResponseServer(
            details="Server could not access the mtg-vectors symbol manifest!"
        )
