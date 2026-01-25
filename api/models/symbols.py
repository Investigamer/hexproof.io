"""
* Models relating to MTG Symbol objects
"""
# Standard Library Imports
from contextlib import suppress
from functools import cache
from pathlib import Path
from typing import Optional

# Third Party Imports
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Model, CharField, ForeignKey, SET_NULL, CASCADE, TextChoices
from hexproof.providers.vectors.enums import SymbolRarity, RarityNameMap
from hexproof.providers.vectors import schema as Vectors
from omnitils.files import load_data_file
from omnitils.schema import Schema

# Local Imports
from api.apps import HexproofConfig

"""
* Models
"""


class SymbolSet(Model):
    """Symbol collection for symbol type 'Set'. Records the rarity types supported by this symbol."""

    class Rarities(TextChoices):
        """Rarities used for the `supported` Field."""
        EIGHTY = SymbolRarity.EIGHTY
        BONUS = SymbolRarity.B
        COMMON = SymbolRarity.C
        HALF = SymbolRarity.H
        MYTHIC = SymbolRarity.M
        RARE = SymbolRarity.R
        SPECIAL = SymbolRarity.S
        TIMESHIFTED = SymbolRarity.T
        UNCOMMON = SymbolRarity.U
        WATERMARK = SymbolRarity.WM

    code = CharField(max_length=25, unique=True)
    parent = ForeignKey(to='self', on_delete=CASCADE, null=True, default=None)
    supported: list = ArrayField(
        CharField(max_length=12, choices=Rarities),
        blank=True, default=set)

    """
    * Schemas
    """

    class InputSchema(Schema):
        """SymbolSet model schema for input values."""
        code: str
        parent: Optional['SymbolSet'] = None
        supported: list[str]

    """
    * Model Properties
    """

    @property
    def alias(self):
        """Returns the parent's code if parent exists, otherwise return code."""
        if self.parent:
            return self.parent.code
        return self.code

    """
    * Getter Methods
    """

    def get_symbol_uri_map(self) -> dict[SymbolRarity, str]:
        """SetURISymbolSchema: Returns a dictionary of rarities mapped to their SVG endpoint."""
        return dict(sorted({
            r: str(HexproofConfig.API_SYMBOLS_SET / self.alias.lower() / r.lower())
            for r in self.supported
        }.items()))

    def get_symbol_path_map(self) -> dict[SymbolRarity, Path]:
        """dict[str, Path]: Returns a dictionary of rarities mapped to their SVG file path."""
        return dict(sorted({
            r: (HexproofConfig.PATH.VECTORS_SET / self.alias / r).with_suffix('.svg')
            for r in self.supported
        }.items()))

    def get_symbol_path(self, rarity: str):
        """Path: Returns a Path object leading to an SVG symbol asset for a given rarity of this symbol collection.

        Args:
            rarity: Rarity to use from the symbol collection.
        """
        return (HexproofConfig.PATH.VECTORS_SET / self.alias / rarity.upper()).with_suffix('.svg')

    def get_symbol_uri(self, rarity: str):
        """str: Returns an API URI pointing to an SVG symbol asset for a given rarity of this symbol collection.

        Args:
            rarity: Rarity to use from the symbol collection.
        """
        return str(HexproofConfig.API_SYMBOLS_SET / self.alias / rarity.upper())

    """
    * Checks
    """

    def supports_watermark(self) -> bool:
        """bool: Whether this 'SymbolSet' supports a watermark symbol."""
        return bool(SymbolRarity.WM in self.supported)

    """
    * Class Methods
    """

    @classmethod
    def get_default_symbol(cls) -> Optional['SymbolSet']:
        """Optional[SymbolSet]: Attempt to get the default SymbolSet, otherwise None."""
        with suppress(Exception):
            try:
                return cls.objects.get(code='DEFAULT')
            except ObjectDoesNotExist:
                return cls.objects.first()
        return


class SymbolWatermark(Model):
    """Symbol collection for symbol type 'Watermark'. Some are 'Set' watermarks with a 'SymbolSet' parent."""
    name = CharField(max_length=255, unique=True)
    parent_symbol_set = ForeignKey(SymbolSet, on_delete=SET_NULL, null=True, default=None)

    """
    * Getter Methods
    """

    def get_symbol_path(self) -> Path:
        """Path: Return a Path object leading to an SVG symbol asset for this watermark."""
        if self.parent_symbol_set:
            return self.parent_symbol_set.get_symbol_path('WM')
        return (HexproofConfig.PATH.VECTORS_WM / self.name).with_suffix('.svg')

    def get_symbol_uri(self) -> str:
        """str: Return an API URI pointing to an SVG symbol asset."""
        if self.parent_symbol_set:
            return self.parent_symbol_set.get_symbol_uri('WM')
        return str(HexproofConfig.API_SYMBOLS_WATERMARK / self.name)


