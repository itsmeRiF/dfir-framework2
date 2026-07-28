"""
CyberX DFIR Event Normalizer
"""


class EventNormalizer:


    @staticmethod
    def normalize(
        event
    ):

        return {

            "timestamp": event.get(
                "Timestamp"
            ),

            "source": event.get(
                "Channel"
            ),

            "artifact": "evtx",

            "computer": event.get(
                "Computer"
            ),

            "user": EventNormalizer.extract_user(
                event.get("Details")
            ),

            "event_id": event.get(
                "EventID"
            ),

            "severity": event.get(
                "Level",
                "INFO"
            ),

            "message": event.get(
                "RuleTitle"
            ),

            "details": event.get(
                "Details"
            ),

            "rule_id": event.get(
                "RuleID"
            ),

            "raw": event

        }


    @staticmethod
    def extract_user(
        details
    ):

        if not details:
            return None


        for item in details.split("¦"):

            item = item.strip()

            if item.startswith(
                "SrcUser:"
            ):

                return item.replace(
                    "SrcUser:",
                    ""
                ).strip()


        return None