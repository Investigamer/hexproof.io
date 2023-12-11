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
from hexproof.models import Meta
from hexproof.sources.github import fetch as Github
from hexproof.utils.archive import unpack_zip

"""
* Request Funcs
"""


def update_package_symbols_set(url: Optional[yarl.URL] = None) -> None:
    """Updates our 'Set' symbol local assets."""

    # Ensure path exists
    path = HexproofConfig.DIR_SYMBOLS / 'package.zip'
    path.parent.mkdir(mode=755, parents=True, exist_ok=True)

    # Download the zip package
    url = url or HexproofConfig.URIS['VECTORS'] / 'package.zip'
    Github.get_archive_zip(url, path)

    # Unpack the zip package
    unpack_zip(path, remove=False)


def update_manifest_symbols_set() -> tuple[bool, dict]:
    """Update our Set' symbol manifest."""

    # Pathing
    manifest_path = HexproofConfig.DIRS['ASSETS'] / 'manifest.json'
    manifest_url = HexproofConfig.URIS['VECTORS'] / 'manifest.json'

    # Request the updated manifest
    try:
        manifest = Github.get_manifest_data(manifest_url)
    except RequestException:
        return False, {'object': 'error', 'reason': 'MTG Vectors repository unavailable!', 'status': 404}
    except json.JSONDecodeError:
        return False, {'object': 'error', 'reason': 'MTG Vectors manifest is unreadable!', 'status': 502}

    # Check existing manifest if it exists
    with suppress(Exception):
        current = Meta.objects.get(resource='symbols').version_formatted
        if current == manifest.get('meta', {}).get('version', ''):
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
