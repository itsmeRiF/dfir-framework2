from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from sqlalchemy import func

from database.db import db

from models.case import Case
from models.evidence import Evidence
from models.event import Event
from models.incident import Incident

from utils import case_stats
from utils.timezone import format_ist


cases_bp = Blueprint(
    "cases",
    __name__
)


# Shortcuts on each case card. Every analysis route is case-scoped,
# so these are built per case as /analysis/<tool>/<case_id>.
CASE_TOOLS = [
    ("Evidence",  "evidence",  "bi-hdd-fill"),
    ("Events",    "events",    "bi-list-ul"),
    ("Timeline",  "timeline",  "bi-clock-history"),
    ("Incidents", "incidents", "bi-exclamation-triangle-fill"),
    ("Memory",    "memory",    "bi-memory"),
]


def _counts(model, *filters):
    """{case_id: row count} for one model, optionally filtered."""

    query = db.session.query(
        model.case_id,
        func.count(model.id)
    )

    for condition in filters:
        query = query.filter(condition)

    return dict(
        query.group_by(model.case_id).all()
    )


# =========================================================
# CASE LIST
# =========================================================

@cases_bp.route("/cases", methods=["GET"])
@login_required
def list_cases():

    cases = (
        Case.query
        .order_by(
            Case.created_at.desc(),
            Case.id.desc()
        )
        .all()
    )


    # One grouped query per metric rather than three per case.
    evidence = _counts(Evidence)
    events = _counts(Event)
    incidents = _counts(Incident)

    alerts = _counts(
        Event,
        func.lower(Event.severity).in_(["critical", "high"])
    )

    # Newest event per case — "last activity" on the card.
    latest = dict(
        db.session.query(
            Event.case_id,
            func.max(Event.timestamp)
        )
        .filter(Event.timestamp.isnot(None))
        .group_by(Event.case_id)
        .all()
    )

    # The same colour the case wears in every chart and global view.
    chips = case_stats.case_chips()


    case_data = []


    for case in cases:

        name = case.case_name or ("Case #%s" % case.id)

        case_data.append({

            "case": case,

            "color": case_stats.chip_for(chips, case.id)["color"],

            # Two letters for the card avatar, from the case name.
            "initials": "".join(
                word[0]
                for word in name.split()[:2]
            ).upper() or "CX",

            "evidence_count": evidence.get(case.id, 0),

            "event_count": events.get(case.id, 0),

            "incident_count": incidents.get(case.id, 0),

            "alert_count": alerts.get(case.id, 0),

            "last_activity": format_ist(latest.get(case.id)),

            "tags": [
                tag.strip()
                for tag in (case.tags or "").split(",")
                if tag.strip()
            ],

        })


    totals = {

        "cases": len(case_data),

        "open": sum(
            1
            for item in case_data
            if (item["case"].status or "").lower() == "open"
        ),

        "closed": sum(
            1
            for item in case_data
            if (item["case"].status or "").lower() == "closed"
        ),

        "evidence": sum(item["evidence_count"] for item in case_data),

        "events": sum(item["event_count"] for item in case_data),

        "incidents": sum(item["incident_count"] for item in case_data),

        "alerts": sum(item["alert_count"] for item in case_data),

    }


    # Dropdowns list only what the page actually holds.
    def present(field):

        return sorted({
            (getattr(item["case"], field) or "").strip().lower()
            for item in case_data
            if (getattr(item["case"], field) or "").strip()
        })


    return render_template(
        "analysis/cases.html",
        cases=case_data,
        totals=totals,
        case_tools=CASE_TOOLS,
        statuses=present("status"),
        severities=present("severity"),
        priorities=present("priority"),
        incident_types=present("incident_type"),
    )



@cases_bp.route("/cases/new")
@login_required
def new_case():

    return render_template(
        "analysis/new_case.html"
    )



# =========================================================
# CREATE CASE
# =========================================================

@cases_bp.route(
    "/cases/create",
    methods=["POST"]
)
@login_required
def create_case():


    new_case = Case(

        case_name=request.form.get(
            "case_name"
        ),

        description=request.form.get(
            "description"
        ),


        incident_type=request.form.get(
            "incident_type"
        ),

        priority=request.form.get(
            "priority",
            "medium"
        ),

        severity=request.form.get(
            "severity",
            "medium"
        ),


        organization=request.form.get(
            "organization"
        ),

        department=request.form.get(
            "department"
        ),


        lead_investigator=request.form.get(
            "lead_investigator"
        ),


        status=request.form.get(
            "status",
            "open"
        ),


        tags=request.form.get(
            "tags"
        ),


        remarks=request.form.get(
            "remarks"
        )

    )


    db.session.add(
        new_case
    )

    db.session.commit()


    # Generate CX-YYYY-0001
    new_case.generate_case_number()


    db.session.commit()


    return redirect(
        url_for(
            "cases.list_cases"
        )
    )