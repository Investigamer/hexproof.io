"""
* MTGJSON Types
"""
# Standard Library Imports
from typing import Literal
from typing_extensions import NotRequired, TypedDict


"""
* Types: Metadata
"""


class Meta(TypedDict):
    """Model describing the properties of the MTGJSON application meta data."""
    date: str
    version: str


"""
* Types: Translations
"""

# Translations object
Translations = TypedDict(
    'Translations', {
        'Ancient Greek': NotRequired[str],
        'Arabic': NotRequired[str],
        'Chinese Simplified': NotRequired[str],
        'Chinese Traditional': NotRequired[str],
        'French': NotRequired[str],
        'German': NotRequired[str],
        'Hebrew': NotRequired[str],
        'Italian': NotRequired[str],
        'Japanese': NotRequired[str],
        'Korean': NotRequired[str],
        'Latin': NotRequired[str],
        'Phyrexian': NotRequired[str],
        'Portuguese (Brazil)': NotRequired[str],
        'Russian': NotRequired[str],
        'Sanskrit': NotRequired[str],
        'Spanish': NotRequired[str]
    }
)


"""
* Types: Identifiers
"""


class Identifiers(TypedDict):
    """Model describing the properties of identifiers associated to a card."""
    cardKingdomEtchedId: NotRequired[str]
    cardKingdomFoilId: NotRequired[str]
    cardKingdomId: NotRequired[str]
    cardsphereId: NotRequired[str]
    mcmId: NotRequired[str]
    mcmMetaId: NotRequired[str]
    mtgArenaId: NotRequired[str]
    mtgjsonFoilVersionId: NotRequired[str]
    mtgjsonNonFoilVersionId: NotRequired[str]
    mtgjsonV4Id: NotRequired[str]
    mtgoFoilId: NotRequired[str]
    mtgoId: NotRequired[str]
    multiverseId: NotRequired[str]
    scryfallId: NotRequired[str]
    scryfallOracleId: NotRequired[str]
    scryfallIllustrationId: NotRequired[str]
    tcgplayerProductId: NotRequired[str]
    tcgplayerEtchedProductId: NotRequired[str]


"""
* Types: URLs
"""


class PurchaseUrls(TypedDict):
    """Model describing the properties of links to purchase a product from a marketplace."""
    cardKingdom: NotRequired[str]
    cardKingdomEtched: NotRequired[str]
    cardKingdomFoil: NotRequired[str]
    cardmarket: NotRequired[str]
    tcgplayer: NotRequired[str]
    tcgplayerEtched: NotRequired[str]


"""
* Types: Sealed Product
"""


class SealedProductCard(TypedDict):
    """Model describing the 'card' product configuration in SealedProductContents."""
    foil: bool
    name: str
    number: str
    set: str
    uuid: str


class SealedProductDeck(TypedDict):
    """Model describing the 'deck' product configuration in SealedProductContents."""
    name: str
    set: str


class SealedProductOther(TypedDict):
    """Model describing the 'obscure' product configuration in SealedProductContents."""
    name: str


class SealedProductPack(TypedDict):
    """Model describing the 'pack' product configuration in SealedProductContents."""
    code: str
    set: str


class SealedProductSealed(TypedDict):
    """Model describing the 'sealed' product configuration in SealedProductContents."""
    count: int
    name: str
    set: str
    uuid: str


class SealedProductContents(TypedDict):
    """Model describing the contents properties of a purchasable product in a Set Data Model."""
    card: NotRequired[list[SealedProductCard]]
    deck: NotRequired[list[SealedProductDeck]]
    other: NotRequired[list[SealedProductOther]]
    pack: NotRequired[list[SealedProductPack]]
    sealed: NotRequired[list[SealedProductSealed]]
    variable: NotRequired[list[dict[Literal['configs']], list['SealedProductContents']]]


class SealedProduct(TypedDict):
    """Model describing the properties for the purchasable product of a Set Data Model."""
    cardCount: NotRequired[int]
    category: NotRequired[str]
    contents: NotRequired[SealedProductContents]
    identifiers: Identifiers
    name: str
    productSize: NotRequired[int]
    purchaseUrls: PurchaseUrls
    releaseDate: NotRequired[str]
    subtype: NotRequired[str]
    uuid: str


"""
* Types: Cards
"""


class CardSet(TypedDict):
    pass


class CardToken(TypedDict):
    pass


"""
* Types: Boosters
"""


class BoosterConfig(TypedDict):
    pass


"""
* Types: Decks
"""


class DeckSet(TypedDict):
    pass


"""
* Types: Sets
"""


class SetList(TypedDict):
    """Model describing the meta data properties of an individual Set."""
    baseSetSize: int
    block: NotRequired[str]
    code: str
    codeV3: NotRequired[str]
    isForeignOnly: NotRequired[bool]
    isFoilOnly: bool
    isNonFoilOnly: NotRequired[bool]
    isOnlineOnly: bool
    isPaperOnly: NotRequired[bool]
    isPartialPreview: NotRequired[bool]
    keyruneCode: str
    mcmId: NotRequired[int]
    mcmIdExtras: NotRequired[int]
    mcmName: NotRequired[str]
    mtgoCode: NotRequired[str]
    name: str
    parentCode: NotRequired[str]
    releaseDate: str
    sealedProduct: list[SealedProduct]
    tcgplayerGroupId: NotRequired[int]
    totalSetSize: int
    translations: Translations
    type: str


class Set(TypedDict):
    """Model describing the properties of an individual set."""
    baseSetSize: int
    block: NotRequired[str]
    booster: NotRequired[dict[str, list[BoosterConfig]]]
    cards: list[CardSet]
    cardsphereSetId: NotRequired[int]
    code: str
    codeV3: NotRequired[str]
    decks: list[DeckSet]
    isForeignOnly: NotRequired[bool]
    isFoilOnly: bool
    isNonFoilOnly: NotRequired[bool]
    isOnlineOnly: bool
    isPaperOnly: NotRequired[bool]
    isPartialPreview: NotRequired[bool]
    keyruneCode: str
    languages: NotRequired[list[str]]
    mcmId: NotRequired[int]
    mcmIdExtras: NotRequired[int]
    mcmName: NotRequired[str]
    mtgoCode: NotRequired[str]
    name: str
    parentCode: NotRequired[str]
    releaseDate: str
    sealedProduct: list[SealedProduct]
    tcgplayerGroupId: NotRequired[int]
    tokens: list[CardToken]
    tokenSetCode: NotRequired[str]
    totalSetSize: int
    translations: Translations
    type: str
