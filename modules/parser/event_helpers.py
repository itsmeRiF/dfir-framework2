"""Normalize parsed artifact records into the framework event dict format."""


def make_event(
    *,
    timestamp=None,
    computer="",
    channel="",
    event_id="",
    record_id="",
    rule_title="",
    rule_id="",
    severity="informational",
    details="",
    extra_info="",
):
    return {
        "timestamp": timestamp,
        "computer": computer or "",
        "channel": channel or "",
        "event_id": str(event_id or ""),
        "record_id": str(record_id or ""),
        "rule_title": rule_title or "",
        "rule_id": rule_id or "",
        "severity": severity or "informational",
        "details": details or "",
        "extra_info": extra_info or "",
    }
