from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from models.case import Case
from models.evidence import Evidence

from modules.evidence.service import EvidenceService
from utils.timezone import format_ist


evidence_bp = Blueprint(
    "evidence",
    __name__
)



# =====================================================
# Evidence Dashboard
# =====================================================

@evidence_bp.route(
    "/evidence/<int:case_id>"
)
def evidence_page(case_id):

    case = Case.query.get_or_404(
        case_id
    )


    evidences = (
        Evidence.query
        .filter_by(
            case_id=case_id
        )
        .order_by(
            Evidence.id.desc()
        )
        .all()
    )


    return render_template(
        "evidence/dashboard.html",
        case=case,
        case_id=case_id,
        evidences=evidences,
        format_ist=format_ist
    )





# =====================================================
# Upload Evidence
# =====================================================

@evidence_bp.route(
    "/evidence/upload/<int:case_id>",
    methods=["POST"]
)
def upload_evidence(case_id):


    Case.query.get_or_404(
        case_id
    )


    file = request.files.get(
        "file"
    )


    if not file:

        flash(
            "Please select a file.",
            "danger"
        )

        return redirect(
            url_for(
                "evidence.evidence_page",
                case_id=case_id
            )
        )



    try:

        result = EvidenceService.upload(

            file=file,

            case_id=case_id

        )


        flash(
            result["message"],
            "success"
        )



    except Exception as e:


        flash(
            str(e),
            "danger"
        )



    return redirect(

        url_for(
            "evidence.evidence_page",
            case_id=case_id
        )

    )

# =====================================================
# Re-analyze Evidence
# =====================================================
@evidence_bp.route(
    "/evidence/reanalyze/<int:evidence_id>",
    methods=["POST"]
)
def reanalyze(evidence_id):

    from modules.evidence.reanalyze import EvidenceReanalyzer

    try:

        result = EvidenceReanalyzer.run(
            evidence_id
        )

        flash(
            "Evidence re-analyzed successfully.",
            "success"
        )

    except Exception as e:

        flash(
            f"Re-analysis failed: {str(e)}",
            "danger"
        )


    return redirect(
        request.referrer
    )