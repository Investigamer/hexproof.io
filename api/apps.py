# Standard Library Imports
from pathlib import Path

# Third Party Imports
from django.apps import AppConfig
from django.utils.functional import classproperty
from omnitils.files import mkdir_full_perms, get_project_version
from omnitils.logs import Logger, logger
from omnitils.schema import Schema
import yarl

# Local Imports
from core import settings

"""
* Schemas
"""


class AppPaths(Schema):
    """Known app directories used by the Hexproof project."""

    # Base directory of the project
    BASE: Path = settings.BASE_DIR

    # Cache directory for storing data files, packages, and resources
    CACHE: Path = mkdir_full_perms(settings.BASE_DIR / '.cache')

    # Project file
    APP_MANIFEST: Path = BASE / 'pyproject.toml'

    # MTGJSON Cache
    MTGJSON: Path = mkdir_full_perms(CACHE / 'mtgjson')
    MTGJSON_META: Path = (MTGJSON / 'Meta').with_suffix('.json')
    MTGJSON_SETS: Path = MTGJSON / 'AllSetFiles'
    MTGJSON_SET_LIST: Path = (MTGJSON / 'SetList').with_suffix('.json')

    # Scryfall Cache
    SCRYFALL: Path = mkdir_full_perms(CACHE / 'scryfall')
    SCRYFALL_SET_LIST: Path = (SCRYFALL / 'set_list').with_suffix('.json')

    # MTG-Vectors cache
    VECTORS: Path = CACHE / 'vectors'
    VECTORS_MANIFEST: Path = (VECTORS / 'manifest').with_suffix('.json')
    VECTORS_PACKAGE: Path = (VECTORS / 'package').with_suffix('.zip')
    VECTORS_SET: Path = VECTORS / 'set'
    VECTORS_WM: Path = VECTORS / 'watermark'


class AppUrls(Schema):
    """Known app URI locations for asset collection."""

    class Config:
        arbitrary_types_allowed = True

    # API URL to use for URI values in API response
    API: yarl.URL = yarl.URL(
        settings.ENV('URL_API', default='https://api.hexproof.io'))

    # CDN URL to use for URI values in API response
    CDN: yarl.URL = yarl.URL(
        settings.ENV('URL_CDN', default='https://cdn.hexproof.io'))

    # Mtg-vectors repository file URL
    VECTORS_REPO: str = settings.ENV('MTG_VECTORS', default='Investigamer/mtg-vectors')
    VECTORS: yarl.URL = yarl.URL('https://api.github.com/repos') / VECTORS_REPO / 'releases/latest'


"""
* Global Objects
"""


class HexproofConfig(AppConfig):
    name: str = 'api'
    default_auto_field: str = 'django.db.models.BigAutoField'
    PATH: AppPaths = AppPaths()
    URLS: AppUrls = AppUrls()
    logger: Logger = logger

    # Authentication
    AUTH_GITHUB: str = settings.ENV('AUTH_GITHUB', default=None)

    """
    * Utility Class Methods
    """

    @classmethod
    def get_current_version(cls) -> str:
        """Returns the current project version defined in `pyproject.toml`."""
        return get_project_version(cls.PATH.APP_MANIFEST)

    """
    * API Route Reference
    """

    @classproperty
    def API_SETS(self) -> yarl.URL:
        """URL: https://api.hexproof.io/sets"""
        return self.URLS.API / 'sets'

    @classproperty
    def API_SYMBOLS(self) -> yarl.URL:
        """URL: https://api.hexproof.io/symbols"""
        return self.URLS.API / 'symbols'

    @classproperty
    def API_SYMBOLS_SET(self) -> yarl.URL:
        """URL: https://api.hexproof.io/symbols/set"""
        return self.URLS.API / 'symbols' / 'set'

    @classproperty
    def API_SYMBOLS_WATERMARK(self) -> yarl.URL:
        """URL: https://api.hexproof.io/symbols/watermark"""
        return self.URLS.API / 'symbols' / 'watermark'
