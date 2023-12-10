"""
* Models relating to MTG Symbol objects
"""
# Standard Library Imports
from contextlib import suppress
from functools import cache
from pathlib import Path
from typing import Optional

# Third Party Imports
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Model, CharField, ManyToManyField, ForeignKey, SET_NULL, QuerySet, CASCADE
import yarl

# Local Imports
from hexproof.apps import HexproofConfig
from hexproof.schemas import SetSymbolURI

"""
* Models
"""


class SymbolRarity(Model):
    """Symbol rarities supported by 'SymbolCollectionSet' symbols."""
    code = CharField(max_length=10, unique=True)
    name = CharField(max_length=255, unique=True)

    """
    * Core Model Methods
    """

    def delete(self, using=None, keep_parents=False):
        """Removes a 'SymbolRarity' object from the database."""
        super().delete(using=using, keep_parents=keep_parents)
        SymbolRarity.get_rarity.cache_clear()

    """
    * Class Methods
    """

    @classmethod
    @cache
    def get_rarity(cls, rarity: str) -> 'SymbolRarity':
        """Returns a specific rarity from the 'SymbolRarity' model."""
        try:
            return cls.objects.get(code=rarity.upper())
        except ObjectDoesNotExist:
            return cls.objects.get(name=rarity.lower().title())

    @classmethod
    def get_watermark(cls) -> 'SymbolRarity':
        """Returns the recognized 'watermark' rarity with code 'WM'."""
        return cls.get_rarity('WM')


class SymbolCollectionSet(Model):
    """Symbol collection for symbol type 'Set'. Records the rarity types supported by this symbol."""
    code = CharField(max_length=10, unique=True)
    parent = ForeignKey(to='self', on_delete=CASCADE, null=True, default=None)
    supported = ManyToManyField(SymbolRarity)

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

    def get_symbol_uri_map(self) -> SetSymbolURI:
        """SetURISymbolSchema: Returns a dictionary of rarities mapped to their SVG endpoint."""
        obj = {
            rarity.code: str(HexproofConfig.API_SYMBOLS_SET / self.alias.lower() / rarity.code.lower())
            for rarity in self.supported.all()
        }
        return dict(sorted(obj.items()))

    def get_symbol_path_map(self) -> dict[str, Path]:
        """dict[str, Path]: Returns a dictionary of rarities mapped to their SVG file path."""
        obj = {
            rarity.code: (
                HexproofConfig.DIR_SYMBOLS_SET / self.alias / rarity.code
            ).with_suffix('.svg') for rarity in self.supported.all()
        }
        return dict(sorted(obj.items()))

    def get_symbol_path(self, rarity: str):
        """Path: Returns a Path object leading to an SVG symbol asset for a given rarity of this symbol collection.

        Args:
            rarity: Rarity to use from the symbol collection.
        """
        return (HexproofConfig.DIR_SYMBOLS_SET / self.alias / rarity.upper()).with_suffix('.svg')

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
        """bool: Whether this 'SymbolCollectionSet' supports a watermark symbol."""
        return self.supported.contains(SymbolRarity.get_watermark())

    """
    * Class Methods
    """

    @classmethod
    def get_default_symbol(cls) -> Optional['SymbolCollectionSet']:
        """Optional[SymbolCollectionSet]: Attempt to get the default SymbolCollectionSet, otherwise None."""
        with suppress(Exception):
            try:
                return cls.objects.get(code='DEFAULT')
            except ObjectDoesNotExist:
                return cls.objects.first()
        return


class SymbolCollectionWatermark(Model):
    """Symbol collection for symbol type 'Watermark'.
    Some are 'Set' watermarks with a 'SymbolCollectionSet' parent."""
    name = CharField(max_length=255, unique=True)
    parent_symbol_set = ForeignKey(SymbolCollectionSet, on_delete=SET_NULL, null=True, default=None)

    """
    * Getter Methods
    """

    def get_symbol_path(self) -> Path:
        """Path: Return a Path object leading to an SVG symbol asset for this watermark."""
        if self.parent_symbol_set:
            return self.parent_symbol_set.get_symbol_path('WM')
        return (HexproofConfig.DIR_SYMBOLS_WATERMARK / self.name).with_suffix('.svg')

    def get_symbol_uri(self) -> str:
        """str: Return an API URI pointing to an SVG symbol asset."""
        if self.parent_symbol_set:
            return self.parent_symbol_set.get_symbol_uri('WM')
        return str(HexproofConfig.API_SYMBOLS_WATERMARK / self.name)


"""
* Symbol Rarities Utils
"""


def add_or_update_symbol_rarities(d: dict) -> None:
    """Update an existing 'SymbolRarity' if matching code exists, otherwise add a new one."""
    found = []
    for code, name in d.items():
        try:
            obj = SymbolRarity.objects.get(code=code.upper())
            obj.name = name.title()
            obj.save()
        except ObjectDoesNotExist:
            obj = SymbolRarity.objects.create(code=code.upper(), name=name.title())
        found.append(obj.code)

    # Remove rarities not provided
    for rarity in SymbolRarity.objects.exclude(code__in=found):
        rarity.delete()

    # Clear 'get_rarity' cache
    SymbolRarity.get_rarity.cache_clear()


