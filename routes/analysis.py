from flask import Blueprint, render_template, redirect, url_for
from sqlalchemy import func

from database.db import db

from models.case import Case
from models.evidence import Evidence
from models.event import Event
from models.incident import Incident
from models.memory import MemoryAnalysis
from models.memory_process import MemoryProcess
from models.memory_network import MemoryNetwork
from models.memory_ioc import MemoryIOC

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


# =========================================================
# MEMORY ANALYSIS
# =========================================================

# =========================================================
# MEMORY ANALYSIS
# =========================================================

@analysis_bp.route("/analysis/memory/<int:case_id>")
def memory(case_id):

    memory = MemoryAnalysis.query.filter_by(
        case_id=case_id
    ).first()


    processes = (
        MemoryProcess.query
        .filter_by(case_id=case_id)
        .order_by(MemoryProcess.id.desc())
        .all()
    )


    networks = (
        MemoryNetwork.query
        .filter_by(case_id=case_id)
        .order_by(MemoryNetwork.id.desc())
        .all()
    )


    iocs = (
        MemoryIOC.query
        .filter_by(case_id=case_id)
        .order_by(MemoryIOC.id.desc())
        .all()
    )


    return render_template(
        "analysis/memory.html",

        case_id=case_id,

        memory=memory,

        processes=processes,

        networks=networks,

        iocs=iocs
    )
@analysis_bp.route("/analysis/validation/<int:case_id>")
def validation(case_id):

    return render_template(
        "analysis/validation.html",
        case_id=case_id
    )