"""
CyberX DFIR Framework
modules/evidence/hashing.py

Provides cryptographic hash calculation for evidence files.

Features
--------
- MD5
- SHA1
- SHA256
- SHA512
- Chunked reading (large forensic images supported)
- File validation
- Human-readable file size
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Dict

# Read files in 8 MB chunks
CHUNK_SIZE = 8 * 1024 * 1024


class HashingError(Exception):
    """Raised when hashing cannot be completed."""
    pass


def _validate_file(file_path: str | Path) -> Path:
    """
    Validate evidence file.

    Returns
    -------
    pathlib.Path
    """

    path = Path(file_path)

    if not path.exists():
        raise HashingError(f"File does not exist: {path}")

    if not path.is_file():
        raise HashingError(f"Not a valid file: {path}")

    return path


def _hash_file(path: Path, algorithm: str) -> str:
    """
    Calculate hash using supplied hashlib algorithm.
    """

    try:
        hasher = hashlib.new(algorithm)

    except Exception as exc:
        raise HashingError(
            f"Unsupported hash algorithm: {algorithm}"
        ) from exc

    with path.open("rb") as f:

        while True:

            chunk = f.read(CHUNK_SIZE)

            if not chunk:
                break

            hasher.update(chunk)

    return hasher.hexdigest()


def md5(file_path: str | Path) -> str:
    """
    Calculate MD5.
    """

    path = _validate_file(file_path)

    return _hash_file(path, "md5")


def sha1(file_path: str | Path) -> str:
    """
    Calculate SHA1.
    """

    path = _validate_file(file_path)

    return _hash_file(path, "sha1")


def sha256(file_path: str | Path) -> str:
    """
    Calculate SHA256.
    """

    path = _validate_file(file_path)

    return _hash_file(path, "sha256")


def sha512(file_path: str | Path) -> str:
    """
    Calculate SHA512.
    """

    path = _validate_file(file_path)

    return _hash_file(path, "sha512")


def calculate_hashes(file_path: str | Path) -> Dict[str, str]:
    """
    Calculate all supported hashes.

    Returns
    -------
    dict
    """

    path = _validate_file(file_path)

    return {

        "md5": _hash_file(path, "md5"),

        "sha1": _hash_file(path, "sha1"),

        "sha256": _hash_file(path, "sha256"),

        "sha512": _hash_file(path, "sha512")

    }


def file_size(file_path: str | Path) -> int:
    """
    Return file size in bytes.
    """

    path = _validate_file(file_path)

    return path.stat().st_size


def human_size(size: int) -> str:
    """
    Convert bytes to readable size.
    """

    units = [

        "Bytes",

        "KB",

        "MB",

        "GB",

        "TB",

        "PB"

    ]

    value = float(size)

    for unit in units:

        if value < 1024:

            if unit == "Bytes":
                return f"{int(value)} {unit}"

            return f"{value:.2f} {unit}"

        value /= 1024

    return f"{value:.2f} EB"


def evidence_metadata(file_path: str | Path) -> Dict:
    """
    Complete metadata for uploaded evidence.

    Returns
    -------
    {
        filename,
        extension,
        size,
        size_human,
        md5,
        sha1,
        sha256,
        sha512
    }
    """

    path = _validate_file(file_path)

    hashes = calculate_hashes(path)

    size = file_size(path)

    return {

        "filename": path.name,

        "filepath": str(path),

        "extension": path.suffix.lower(),

        "size": size,

        "size_human": human_size(size),

        "md5": hashes["md5"],

        "sha1": hashes["sha1"],

        "sha256": hashes["sha256"],

        "sha512": hashes["sha512"]

    }


if __name__ == "__main__":

    import sys

    if len(sys.argv) != 2:

        print("Usage:")

        print("python hashing.py <file>")

        raise SystemExit(1)

    info = evidence_metadata(sys.argv[1])

    print("\n========== Evidence ==========")

    print(f"File     : {info['filename']}")

    print(f"Size     : {info['size_human']}")

    print(f"MD5      : {info['md5']}")

    print(f"SHA1     : {info['sha1']}")

    print(f"SHA256   : {info['sha256']}")

    print(f"SHA512   : {info['sha512']}")