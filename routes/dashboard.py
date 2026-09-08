from flask import Blueprint, render_template
from sqlalchemy import func

from database.db import db

from models.case import Case
from models.evidence import Evidence
from models.event import Event

from utils import case_stats
from utils.timezone import format_ist, to_ist

dashboard_bp = Blueprint("dashboard", __name__)


# Severity order (highest first) + the colour / icon used to render it.
SEVERITY_META = [
    ("critical",      "#dc3545", "bi-exclamation-octagon-fill"),
    ("high",          "#fd7e14", "bi-exclamation-triangle-fill"),
    ("medium",        "#ffc107", "bi-exclamation-circle-fill"),
    ("low",           "#0dcaf0", "bi-info-circle-fill"),
    ("informational", "#6c757d", "bi-dot"),
]

# Readable foreground once a severity's own colour becomes a solid
# background — white would fail on the yellow and cyan steps.
SEVERITY_INK = {
    "critical":      "#ffffff",
    "high":          "#3d1c00",
    "medium":        "#3f2d00",
    "low":           "#053640",
    "informational": "#ffffff",
}

# Rows in the recent-activity table. Filtering and sorting happen in the
# browser, so this is the whole working set — big enough to be worth
# slicing, small enough to ship in one page.
RECENT_ACTIVITY_LIMIT = 60

# Shortcuts shown on each recent-case card. Every analysis route is
# case-scoped (/<tool>/<case_id>), so these are built per case.
#
# Reports is deliberately absent: its blueprint is not registered, so
# the link only ever produced a 404.
CASE_TOOLS = [
    ("Analysis",  "analysis",  "bi-graph-up-arrow"),
    ("Timeline",  "timeline",  "bi-clock-history"),
    ("Events",    "events",    "bi-list-ul"),
    ("Evidence",  "evidence",  "bi-hdd-fill"),
    ("Incidents", "incidents", "bi-shield-exclamation"),
    ("Memory",    "memory",    "bi-memory"),
]


def _count_by(column, **filters):
    """Return {value: count} for a grouped count on `column`."""
    query = db.session.query(column, func.count(Event.id))

    if filters:
        query = query.filter_by(**filters)

    return {
        key: count
        for key, count in query.group_by(column).all()
        if key is not None
    }


def _severity_breakdown():
    """Counts per severity, in fixed order, with colours for the donut."""
    counts = _count_by(Event.severity)

    # Normalise keys: the parsers write lowercase, but be forgiving.
    normalised = {}
    for key, count in counts.items():
        normalised[str(key).lower()] = normalised.get(str(key).lower(), 0) + count

    breakdown = []
    for name, colour, icon in SEVERITY_META:
        breakdown.append({
            "name": name,
            "label": name.capitalize(),
            "count": normalised.get(name, 0),
            "color": colour,
            "icon": icon,
        })

    return breakdown


def _hourly_profile():
    """Events per hour of the IST day, pooled across the whole dataset.

    Anchored to time-of-day rather than to a calendar window, so it says
    something ("this estate is busy at 03:00") no matter how old the
    evidence is.
    """

    rows = (
        db.session.query(Event.timestamp)
        .filter(Event.timestamp.isnot(None))
        .all()
    )

    buckets = [0] * 24

    for (timestamp,) in rows:
        buckets[to_ist(timestamp).hour] += 1

    total = sum(buckets)
    peak = max(buckets) if buckets else 0

    # Outside 07:00-19:00 is worth calling out on its own.
    off_hours = sum(buckets[:7]) + sum(buckets[19:])

    return {
        "labels": ["%02d" % hour for hour in range(24)],
        "counts": buckets,
        "total": total,
        "peak": peak,
        "peak_hour": "%02d:00" % buckets.index(peak) if peak else None,
        "off_hours": off_hours,
        "off_share": round(off_hours / total * 100) if total else 0,
    }


def _events_per_case():
    """Event counts per case, in the palette each case wears elsewhere."""

    counts = dict(
        db.session.query(Event.case_id, func.count(Event.id))
        .group_by(Event.case_id)
        .all()
    )

    chips = case_stats.case_chips()

    rows = [
        {
            "id": case_id,
            "name": chip["name"],
            "color": chip["color"],
            "count": counts.get(case_id, 0),
        }
        for case_id, chip in chips.items()
        if counts.get(case_id, 0)
    ]

    return sorted(rows, key=lambda row: row["count"], reverse=True)


