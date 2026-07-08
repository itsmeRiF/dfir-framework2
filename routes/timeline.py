from flask import Blueprint, render_template
from flask_login import login_required

from models.event import Event

timeline_bp = Blueprint("timeline", __name__)


@timeline_bp.route("/timeline/<int:case_id>")
@login_required
def timeline(case_id):
    events = Event.query.filter_by(case_id=case_id).all()
    events = sorted(events, key=lambda x: str(x.timestamp))
    return render_template("timeline.html", events=events, case_id=case_id)
