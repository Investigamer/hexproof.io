"""
* Models relating to MTG Set objects
"""
# Standard Library Imports
from contextlib import suppress

# Third Party Imports
import yarl
from django.db.models import Model, TextChoices, ForeignKey, SET_NULL
from django.db.models.fields import TextField, IntegerField, BooleanField, DateField, CharField

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
    block = TextField(blank=True, null=True, default='')
    block_code = CharField(max_length=255, blank=True, null=True, default='')

    # Set Model Codes
    code = CharField(max_length=255, unique=True)
    code_alt = CharField(max_length=255, blank=True, default='')
    code_arena = CharField(max_length=255, blank=True, default='')
    code_keyrune = CharField(max_length=255, blank=True, default='')
    code_mtgo = CharField(max_length=255, blank=True, default='')
    code_parent = CharField(max_length=255, blank=True, default='')

    # Set Model Counts
    count_cards = IntegerField()
    count_printed = IntegerField(blank=True, null=True)
    count_tokens = IntegerField(default=0)

    # Set Model Dates
    date_released = DateField()

    # Set Model ID's
    id_cardmarket = IntegerField(blank=True, null=True, default=None)
    id_cardmarket_extras = IntegerField(blank=True, null=True, default=None)
    id_cardsphere = IntegerField(blank=True, null=True, default=None)
    id_oracle = TextField(unique=True)
    id_tcgplayer = IntegerField(blank=True, null=True, default=None)

    # Set Model Names
    name = TextField()
    name_cardmarket = TextField(blank=True, default='')

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
    type = CharField(max_length=255, choices=SetTypeChoices.choices, default=SetTypeChoices.EXPANSION)

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
        return SetURIScryfallSchema(
            object=str(SCRY_URL.API_SETS / self.id_oracle),
            page=str(SCRY_URL.ROOT_SETS / self.code),
            parent=str(SCRY_URL.API_SETS / self.code_parent) if self.code_parent else None,
            search=str(SCRY_URL.API_CARDS_SEARCH.with_query({
                'q': f'e:{self.code}',
                'include_extras': 'true',
                'include_variations': 'true',
                'unique': 'prints',
                'order': 'set'
            })),
            icon=str(yarl.URL(str(self.scryfall_icon_uri)))
        )

    """
    * Flags Object
    """

    @property
    def flags(self) -> SetFlagsSchema:
        """Object containing boolean flags."""
        return SetFlagsSchema(
            is_digital_only=self.is_digital_only,
            is_foil_only=self.is_foil_only,
            is_foreign_only=self.is_foreign_only,
            is_nonfoil_only=self.is_nonfoil_only,
            is_paper_only=self.is_paper_only,
            is_preview=self.is_preview,
        )

    """
    * API Return Objects
    """

    @property
    def _api_obj(self) -> SetSchema:
        """The main comprehensive API object Schema for the 'Set' model."""

        # Get the symbol URI map and code, revert to default if unavailable
        symbol = self.symbol if self.symbol is not None else SymbolCollectionSet.get_default_symbol()
        symbol_map, symbol_code = (
            symbol.get_symbol_uri_map(), symbol.code.lower()
        ) if symbol is not None else (None, 'default')

        # Return the formatted schema
        return SetSchema(
            block=self.block or None,
            block_code=self.block_code or None,
            code=self.code,
            code_alt=self.code_alt or None,
            code_arena=self.code_arena or None,
            code_keyrune=self.code_keyrune or None,
            code_mtgo=self.code_mtgo or None,
            code_parent=self.code_parent or None,
            code_symbol=symbol_code,
            count_cards=self.count_cards,
            count_printed=self.count_printed or None,
            count_tokens=self.count_tokens,
            date_released=self.date_released.strftime('%Y-%m-%d'),
            flags=self.flags,
            id=self.id_oracle,
            id_cardmarket=self.id_cardmarket or None,
            id_cardmarket_extras=self.id_cardmarket_extras or None,
            id_cardsphere=self.id_cardsphere or None,
            id_tcgplayer=self.id_tcgplayer or None,
            name=self.name,
            name_cardmarket=self.name_cardmarket or None,
            type=self.type,
            uris_scryfall=self.uris_scryfall,
            uris_symbol=symbol_map
        )


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
