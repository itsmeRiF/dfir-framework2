"""
CyberX DFIR Parser Manager

Controls parser execution lifecycle.
"""

import logging

from modules.parser.router import ParserRouter
from modules.parser.exceptions import (
    ParserExecutionError
)


logger = logging.getLogger(__name__)


class ParserManager:


    @classmethod
    def process(
        cls,
        evidence
    ):

        try:

            parser = ParserRouter.get(
                evidence.artifact_type
            )

            logger.info(
                "Using parser %s for evidence %s",
                parser.name,
                evidence.id
            )


            result = parser.parse(
                evidence
            )


            return result


        except Exception as exc:

            logger.exception(
                "Parser execution failed."
            )

            raise ParserExecutionError(
                str(exc)
            )