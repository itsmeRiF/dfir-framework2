"""
CyberX DFIR Framework
Evidence Validator

Validates uploaded evidence before storage.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import BinaryIO

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from modules.evidence.exceptions import ValidationError


class EvidenceValidator:

    MAX_FILE_SIZE = 100 * 1024 * 1024 * 1024      # 100 GB

    SUPPORTED_EXTENSIONS = {

        ".evtx",
        ".evt",

        ".raw",
        ".mem",
        ".dmp",
        ".bin",

        ".dd",
        ".001",
        ".e01",
        ".aff4",

        ".vhd",
        ".vhdx",

        ".pcap",
        ".pcapng",

        ".log",
        ".csv",
        ".json",
        ".xml",

        ".zip",
        ".7z",
        ".tar",
        ".gz",

        ".reg",
        ".dat",
        ".hve"
    }

    BLOCKED_EXTENSIONS = {

        ".exe",
        ".dll",
        ".bat",
        ".cmd",
        ".com",
        ".scr",
        ".ps1",
        ".vbs",
        ".js",
        ".msi"

    }

    WINDOWS_RESERVED = {

        "CON",
        "PRN",
        "AUX",
        "NUL",

        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",

        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9"

    }

    @classmethod
    def validate(
        cls,
        file: FileStorage
    ) -> dict:

        if file is None:
            raise ValidationError("No file received.")

        if not file.filename:
            raise ValidationError("Filename is empty.")

        filename = secure_filename(file.filename)

        if filename == "":
            raise ValidationError("Invalid filename.")

        if ".." in filename:
            raise ValidationError("Invalid filename.")

        stem = Path(filename).stem.upper()

        if stem in cls.WINDOWS_RESERVED:
            raise ValidationError(
                f"'{stem}' is a reserved Windows filename."
            )

        extension = Path(filename).suffix.lower()

        if extension in cls.BLOCKED_EXTENSIONS:

            raise ValidationError(
                f"{extension} files are not allowed."
            )

        if extension not in cls.SUPPORTED_EXTENSIONS:

            raise ValidationError(
                f"Unsupported evidence type ({extension})."
            )

        size = cls._get_size(file)

        if size == 0:

            raise ValidationError(
                "Uploaded file is empty."
            )

        if size > cls.MAX_FILE_SIZE:

            raise ValidationError(
                "File exceeds maximum allowed size."
            )

        return {

            "filename": filename,

            "original_filename": file.filename,

            "extension": extension,

            "filesize": size

        }

    @staticmethod
    def _get_size(
        file: FileStorage
    ) -> int:

        stream: BinaryIO = file.stream

        position = stream.tell()

        stream.seek(0, os.SEEK_END)

        size = stream.tell()

        stream.seek(position)

        return size