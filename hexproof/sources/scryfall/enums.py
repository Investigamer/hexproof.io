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
    ROOT_SETS = ROOT / 'sets'
    API_BULK = API / 'bulk-data'
    API_SETS = API / 'sets'
    API_CARDS = API / 'cards'
    API_CARDS_SEARCH = API / 'cards' / 'search'
