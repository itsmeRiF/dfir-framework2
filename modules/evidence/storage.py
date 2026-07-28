"""
CyberX DFIR Framework
Evidence Storage Manager
"""

from __future__ import annotations

import secrets
from datetime import datetime
from pathlib import Path

from werkzeug.datastructures import FileStorage

from modules.evidence.exceptions import StorageError


class EvidenceStorage:

    @staticmethod
    def generate_filename(extension: str) -> str:
        """
        Generates a unique storage filename.

        Example:
        20260723_184512_A91C4F.evtx
        """

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        random = secrets.token_hex(3).upper()

        return f"{timestamp}_{random}{extension}"

    @classmethod
    def save(
        cls,
        file: FileStorage,
        upload_root: str,
        case_id: int,
        artifact_type: str,
        extension: str
    ) -> dict:

        try:

            base = Path(upload_root)

            folder = (
                base /
                f"Case_{case_id:06d}" /
                artifact_type
            )

            folder.mkdir(
                parents=True,
                exist_ok=True
            )

            filename = cls.generate_filename(
                extension
            )

            filepath = folder / filename

            file.save(filepath)

            return {

                "filename": filename,

                "filepath": str(filepath),

                "directory": str(folder)

            }

        except Exception as ex:

            raise StorageError(
                f"Unable to save evidence: {ex}"
            )