"""
CyberX DFIR Framework
Evidence Module Exceptions

Author : CyberX DFIR
"""

from typing import Optional


class EvidenceError(Exception):
    """
    Base exception for all Evidence related errors.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ValidationError(EvidenceError):
    """
    Raised when uploaded evidence fails validation.
    """

    pass


class DuplicateEvidenceError(EvidenceError):
    """
    Raised when an evidence file already exists.
    """

    def __init__(
        self,
        message: str,
        sha256: Optional[str] = None,
        evidence_id: Optional[int] = None
    ):
        super().__init__(message)

        self.sha256 = sha256
        self.evidence_id = evidence_id


class StorageError(EvidenceError):
    """
    Raised when evidence cannot be stored.
    """

    pass


class HashingError(EvidenceError):
    """
    Raised when hashing fails.
    """

    pass


class DetectionError(EvidenceError):
    """
    Raised when artifact detection fails.
    """

    pass


class QueueError(EvidenceError):
    """
    Raised when parser queue operation fails.
    """

    pass


class ParserError(EvidenceError):
    """
    Raised when parser execution fails.
    """

    pass