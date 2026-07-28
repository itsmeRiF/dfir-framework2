"""
CyberX DFIR Framework
Evidence Queue Manager

Version 1.0

Simple queue manager.
Designed to be replaced later by Celery/Redis
without changing the service layer.
"""

from __future__ import annotations

from datetime import datetime

from database.db import db
from models.evidence import Evidence

from modules.evidence.exceptions import QueueError


class QueueStatus:

    QUEUED = "Queued"

    RUNNING = "Running"

    COMPLETED = "Completed"

    FAILED = "Failed"


class EvidenceQueue:

    @staticmethod
    def queue(evidence: Evidence) -> None:
        """
        Queue newly uploaded evidence.
        """

        try:

            evidence.status = QueueStatus.QUEUED

            db.session.commit()

        except Exception as ex:

            db.session.rollback()

            raise QueueError(
                f"Unable to queue evidence: {ex}"
            )

    @staticmethod
    def start(evidence: Evidence) -> None:
        """
        Mark evidence as processing.
        """

        try:

            evidence.status = QueueStatus.RUNNING

            db.session.commit()

        except Exception as ex:

            db.session.rollback()

            raise QueueError(
                f"Unable to start queue: {ex}"
            )

    @staticmethod
    def complete(evidence: Evidence) -> None:
        """
        Mark evidence processing completed.
        """

        try:

            evidence.status = QueueStatus.COMPLETED

            db.session.commit()

        except Exception as ex:

            db.session.rollback()

            raise QueueError(
                f"Unable to complete queue: {ex}"
            )

    @staticmethod
    def fail(
        evidence: Evidence,
        reason: str | None = None
    ) -> None:
        """
        Mark evidence processing failed.
        """

        try:

            evidence.status = QueueStatus.FAILED

            db.session.commit()

        except Exception as ex:

            db.session.rollback()

            raise QueueError(
                f"Unable to fail queue: {ex}"
            )