from modules.parser.registry import register_parsers
from modules.parser.router import ParserRouter


register_parsers()


parser = ParserRouter.get(
    "evtx"
)


print(
    parser.name
)

print(
    parser.artifact_type
)