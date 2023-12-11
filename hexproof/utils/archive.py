"""
* Compressing and Unpacking Archives
"""
# Standard Library Imports
import os
import tarfile
import zipfile
from pathlib import Path


def unpack_tar_gz(path: Path, remove: bool = True) -> None:
    """Unpacks a `.tar.gz` archive.

    Args:
        path: Path to the archive file.
        remove: Whether to remove the zip after unpacking.
    """
    with tarfile.open(path, 'r:gz') as tar:
        tar.extractall(path=path.parent)
    if remove:
        os.remove(path)


def unpack_zip(path: Path, remove: bool = True) -> None:
    """Unpacks a `.zip` archive.

    Args:
        path: Path to the archive file.
        remove: Whether to remove the zip after unpacking.
    """
    # Unpack the zip file
    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(path=path.parent)
    if remove:
        os.remove(path)
