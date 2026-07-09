"""RAM dump / memory image analysis."""

import os
import re
import subprocess
import sys
from datetime import datetime

from modules.analysis.artifact_ioc import MEMORY_IOC_PATTERNS
from modules.parser.event_helpers import make_event

MAX_STRING_SCAN_BYTES = 64 * 1024 * 1024
PROCESS_HINTS = (
    b"powershell.exe", b"cmd.exe", b"rundll32.exe", b"mshta.exe",
    b"wscript.exe", b"mimikatz", b"lsass.exe", b"svchost.exe",
)


def _extract_strings(data: bytes, min_len: int = 6) -> set[str]:
    ascii_strings = re.findall(rb"[\x20-\x7e]{%d,}" % min_len, data)
    wide_strings = re.findall(
        (rb"(?:[\x20-\x7e]\x00){%d,}" % min_len),
        data,
    )
    results = set()
    for s in ascii_strings:
        results.add(s.decode("ascii", errors="ignore"))
    for s in wide_strings:
        try:
            results.add(s.decode("utf-16-le", errors="ignore"))
        except UnicodeDecodeError:
            continue
    return results


def _detect_dump_type(filepath: str) -> str:
    with open(filepath, "rb") as f:
        header = f.read(16)
    if header[:4] == b"PAGE":
        return "Windows Crash Dump"
    if header[:4] == b"\x4d\x5a":
        return "Hibernation / Hybrid Dump"
    if header[:8] == b"MDMPMDMP":
        return "Minidump"
    return "Raw Memory Dump"


def _run_volatility(filepath: str, output_dir: str) -> list[dict]:
    events = []
    vol_cmd = None
    for candidate in ("vol", "volatility3", "python"):
        try:
            if candidate == "python":
                probe = subprocess.run(
                    [sys.executable, "-m", "volatility3.cli", "-h"],
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                if probe.returncode == 0:
                    vol_cmd = [sys.executable, "-m", "volatility3.cli"]
                    break
            else:
                probe = subprocess.run(
                    [candidate, "-h"],
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                if probe.returncode == 0:
                    vol_cmd = [candidate]
                    break
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue

    if not vol_cmd:
        return events
## Lets add other plugins while we perform better with this as we grow! --itsmeRiF
    plugins = (
        ("windows.pslist.PsList", "Process List"),
        ("windows.netscan.NetScan", "Network Connections"),
        ("windows.malfind.Malfind", "Suspicious Memory Regions"),
    )

    for plugin, label in plugins:
        try:
            result = subprocess.run(
                [*vol_cmd, "-f", filepath, plugin],
                capture_output=True,
                text=True,
                timeout=120,
                errors="ignore",
            )
            output = (result.stdout or "") + (result.stderr or "")
            if not output.strip():
                continue

            report_path = os.path.join(output_dir, f"{plugin.replace('.', '_')}.txt")
            with open(report_path, "w", encoding="utf-8", errors="ignore") as fh:
                fh.write(output)

            line_count = len([ln for ln in output.splitlines() if ln.strip()])
            events.append(
                make_event(
                    timestamp=datetime.utcnow(),
                    computer=os.path.basename(filepath),
                    channel="Memory",
                    event_id=f"MEM-{plugin.split('.')[-1].upper()}",
                    rule_title=f"Volatility: {label}",
                    rule_id=f"VOL_{plugin.split('.')[-1].upper()}",
                    severity="medium" if "malfind" in plugin.lower() else "informational",
                    details=f"{label} extracted ({line_count} lines). Report: {report_path}",
                    extra_info=output[:2000],
                )
            )
        except (subprocess.TimeoutExpired, OSError):
            continue

    return events


def parse_memory_dump(filepath: str, output_dir: str | None = None) -> list[dict]:
    output_dir = output_dir or os.path.dirname(filepath)
    os.makedirs(output_dir, exist_ok=True)

    dump_type = _detect_dump_type(filepath)
    file_size = os.path.getsize(filepath)
    events: list[dict] = [
        make_event(
            timestamp=datetime.utcnow(),
            computer=os.path.basename(filepath),
            channel="Memory",
            event_id="MEM-INFO",
            rule_title="Memory Dump Identified",
            rule_id="MEMORY_DUMP_INFO",
            severity="informational",
            details=f"Type: {dump_type} | Size: {file_size:,} bytes",
        )
    ]

    with open(filepath, "rb") as f:
        sample = f.read(min(file_size, MAX_STRING_SCAN_BYTES))

    strings = _extract_strings(sample)
    seen_rules = set()

    for text in strings:
        lower = text.lower()
        for needle, severity, rule_id in MEMORY_IOC_PATTERNS:
            if needle.lower() not in lower:
                continue
            if rule_id in seen_rules:
                break
            seen_rules.add(rule_id)
            events.append(
                make_event(
                    timestamp=datetime.utcnow(),
                    channel="Memory",
                    event_id=f"IOC-{rule_id}",
                    rule_title="Memory IOC Match",
                    rule_id=rule_id,
                    severity=severity,
                    details=f"Pattern '{needle}' found in memory strings: {text[:300]}",
                )
            )
            break

    for hint in PROCESS_HINTS:
        if hint.lower() in sample.lower():
            name = hint.decode("ascii", errors="ignore")
            events.append(
                make_event(
                    timestamp=datetime.utcnow(),
                    channel="Memory",
                    event_id=f"PROC-{name.upper()}",
                    rule_title="Process Name String in Memory",
                    rule_id="MEMORY_PROCESS_STRING",
                    severity="medium" if name.lower() in ("mimikatz", "powershell.exe") else "informational",
                    details=f"Process-related string '{name}' observed in memory sample.",
                )
            )

    events.extend(_run_volatility(filepath, output_dir))
    return events
