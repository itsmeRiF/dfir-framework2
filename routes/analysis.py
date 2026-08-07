from flask import Blueprint, render_template, redirect, request, url_for
from flask_login import login_required
from sqlalchemy import func, or_

from datetime import datetime

from database.db import db

from models.case import Case
from models.evidence import Evidence
from models.event import Event
from models.incident import Incident
from models.memory import MemoryAnalysis

from utils import case_stats
from utils.timezone import format_ist


analysis_bp = Blueprint(
    "analysis",
    __name__
)


# =========================================================
# ANALYSIS HOME
# =========================================================

@analysis_bp.route("/analysis/<int:case_id>")
def analysis_home(case_id):

    return redirect(
        url_for(
            "analysis.dashboard",
            case_id=case_id
        )
    )


# =========================================================
# ALL-CASES DASHBOARD
#
# The sidebar's Dashboard tab has no case to point at while
# you are on /cases, so it lands here: the same tab counters,
# rolled up across every case and charted.
# =========================================================

@analysis_bp.route("/analysis/dashboard/")
def global_dashboard():

    return render_template(
        "analysis/global_dashboard.html",
        **case_stats.overview()
    )


# =========================================================
# DASHBOARD
# =========================================================

@analysis_bp.route("/analysis/dashboard/<int:case_id>")
def dashboard(case_id):

    case = Case.query.get_or_404(case_id)

    evidence_count = Evidence.query.filter_by(
        case_id=case_id
    ).count()

    event_count = Event.query.filter_by(
        case_id=case_id
    ).count()

    incident_count = Incident.query.filter_by(
        case_id=case_id
    ).count()

    memory = MemoryAnalysis.query.filter_by(
        case_id=case_id
    ).first()

    if memory:

        memory_summary = {

            "processes": memory.process_count,

            "network": memory.network_count,

            "malfind": memory.malfind_count,

            "dlls": memory.dll_count,

            "drivers": memory.driver_count,

            "services": memory.service_count

        }

        risk_score = getattr(memory, "risk_score", None)

        if risk_score is None:
            risk_score = memory.malfind_count * 10

    else:

        memory_summary = None
        risk_score = 0

    latest_events = (
        Event.query
        .filter_by(case_id=case_id)
        .order_by(Event.timestamp.desc())
        .limit(10)
        .all()
    )

    latest_evidence = (
        Evidence.query
        .filter_by(case_id=case_id)
        .order_by(Evidence.uploaded_at.desc())
        .limit(5)
        .all()
    )

    top_rules = (
        db.session.query(
            Event.rule_title,
            func.count(Event.id)
        )
        .filter(Event.case_id == case_id)
        .group_by(Event.rule_title)
        .order_by(func.count(Event.id).desc())
        .limit(5)
        .all()
    )

    top_hosts = (
        db.session.query(
            Event.computer,
            func.count(Event.id)
        )
        .filter(Event.case_id == case_id)
        .group_by(Event.computer)
        .order_by(func.count(Event.id).desc())
        .limit(5)
        .all()
    )

    severity = {

        "critical": Event.query.filter_by(
            case_id=case_id,
            severity="critical"
        ).count(),

        "high": Event.query.filter_by(
            case_id=case_id,
            severity="high"
        ).count(),

        "medium": Event.query.filter_by(
            case_id=case_id,
            severity="medium"
        ).count(),

        "low": Event.query.filter_by(
            case_id=case_id,
            severity="low"
        ).count()

    }

    return render_template(

        "analysis/dashboard.html",

        case=case,

        case_id=case_id,

        evidence_count=evidence_count,

        event_count=event_count,

        incident_count=incident_count,

        risk_score=risk_score,

        memory=memory_summary,

        latest_events=latest_events,

        latest_evidence=latest_evidence,

        top_rules=top_rules,

        top_hosts=top_hosts,

        severity=severity

    )


# =========================================================
# ALL-CASES EVIDENCE REPOSITORY
#
# The sidebar's Evidence tab has no case to point at while you
# are on /cases, so it lands here: every artifact from every
# case in one repository view.
# =========================================================

@analysis_bp.route("/analysis/evidence/")
def global_evidence():

    return render_template(
        "analysis/global_evidence.html",
        format_ist=format_ist,
        **case_stats.evidence_repository()
    )


# =========================================================
# ALL-CASES EVENT EXPLORER
#
# Same idea as the per-case explorer, with the case as one
# more filter. Paginated server-side: there can be a lot of
# events once several cases have been parsed.
# =========================================================

EVENTS_PER_PAGE = 50


