from flask import Blueprint, render_template
from flask_login import login_required

usn_bp = Blueprint("usn", __name__)


@usn_bp.route("/usn/<int:case_id>")
@login_required
def memory(case_id):

    return render_template(
        "usn.html",
        case_id=case_id
    )