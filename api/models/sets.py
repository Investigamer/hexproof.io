"""
* Models relating to MTG Set objects
"""
# Standard Library Imports
from contextlib import suppress
from typing import Optional

# Third Party Imports
import yarl
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Model, TextChoices, ForeignKey, SET_NULL
from django.db.models.fields import TextField, IntegerField, BooleanField, DateField, CharField
from hexproof.scryfall.enums import ScryURL, SetType
from hexproof.hexapi import schema as Hexproof
from hexproof.mtgjson import schema as MTGJson
from hexproof.scryfall import schema as Scryfall
from hexproof.scryfall import get_url_base, get_icon_code
from ninja import Schema
from omnitils.files import load_data_file

# Local Imports
from api.apps import HexproofConfig
from api.models.symbols import SymbolSet, get_symbol_manifest

"""
* Models
"""


class Set(Model):
    """A unified data model for Magic the Gathering 'Set' objects.

    Sources:
        - Scryfall: https://api.scryfall.com/sets
        - MTGJson: https://mtgjson.com/api/v5/SetList.json
    """

    class SetTypeChoices(TextChoices):
        """Choices based on set 'types' as defined by Scryfall.

        Notes:
            https://scryfall.com/docs/api/sets
        """
        CORE = SetType.Core
        EXPANSION = SetType.Expansion
        MASTERS = SetType.Masters
        ALCHEMY = SetType.Alchemy
        MASTERPIECE = SetType.Masterpiece
        ARSENAL = SetType.Arsenal
        FROM_THE_VAULT = SetType.FromTheVault
        SPELLBOOK = SetType.Spellbook
        PREMIUM_DECK = SetType.PremiumDeck
        DUEL_DECK = SetType.DuelDeck
        DRAFT_INNOVATION = SetType.DraftInnovation
        TREASURE_CHEST = SetType.TreasureChest
        COMMANDER = SetType.Commander
        PLANECHASE = SetType.Planechase
        ARCHENEMY = SetType.Archenemy
        VANGUARD = SetType.Vanguard
        FUNNY = SetType.Funny
        STARTER = SetType.Starter
        BOX = SetType.Box
        PROMO = SetType.Promo
        TOKEN = SetType.Token
        MEMORABILIA = SetType.Memorabilia
        MINIGAME = SetType.Minigame

    # Set Model Block
    block = TextField(blank=True, null=True, default=None)
    block_code = CharField(max_length=255, blank=True, null=True, default=None)

    # Set Model Codes
    code = CharField(max_length=255, unique=True)
    code_alt = CharField(max_length=255, blank=True, null=True, default=None)
    code_arena = CharField(max_length=255, blank=True, null=True, default=None)
    code_keyrune = CharField(max_length=255, blank=True, null=True, default=None)
    code_mtgo = CharField(max_length=255, blank=True, null=True, default=None)
    code_parent = CharField(max_length=255, blank=True, null=True, default=None)

    # Set Model Counts
    count_cards = IntegerField(default=0)
    count_printed = IntegerField(blank=True, null=True)
    count_tokens = IntegerField(default=0)

    # Set Model Dates
    date_released = DateField()

    # Set Model ID's
    id_cardmarket = IntegerField(blank=True, null=True, default=None)
    id_cardmarket_extras = IntegerField(blank=True, null=True, default=None)
    id_cardsphere = IntegerField(blank=True, null=True, default=None)
    id_scryfall = TextField(unique=True)
    id_tcgplayer = IntegerField(blank=True, null=True, default=None)

    # Set Model Names
    name = TextField()
    name_cardmarket = TextField(blank=True, null=True, default=None)

    # Set Model Flags
    is_digital_only = BooleanField(default=False)
    is_foil_only = BooleanField(default=False)
    is_foreign_only = BooleanField(default=False)
    is_nonfoil_only = BooleanField(default=False)
    is_paper_only = BooleanField(default=False)
    is_preview = BooleanField(default=False)

    # Scryfall Specific Data
    scryfall_icon_uri = TextField(default='https://svgs.scryfall.io/sets/default.svg')

    # Image resources
    symbol = ForeignKey(SymbolSet, on_delete=SET_NULL, null=True, default=None)

    # Other Properties
    type = CharField(max_length=255, choices=SetTypeChoices, default=SetTypeChoices.EXPANSION)

    """
    * Model Schema
    """

    class InputSchema(Schema):
        """Set model schema for input values."""

        class Config:
            arbitrary_types_allowed = True

        # Fields
        block: str | None
        block_code: str | None
        code: str
        code_alt: str | None
        code_arena: str | None
        code_keyrune: str | None
        code_mtgo: str | None
        code_parent: str | None
        count_cards: int
        count_printed: int | None
        count_tokens: int
        date_released: str | None
        id_cardmarket: int | None
        id_cardmarket_extras: int | None
        id_cardsphere: int | None
        id_scryfall: str
        id_tcgplayer: int | None
        name: str
        name_cardmarket: str | None
        is_digital_only: bool
        is_foil_only: bool
        is_foreign_only: bool
        is_nonfoil_only: bool
        is_paper_only: bool
        is_preview: bool
        scryfall_icon_uri: str
        symbol: SymbolSet | None
        type: str

    """
    * Core Model Methods
    """

    def save(self, *args, **kwargs):
        """Try to ensure symbol always has a value."""
        if self.symbol is None:
            with suppress(type[self.DoesNotExist]):
                self.symbol = SymbolSet.objects.get(code='DEFAULT')
        super().save(*args, **kwargs)

    """
    * URI Objects
    """

    @property
    def uris_scryfall(self) -> Hexproof.SetURIScryfall:
        """Object containing Scryfall related URI's."""
        return Hexproof.SetURIScryfall(
            object=str(ScryURL.API.Sets.All / self.id_scryfall),
            page=str(ScryURL.Site.Sets / self.code),
            parent=str(ScryURL.API.Sets.All / self.code_parent) if self.code_parent else None,
            search=str(ScryURL.API.Cards.Search.with_query({
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
    def flags(self) -> Hexproof.SetFlags:
        """Object containing boolean flags."""
        return Hexproof.SetFlags(
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
    def _api_obj(self) -> Hexproof.Set:
        """The main comprehensive API object Schema for the 'Set' model."""

        # Get the symbol URI map and code, revert to default if unavailable
        symbol = self.symbol if self.symbol is not None else SymbolSet.get_default_symbol()
        symbol_map, symbol_code = (
            symbol.get_symbol_uri_map(), symbol.code.lower()
        ) if symbol is not None else (None, 'default')

        # Return the formatted schema
        return Hexproof.Set(
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
            id=self.id_scryfall,
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
    * Management functions
    """

    @classmethod
    def create_or_update(
        cls,
        scryfall: Scryfall.Set,
        mtgjson: MTGJson.SetList
    ) -> 'Set':
        """Creates a new 'Set' object or updates an existing 'Set' object.

        Args:
            scryfall: Scryfall data to insert.
            mtgjson: MTGJson data to insert if provided.

        Returns:
            Newly created 'Set' object.
        """
        # Scryfall data required to proceed
        if not scryfall:
            return HexproofConfig.logger.warning(
                f'Scryfall data not provided!')
        code = scryfall.code

        # Load mtgjson set data
        try:
            # Todo: Isolate the step for this data so we can load it piecemeal with low memory overhead
            mtgjson_set: Optional[MTGJson.Set] = MTGJson.Set(
                **load_data_file(
                    path=(HexproofConfig.PATH.MTGJSON_SETS / code.upper()).with_suffix('.json')))
        except (FileNotFoundError, ValueError, OSError):
            # No MTGJSON data file found for this set
            mtgjson_set: Optional[MTGJson.Set] = None

        # Add scryfall data
        set_obj = Set.InputSchema(

            # Scryfall Only
            block_code=scryfall.block_code,
            code=code,
            code_arena=scryfall.arena_code,
            id_scryfall=scryfall.id,
            id_tcgplayer=scryfall.tcgplayer_id,
            is_foil_only=scryfall.foil_only,
            is_nonfoil_only=scryfall.nonfoil_only,
            is_digital_only=scryfall.digital,
            name=scryfall.name,
            scryfall_icon_uri=str(get_url_base(scryfall.icon_svg_uri)),
            type=scryfall.set_type,

            # MTGJSON Only
            code_alt=mtgjson.codeV3 if mtgjson else None,
            code_keyrune=mtgjson.keyruneCode if mtgjson else None,
            id_cardmarket=mtgjson.mcmId if mtgjson else None,
            id_cardmarket_extras=mtgjson.mcmIdExtras if mtgjson else None,
            is_foreign_only=mtgjson.isForeignOnly if (
                    mtgjson and mtgjson.isForeignOnly is not None
            ) else False,
            is_paper_only=mtgjson.isPaperOnly if (
                    mtgjson and mtgjson.isPaperOnly is not None
            ) else False,
            is_preview=mtgjson.isPartialPreview if (
                mtgjson and mtgjson.isPartialPreview is not None
            ) else False,
            name_cardmarket=mtgjson.mcmName if mtgjson else None,

            # Scryfall, with MTGJSON fallback
            block=scryfall.block or (mtgjson.block if mtgjson else None),
            code_mtgo=scryfall.mtgo_code or (mtgjson.mtgoCode if mtgjson else None),
            code_parent=scryfall.parent_set_code or (mtgjson.parentCode if mtgjson else None),
            count_cards=scryfall.card_count or (mtgjson.totalSetSize if mtgjson else None),
            count_printed=scryfall.printed_size or (mtgjson.baseSetSize if mtgjson else None),
            date_released=scryfall.released_at or (mtgjson.releaseDate if mtgjson else None),

            # Special conditional processing
            count_tokens=scryfall.card_count if (
                scryfall.set_type == SetType.Token
            ) else (len(mtgjson_set.tokens) if mtgjson_set else 0),
            id_cardsphere=mtgjson_set.cardsphereSetId if mtgjson_set else None,
            symbol=match_symbol_to_set(scryfall))

        # Update existing 'Set' model object, or create new
        if query := Set.objects.filter(code=code):
            query.update(**set_obj.model_dump())
            return query.first()
        return Set.objects.create(**set_obj.model_dump())


"""
* Symbol Data
"""


def match_symbol_to_set(set_obj: Scryfall.Set) -> Optional[SymbolSet]:
    """Try to figure out the appropriate `SymbolSet` instance for a given unified 'Set' object.

    Args:
        set_obj: Scryfall 'Set' object.

    Returns:
        'SymbolSet' instance or `None` if not found.
    """
    # Establish needed data
    set_code = set_obj.code.upper()
    icon_code = get_icon_code(set_obj.icon_svg_uri).upper()

    # Check if this set is manually routed
    if route := get_symbol_manifest().set.routes.get(set_code):
        with suppress(ObjectDoesNotExist):
            symbol = SymbolSet.objects.get(code=route)
            if symbol.parent:
                # Symbol is an alias
                return symbol.parent
            return symbol

    # Check if icon has a match
    with suppress(ObjectDoesNotExist):
        symbol = SymbolSet.objects.get(code=icon_code)
        if symbol.parent:
            # Symbol is an alias
            return symbol.parent
        return symbol

    # Symbol not identified
    with suppress(ObjectDoesNotExist):
        symbol = SymbolSet.get_default_symbol()
        parent = f'[{set_obj.parent_set_code.upper()}]' if set_obj.parent_set_code else ''
        HexproofConfig.logger.warning(
            f'Set({set_code}{parent} | {set_obj.set_type} | {icon_code}) — '
            f'No identifiable symbol. Using DEFAULT.')
        return symbol
    HexproofConfig.logger.error(
        f'Unable to identify symbol for set: {set_code}. '
        f'Unable to fallback to DEFAULT!')
    return
