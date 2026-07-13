from flask import Blueprint, render_template
from flask_login import login_required

jumplist_bp = Blueprint("jumplist", __name__)


@jumplist_bp.route("/jumplist/<int:case_id>")
@login_required
def memory(case_id):

    return render_template(
        "jumplist.html",
        case_id=case_id
    )