from flask import Blueprint, render_template
from flask_login import login_required

recyclebin_bp = Blueprint("recyclebin", __name__)


@recyclebin_bp.route("/recyclebin/<int:case_id>")
@login_required
def memory(case_id):

    return render_template(
        "recyclebin.html",
        case_id=case_id
    )