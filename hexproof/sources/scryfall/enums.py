"""
* Scryfall Enums
"""
# Standard Library Imports
from dataclasses import dataclass

# Third Party Imports
import yarl


@dataclass
class SCRY_URL:
    ROOT = yarl.URL('https://scryfall.com')
    API = yarl.URL('https://api.scryfall.com')
    ROOT_SETS = yarl.URL('https://scryfall.com/sets')
    API_SETS = yarl.URL('https://api.scryfall.com/sets')
    API_CARDS = yarl.URL('https://api.scryfall.com/cards')
    API_CARDS_SEARCH = yarl.URL('https://api.scryfall.com/cards/search')
