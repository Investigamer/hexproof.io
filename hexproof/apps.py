# Standard Library Imports
from pathlib import Path
from typing_extensions import TypedDict

import yarl
# Third Party Imports
from django.apps import AppConfig
from django.utils.functional import classproperty


class AppDirs(TypedDict):
    """Known app directories used by the Hexproof project."""
    ASSETS: Path
    CACHE: Path


class AppURIs(TypedDict):
    """Known app URI locations for asset collection."""
    VECTORS: yarl.URL


class HexproofConfig(AppConfig):
    name = 'hexproof'
    default_auto_field = 'django.db.models.BigAutoField'
    API_URL: yarl.URL = yarl.URL('https://api.hexproof.io')
    DIRS: AppDirs = {
        'ASSETS': Path(__file__).resolve().parent.parent / '.assets',
        'CACHE': Path(__file__).resolve().parent.parent / '.cache'
    }
    URIS: AppURIs = {
        'VECTORS': yarl.URL('https://raw.githubusercontent.com/Investigamer/mtg-vectors/main')
    }

    @classproperty
    def DIR_SYMBOLS_SET(self) -> Path:
        return self.DIRS['ASSETS'] / 'symbols' / 'set'

    @classproperty
    def API_SYMBOLS_SET(self) -> yarl.URL:
        return self.API_URL / 'symbols' / 'set'


HexproofConfig.DIRS['CACHE'].mkdir(mode=711, parents=True, exist_ok=True)
HexproofConfig.DIRS['ASSETS'].mkdir(mode=711, parents=True, exist_ok=True)
