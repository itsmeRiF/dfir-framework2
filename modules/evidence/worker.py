"""
CyberX DFIR Framework
Evidence Processing Worker
"""

from __future__ import annotations

import os
import logging

from flask import current_app

from database.db import db

from models.evidence import Evidence

from modules.evidence.queue import (
    EvidenceQueue
)

from modules.parser.artifact_router import (
    parse_artifact
)

from modules.events.importer import (
    EventImporter
)

from modules.memory.importer import (
    MemoryImporter
)


logger = logging.getLogger(__name__)


class EvidenceWorker:


    @classmethod
    def process(
        cls,
        evidence_id: int
    ):

        evidence = Evidence.query.get_or_404(
            evidence_id
        )


        output_dir = os.path.join(

            current_app.config.get(
                "OUTPUT_FOLDER",
                "output"
            ),

            "evidence",

            str(evidence.case_id),

            str(evidence.id)

        )


        os.makedirs(
            output_dir,
            exist_ok=True
        )


        try:

            logger.info(
                "Processing evidence %s",
                evidence.id
            )


            # ----------------------------------
            # Queue -> Running
            # ----------------------------------

            EvidenceQueue.start(
                evidence
            )


            # ----------------------------------
            # Artifact Type
            # ----------------------------------

            artifact_type = (

                evidence.artifact_type or ""

            ).lower()


            logger.info(
                "Artifact type: %s",
                artifact_type
            )


            # ----------------------------------
            # Tool Path
            # ----------------------------------

            tool_path = current_app.config.get(
                "HAYABUSA_PATH"
            )


            logger.info(
                "Tool path: %s",
                tool_path
            )


            # ----------------------------------
            # Parse Artifact
            # ----------------------------------

            results = parse_artifact(

                artifact_type,

                evidence.filepath,

                output_dir,

                tool_path

            )


            logger.info(

                "Parser returned %s records",

                len(results)

            )


            # ----------------------------------
            # Memory Processing
            # ----------------------------------

            memory_summary = None


            if artifact_type == "memory":


                memory_summary = MemoryImporter.import_memory(

                    evidence.case_id,

                    output_dir

                )


                logger.info(

                    "Memory analysis completed: %s",

                    memory_summary

                )
                        
            # ----------------------------------
            # Import Events
            # Only EVTX goes to Event Logs
            # ----------------------------------

            imported = 0


            if artifact_type == "evtx":

                imported = EventImporter.import_events(

                    results,

                    evidence.case_id,

                    evidence.id

                )



            logger.info(

                "%s events imported",

                imported

            )


            # ----------------------------------
            # Complete
            # ----------------------------------

            EvidenceQueue.complete(
                evidence
            )


            evidence.completed_at = db.func.now()

            db.session.commit()



            return {

                "success": True,

                "evidence_id": evidence.id,

                "events": imported,

                "memory": memory_summary,

                "status": evidence.status

            }



        except Exception as ex:


            logger.exception(
                "Evidence processing failed"
            )


            EvidenceQueue.fail(

                evidence,

                str(ex)

            )


            evidence.error_message = str(ex)


            db.session.commit()


            raise