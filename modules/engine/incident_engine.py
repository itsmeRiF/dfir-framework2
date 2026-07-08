from collections import defaultdict
from datetime import timedelta


def build_incidents(events):
    """
    Convert raw events → incidents (EVTX + artifact analysis).
    """
    incidents = []

    # --- GROUP 1: Brute Force Detection (EventID 4625) ---
    failed_logons = [e for e in events if e["event_id"] == "4625"]

    if len(failed_logons) >= 5:
        timestamps = [e["timestamp"] for e in failed_logons if e["timestamp"]]
        incidents.append({
            "title": "Possible Brute Force Attack",
            "severity": "high",
            "rule": "4625_Failure_Cluster",
            "event_count": len(failed_logons),
            "first_seen": min(timestamps) if timestamps else None,
            "last_seen": max(timestamps) if timestamps else None,
        })

    # --- GROUP 2: Privilege escalation (4624 + 4672) ---
    priv_events = [e for e in events if e["event_id"] in ["4624", "4672"]]

    if len(priv_events) >= 3:
        timestamps = [e["timestamp"] for e in priv_events if e["timestamp"]]
        incidents.append({
            "title": "Privilege Activity Detected",
            "severity": "medium",
            "rule": "Privilege_Escalation_Chain",
            "event_count": len(priv_events),
            "first_seen": min(timestamps) if timestamps else None,
            "last_seen": max(timestamps) if timestamps else None,
        })

    # --- GROUP 3: Credential access patterns ---
    cred_events = [e for e in events if "Credential" in e.get("rule_title", "")]

    if len(cred_events) >= 3:
        timestamps = [e["timestamp"] for e in cred_events if e["timestamp"]]
        incidents.append({
            "title": "Credential Access Activity",
            "severity": "medium",
            "rule": "Credential_Manager_Activity",
            "event_count": len(cred_events),
            "first_seen": min(timestamps) if timestamps else None,
            "last_seen": max(timestamps) if timestamps else None,
        })

    # --- GROUP 4: Suspicious Prefetch (LOLbins) ---
    prefetch_hits = [
        e for e in events
        if e.get("channel") == "Prefetch" and e.get("severity") in ("high", "critical")
    ]
    if prefetch_hits:
        timestamps = [e["timestamp"] for e in prefetch_hits if e["timestamp"]]
        incidents.append({
            "title": "Suspicious Program Execution (Prefetch)",
            "severity": "high",
            "rule": "Prefetch_LOLBin",
            "event_count": len(prefetch_hits),
            "first_seen": min(timestamps) if timestamps else None,
            "last_seen": max(timestamps) if timestamps else None,
        })

    # --- GROUP 5: Suspicious JumpList entries ---
    jumplist_hits = [
        e for e in events
        if e.get("channel") == "JumpList" and e.get("severity") in ("high", "critical")
    ]
    if len(jumplist_hits) >= 2:
        timestamps = [e["timestamp"] for e in jumplist_hits if e["timestamp"]]
        incidents.append({
            "title": "Suspicious User Activity (JumpList)",
            "severity": "high",
            "rule": "JumpList_Suspicious_Target",
            "event_count": len(jumplist_hits),
            "first_seen": min(timestamps) if timestamps else None,
            "last_seen": max(timestamps) if timestamps else None,
        })

    # --- GROUP 6: Registry persistence ---
    registry_hits = [
        e for e in events
        if e.get("channel") == "Registry" and e.get("severity") in ("high", "medium")
    ]
    if registry_hits:
        timestamps = [e["timestamp"] for e in registry_hits if e["timestamp"]]
        incidents.append({
            "title": "Registry Persistence / Autostart Activity",
            "severity": "high",
            "rule": "Registry_Persistence",
            "event_count": len(registry_hits),
            "first_seen": min(timestamps) if timestamps else None,
            "last_seen": max(timestamps) if timestamps else None,
        })

    # --- GROUP 7: Memory IOCs ---
    memory_hits = [
        e for e in events
        if e.get("channel") == "Memory" and e.get("severity") in ("high", "critical")
    ]
    if memory_hits:
        timestamps = [e["timestamp"] for e in memory_hits if e["timestamp"]]
        incidents.append({
            "title": "Memory IOC / Malware Indicator",
            "severity": "critical",
            "rule": "Memory_IOC",
            "event_count": len(memory_hits),
            "first_seen": min(timestamps) if timestamps else None,
            "last_seen": max(timestamps) if timestamps else None,
        })

    return incidents
