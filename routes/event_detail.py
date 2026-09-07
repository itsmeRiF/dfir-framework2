"""
CyberX DFIR
Event Detail View
"""

from flask import Blueprint, render_template
from flask_login import login_required

from models.case import Case
from models.event import Event

from utils.timezone import format_ist


event_detail_bp = Blueprint(
    "event_detail",
    __name__
)


@event_detail_bp.route("/event/<int:event_id>")
@login_required
def event_detail(event_id):

    event = Event.query.get_or_404(
        event_id
    )

    # The sidebar and the header both name the case this event
    # belongs to, so it is fetched once here.
    case = (
        Case.query.get(event.case_id)
        if event.case_id else None
    )

    return render_template(
        "analysis/event_detail.html",
        event=event,
        case=case,
        case_id=event.case_id,
        format_ist=format_ist
    )