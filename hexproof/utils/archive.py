"""
* Compressing and Unpacking Archives
"""
# Standard Library Imports
import os
import tarfile
import zipfile
from pathlib import Path


def unpack_tar_gz(path: Path) -> None:
    """Unpacks a `.tar.gz` archive.

    Args:
        path: Path to the archive file.
    """
    with tarfile.open(path, 'r:gz') as tar:
        tar.extractall(path=path.parent)
    os.remove(path)


def unpack_zip(path: Path) -> None:
    """Unpacks a `.zip` archive.

    Args:
        path: Path to the archive file.
    """
    # Unpack the zip file
    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(path=path.parent)
    os.remove(path)
