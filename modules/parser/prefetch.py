"""Windows Prefetch (.pf) artifact parser."""

import os
import struct
from datetime import datetime, timedelta

from modules.analysis.artifact_ioc import prefetch_severity
from modules.parser.event_helpers import make_event

WINDOWS_EPOCH = datetime(1601, 1, 1)


def _filetime_to_datetime(filetime: int):
    if not filetime:
        return None
    try:
        return WINDOWS_EPOCH + timedelta(microseconds=filetime // 10)
    except (OverflowError, ValueError):
        return None


def _decompress_mam(data: bytes) -> bytes | None:
    """Decompress Win10+ MAM-compressed prefetch using Windows RtlDecompressBufferEx."""
    if len(data) < 8 or data[:3] != b"MAM":
        return None

    try:
        import ctypes
        from ctypes import wintypes

        ntdll = ctypes.WinDLL("ntdll")
        decompress = ntdll.RtlDecompressBufferEx
        decompress.argtypes = [
            wintypes.USHORT,
            ctypes.POINTER(ctypes.c_ubyte),
            wintypes.ULONG,
            ctypes.POINTER(ctypes.c_ubyte),
            wintypes.ULONG,
            ctypes.POINTER(wintypes.ULONG),
            ctypes.c_void_p,
        ]
        decompress.restype = wintypes.ULONG

        uncompressed_size = struct.unpack_from("<I", data, 4)[0]
        src = (ctypes.c_ubyte * len(data))(*data)
        dst = (ctypes.c_ubyte * uncompressed_size)()
        final_size = wintypes.ULONG(0)

        status = decompress(
            4,  # COMPRESSION_FORMAT_XPRESS_HUFF
            dst,
            uncompressed_size,
            src,
            len(data),
            ctypes.byref(final_size),
            None,
        )
        if status == 0:
            return bytes(dst[: final_size.value])
    except OSError:
        pass
    return None


def _read_utf16(data: bytes, offset: int, max_chars: int = 260) -> str:
    end = offset + max_chars * 2
    chunk = data[offset:end]
    try:
        return chunk.decode("utf-16-le").split("\x00", 1)[0].strip()
    except UnicodeDecodeError:
        return ""


def _parse_scca(data: bytes, source_name: str) -> dict | None:
    if len(data) < 84 or data[:4] != b"SCCA":
        return None

    version = struct.unpack_from("<I", data, 4)[0]
    exec_name = _read_utf16(data, 16)

    run_count = 0
    last_run = None
    file_refs = []

    if version >= 30:
        run_count = struct.unpack_from("<I", data, 0xD0)[0]
        for i in range(8):
            ft = struct.unpack_from("<Q", data, 0x80 + i * 8)[0]
            ts = _filetime_to_datetime(ft)
            if ts and (last_run is None or ts > last_run):
                last_run = ts
    elif version >= 26:
        run_count = struct.unpack_from("<I", data, 0x98)[0]
        ft = struct.unpack_from("<Q", data, 0x78)[0]
        last_run = _filetime_to_datetime(ft)
    else:
        run_count = struct.unpack_from("<I", data, 0x98)[0] if len(data) > 0x9C else 0

    if version >= 17 and len(data) > 0x64:
        file_count = struct.unpack_from("<I", data, 0x60)[0]
        offset = struct.unpack_from("<I", data, 0x64)[0]
        for _ in range(min(file_count, 128)):
            if offset + 4 > len(data):
                break
            str_off = struct.unpack_from("<I", data, offset)[0]
            name = _read_utf16(data, str_off, 128) if str_off < len(data) else ""
            if name:
                file_refs.append(name)
            offset += 4

    return {
        "executable": exec_name or os.path.basename(source_name).rsplit("-", 1)[0],
        "version": version,
        "run_count": run_count,
        "last_run": last_run,
        "files_accessed": file_refs[:20],
        "source": source_name,
    }


def parse_prefetch(filepath: str) -> list[dict]:
    with open(filepath, "rb") as f:
        raw = f.read()

    if raw[:3] == b"MAM":
        decompressed = _decompress_mam(raw)
        if decompressed:
            raw = decompressed

    record = _parse_scca(raw, os.path.basename(filepath))
    if not record:
        return []

    exe = record["executable"]
    severity = prefetch_severity(exe)
    files_preview = ", ".join(record["files_accessed"][:5])
    details = (
        f"Executable: {exe} | Runs: {record['run_count']} | "
        f"Last Run: {record['last_run'] or 'Unknown'}"
    )
    if files_preview:
        details += f" | Files: {files_preview}"

    return [
        make_event(
            timestamp=record["last_run"],
            computer=os.path.splitext(os.path.basename(filepath))[0],
            channel="Prefetch",
            event_id=f"PF-{exe.upper()}",
            record_id=os.path.basename(filepath),
            rule_title="Prefetch Execution Record",
            rule_id="PREFETCH_EXEC",
            severity=severity,
            details=details,
            extra_info=f"version={record['version']};files={len(record['files_accessed'])}",
        )
    ]