"""
* Symbol Manifest Utils
"""


@cache
def get_symbol_manifest() -> Vectors.Manifest:
    """Return the current mtg-vectors symbol manifest."""
    return Vectors.Manifest(
        **load_data_file(
            HexproofConfig.PATH.VECTORS_MANIFEST))


"""
* Symbol Rarity Utils
"""


def get_symbol_rarity(rarity: str) -> Optional[str]:
    """Identifies a 'SymbolRarity' using a given string and returns it. Return None
        if no clear match can be made.

    Args:
        rarity: String representing a 'SymbolRarity', e.g. 'R' or 'rare'

    Returns:
        A recognized 'SymbolRarity' string.
    """
    rarity = rarity.upper()
    if rarity in SymbolRarity:
        return rarity
    if rarity in RarityNameMap:
        return str(RarityNameMap[rarity])
    return None


"""
* Symbol Set Utils
"""


def create_or_update_symbol_set(
    code: str,
    supported: list[SymbolRarity | str],
    code_parent: Optional[str] = None
) -> Optional[SymbolSet]:
    """Creates a new 'SymbolSet' object or updates an existing one.

    Args:
        code: Set code for the 'SymbolSet'.
        supported: Rarities supported by the 'SymbolSet'.
        code_parent: Parent 'SymbolSet' code to look for, if provided.

    Returns:
        New or updated 'SymbolSet' object.
    """

    # Only include supported rarity strings
    rarities: list[str] = list(set(n for n in SymbolRarity if str(n) in supported))

    # Check for a valid parent
    parent, parents = None, SymbolSet.objects.filter(code=code_parent)
    if code_parent and parents:
        parent = parents.first()

    # Check for an existing object
    if query := SymbolSet.objects.filter(code=code):

        # Update existing object
        obj: SymbolSet = query.first()
        obj.supported = rarities
        if parent is not None:
            obj.parent = parent
        obj.save()
        return obj

    # Create new object
    try:
        obj = SymbolSet.objects.create(
            code=code,
            supported=rarities,
            parent=parent)
    except Exception as e:
        # Failed to create object
        HexproofConfig.logger.exception(e)
        HexproofConfig.logger.error(
            f"Failed to create new 'SymbolSet' object!\n"
            f"Details: {code} | {rarities} | {parent}")
        return
    return obj


def add_or_update_symbol_sets(data: dict[str, Vectors.SetSymbolMap]) -> None:
    """Update all existing 'SymbolSet' objects or add new ones."""
    found = []
    for code, symbol_map in data.items():

        # Add parent symbol
        code = code.upper()
        create_or_update_symbol_set(
            code=code,
            supported=symbol_map.rarities)
        found.append(code)

        # Add alias symbol
        for child in symbol_map.children:
            child = child.upper()
            create_or_update_symbol_set(
                code=child,
                supported=symbol_map.rarities,
                code_parent=code)
            found.append(child)

    # Remove sets not provided
    for symbol in SymbolSet.objects.exclude(code__in=found):
        symbol.delete()


"""
* Symbol Watermark Utilities
"""


def add_or_update_symbol_watermark_parents() -> list[str]:
    """Adds a watermark with parent linkage for each 'SymbolSet' who supports 'WM' symbol."""
    # Find each 'SymbolSet' that supports watermark
    found = []
    for symbol in SymbolSet.objects.filter(supported__contains=[SymbolRarity.WM]):
        try:
            # Watermark already exists
            obj = SymbolWatermark.objects.get(parent_symbol_set=symbol)
        except ObjectDoesNotExist:
            # Add new watermark
            obj = SymbolWatermark.objects.create(
                name=f'set{symbol.code.lower()}', parent_symbol_set=symbol)
        found.append(obj.name)
    return found


def add_or_update_symbol_watermarks(watermarks: list[str]) -> None:
    """Update an existing 'SymbolRarity' if matching code exists, otherwise add a new one."""
    found = []
    for wm in watermarks:

        # Check if watermark exists
        name = wm.lower()
        if not SymbolWatermark.objects.filter(name=name):
            # Add new watermark
            SymbolWatermark.objects.create(name=name)
        found.append(name)

    # Add or update symbol watermarks with parents
    found.extend(add_or_update_symbol_watermark_parents())

    # Remove watermarks not provided in the list or with parents not present
    for wm in SymbolWatermark.objects.exclude(name__in=found):
        wm.delete()
