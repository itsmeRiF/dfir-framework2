from flask import Blueprint, render_template
from flask_login import login_required

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/reports/<int:case_id>")
@login_required
def memory(case_id):

    return render_template(
        "reports.html",
        case_id=case_id
    )