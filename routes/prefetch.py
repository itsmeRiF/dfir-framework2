from flask import Blueprint, render_template
from flask_login import login_required

prefetch_bp = Blueprint("prefetch", __name__)


@prefetch_bp.route("/prefetch/<int:case_id>")
@login_required
def memory(case_id):

    return render_template(
        "prefetch.html",
        case_id=case_id
    )