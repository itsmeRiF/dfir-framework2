from flask import Blueprint, render_template
from flask_login import login_required

mft_bp = Blueprint("mft", __name__)


@mft_bp.route("/mft/<int:case_id>")
@login_required
def memory(case_id):

    return render_template(
        "mft.html",
        case_id=case_id
    )