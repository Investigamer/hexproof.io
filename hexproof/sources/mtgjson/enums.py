"""
* MTGJSON Enums
"""
# Standard Library Imports
from dataclasses import dataclass

# Third Party Imports
import yarl


@dataclass
class MTJ_URL:
    API = yarl.URL('https://mtgjson.com/api/v5')
    API_SET_LIST = yarl.URL('https://mtgjson.com/api/v5/SetList.json')
    API_SET_ALL = yarl.URL('https://mtgjson.com/api/v5/AllSetFiles.tar.gz')
