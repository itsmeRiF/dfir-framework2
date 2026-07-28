"""
Parser Router
"""

from modules.parser.exceptions import (
    ParserNotFound
)


class ParserRouter:

    _parsers = {}

    @classmethod
    def register(
        cls,
        parser
    ):

        cls._parsers[
            parser.artifact_type
        ] = parser

    @classmethod
    def get(
        cls,
        artifact_type
    ):

        parser = cls._parsers.get(
            artifact_type
        )

        if parser is None:

            raise ParserNotFound(
                f"No parser registered for "
                f"{artifact_type}"
            )

        return parser