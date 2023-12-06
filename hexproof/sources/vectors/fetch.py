"""
* MTG Vectors Request Handling
"""
# Standard Library Imports
from contextlib import suppress
from typing import Optional
import json

# Third Party Imports
from requests import RequestException
import yarl

# Local Imports
from hexproof.apps import HexproofConfig
from hexproof.sources.github import fetch as Github
from hexproof.utils.archive import unpack_zip

"""
* Request Funcs
"""


def update_package_symbols_set(url: Optional[yarl.URL] = None) -> None:
    """Updates our 'Set' symbol local assets."""

    # Ensure path exists
    path = HexproofConfig.DIR_SYMBOLS_SET / 'set.zip'
    path.mkdir(mode=755, parents=True, exist_ok=True)

    # Download the zip package
    url = url or HexproofConfig.URIS['VECTORS'] / 'package' / 'sets.zip'
    Github.get_archive_zip(url, path)

    # Unpack the zip package
    unpack_zip(path)


def update_manifest_symbols_set() -> tuple[bool, dict]:
    """Update our Set' symbol manifest."""

    # Pathing
    manifest_path = HexproofConfig.DIRS['ASSETS'] / 'manifest.set.json'
    manifest_url = HexproofConfig.URIS['VECTORS'] / 'data' / 'manifest.set.json'

    # Request the updated manifest
    try:
        manifest = Github.get_manifest_data(manifest_url)
    except RequestException:
        return False, {'object': 'error', 'reason': 'MTG Vectors repository unavailable!', 'status': 404}
    except json.JSONDecodeError:
        return False, {'object': 'error', 'reason': 'MTG Vectors manifest is unreadable!', 'status': 502}

    # Check existing manifest if it exists
    with suppress(Exception):
        if manifest_path.is_file():
            with open(manifest_path, 'r', encoding='utf-8') as f:
                data = json.load(f) or {}
            if data.get('meta', {}).get('version', '') == manifest.get('meta', {}).get('version', ''):
                return False, {'object': 'message', 'message': 'Set symbols are already up-to-date!'}

    # Update existing manifest
    with suppress():
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f)
        return True, manifest
    return False, {
        'object': 'error',
        'reason': "MTG Vectors updated set symbol manifest couldn't be written!",
        'status': 502}