def _top_channels(limit=6):
    """Busiest log sources — where the events are actually coming from."""

    rows = (
        db.session.query(Event.channel, func.count(Event.id))
        .filter(Event.channel.isnot(None))
        .group_by(Event.channel)
        .order_by(func.count(Event.id).desc())
        .limit(limit)
        .all()
    )

    if not rows:
        return []

    top = rows[0][1] or 1

    return [
        {
            "label": channel,
            "count": hits,
            "percent": round(hits / top * 100),
        }
        for channel, hits in rows
    ]


def _evidence_mix():
    """Artifact types held, with the storage each accounts for."""

    rows = (
        db.session.query(
            Evidence.artifact_type,
            func.count(Evidence.id),
            func.sum(Evidence.filesize),
        )
        .group_by(Evidence.artifact_type)
        .order_by(func.count(Evidence.id).desc())
        .all()
    )

    # A fixed slot per type, so a type keeps its colour between reloads.
    palette = ["#2a78d6", "#7c3aed", "#0d9488", "#eb6834", "#db2777", "#12a150"]

    return [
        {
            "label": artifact or "Unclassified",
            "count": hits,
            "size": case_stats.human_size(total or 0),
            "color": palette[index % len(palette)],
        }
        for index, (artifact, hits, total) in enumerate(rows)
    ]


def _recent_cases(limit=4):
    """Most recent cases, each with its own evidence / event rollup."""
    cases = (
        Case.query
        .order_by(Case.created_at.desc(), Case.id.desc())
        .limit(limit)
        .all()
    )

    evidence_per_case = dict(
        db.session.query(Evidence.case_id, func.count(Evidence.id))
        .group_by(Evidence.case_id)
        .all()
    )

    events_per_case = dict(
        db.session.query(Event.case_id, func.count(Event.id))
        .group_by(Event.case_id)
        .all()
    )

    critical_per_case = dict(
        db.session.query(Event.case_id, func.count(Event.id))
        .filter(func.lower(Event.severity).in_(["critical", "high"]))
        .group_by(Event.case_id)
        .all()
    )

    cards = []

    for case in cases:
        cards.append({
            "id": case.id,
            "name": case.case_name,
            "description": case.description,
            "status": (case.status or "open").capitalize(),
            "created_at": case.created_at,
            "evidence_count": evidence_per_case.get(case.id, 0),
            "event_count": events_per_case.get(case.id, 0),
            "alert_count": critical_per_case.get(case.id, 0),
        })

    return cards


def _top_detections(limit=5):
    """Most frequently triggered rules, ranked by hit count."""
    rows = (
        db.session.query(
            Event.rule_title,
            func.lower(Event.severity),
            func.count(Event.id).label("hits"),
        )
        .filter(Event.rule_title.isnot(None))
        .group_by(Event.rule_title, func.lower(Event.severity))
        .order_by(func.count(Event.id).desc())
        .limit(limit)
        .all()
    )

    if not rows:
        return []

    top = rows[0][2] or 1

    return [
        {
            "title": title,
            "severity": severity or "informational",
            "hits": hits,
            # Bar width relative to the most-hit rule.
            "percent": round((hits / top) * 100),
        }
        for title, severity, hits in rows
    ]


def _top_hosts(limit=5):
    """Noisiest machines, ranked by event count."""
    rows = (
        db.session.query(Event.computer, func.count(Event.id).label("hits"))
        .filter(Event.computer.isnot(None))
        .group_by(Event.computer)
        .order_by(func.count(Event.id).desc())
        .limit(limit)
        .all()
    )

    if not rows:
        return []

    top = rows[0][1] or 1

    return [
        {
            "computer": computer,
            "hits": hits,
            "percent": round((hits / top) * 100),
        }
        for computer, hits in rows
    ]


