"""
CyberX DFIR EVTX Parser
"""

from modules.parser.base import BaseParser
from modules.parser.engines.hayabusa import HayabusaEngine
from modules.parser.normalizer import EventNormalizer


class EVTXParser(BaseParser):

    name = "EVTX Parser"

    artifact_type = "evtx"


    @classmethod
    def parse(
        cls,
        evidence
    ):

        raw_events = HayabusaEngine.parse(
            evidence.filepath
        )

        events = []

        for event in raw_events:

            normalized = EventNormalizer.normalize(
                event
            )

            events.append(
                normalized
            )

        return events