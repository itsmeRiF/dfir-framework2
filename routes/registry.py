from flask import Blueprint, render_template
from flask_login import login_required

registry_bp = Blueprint(
    "registry",
    __name__
)

@registry_bp.route("/registry/<int:case_id>")
@login_required
def registry(case_id):

    return render_template(
        "registry.html",
        case_id=case_id
    )    