@dashboard_bp.route("/dashboard")
def dashboard():

    # Headline statistics
    total_cases = Case.query.count()
    evidence_count = Evidence.query.count()
    event_count = Event.query.count()

    critical_count = (
        Event.query
        .filter(func.lower(Event.severity) == "critical")
        .count()
    )

    high_count = (
        Event.query
        .filter(func.lower(Event.severity) == "high")
        .count()
    )

    open_cases = (
        Case.query
        .filter(func.lower(Case.status) == "open")
        .count()
    )

    closed_cases = total_cases - open_cases

    severity_breakdown = _severity_breakdown()

    hourly = _hourly_profile()
    events_per_case = _events_per_case()
    top_channels = _top_channels()
    evidence_mix = _evidence_mix()

    # How much calendar the parsed events actually cover.
    span = (
        db.session.query(
            func.min(Event.timestamp),
            func.max(Event.timestamp)
        )
        .filter(Event.timestamp.isnot(None))
        .first()
    )

    coverage_days = (
        (to_ist(span[1]).date() - to_ist(span[0]).date()).days + 1
        if span and span[0] and span[1] else 0
    )

    # Latest activity feed
    recent_events = (
        Event.query
        .order_by(Event.timestamp.desc())
        .limit(RECENT_ACTIVITY_LIMIT)
        .all()
    )

    severity_icons = {name: icon for name, _, icon in SEVERITY_META}
    severity_colors = {name: colour for name, colour, _ in SEVERITY_META}

    # Worst first, so the table can sort by risk rather than alphabet.
    severity_ranks = {
        name: index
        for index, (name, _, _) in enumerate(SEVERITY_META)
    }

    # Case names, so a row says which investigation it came from.
    case_names = dict(
        db.session.query(Case.id, Case.case_name).all()
    )

    recent_activity = []

    for event in recent_events:

        severity = (event.severity or "informational").lower()

        # Spelling varies between parsers; the table filters on one key.
        if severity in ("med",):
            severity = "medium"
        elif severity in ("info", "information"):
            severity = "informational"

        recent_activity.append({
            "id": event.id,
            "time": to_ist(event.timestamp),
            "time_display": format_ist(event.timestamp),
            "description": f"{event.rule_title} ({event.computer})",
            "rule_title": event.rule_title,
            "computer": event.computer,
            "channel": event.channel,
            "event_id": event.event_id,
            "case_id": event.case_id,
            "case_name": case_names.get(event.case_id),
            "severity": severity,
            "rank": severity_ranks.get(severity, len(SEVERITY_META)),
            "color": severity_colors.get(severity, "#6c757d"),
            "icon": severity_icons.get(severity, "bi-dot"),
            "status": severity.capitalize(),
        })

    # One button per severity, counted over the rows actually in the
    # table so a button never promises results it cannot show.
    activity_filters = [{
        "name": "all",
        "label": "All",
        "count": len(recent_activity),
        "color": "#0d6efd",
        "ink": "#ffffff",
        "icon": "bi-collection",
    }]

    # How many exist in total, not just in this window — a severity with
    # nothing recent can still point at the full explorer.
    overall = {row["name"]: row["count"] for row in severity_breakdown}

    for name, colour, icon in SEVERITY_META:
        activity_filters.append({
            "name": name,
            "label": name.capitalize(),
            "count": sum(
                1
                for item in recent_activity
                if item["severity"] == name
            ),
            "overall": overall.get(name, 0),
            "color": colour,
            "ink": SEVERITY_INK.get(name, "#ffffff"),
            "icon": icon,
        })

    # Distinct values for the header dropdowns.
    activity_hosts = sorted({
        item["computer"]
        for item in recent_activity
        if item["computer"]
    })

    activity_cases = sorted(
        {
            (item["case_id"], item["case_name"] or "Case #%s" % item["case_id"])
            for item in recent_activity
            if item["case_id"]
        },
        key=lambda row: row[1].lower()
    )

    return render_template(
        "dashboard.html",

        total_cases=total_cases,
        open_cases=open_cases,
        closed_cases=closed_cases,

        evidence_count=evidence_count,
        event_count=event_count,

        critical_count=critical_count,
        high_count=high_count,

        severity_breakdown=severity_breakdown,

        hourly=hourly,
        events_per_case=events_per_case,
        top_channels=top_channels,
        evidence_mix=evidence_mix,
        coverage_days=coverage_days,

        recent_cases=_recent_cases(),
        case_tools=CASE_TOOLS,

        top_detections=_top_detections(),
        top_hosts=_top_hosts(),

        recent_activity=recent_activity,
        activity_filters=activity_filters,
        activity_hosts=activity_hosts,
        activity_cases=activity_cases,
        activity_limit=RECENT_ACTIVITY_LIMIT,
    )
