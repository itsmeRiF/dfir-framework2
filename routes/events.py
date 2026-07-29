from flask import Blueprint, render_template, request, Response
from flask_login import login_required
from sqlalchemy import or_, func

from database.db import db
from models.event import Event

import csv
import io


events_bp = Blueprint(
    "events",
    __name__
)


# =========================================================
# EVENT EXPLORER
# =========================================================

@events_bp.route("/events/<int:case_id>")
@login_required
def view_events(case_id):

    page = request.args.get(
        "page",
        1,
        type=int
    )

    search = request.args.get(
        "search",
        ""
    ).strip()

    severity = request.args.get(
        "severity",
        ""
    ).strip()

    computer = request.args.get(
        "computer",
        ""
    ).strip()

    channel = request.args.get(
        "channel",
        ""
    ).strip()

    rule = request.args.get(
        "rule",
        ""
    ).strip()

    eventid = request.args.get(
        "eventid",
        ""
    ).strip()

    evidence_id = request.args.get(
        "evidence_id",
        type=int
    )

    sort = request.args.get(
        "sort",
        "timestamp"
    )

    order = request.args.get(
        "order",
        "desc"
    )


    # -----------------------------------------------------
    # BASE QUERY
    # -----------------------------------------------------

    query = Event.query.filter(
        Event.case_id == case_id
    )


    # Evidence specific filtering

    if evidence_id:

        query = query.filter(
            Event.evidence_id == evidence_id
        )


    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    if search:

        query = query.filter(
            or_(
                Event.details.ilike(
                    f"%{search}%"
                ),

                Event.rule_title.ilike(
                    f"%{search}%"
                ),

                Event.computer.ilike(
                    f"%{search}%"
                )
            )
        )


    # -----------------------------------------------------
    # FILTERS
    # -----------------------------------------------------

    if severity:

        query = query.filter(
            Event.severity == severity
        )


    if computer:

        query = query.filter(
            Event.computer == computer
        )


    if channel:

        query = query.filter(
            Event.channel == channel
        )


    if rule:

        query = query.filter(
            Event.rule_title == rule
        )


    if eventid:

        query = query.filter(
            Event.event_id == eventid
        )



    # -----------------------------------------------------
    # SORTING
    # -----------------------------------------------------

    sort_columns = {

        "timestamp": Event.timestamp,

        "severity": Event.severity,

        "computer": Event.computer,

        "eventid": Event.event_id

    }


    column = sort_columns.get(
        sort,
        Event.timestamp
    )


    if order == "asc":

        query = query.order_by(
            column.asc()
        )

    else:

        query = query.order_by(
            column.desc()
        )



    # -----------------------------------------------------
    # STATISTICS
    # -----------------------------------------------------

    stats_query = Event.query.filter(
        Event.case_id == case_id
    )


    if evidence_id:

        stats_query = stats_query.filter(
            Event.evidence_id == evidence_id
        )


    stats = (
        db.session.query(
            func.lower(Event.severity),
            func.count(Event.id)
        )
        .filter(
            Event.case_id == case_id
        )
    )


    if evidence_id:

        stats = stats.filter(
            Event.evidence_id == evidence_id
        )


    stats = (
        stats.group_by(
            func.lower(Event.severity)
        )
        .all()
    )


    severity_counts = {}


    for sev, count in stats:

        key = (
            sev or ""
        ).lower().strip()

        severity_counts[key] = count



    total = (
        stats_query.count()
    )


    critical = severity_counts.get(
        "critical",
        0
    )


    high = severity_counts.get(
        "high",
        0
    )


    medium = (
        severity_counts.get("medium", 0)
        +
        severity_counts.get("med", 0)
    )


    low = severity_counts.get(
        "low",
        0
    )


    informational = (

        severity_counts.get(
            "informational",
            0
        )

        +

        severity_counts.get(
            "information",
            0
        )

        +

        severity_counts.get(
            "info",
            0
        )

    )



    # -----------------------------------------------------
    # DROPDOWN DATA
    # -----------------------------------------------------

    computers = (

        db.session.query(
            Event.computer
        )
        .filter_by(
            case_id=case_id
        )
        .distinct()
        .order_by(
            Event.computer
        )
        .all()

    )


    channels = (

        db.session.query(
            Event.channel
        )
        .filter_by(
            case_id=case_id
        )
        .distinct()
        .order_by(
            Event.channel
        )
        .all()

    )


    rules = (

        db.session.query(
            Event.rule_title
        )
        .filter_by(
            case_id=case_id
        )
        .distinct()
        .order_by(
            Event.rule_title
        )
        .all()

    )



    # -----------------------------------------------------
    # PAGINATION
    # -----------------------------------------------------

    pagination = query.paginate(

        page=page,

        per_page=25,

        error_out=False

    )



    return render_template(

        "analysis/events.html",

        events=pagination.items,

        pagination=pagination,

        case_id=case_id,

        evidence_id=evidence_id,

        total=total,

        critical=critical,

        high=high,

        medium=medium,

        low=low,

        informational=informational,

        computers=computers,

        channels=channels,

        rules=rules,

        search=search,

        severity_filter=severity,

        computer_filter=computer,

        channel_filter=channel,

        rule_filter=rule,

        eventid_filter=eventid,

        sort=sort,

        order=order

    )



# =========================================================
# EXPORT EVENTS
# =========================================================

@events_bp.route(
    "/events/export/<int:case_id>"
)
@login_required
def export_events(case_id):

    evidence_id = request.args.get(
        "evidence_id",
        type=int
    )


    query = Event.query.filter(
        Event.case_id == case_id
    )


    if evidence_id:

        query = query.filter(
            Event.evidence_id == evidence_id
        )


    events = query.all()



    output = io.StringIO()

    writer = csv.writer(
        output
    )


    writer.writerow([

        "Timestamp",

        "Computer",

        "Channel",

        "EventID",

        "Severity",

        "Rule",

        "Details"

    ])



    for event in events:

        writer.writerow([

            event.timestamp,

            event.computer,

            event.channel,

            event.event_id,

            event.severity,

            event.rule_title,

            event.details

        ])



    output.seek(0)



    return Response(

        output,

        mimetype="text/csv",

        headers={

            "Content-Disposition":
            f"attachment; filename=case_{case_id}_events.csv"

        }

    )