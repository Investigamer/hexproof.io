"""
* Models relating to MTG Set objects
"""
# Standard Library Imports
from contextlib import suppress

# Third Party Imports
import yarl
from django.db.models import Model, TextChoices, ForeignKey, SET_NULL
from django.db.models.fields import TextField, IntegerField, BooleanField, DateField

# Local Imports
import hexproof.sources.mtgjson.types as MTJ
from hexproof.models.mtg.symbols import SymbolCollectionSet
from hexproof.sources.scryfall.enums import SCRY_URL
from hexproof.schemas.mtg.sets import SetURIScryfallSchema, SetFlagsSchema, SetSchema

"""
* Enums
"""


class SetTypeChoices(TextChoices):
    """Determines the permission level of an APIKey."""
    CORE = ('core', 'Core')
    EXPANSION = ('expansion', 'Expansion')
    MASTERS = ('masters', 'Masters')
    ALCHEMY = ('alchemy', 'Alchemy')
    MASTERPIECE = ('masterpiece', 'Masterpiece')
    ARSENAL = ('arsenal', 'Arsenal')
    FROM_THE_VAULT = ('from_the_vault', 'From the Vault')
    SPELLBOOK = ('spellbook', 'Spellbook')
    PREMIUM_DECK = ('premium_deck', 'Premium Deck')
    DUEL_DECK = ('duel_deck', 'Duel Deck')
    DRAFT_INNOVATION = ('draft_innovation', 'Draft Innovation')
    TREASURE_CHEST = ('treasure_chest', 'Treasure Chest')
    COMMANDER = ('commander', 'Commander')
    PLANECHASE = ('planechase', 'Planechase')
    ARCHENEMY = ('archenemy', 'Archenemy')
    VANGUARD = ('vanguard', 'Vanguard')
    FUNNY = ('funny', 'Funny')
    STARTER = ('starter', 'Starter')
    BOX = ('box', 'Box')
    PROMO = ('promo', 'Promo')
    TOKEN = ('token', 'Token')
    MEMORABILIA = ('memorabilia', 'Memorabilia')
    MINIGAME = ('minigame', 'Minigame')


"""
* Models
"""


