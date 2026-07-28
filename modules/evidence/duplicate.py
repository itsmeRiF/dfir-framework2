"""
CyberX DFIR Framework
Duplicate Evidence Detection

Checks whether an evidence file already exists
using SHA256 hash.
"""

from __future__ import annotations

from typing import Optional

from models.evidence import Evidence


class DuplicateChecker:
    """
    Detect duplicate evidence using SHA256 hash.
    """

    @staticmethod
    def find_by_sha256(sha256: str) -> Optional[Evidence]:
        """
        Returns the matching Evidence object if found.
        """

        if not sha256:
            return None

        return (
            Evidence.query
            .filter_by(sha256=sha256)
            .first()
        )

    @classmethod
    def is_duplicate(cls, sha256: str) -> bool:
        """
        Returns True if evidence already exists.
        """

        return cls.find_by_sha256(sha256) is not None

    @classmethod
    def get_duplicate_details(cls, sha256: str) -> Optional[dict]:
        """
        Returns duplicate evidence details.

        Used by UI/API to show meaningful information.
        """

        evidence = cls.find_by_sha256(sha256)

        if evidence is None:
            return None

        return {

            "duplicate": True,

            "evidence_id": evidence.id,

            "case_id": evidence.case_id,

            "filename": evidence.filename,

            "original_filename": evidence.original_filename,

            "artifact_type": evidence.artifact_type,

            "parser": evidence.parser,

            "status": evidence.status,

            "sha256": evidence.sha256,

            "uploaded_at": evidence.uploaded_at

        }

    @classmethod
    def verify(cls, sha256: str) -> tuple[bool, Optional[dict]]:
        """
        Returns

        (False, None)

        or

        (True, duplicate_details)
        """

        duplicate = cls.get_duplicate_details(sha256)

        if duplicate:

            return True, duplicate

        return False, None