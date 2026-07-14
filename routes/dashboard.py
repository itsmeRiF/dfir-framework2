from datetime import timedelta

from flask import Blueprint, render_template
from sqlalchemy import func

from database.db import db

from models.case import Case
from models.evidence import Evidence
from models.event import Event

from utils.timezone import format_ist, ist_day_start_as_utc, now_ist, to_ist

dashboard_bp = Blueprint("dashboard", __name__)


# Severity order (highest first) + the colour / icon used to render it.
SEVERITY_META = [
    ("critical",      "#dc3545", "bi-exclamation-octagon-fill"),
    ("high",          "#fd7e14", "bi-exclamation-triangle-fill"),
    ("medium",        "#ffc107", "bi-exclamation-circle-fill"),
    ("low",           "#0dcaf0", "bi-info-circle-fill"),
    ("informational", "#6c757d", "bi-dot"),
]

ACTIVITY_DAYS = 14

# Shortcuts shown on each recent-case card. Every analysis route is
# case-scoped (/<tool>/<case_id>), so these are built per case.
CASE_TOOLS = [
    ("Analysis",  "analysis",  "bi-graph-up-arrow"),
    ("Timeline",  "timeline",  "bi-clock-history"),
    ("Events",    "events",    "bi-list-ul"),
    ("Evidence",  "evidence",  "bi-hdd-fill"),
    ("Incidents", "incidents", "bi-shield-exclamation"),
    ("Reports",   "reports",   "bi-file-earmark-text"),
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


def _activity_series():
    """Event counts per IST calendar day for the last ACTIVITY_DAYS days."""
    today = now_ist().date()
    start = today - timedelta(days=ACTIVITY_DAYS - 1)

    # The column holds naive UTC, so the lower bound is IST midnight in UTC terms.
    rows = (
        db.session.query(Event.timestamp)
        .filter(Event.timestamp.isnot(None))
        .filter(Event.timestamp >= ist_day_start_as_utc(start))
        .all()
    )

    buckets = {start + timedelta(days=offset): 0 for offset in range(ACTIVITY_DAYS)}

    for (timestamp,) in rows:
        day = to_ist(timestamp).date()
        if day in buckets:
            buckets[day] += 1

    days = sorted(buckets)

    return {
        "labels": [day.strftime("%d %b") for day in days],
        "values": [buckets[day] for day in days],
        "total": sum(buckets.values()),
    }


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
    activity = _activity_series()

    # Latest activity feed
    recent_events = (
        Event.query
        .order_by(Event.timestamp.desc())
        .limit(10)
        .all()
    )

    severity_icons = {name: icon for name, _, icon in SEVERITY_META}

    recent_activity = []

    for event in recent_events:

        severity = (event.severity or "informational").lower()

        recent_activity.append({
            "time": to_ist(event.timestamp),
            "time_display": format_ist(event.timestamp),
            "description": f"{event.rule_title} ({event.computer})",
            "rule_title": event.rule_title,
            "computer": event.computer,
            "channel": event.channel,
            "case_id": event.case_id,
            "severity": severity,
            "icon": severity_icons.get(severity, "bi-dot"),
            "status": severity.capitalize(),
        })

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

        activity_labels=activity["labels"],
        activity_values=activity["values"],
        activity_total=activity["total"],
        activity_days=ACTIVITY_DAYS,

        recent_cases=_recent_cases(),
        case_tools=CASE_TOOLS,

        top_detections=_top_detections(),
        top_hosts=_top_hosts(),

        recent_activity=recent_activity,
    )
