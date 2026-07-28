"""
CyberX DFIR
Event Detail View
"""

from flask import Blueprint, render_template
from flask_login import login_required

from models.event import Event


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

    return render_template(
        "analysis/event_detail.html",
        event=event
    )