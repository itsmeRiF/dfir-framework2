"""
CyberX DFIR Evidence Processing Worker

Handles post-upload evidence processing.
"""

import logging

from modules.evidence.queue import (
    EvidenceQueue
)

from modules.parser.manager import (
    ParserManager
)

from modules.events.importer import (
    EventImporter
)


logger = logging.getLogger(__name__)


class EvidenceWorker:


    @classmethod
    def process(
        cls,
        evidence
    ):

        try:

            logger.info(
                "Processing evidence %s",
                evidence.id
            )


            # Mark running

            EvidenceQueue.start(
                evidence
            )


            # Parse artifact

            events = ParserManager.process(
                evidence
            )


            logger.info(
                "Parser returned %s events",
                len(events)
            )


            # Store events

            imported = EventImporter.import_events(
                events,
                evidence.case_id
            )


            logger.info(
                "%s events imported",
                imported
            )


            # Complete

            EvidenceQueue.complete(
                evidence
            )


            return {

                "success": True,

                "evidence_id": evidence.id,

                "events": imported

            }


        except Exception as exc:


            logger.exception(
                "Evidence processing failed"
            )


            EvidenceQueue.fail(
                evidence,
                str(exc)
            )


            raise