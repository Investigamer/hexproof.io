"""
* MTG Vectors Enums
"""
# Standard Library Imports
from dataclasses import dataclass

# Third Party Imports
import yarl

# Local Imports
from hexproof.apps import HexproofConfig


@dataclass
class URL:
    MANIFEST = HexproofConfig.URIS['VECTORS'] / 'manifest.json'
    PACKAGE = HexproofConfig.URIS['VECTORS'] / 'package.zip'
