"""
* Generic Source Enums
"""
# Standard Library Imports
from dataclasses import dataclass

# Third Party Imports
import yarl


@dataclass
class STORE_URL:
    MCM_SET = yarl.URL('https://cardmarket.com/en/Magic/Expansions')
