"""
CyberX Event Importer

Stores normalized forensic events
into database.
"""

import logging

from database.db import db
from models.event import Event

from modules.events.mapper import EventMapper


logger = logging.getLogger(__name__)


class EventImporter:


    @classmethod
    def import_events(
        cls,
        events,
        case_id
    ):

        if not events:

            return 0


        records = []


        for event in events:

            mapped = EventMapper.map(
                event,
                case_id
            )

            records.append(
                Event(
                    **mapped
                )
            )


        try:

            db.session.bulk_save_objects(
                records
            )

            db.session.commit()


            logger.info(
                "%s events imported for case %s",
                len(records),
                case_id
            )


            return len(records)


        except Exception:

            db.session.rollback()

            logger.exception(
                "Event import failed"
            )

            raise