@analysis_bp.route("/analysis/events/")
@login_required
def global_events():

    page = request.args.get("page", 1, type=int)

    search = request.args.get("search", "").strip()

    case_filter = request.args.get("case", type=int)

    severity = request.args.get("severity", "").strip().lower()

    computer = request.args.get("computer", "").strip()

    channel = request.args.get("channel", "").strip()


    # Everything except severity, so the severity tiles keep
    # showing what is one click away.
    conditions = []

    if case_filter:
        conditions.append(Event.case_id == case_filter)

    if search:
        conditions.append(
            or_(
                Event.details.ilike(f"%{search}%"),
                Event.rule_title.ilike(f"%{search}%"),
                Event.computer.ilike(f"%{search}%")
            )
        )

    if computer:
        conditions.append(Event.computer == computer)

    if channel:
        conditions.append(Event.channel == channel)


    counts = dict(
        db.session.query(
            func.lower(Event.severity),
            func.count(Event.id)
        )
        .filter(*conditions)
        .group_by(func.lower(Event.severity))
        .all()
    )

    def severity_total(*names):

        return sum(
            counts.get(name, 0)
            for name in names
        )


    query = Event.query.filter(*conditions)

    if severity:
        query = query.filter(
            func.lower(Event.severity) == severity
        )

    pagination = (
        query
        .order_by(
            Event.timestamp.desc(),
            Event.id.desc()
        )
        .paginate(
            page=page,
            per_page=EVENTS_PER_PAGE,
            error_out=False
        )
    )


    chips = case_stats.case_chips()

    rows = [
        {
            "event": event,
            "case": case_stats.chip_for(chips, event.case_id)
        }
        for event in pagination.items
    ]


    def distinct(column):
        """Dropdown values, narrowed to the case being looked at."""

        query = (
            db.session.query(column)
            .filter(column.isnot(None))
        )

        if case_filter:
            query = query.filter(Event.case_id == case_filter)

        return [
            value
            for (value,) in (
                query
                .distinct()
                .order_by(column)
                .all()
            )
            if value
        ]


    totals = {

        "events": sum(counts.values()),

        "critical": severity_total("critical"),

        "high": severity_total("high"),

        "medium": severity_total("medium", "med"),

        "low": severity_total("low"),

        "informational": severity_total(
            "informational",
            "information",
            "info"
        )

    }


    return render_template(

        "analysis/global_events.html",

        rows=rows,

        pagination=pagination,

        totals=totals,

        matched=pagination.total,

        filter_cases=list(chips.values()),

        computers=distinct(Event.computer),

        channels=distinct(Event.channel),

        filters={
            "search": search,
            "case": case_filter or "",
            "severity": severity,
            "computer": computer,
            "channel": channel
        },

        # Keeps the current filters on every pagination link.
        query_args={
            key: value
            for key, value in request.args.items()
            if key != "page"
        },

        # The severity tiles switch one filter and leave the
        # rest of the query alone.
        severity_args={
            key: value
            for key, value in request.args.items()
            if key not in ("page", "severity")
        },

        format_ist=format_ist

    )


# =========================================================
# ALL-CASES TIMELINE
#
# Every case's activity on one day axis, so investigations
# can be lined up against each other.
# =========================================================

@analysis_bp.route("/analysis/timeline/")
def global_timeline():

    def parse(value):

        if not value:
            return None

        try:
            return datetime.fromisoformat(value)

        except ValueError:
            return None


    start_raw = request.args.get("start", "").strip()

    end_raw = request.args.get("end", "").strip()

    start = parse(start_raw)

    end = parse(end_raw)


    return render_template(

        "analysis/global_timeline.html",

        start=start_raw if start else "",

        end=end_raw if end else "",

        format_ist=format_ist,

        **case_stats.timeline_overview(
            start=start,
            end=end
        )

    )


# =========================================================
# ALL-CASES INCIDENTS
# =========================================================

@analysis_bp.route("/analysis/incidents/")
def global_incidents():

    return render_template(
        "analysis/global_incidents.html",
        format_ist=format_ist,
        **case_stats.incident_overview()
    )


# =========================================================
# ALL-CASES MEMORY
# =========================================================

@analysis_bp.route("/analysis/memory/")
@login_required
def global_memory():

    return render_template(
        "analysis/global_memory.html",
        **case_stats.memory_overview()
    )


# =========================================================
# WRAPPERS
# =========================================================

@analysis_bp.route("/analysis/evidence/<int:case_id>")
def evidence(case_id):

    return redirect(
        url_for(
            "evidence.evidence_page",
            case_id=case_id
        )
    )


@analysis_bp.route("/analysis/events/<int:case_id>")
def events(case_id):

    return redirect(
        url_for(
            "events.view_events",
            case_id=case_id
        )
    )


@analysis_bp.route("/analysis/timeline/<int:case_id>")
def timeline(case_id):

    return redirect(
        url_for(
            "timeline.timeline",
            case_id=case_id
        )
    )


@analysis_bp.route("/analysis/incidents/<int:case_id>")
def incidents(case_id):

    return redirect(
        url_for(
            "incident.incidents",
            case_id=case_id
        )
    )



@analysis_bp.route("/analysis/memory/<int:case_id>")
def memory(case_id):

    return redirect(
        url_for(
            "memory.memory_analysis",
            case_id=case_id
        )
    )
@analysis_bp.route("/analysis/validation/<int:case_id>")
def validation(case_id):

    return render_template(
        "analysis/validation.html",
        case_id=case_id
    )