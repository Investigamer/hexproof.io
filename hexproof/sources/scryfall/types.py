"""
* Scryfall Data Types
"""
# Standard Library Imports
from typing import TypedDict, Literal, Union
from typing_extensions import NotRequired

SetTypes = Union[
    Literal['core'],
    Literal['expansion'],
    Literal['masters'],
    Literal['alchemy'],
    Literal['masterpiece'],
    Literal['arsenal'],
    Literal['from_the_vault'],
    Literal['spellbook'],
    Literal['premium_deck'],
    Literal['duel_deck'],
    Literal['draft_innovation'],
    Literal['treasure_chest'],
    Literal['commander'],
    Literal['planechase'],
    Literal['archenemy'],
    Literal['vanguard'],
    Literal['funny'],
    Literal['starter'],
    Literal['box'],
    Literal['promo'],
    Literal['token'],
    Literal['memorabilia'],
    Literal['minigame']
]


class Set(TypedDict):
    """Scryfall 'Set' object representing a group of related Magic cards."""
    arena_code: NotRequired[str]
    block: NotRequired[str]
    block_code: NotRequired[str]
    card_count: int
    code: str
    digital: bool
    foil_only: bool
    icon_svg_uri: str
    id: str
    mtgo_code: NotRequired[str]
    name: str
    nonfoil_only: bool
    object: Literal['set']
    parent_set_code: NotRequired[str]
    printed_size: NotRequired[int]
    released_at: NotRequired[str]
    scryfall_uri: str
    search_uri: str
    set_type: SetTypes
    tcgplayer_id: NotRequired[int]
    uri: str
