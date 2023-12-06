"""
* Set Model Schemas
"""
# Standard Library Imports
from typing import TypedDict, NotRequired


class SetFlagsSchema(TypedDict):
    """Boolean flags for the Set object."""
    is_digital_only: bool
    is_foil_only: bool
    is_foreign_only: bool
    is_nonfoil_only: bool
    is_paper_only: bool
    is_preview: bool


class SetURIScryfallSchema(TypedDict):
    """Scryfall URI's for Set object."""
    icon: NotRequired[str]
    object: NotRequired[str]
    page: NotRequired[str]
    parent: NotRequired[str]
    search: NotRequired[str]
    symbol: NotRequired[str]


SetURISymbolSchema = TypedDict('SetURISymbolSchema', {
    '80': NotRequired[str],
    'bonus': NotRequired[str],
    'common': NotRequired[str],
    'half': NotRequired[str],
    'mythic': NotRequired[str],
    'rare': NotRequired[str],
    'special': NotRequired[str],
    'timeshifted': NotRequired[str],
    'uncommon': NotRequired[str],
    'watermark': NotRequired[str]
})
SetURISymbolSchema.__doc__ = "Endpoint URI's for 'Set' Symbol SVG assets."


class SetSchema(TypedDict):
    """Entire Set object as an API return schema."""
    block: NotRequired[str]
    block_code: NotRequired[str]
    code: str
    code_alt: NotRequired[str]
    code_arena: NotRequired[str]
    code_keyrune: NotRequired[str]
    code_mtgo: NotRequired[str]
    code_parent: NotRequired[str]
    code_symbol: str
    count_cards: int
    count_printed: NotRequired[int]
    count_tokens: int
    date_released: str
    flags: SetFlagsSchema
    id: str
    id_cardmarket: NotRequired[int]
    id_cardmarket_extras: NotRequired[int]
    id_cardsphere: NotRequired[int]
    id_tcgplayer: NotRequired[int]
    name: str
    name_cardmarket: NotRequired[str]
    type: str
    uris_scryfall: SetURIScryfallSchema
    uris_symbol: SetURISymbolSchema
