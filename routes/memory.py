from flask import Blueprint, render_template
from flask_login import login_required

memory_bp = Blueprint("memory", __name__)


@memory_bp.route("/memory/<int:case_id>")
@login_required
def memory(case_id):

    return render_template(
        "memory.html",
        case_id=case_id
    )