"""
* Symbol Set Utils
"""


def match_symbol_to_set(d: dict) -> Optional[SymbolCollectionSet]:
    """Try to figure out the appropriate `SymbolCollectionSet` instance for a given unified 'Set' object.

    Args:
        d: Unified 'Set' data object.
    """
    # Establish needed data
    code = d['code'].upper()

    # Check if this set has a clean match
    try:
        obj = SymbolCollectionSet.objects.get(code=code)
        return obj.parent or obj
    except ObjectDoesNotExist:

        # Format the icon
        icon = d.get('scryfall_icon_uri', '')
        icon = yarl.URL(icon).with_suffix('').name.upper() if icon else None

        # Check if icon is recognized
        if icon:
            with suppress(ObjectDoesNotExist):
                obj = SymbolCollectionSet.objects.get(code=icon)
                return obj.parent or obj

    # Resort to default
    with suppress(ObjectDoesNotExist):
        obj = SymbolCollectionSet.objects.get(code='DEFAULT')
        print(f"Symbol Set to Default: "
              f"{code}[{(d.get('code_parent') or '—').upper()}] / "
              f"{d.get('type', 'normal')} / {icon}")
        return obj
    return


def add_symbol_set(
        code: str,
        supported: QuerySet[SymbolRarity],
        parent: Optional[SymbolCollectionSet] = None
) -> SymbolCollectionSet:
    """Add a new 'SymbolCollectionSet' to the database."""
    obj = SymbolCollectionSet.objects.create(code=code, parent=parent)
    obj.supported.set(supported)
    obj.save()
    return obj


def update_symbol_set(
    code: str,
    supported: QuerySet[SymbolRarity],
    parent: Optional[SymbolCollectionSet] = None
) -> SymbolCollectionSet:
    """Update an existing 'SymbolCollectionSet' in the database."""
    obj = SymbolCollectionSet.objects.get(code=code.upper())
    obj.supported.set(supported)
    obj.parent = parent
    obj.save()
    return obj


def add_or_update_symbol_set(
    code: str,
    supported: list[str],
    code_parent: Optional[str] = None
) -> SymbolCollectionSet:
    """Update an existing 'SymbolCollectionSet' if matching code exists, otherwise add a new one."""
    rarities = SymbolRarity.objects.filter(code__in=supported)
    try:
        parent = SymbolCollectionSet.objects.get(code=code_parent) if code_parent else None
    except ObjectDoesNotExist:
        parent = None
    # Update existing 'SymbolCollectionSet'
    try:
        return update_symbol_set(code=code, parent=parent, supported=rarities)
    except ObjectDoesNotExist:
        # Add a new 'SymbolCollectionSet'
        return add_symbol_set(code=code, parent=parent, supported=rarities)


def add_or_update_symbol_sets(data: dict[str, tuple[list[str], Optional[str]]]) -> None:
    """Update all existing 'SymbolCollectionSet' objects or add new ones."""
    found = []
    for code, data in data.items():
        # Add or update set
        supported, code_parent = data
        found.append(
            add_or_update_symbol_set(
                code=code, supported=supported, code_parent=code_parent
            ).code)

    # Remove sets not provided
    for symbol in SymbolCollectionSet.objects.exclude(code__in=found):
        symbol.delete()


"""
* Symbol Watermark Utilities
"""


def add_or_update_symbol_watermark_parents() -> list[str]:
    """Adds a watermark with parent linkage for each 'SymbolCollectionSet' who supports 'WM' symbol."""
    # Get the watermark rarity
    try:
        WM = SymbolRarity.get_rarity('WM')
    except ObjectDoesNotExist:
        print("Watermark rarity doesn't exist in the database!")
        return []

    # Find each 'SymbolCollectionSet' that supports watermark
    found = []
    for symbol in SymbolCollectionSet.objects.filter(supported=WM):
        try:
            # Watermark already exists
            obj = SymbolCollectionWatermark.objects.get(parent_symbol_set=symbol)
        except ObjectDoesNotExist:
            # Add new watermark
            obj = SymbolCollectionWatermark.objects.create(
                name=f'set{symbol.code.lower()}', parent_symbol_set=symbol)
        found.append(obj.name)
    return found


def add_or_update_symbol_watermarks(watermarks: list[str]) -> None:
    """Update an existing 'SymbolRarity' if matching code exists, otherwise add a new one."""
    found = []
    for wm in watermarks:
        try:
            # Watermark already exists
            obj = SymbolCollectionWatermark.objects.get(name=wm.lower())
        except ObjectDoesNotExist:
            # Add new watermark
            obj = SymbolCollectionWatermark.objects.create(name=wm.lower())
        found.append(obj.name)

    # Add or update symbol watermarks with parents
    found.extend(add_or_update_symbol_watermark_parents())

    # Remove watermarks not provided in the list or with parents not present
    for wm in SymbolCollectionWatermark.objects.exclude(name__in=found):
        wm.delete()
