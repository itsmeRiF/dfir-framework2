from flask import Blueprint, render_template

from database.db import db

from models.case import Case
from models.evidence import Evidence
from models.event import Event

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
def dashboard():

    # Statistics
    total_cases = Case.query.count()

    evidence_count = Evidence.query.count()

    event_count = Event.query.count()

    critical_count = Event.query.filter_by(
        severity="critical"
    ).count()

    # Latest Activity
    recent_events = (
        Event.query
        .order_by(Event.timestamp.desc())
        .limit(10)
        .all()
    )

    recent_activity = []

    for event in recent_events:

        recent_activity.append({

            "time": event.timestamp,

            "description": f"{event.rule_title} ({event.computer})",

            "status": event.severity.capitalize()

        })

    return render_template(

        "dashboard.html",

        total_cases=total_cases,

        evidence_count=evidence_count,

        event_count=event_count,

        critical_count=critical_count,

        recent_activity=recent_activity

    )