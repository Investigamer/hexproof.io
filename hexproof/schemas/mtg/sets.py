"""
* Set Model Schemas
"""
# Standard Library Imports
from typing import Optional

# Third Party Imports
from ninja import Schema

# Local Imports
from hexproof.schemas.mtg.symbols import SetSymbolURI


class SetFlagsSchema(Schema):
    """Boolean flags for the Set object."""
    is_digital_only: bool
    is_foil_only: bool
    is_foreign_only: bool
    is_nonfoil_only: bool
    is_paper_only: bool
    is_preview: bool


class SetURIScryfallSchema(Schema):
    """Scryfall URI's for Set object."""
    icon: Optional[str]
    object: Optional[str]
    page: Optional[str]
    parent: Optional[str]
    search: Optional[str]


class SetSchema(Schema):
    """Entire Set object as an API return schema."""
    block: Optional[str]
    block_code: Optional[str]
    code: str
    code_alt: Optional[str]
    code_arena: Optional[str]
    code_keyrune: Optional[str]
    code_mtgo: Optional[str]
    code_parent: Optional[str]
    code_symbol: str
    count_cards: int
    count_printed: Optional[int]
    count_tokens: int
    date_released: str
    flags: SetFlagsSchema
    id: str
    id_cardmarket: Optional[int]
    id_cardmarket_extras: Optional[int]
    id_cardsphere: Optional[int]
    id_tcgplayer: Optional[int]
    name: str
    name_cardmarket: Optional[str]
    type: str
    uris_scryfall: SetURIScryfallSchema
    uris_symbol: SetSymbolURI
