"""
CyberX DFIR Framework
modules/evidence/service.py

Main orchestration layer for Evidence Upload.

Workflow

Validate
    ↓
Detect Artifact
    ↓
Store File
    ↓
Calculate Hashes
    ↓
Duplicate Check
    ↓
Create Evidence Record
    ↓
Queue Parser
"""

from __future__ import annotations

import logging
from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError
from flask import current_app

from database.db import db
from models.evidence import Evidence

from modules.evidence.validator import EvidenceValidator
from modules.evidence.detector import EvidenceDetector
from modules.evidence.storage import EvidenceStorage
from modules.evidence.duplicate import DuplicateChecker
from modules.evidence.queue import (
    EvidenceQueue,
    QueueStatus
)

from modules.evidence.hashing import calculate_hashes

from modules.evidence.exceptions import (
    ValidationError,
    DuplicateEvidenceError,
    StorageError,
    QueueError
)

logger = logging.getLogger(__name__)


class EvidenceService:

    @classmethod
    def upload(
        cls,
        *,
        file,
        case_id: int
    ) -> dict:

        storage = None

        try:

            logger.info(
                "Starting upload for case %s",
                case_id
            )
            
            metadata = cls._validate_upload(file)

            artifact = cls._detect_artifact(
                metadata
            )

            storage = cls._store_evidence(
                file=file,
                case_id=case_id,
                metadata=metadata,
                artifact=artifact
            )
            
            logger.info(
                "Stored evidence at %s",
                storage["filepath"]
            )

            # ----------------------------------------
            # Calculate hashes
            # ----------------------------------------

            hashes = cls._calculate_hashes(
                storage["filepath"]
            )

            # ----------------------------------------
            # Duplicate detection
            # ----------------------------------------

            duplicate = cls._check_duplicate(
                hashes["sha256"]
            )

            if duplicate:

                cls._cleanup_file(
                    storage["filepath"]
                )

                raise DuplicateEvidenceError(
                    message="Evidence already exists.",
                    sha256=duplicate["sha256"],
                    evidence_id=duplicate["evidence_id"]
                )

            # ----------------------------------------
            # Create DB record
            # ----------------------------------------

            evidence = cls._create_record(

                case_id=case_id,
                storage=storage,
                metadata=metadata,
                artifact=artifact,
                hashes=hashes
            )
            

            db.session.add(
                evidence
            )

            db.session.commit()

            logger.info(
                "Evidence #%s inserted.",
                evidence.id
            )

            # ----------------------------------------
            # Queue
            # ----------------------------------------

            cls._queue_parser(
                evidence
            )

            logger.info(
                "Evidence queued."
            )

            return cls._response(
                evidence
            )






        except ValidationError:

            raise

        except DuplicateEvidenceError:

            raise

        except StorageError:

            db.session.rollback()

            raise

        except QueueError:

            db.session.rollback()

            raise

        except SQLAlchemyError:

            db.session.rollback()

            if storage:

                cls._cleanup_file(
                    storage["filepath"]
                )

            logger.exception(
                "Database transaction failed."
            )

            raise

        except Exception:

            db.session.rollback()

            if storage:

                cls._cleanup_file(
                    storage["filepath"]
                )

            logger.exception(
                "Unexpected upload failure."
            )

            raise
    
    
    
    @staticmethod
    def _queue_parser(evidence):

        EvidenceQueue.queue(
            evidence
        )
    
    
    @staticmethod
    def _create_record(
        case_id,
        storage,
        metadata,
        artifact,
        hashes
    ):

        return Evidence(

            case_id=case_id,

            filename=storage["filename"],

            original_filename=metadata[
                "original_filename"
            ],

            filepath=storage["filepath"],

            filesize=metadata["filesize"],

            artifact_type=artifact[
                "artifact_type"
            ],

            parser=artifact["parser"],

            status=QueueStatus.QUEUED,

            md5=hashes["md5"],

            sha1=hashes["sha1"],

            sha256=hashes["sha256"],

            sha512=hashes["sha512"]

        )
    
    
    
    @staticmethod
    def _check_duplicate(sha256):

        return DuplicateChecker.get_duplicate_details(
            sha256
        )
    
    
    @staticmethod
    def _calculate_hashes(filepath):

        return calculate_hashes(
            filepath
        )
    
    
    @staticmethod
    def _store_evidence(
        file,
        case_id,
        metadata,
        artifact
    ):

        return EvidenceStorage.save(

            file=file,

            upload_root=current_app.config[
                "UPLOAD_FOLDER"
            ],

            case_id=case_id,

            artifact_type=artifact[
                "artifact_type"
            ],

            extension=metadata[
                "extension"
            ]

        )
    
    
    
    @staticmethod
    def _detect_artifact(metadata):

        return EvidenceDetector.detect(
            metadata["filename"]
        )
    
    
    
    @staticmethod
    def _validate_upload(file):

        return EvidenceValidator.validate(
            file
        )
    
    
    
    
    @staticmethod
    def _cleanup_file(
        filepath: str | None
    ) -> None:
        """
        Remove uploaded file if transaction fails.
        """

        if not filepath:
            return

        try:

            path = Path(filepath)

            if path.exists():

                path.unlink()

                logger.warning(
                    "Removed orphan file: %s",
                    filepath
                )

        except Exception:

            logger.exception(
                "Unable to cleanup orphan evidence."
            )

    @staticmethod
    def _response(
        evidence: Evidence
    ) -> dict:
        """
        Standard upload response.
        """

        return {

            "success": True,

            "message": "Evidence uploaded successfully.",

            "evidence": {

                "id": evidence.id,

                "case_id": evidence.case_id,

                "filename": evidence.original_filename,

                "stored_filename": evidence.filename,

                "artifact_type": evidence.artifact_type,

                "parser": evidence.parser,

                "status": evidence.status,

                "filesize": evidence.filesize,

                "md5": evidence.md5,

                "sha1": evidence.sha1,

                "sha256": evidence.sha256,

                "sha512": evidence.sha512,

                "uploaded_at": (
                    evidence.uploaded_at.isoformat()
                    if evidence.uploaded_at
                    else None
                )

            }

        }    