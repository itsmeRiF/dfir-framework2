from flask import Blueprint, render_template
from flask_login import login_required

analysis_bp = Blueprint("analysis", __name__)


@analysis_bp.route("/analysis/<int:case_id>")
@login_required
def analysis(case_id):

    return render_template(
        "analysis.html",
        case_id=case_id
    )