class Set(Model):
    """A unified data model for Magic the Gathering 'Set' objects.

    Sources:
        - Scryfall: https://api.scryfall.com/sets
        - MTGJson: https://mtgjson.com/api/v5/SetList.json
    """

    # Set Model Block
    block = TextField(default='', blank=True)
    block_code = TextField(default='', blank=True)

    # Set Model Codes
    code = TextField(unique=True)
    code_alt = TextField(blank=True)
    code_arena = TextField(blank=True)
    code_keyrune = TextField(blank=True)
    code_mtgo = TextField(blank=True)
    code_parent = TextField(blank=True)

    # Set Model Counts
    count_cards = IntegerField()
    count_printed = IntegerField(null=True, blank=True)
    count_tokens = IntegerField(default=0)

    # Set Model Dates
    date_released = DateField()

    # Set Model ID's
    id_cardmarket = IntegerField(null=True, blank=True, default=None)
    id_cardmarket_extras = IntegerField(null=True, blank=True, default=None)
    id_cardsphere = IntegerField(null=True, blank=True, default=None)
    id_oracle = TextField(unique=True)
    id_tcgplayer = IntegerField(null=True, blank=True, default=None)

    # Set Model Names
    name = TextField()
    name_cardmarket = TextField(blank=True)

    # Set Model Flags
    is_digital_only = BooleanField(default=False)
    is_foil_only = BooleanField(default=False)
    is_foreign_only = BooleanField(default=False)
    is_nonfoil_only = BooleanField(default=False)
    is_paper_only = BooleanField(default=False)
    is_preview = BooleanField(default=False)

    # Scryfall Specific Data
    scryfall_icon_uri = TextField()

    # Image resources
    symbol = ForeignKey(SymbolCollectionSet, on_delete=SET_NULL, null=True, default=None)

    # Other Properties
    type = TextField(choices=SetTypeChoices.choices, default=SetTypeChoices.EXPANSION)

    """
    * Core Model Methods
    """

    def save(self, *args, **kwargs):
        """Try to ensure symbol always has a value."""
        if self.symbol is None:
            with suppress(type[self.DoesNotExist]):
                self.symbol = SymbolCollectionSet.objects.get(code='DEFAULT')
        super().save(*args, **kwargs)

    """
    * URI Objects
    """

    @property
    def uris_scryfall(self) -> SetURIScryfallSchema:
        """Object containing Scryfall related URI's."""
        obj = {
            'object': str(SCRY_URL.API_SETS / self.id_oracle),
            'page': str(SCRY_URL.ROOT_SETS / self.code),
            'search': str(SCRY_URL.API_CARDS_SEARCH.with_query({
                'q': f'e:{self.code}',
                'include_extras': 'true',
                'include_variations': 'true',
                'unique': 'prints',
                'order': 'set'
            })),
            'icon': str(yarl.URL(str(self.scryfall_icon_uri)))
        }
        # Add parent code if necessary
        if self.code_parent:
            obj['parent'] = str(SCRY_URL.API_SETS / self.code_parent)
        return dict(sorted(obj.items()))

    """
    * Flags Object
    """

    @property
    def flags(self) -> SetFlagsSchema:
        """Object containing boolean flags."""
        return {
            'is_digital_only': self.is_digital_only,
            'is_foil_only': self.is_foil_only,
            'is_foreign_only': self.is_foreign_only,
            'is_nonfoil_only': self.is_nonfoil_only,
            'is_paper_only': self.is_paper_only,
            'is_preview': self.is_preview,
        }

    """
    * API Return Objects
    """

    @property
    def _api_obj(self) -> SetSchema:
        # Get the symbol URI map and code, revert to default if unavailable
        symbol = self.symbol if self.symbol is not None else SymbolCollectionSet.get_default_symbol()
        symbol_map, symbol_code = (
            symbol.get_symbol_uri_map(), symbol.code.lower()
        ) if symbol is not None else (None, 'default')
        return {
            k: v for k, v in {
                'block': self.block,
                'block_code': self.block_code,
                'code': self.code,
                'code_alt': self.code_alt,
                'code_arena': self.code_arena,
                'code_keyrune': self.code_keyrune,
                'code_mtgo': self.code_mtgo,
                'code_parent': self.code_parent,
                'code_symbol': symbol_code,
                'count_cards': self.count_cards,
                'count_printed': self.count_printed,
                'count_tokens': self.count_tokens,
                'date_released': self.date_released.strftime('%Y-%m-%d'),
                'flags': self.flags,
                'id': self.id_oracle,
                'id_cardmarket': self.id_cardmarket,
                'id_cardmarket_extras': self.id_cardmarket_extras,
                'id_cardsphere': self.id_cardsphere,
                'id_tcgplayer': self.id_tcgplayer,
                'name': self.name,
                'name_cardmarket': self.name_cardmarket,
                'type': self.type,
                'uris_scryfall': self.uris_scryfall,
                'uris_symbol': symbol_map
            }.items() if v not in [None, '']
        }


"""
* Utility Funcs
"""


def add_mtgjson_set_data(d: dict, set_data: MTJ.Set) -> None:
    """Add additional MTGJSON 'Set' data to unified 'Set' dictionary.

    Args:
        d: Unified 'Set' data dictionary.
        set_data: MTGJSON 'Set' data from a local JSON file.

    Notes:
        Mutates the given unified 'Set' data dictionary.
    """
    # Add token count
    d['count_tokens'] = d.get('count_cards', 0) if (
        d['type'] == 'token'
    ) else len(set_data.get('tokens', []))

    # Add cardsphere ID
    d['id_cardsphere'] = set_data.get('cardsphereSetId')
