"""
* Working with Files
"""
# Standard Library Imports
import os
import json
from contextlib import suppress
from pathlib import Path
from typing import Optional, Callable, Union
from typing_extensions import TypedDict
from threading import Lock

# Third Party Imports
from yaml import (
    load as yaml_load,
    dump as yaml_dump,
    Loader as yamlLoader,
    Dumper as yamlDumper)
from tomlkit import dump as toml_dump, load as toml_load

"""
* Types
"""


class DataFileType (TypedDict):
    """Data file type (json, toml, yaml, etc)."""
    load: Callable
    dump: Callable
    load_kw: dict[str, Union[Callable, bool, str]]
    dump_kw: dict[str, Union[Callable, bool, str]]


"""Data File: TOML (.toml) data type."""
DataFileTOML = DataFileType(
    load=toml_load,
    dump=toml_dump,
    load_kw={},
    dump_kw={'sort_keys': True})

"""Data File: YAML (.yaml) data type."""
DataFileYAML = DataFileType(
    load=yaml_load,
    dump=yaml_dump,
    load_kw={
        'Loader': yamlLoader},
    dump_kw={
        'allow_unicode': True,
        'Dumper': yamlDumper,
        'sort_keys': True,
        'indent': 2,
    })

"""Data File: JSON (.json) data type."""
DataFileJSON = DataFileType(
    load=json.load,
    dump=json.dump,
    load_kw={},
    dump_kw={
        'sort_keys': True,
        'indent': 2,
        'ensure_ascii': False
    })


"""
* Constants
"""

# File util locking mechanism
util_file_lock = Lock()

# Data types alias map
data_types: dict[str, DataFileType] = {
    '.toml': DataFileTOML,
    '.yaml': DataFileYAML,
    '.yml': DataFileYAML,
    '.json': DataFileJSON,
}
supported_data_types = tuple(data_types.keys())


"""
* File Info Utils
"""


def get_file_size_mb(file_path: Union[str, os.PathLike], decimal: int = 1) -> float:
    """
    Get a file's size in megabytes rounded.
    @param file_path: Path to the file.
    @param decimal: Number of decimal places to allow when rounding.
    @return: Float representing the filesize in megabytes rounded.
    """
    return round(os.path.getsize(file_path) / (1024 * 1024), decimal)


"""
* Data File Utils
"""


def validate_data_file(path: Path) -> None:
    """Checks if a data file exists and is a valid data file type. Raises an exception if validation fails.

    Args:
        path: Path to the data file.

    Raises:
        FileNotFoundError: If data file does not exist.
        ValueError: If data file type not supported.
    """
    # Check if file exists
    if not path.is_file():
        raise FileNotFoundError(f"Data file doesn't exist on the server:\n{str(path)}")

    # Check if data file is a supported data type
    if path.suffix.lower() not in supported_data_types:
        raise ValueError("Data file provided does not match a supported data file type.\n"
                         f"Types supported: {', '.join(supported_data_types)}\n"
                         f"Type received: {path.suffix}")


def load_data_file(
    path: Path,
    config: Optional[dict] = None
) -> Union[list, dict, tuple, set]:
    """Load data  object from a data file.

    Args:
        path: Path to the data file to be loaded.
        config: Dict data to modify DataFileType configuration for this data load procedure.

    Returns:
        Data object such as dict, list, tuple, set, etc.

    Raises:
        FileNotFoundError: If data file does not exist.
        ValueError: If data file type not supported.
        OSError: If dumping to data file fails.
    """
    # Check if data file is valid
    validate_data_file(path)

    # Pull the parser and insert user config into kwargs
    parser: DataFileType = data_types.get(path.suffix.lower(), {}).copy()
    kwargs = parser['load_kw'].update(config) if config else parser['load_kw']

    # Attempt to load data
    with util_file_lock, suppress(Exception), open(path, 'r', encoding='utf-8') as f:
        data = parser['load'](f, **kwargs) or {}
        return data
    raise OSError(f"Unable to load data from data file:\n{str(path)}")


def dump_data_file(
    obj: Union[list, dict, tuple, set],
    path: Path,
    config: Optional[dict] = None
) -> None:
    """Dump data object to a data file.

    Args:
        obj: Iterable or dict object to save to data file.
        path: Path to the data file to be dumped.
        config: Dict data to modify DataFileType configuration for this data dump procedure.

    Raises:
        FileNotFoundError: If data file does not exist.
        ValueError: If data file type not supported.
        OSError: If dumping to data file fails.
    """
    # Check if data file is valid
    validate_data_file(path)

    # Pull the parser and insert user config into kwargs
    parser: DataFileType = data_types.get(path.suffix.lower(), {}).copy()
    kwargs = parser['dump_kw'].update(config) if config else parser['dump_kw']

    # Attempt to dump data
    with suppress(Exception), util_file_lock, open(path, 'w', encoding='utf-8') as f:
        parser['dump'](obj, f, **kwargs)
    raise OSError(f"Unable to dump data from data file:\n{str(path)}")
