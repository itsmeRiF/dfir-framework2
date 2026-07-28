from modules.parser.registry import register_parsers
from modules.parser.manager import ParserManager


class FakeEvidence:

    id = 1

    artifact_type = "evtx"

    filepath = r"sample_memory\Security.evtx"



register_parsers()


evidence = FakeEvidence()


events = ParserManager.process(
    evidence
)


print(events)