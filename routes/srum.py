from flask import Blueprint, render_template
from flask_login import login_required

srum_bp = Blueprint("srum", __name__)


@srum_bp.route("/srum/<int:case_id>")
@login_required
def memory(case_id):

    return render_template(
        "srum.html",
        case_id=case_id
    )