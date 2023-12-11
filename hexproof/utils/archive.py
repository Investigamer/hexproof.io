"""
* Compressing and Unpacking Archives
"""
# Standard Library Imports
import os
import tarfile
import zipfile
from pathlib import Path


def unpack_zip(path: Path, remove: bool = True) -> None:
    """Unpack target 'zip' archive.

    Args:
        path: Path to the archive.
        remove: Whether to remove the archive after unpacking.

    Raises:
        FileNotFoundError: If archive couldn't be located.
    """
    if not path.is_file():
        raise FileNotFoundError(f'Archive not found: {str(path)}')
    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(path=path.parent)
    if remove:
        os.remove(path)


def unpack_tar_gz(path: Path, remove: bool = True) -> None:
    """Unpack target `tar.gz` archive.

    Args:
        path: Path to the archive.
        remove: Whether to remove the archive after unpacking.

    Raises:
        FileNotFoundError: If archive couldn't be located.
    """
    if not path.is_file():
        raise FileNotFoundError(f'Archive not found: {str(path)}')
    with tarfile.open(path, 'r:gz') as tar:
        tar.extractall(path=path.parent)
    if remove:
        os.remove(path)
