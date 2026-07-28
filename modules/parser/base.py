"""
Base Parser Interface

Every parser in CyberX must inherit this class.
"""

from abc import ABC
from abc import abstractmethod


class BaseParser(ABC):

    """
    Common parser interface.
    """

    name = "base"

    artifact_type = None

    @classmethod
    @abstractmethod
    def parse(
        cls,
        evidence
    ):
        """
        Parse evidence.

        Must return normalized events.
        """
        raise NotImplementedError