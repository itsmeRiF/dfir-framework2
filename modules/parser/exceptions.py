"""
Parser Exceptions
"""


class ParserError(Exception):
    """
    Base parser exception.
    """


class ParserNotFound(ParserError):
    """
    No parser available.
    """


class ParserExecutionError(ParserError):
    """
    Parser failed.
    """