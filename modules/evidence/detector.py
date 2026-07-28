"""
CyberX DFIR Framework
Evidence Artifact Detector

Automatically detects evidence type
and assigns the appropriate parser.
"""

from pathlib import Path


class EvidenceDetector:

    FILE_SIGNATURES = {

        # -----------------------
        # Event Logs
        # -----------------------

        ".evtx": ("EVTX", "Hayabusa"),
        ".evt": ("EVTX", "Hayabusa"),

        # -----------------------
        # Memory
        # -----------------------

        ".raw": ("Memory", "Volatility3"),
        ".mem": ("Memory", "Volatility3"),
        ".dmp": ("Memory", "Volatility3"),
        ".bin": ("Memory", "Volatility3"),

        # -----------------------
        # Disk Images
        # -----------------------

        ".dd": ("Disk Image", "Future"),
        ".001": ("Disk Image", "Future"),
        ".e01": ("Disk Image", "Future"),
        ".aff4": ("Disk Image", "Future"),
        ".vhd": ("Disk Image", "Future"),
        ".vhdx": ("Disk Image", "Future"),

        # -----------------------
        # Network
        # -----------------------

        ".pcap": ("Network Capture", "PCAP"),
        ".pcapng": ("Network Capture", "PCAP"),

        # -----------------------
        # Registry
        # -----------------------

        ".reg": ("Registry", "Registry"),

        ".hve": ("Registry", "Registry")
    }

    REGISTRY_FILES = {

        "SAM",
        "SYSTEM",
        "SOFTWARE",
        "SECURITY",
        "DEFAULT",
        "NTUSER.DAT",
        "USRCLASS.DAT",
        "AMCACHE.HVE"
    }

    SPECIAL_FILES = {

        "$MFT": ("MFT", "MFTECmd"),

        "$LOGFILE": ("LogFile", "MFTECmd"),

        "$J": ("USN Journal", "MFTECmd"),

        "$USNJRNL": ("USN Journal", "MFTECmd")
    }

    @classmethod
    def detect(
        cls,
        filename: str
    ) -> dict:

        name = Path(filename).name

        upper = name.upper()

        # ---------------------
        # Registry Names
        # ---------------------

        if upper in cls.REGISTRY_FILES:

            return {

                "artifact_type": "Registry",

                "parser": "Registry"

            }

        # ---------------------
        # Special NTFS Files
        # ---------------------

        if upper in cls.SPECIAL_FILES:

            artifact, parser = cls.SPECIAL_FILES[upper]

            return {

                "artifact_type": artifact,

                "parser": parser

            }

        extension = Path(filename).suffix.lower()

        if extension in cls.FILE_SIGNATURES:

            artifact, parser = cls.FILE_SIGNATURES[extension]

            return {

                "artifact_type": artifact,

                "parser": parser

            }

        return {

            "artifact_type": "Unknown",

            "parser": None

        }