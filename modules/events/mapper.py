"""
Maps normalized parser output
to CyberX Event model.
"""

from datetime import datetime


SEVERITY_MAP = {

    "critical": "critical",
    "crit": "critical",

    "high": "high",

    "medium": "medium",
    "med": "medium",

    "low": "low",

    "informational": "informational",
    "information": "informational",
    "info": "informational"

}


class EventMapper:


    @staticmethod
    def normalize_severity(severity):

        if not severity:
            return "informational"

        value = str(
            severity
        ).strip().lower()

        return SEVERITY_MAP.get(
            value,
            "informational"
        )



    @staticmethod
    def map(
        event,
        case_id
    ):

        timestamp = event.get(
            "timestamp"
        )


        parsed_time = None


        if timestamp:

            try:

                if isinstance(timestamp, datetime):

                    parsed_time = timestamp

                else:

                    parsed_time = datetime.fromisoformat(
                        str(timestamp).replace(
                            "Z",
                            "+00:00"
                        )
                    )

            except Exception:

                parsed_time = None



        raw = event.get(
            "raw",
            {}
        )


        if raw is None:

            raw = {}



        return {


            "case_id": case_id,


            "timestamp": parsed_time,


            "computer": event.get(
                "computer"
            ),



            "channel": (

                event.get("source")

                or

                event.get("channel")

            ),



            "event_id": str(

                event.get(
                    "event_id",
                    ""
                )

            ),



            "record_id": raw.get(
                "RecordID"
            ),



            "rule_title": (

                event.get("rule_title")

                or

                event.get("RuleTitle")

                or

                event.get("message")

                or

                "Unknown"

            ),



            "rule_id": event.get(
                "rule_id"
            ),



            "severity": EventMapper.normalize_severity(

                event.get(
                    "severity"
                )

            ),



            "details": (

                event.get("details")

                or

                event.get("message")

            ),



            "extra_info": raw.get(
                "ExtraFieldInfo"
            )

        }