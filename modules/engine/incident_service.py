"""
CyberX DFIR
Incident Generation Service
"""

from database.db import db

from models.incident import Incident
from modules.engine.incident_engine import build_incidents


class IncidentService:


    @staticmethod
    def generate(
        case_id,
        events
    ):

        detected = build_incidents(
            events
        )


        created = []


        for item in detected:


            incident = Incident(

                case_id=case_id,

                title=item.get(
                    "title"
                ),

                severity=item.get(
                    "severity"
                ),

                rule=item.get(
                    "rule"
                ),

                event_count=item.get(
                    "event_count",
                    0
                ),

                first_seen=item.get(
                    "first_seen"
                ),

                last_seen=item.get(
                    "last_seen"
                )

            )


            db.session.add(
                incident
            )


            created.append(
                incident
            )


        db.session.commit()


        return created