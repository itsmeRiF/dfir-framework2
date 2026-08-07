from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)
from database.db import db
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

    evidence = Evidence.query.get_or_404(
        evidence_id
    )

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


    # Back where the button was pressed — the case page or the
    # all-cases repository — falling back to the case page.
    return redirect(

        request.referrer
        or url_for(
            "evidence.evidence_page",
            case_id=evidence.case_id
        )

    )

# =====================================================
# Delete Evidence
# =====================================================

@evidence_bp.route(
    "/evidence/delete/<int:evidence_id>",
    methods=["POST"]
)
def delete_evidence(evidence_id):


    from models.event import Event
    from models.memory_process import MemoryProcess
    from models.memory_network import MemoryNetwork
    from models.memory_ioc import MemoryIOC

    import os
    import shutil


    evidence = Evidence.query.get_or_404(
        evidence_id
    )


    case_id = evidence.case_id


    # Captured before the row goes, so the redirect below can send
    # the deleter back to the page they came from.
    origin = request.referrer


    try:

        # -----------------------------
        # Delete Events
        # -----------------------------

        Event.query.filter_by(
            evidence_id=evidence_id
        ).delete()
        
        
        Event.query.filter_by(
            evidence_id=evidence_id
        ).delete(
            synchronize_session=False
        )



        # -----------------------------
        # Delete Memory Data
        # -----------------------------

        if evidence.artifact_type == "Memory":

            
            MemoryProcess.query.filter_by(
                case_id=case_id
            ).delete(
                synchronize_session=False
            )
            

            MemoryNetwork.query.filter_by(
                case_id=case_id
            ).delete(
                synchronize_session=False
            )


            MemoryIOC.query.filter_by(
                case_id=case_id
            ).delete(
                synchronize_session=False
            )



        # -----------------------------
        # Delete Physical File
        # -----------------------------

        if evidence.filepath:

            if os.path.exists(
                evidence.filepath
            ):

                os.remove(
                    evidence.filepath
                )



        # -----------------------------
        # Delete Output
        # -----------------------------

        output_dir = os.path.join(

            "output",

            "evidence",

            str(case_id),

            str(evidence_id)

        )


        if os.path.exists(output_dir):

            shutil.rmtree(
                output_dir
            )



        # -----------------------------
        # Delete DB Record
        # -----------------------------

        db.session.delete(
            evidence
        )


        db.session.commit()



        flash(
            "Evidence deleted successfully.",
            "success"
        )


    except Exception as e:


        db.session.rollback()


        flash(
            str(e),
            "danger"
        )


    return redirect(

        origin
        or url_for(
            "evidence.evidence_page",
            case_id=case_id
        )

    )
