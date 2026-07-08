"""Route evidence files to the correct artifact parser."""

import os

from modules.parser.hayabusa import run_hayabusa
from modules.parser.jumplist import parse_jumplist
from modules.parser.memory import parse_memory_dump
from modules.parser.prefetch import parse_prefetch
from modules.parser.registry_parser import parse_registry

ARTIFACT_TYPES = {
    "evtx": {
        "label": "Windows Event Log (.evtx)",
        "extensions": {".evtx"},
    },
    "prefetch": {
        "label": "Prefetch (.pf)",
        "extensions": {".pf"},
    },
    "jumplist": {
        "label": "Jump List (.automaticDestinations-ms / .customDestinations-ms)",
        "extensions": {".automaticdestinations-ms", ".customdestinations-ms"},
    },
    "registry": {
        "label": "Registry Hive (SYSTEM/SOFTWARE/SAM/NTUSER/etc.)",
        "extensions": {".dat", ".hiv", ".registry"},
    },
    "memory": {
        "label": "RAM Dump (.raw/.mem/.dmp/.vmem)",
        "extensions": {".raw", ".mem", ".dmp", ".vmem", ".img"},
    },
}

REGISTRY_HIVE_NAMES = {
    "system", "software", "sam", "security", "ntuser.dat", "usrclass.dat",
    "amcache.hve", "default", "UsrClass.dat", "NTUSER.DAT",
}


def detect_artifact_type(filename: str, requested: str | None = None) -> str:
    if requested and requested in ARTIFACT_TYPES:
        return requested

    lower = filename.lower()
    _, ext = os.path.splitext(lower)

    if ext in ARTIFACT_TYPES["prefetch"]["extensions"]:
        return "prefetch"
    if ext in ARTIFACT_TYPES["jumplist"]["extensions"]:
        return "jumplist"
    if ext in ARTIFACT_TYPES["evtx"]["extensions"]:
        return "evtx"
    if ext in ARTIFACT_TYPES["memory"]["extensions"]:
        return "memory"

    base = os.path.basename(lower)
    if ext in {".dat", ".hiv"} or base in REGISTRY_HIVE_NAMES or "ntuser" in base:
        return "registry"

    return requested or "evtx"


def parse_artifact(
    artifact_type: str,
    filepath: str,
    output_dir: str,
    tool_path: str | None = None,
) -> list[dict]:
    artifact_type = detect_artifact_type(os.path.basename(filepath), artifact_type)

    if artifact_type == "evtx":
        if not tool_path:
            raise FileNotFoundError("Hayabusa tool path is required for EVTX analysis")
        return run_hayabusa(filepath, output_dir, tool_path)

    if artifact_type == "prefetch":
        return parse_prefetch(filepath)

    if artifact_type == "jumplist":
        return parse_jumplist(filepath)

    if artifact_type == "registry":
        return parse_registry(filepath)

    if artifact_type == "memory":
        return parse_memory_dump(filepath, output_dir)

    raise ValueError(f"Unsupported artifact type: {artifact_type}")
