"""Windows Registry hive artifact parser."""

import os
from datetime import datetime

from Registry import Registry

from modules.analysis.artifact_ioc import registry_severity
from modules.parser.event_helpers import make_event

FORENSIC_PATHS = (
    r"Microsoft\Windows\CurrentVersion\Run",
    r"Microsoft\Windows\CurrentVersion\RunOnce",
    r"Microsoft\Windows\CurrentVersion\Explorer\UserAssist",
    r"Microsoft\Windows\CurrentVersion\Explorer\RecentDocs",
    r"Microsoft\Windows NT\CurrentVersion\ProfileList",
    r"CurrentControlSet\Services",
    r"Microsoft\Windows\CurrentVersion\Explorer\RunMRU",
    r"Software\Microsoft\Windows\CurrentVersion\Run",
    r"Software\Microsoft\Windows\CurrentVersion\RunOnce",
)


def _key_timestamp(key) -> datetime | None:
    try:
        ts = key.timestamp()
        if isinstance(ts, datetime):
            return ts
    except (AttributeError, OSError, ValueError):
        pass
    return None


def _value_text(value) -> str:
    try:
        if value.value_type == Registry.RegSZ or value.value_type == Registry.RegExpandSZ:
            return str(value.value())
        if value.value_type == Registry.RegMultiSZ:
            return " | ".join(value.value())
        return repr(value.value())
    except Exception:
        return ""


def _walk_key(key, path_prefix: str, hive_name: str, events: list, depth: int = 0):
    if depth > 6:
        return

    current_path = f"{path_prefix}\\{key.name()}" if path_prefix else key.name()
    normalized = current_path.replace("/", "\\")

    is_forensic = any(fp.lower() in normalized.lower() for fp in FORENSIC_PATHS)

    for value in key.values():
        if value.name() in ("", "(default)") and not is_forensic:
            continue

        val_text = _value_text(value)
        if not val_text and not is_forensic:
            continue

        severity = registry_severity(normalized, val_text)
        if not is_forensic and severity == "informational":
            continue

        rule = "Registry Persistence" if "run" in normalized.lower() else "Registry Forensic Key"
        if r"\Services" in normalized:
            rule = "Registry Service Key"

        details = f"Hive: {hive_name} | Key: {normalized} | Value: {value.name()} = {val_text[:500]}"
        events.append(
            make_event(
                timestamp=_key_timestamp(key),
                computer=hive_name,
                channel="Registry",
                event_id=f"REG-{value.name()}",
                record_id=normalized,
                rule_title=rule,
                rule_id="REGISTRY_ARTIFACT",
                severity=severity,
                details=details,
                extra_info=f"value_type={value.value_type}",
            )
        )

    for subkey in key.subkeys():
        _walk_key(subkey, current_path, hive_name, events, depth + 1)


def parse_registry(filepath: str) -> list[dict]:
    hive_name = os.path.basename(filepath).upper()
    events: list[dict] = []

    try:
        reg = Registry.Registry(filepath)
    except Exception as exc:
        return [
            make_event(
                channel="Registry",
                event_id="REG-ERROR",
                rule_title="Registry Parse Error",
                rule_id="REGISTRY_ERROR",
                severity="low",
                details=f"Failed to open hive {hive_name}: {exc}",
            )
        ]

    root = reg.root()
    _walk_key(root, "", hive_name, events)

    if not events:
        events.append(
            make_event(
                timestamp=_key_timestamp(root),
                computer=hive_name,
                channel="Registry",
                event_id="REG-SUMMARY",
                rule_title="Registry Hive Parsed",
                rule_id="REGISTRY_SUMMARY",
                severity="informational",
                details=f"Hive {hive_name} parsed; no high-value forensic keys matched filters.",
            )
        )

    return events
