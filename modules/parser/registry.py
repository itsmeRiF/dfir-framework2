"""
CyberX DFIR Parser Registry

Registers all available parsers.
"""

from modules.parser.router import ParserRouter


def register_parsers():

    from modules.parser.evtx import EVTXParser


    ParserRouter.register(
        EVTXParser
    )