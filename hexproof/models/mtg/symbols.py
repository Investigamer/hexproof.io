"""
* Models relating to MTG Symbol objects
"""
# Standard Library Imports
from contextlib import suppress
from pathlib import Path
from typing import Optional

# Third Party Imports
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Model, CharField, ManyToManyField
import yarl

# Local Imports
from hexproof.apps import HexproofConfig
from hexproof.schemas.mtg.sets import SetURISymbolSchema

"""
* Models
"""


class SymbolRarity(Model):
    code = CharField(max_length=10, unique=True)
    name = CharField(max_length=255, unique=True)


class SymbolCollectionSet(Model):
    code = CharField(max_length=10, unique=True)
    parent = CharField(max_length=10, null=True, blank=True)
    supported = ManyToManyField(SymbolRarity)

    @property
    def alias(self):
        return self.parent or self.code

    def get_symbol_parent(self) -> 'SymbolCollectionSet':
        """Returns the parent of this 'SymbolCollectionSet' if one exists."""
        with suppress(type[self.DoesNotExist]):
            if self.parent:
                return SymbolCollectionSet.objects.get(code=self.parent)
        raise self.DoesNotExist(f"Symbol '{self.code}' does not have a parent symbol.")

    def get_symbol_uri_map(self) -> SetURISymbolSchema:
        """Returns a dictionary of rarities mapped to their SVG endpoint."""
        obj = {
            mode.name.lower(): str(HexproofConfig.API_SYMBOLS_SET / self.alias.lower() / mode.code.lower())
            for mode in self.supported.all()
        }
        return dict(sorted(obj.items()))

    def get_symbol_path_map(self) -> dict[str, Path]:
        """Returns a dictionary of rarities mapped to their SVG file path."""
        obj = {
            mode.name.lower(): (
                HexproofConfig.DIR_SYMBOLS_SET / self.alias / mode.code
            ).with_suffix('.svg') for mode in self.supported.all()
        }
        return dict(sorted(obj.items()))

    def get_symbol_path(self, rarity: str):
        """Returns a Path object leading to an SVG symbol asset for a given rarity of this symbol collection.

        Args:
            rarity: Rarity to use from the symbol collection.

        Returns:
            A path object leading to the symbol requested.
        """
        return (HexproofConfig.DIR_SYMBOLS_SET / self.alias / rarity).with_suffix('.svg')

    """
    * Class Methods
    """

    @classmethod
    def get_default_symbol(cls) -> Optional['SymbolCollectionSet']:
        """Attempt to get the default SymbolCollectionSet. If unsuccessful, return None."""
        with suppress(Exception):
            try:
                return cls.objects.get(code='DEFAULT')
            except ObjectDoesNotExist:
                return cls.objects.first()
        return


"""
* Util Funcs
"""


def match_symbol_to_set(d: dict) -> Optional[SymbolCollectionSet]:
    """Try to figure out the appropriate `SymbolCollectionSet` instance for a given unified 'Set' object.

    Args:
        d: Unified 'Set' data object.
    """
    # Establish needed data
    code = d['code'].upper()
    parent = d.get('code_parent')
    parent = parent.upper() if parent else None
    icon = d.get('scryfall_icon_uri', '')
    icon = yarl.URL(icon).with_suffix('').name.upper() if icon else None
    set_type = d.get('type', 'normal')

    # Check if this set has a clean match
    with suppress(ObjectDoesNotExist):
        obj = SymbolCollectionSet.objects.get(code=code)
        return obj.get_symbol_parent() if obj.parent else obj

    # Check if icon is recognized
    if icon:
        with suppress(ObjectDoesNotExist):
            obj = SymbolCollectionSet.objects.get(code=icon)
            return obj.get_symbol_parent() if obj.parent else obj

    # Resort to default
    with suppress(ObjectDoesNotExist):
        obj = SymbolCollectionSet.objects.get(code='DEFAULT')
        print(f"Symbol Set to Default: {code}[{parent or '—'}] / {set_type} / {icon}")
        return obj
    return
