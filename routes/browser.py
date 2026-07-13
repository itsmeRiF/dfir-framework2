from flask import Blueprint, render_template
from flask_login import login_required

browser_bp = Blueprint("browser", __name__)


@browser_bp.route("/browser/<int:case_id>")
@login_required
def memory(case_id):

    return render_template(
        "browser.html",
        case_id=case_id
    )