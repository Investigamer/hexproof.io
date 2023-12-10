"""
* Util Funcs for Getting and Managing Project Info
"""
# Local Imports
from .files import load_data_file
from hexproof.apps import HexproofConfig


def get_current_version() -> str:
    """str: Returns the current version of Hexproof API."""
    try:
        return load_data_file(
            HexproofConfig.DIRS['BASE'] / 'pyproject.toml'
        ).get('tool', {}).get('poetry', {}).get('version', '1.0.0')
    except (FileNotFoundError, ValueError, OSError):
        return '1.0.0'
