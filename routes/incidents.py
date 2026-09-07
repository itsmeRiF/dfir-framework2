from flask import Blueprint, render_template

from models.case import Case
from models.incident import Incident

from utils import case_stats
from utils.timezone import format_ist

incident_bp = Blueprint("incident", __name__)


@incident_bp.route("/incidents/<int:case_id>")
def incidents(case_id):

    case = Case.query.get_or_404(case_id)

    data = (
        Incident.query
        .filter_by(case_id=case_id)
        .all()
    )

    # Worst first, then by how many events each covers — an analyst
    # opening this page wants the top of the list to matter.
    rows = sorted(
        (
            {
                "incident": incident,
                "severity": case_stats.normalise_severity(incident.severity),
            }
            for incident in data
        ),
        key=lambda row: (
            case_stats.severity_rank(row["severity"]),
            -(row["incident"].event_count or 0),
        )
    )

    def count(*names):

        return sum(
            1
            for row in rows
            if row["severity"] in names
        )

    totals = {

        "incidents": len(rows),

        "critical": count("critical"),

        "high": count("high"),

        "medium": count("medium"),

        "low": count("low"),

        "events": sum(
            row["incident"].event_count or 0
            for row in rows
        ),

    }

    return render_template(
        "analysis/incidents.html",
        rows=rows,
        format_ist=format_ist,
        totals=totals,
        case=case,
        case_id=case_id,
        severities=sorted(
            {row["severity"] for row in rows},
            key=case_stats.severity_rank
        )
    )