"""Windows Jump List (.automaticDestinations-ms / .customDestinations-ms) parser."""

import os
import struct
from datetime import datetime, timedelta

import olefile

from modules.analysis.artifact_ioc import jumplist_severity
from modules.parser.event_helpers import make_event

WINDOWS_EPOCH = datetime(1601, 1, 1)


def _filetime_to_datetime(filetime: int):
    if not filetime:
        return None
    try:
        return WINDOWS_EPOCH + timedelta(microseconds=filetime // 10)
    except (OverflowError, ValueError):
        return None


def _parse_lnk(data: bytes) -> dict:
    if len(data) < 0x4C or data[:4] != b"\x4C\x00\x00\x00":
        return {}

    flags = struct.unpack_from("<I", data, 0x14)[0]
    has_link_info = bool(flags & 0x2)
    has_name = bool(flags & 0x4)
    has_rel_path = bool(flags & 0x8)
    has_args = bool(flags & 0x20)

    offset = 0x4C
    creation = _filetime_to_datetime(struct.unpack_from("<Q", data, 0x1C)[0])
    access = _filetime_to_datetime(struct.unpack_from("<Q", data, 0x24)[0])
    modified = _filetime_to_datetime(struct.unpack_from("<Q", data, 0x2C)[0])

    if flags & 0x1:
        id_size = struct.unpack_from("<H", data, offset)[0]
        offset += 2 + id_size

    target_path = ""
    if has_link_info and offset + 4 <= len(data):
        link_info_size = struct.unpack_from("<I", data, offset)[0]
        if link_info_size > 0 and offset + link_info_size <= len(data):
            link_info = data[offset : offset + link_info_size]
            if len(link_info) >= 0x1C:
                local_base = struct.unpack_from("<I", link_info, 0x10)[0]
                if local_base and local_base + 2 <= len(link_info):
                    target_path = link_info[local_base:].split(b"\x00\x00", 1)[0].decode(
                        "utf-16-le", errors="ignore"
                    )
        offset += link_info_size

    name = ""
    if has_name and offset + 2 <= len(data):
        size = struct.unpack_from("<H", data, offset)[0]
        offset += 2
        name = data[offset : offset + size * 2].decode("utf-16-le", errors="ignore").strip("\x00")
        offset += size * 2

    rel_path = ""
    if has_rel_path and offset + 2 <= len(data):
        size = struct.unpack_from("<H", data, offset)[0]
        offset += 2
        rel_path = data[offset : offset + size * 2].decode("utf-16-le", errors="ignore").strip("\x00")
        offset += size * 2

    arguments = ""
    if has_args and offset + 2 <= len(data):
        size = struct.unpack_from("<H", data, offset)[0]
        offset += 2
        arguments = data[offset : offset + size * 2].decode("utf-16-le", errors="ignore").strip("\x00")

    return {
        "target_path": target_path or rel_path,
        "name": name,
        "arguments": arguments,
        "creation": creation,
        "access": access,
        "modified": modified,
    }


def _extract_lnk_from_stream(data: bytes) -> bytes | None:
    if len(data) >= 0x4C and data[:4] == b"\x4C\x00\x00\x00":
        return data

    marker = data.find(b"\x4C\x00\x00\x00")
    if marker != -1:
        return data[marker:]
    return None


def parse_jumplist(filepath: str) -> list[dict]:
    if not olefile.isOleFile(filepath):
        return []

    events = []
    app_id = os.path.basename(filepath).split(".")[0]

    with olefile.OleFileIO(filepath) as ole:
        for stream in ole.listdir():
            stream_name = stream[0] if isinstance(stream, (list, tuple)) else stream
            try:
                raw = ole.openstream(stream).read()
            except OSError:
                continue

            lnk_data = _extract_lnk_from_stream(raw)
            if not lnk_data:
                continue

            parsed = _parse_lnk(lnk_data)
            if not parsed.get("target_path") and not parsed.get("name"):
                continue

            target = parsed.get("target_path") or parsed.get("name")
            severity = jumplist_severity(target)
            ts = parsed.get("access") or parsed.get("creation") or parsed.get("modified")
            args = parsed.get("arguments") or ""
            details = f"AppID: {app_id} | Target: {target}"
            if args:
                details += f" | Args: {args}"

            events.append(
                make_event(
                    timestamp=ts,
                    computer=app_id,
                    channel="JumpList",
                    event_id=f"JL-{stream_name}",
                    record_id=str(stream_name),
                    rule_title="Jump List Entry",
                    rule_id="JUMPLIST_ENTRY",
                    severity=severity,
                    details=details,
                    extra_info=f"app_id={app_id}",
                )
            )

    return events
