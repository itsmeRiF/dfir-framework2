from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required

from database.db import db

from models.case import Case
from models.evidence import Evidence
from models.event import Event
from models.incident import Incident


cases_bp = Blueprint(
    "cases",
    __name__
)


# =========================================================
# CASE LIST
# =========================================================

@cases_bp.route("/cases", methods=["GET"])
@login_required
def list_cases():

    cases = (
        Case.query
        .order_by(
            Case.created_at.desc()
        )
        .all()
    )


    case_data = []


    for case in cases:

        case_data.append({

            "case": case,

            "evidence_count":
                Evidence.query
                .filter_by(case_id=case.id)
                .count(),

            "event_count":
                Event.query
                .filter_by(case_id=case.id)
                .count(),

            "incident_count":
                Incident.query
                .filter_by(case_id=case.id)
                .count()

        })


    return render_template(
        "analysis/cases.html",
        cases=case_data
    )



@cases_bp.route("/cases/new")
@login_required
def new_case():

    return render_template(
        "analysis/new_case.html"
    )



# =========================================================
# CREATE CASE
# =========================================================

@cases_bp.route(
    "/cases/create",
    methods=["POST"]
)
@login_required
def create_case():


    new_case = Case(

        case_name=request.form.get(
            "case_name"
        ),

        description=request.form.get(
            "description"
        ),


        incident_type=request.form.get(
            "incident_type"
        ),

        priority=request.form.get(
            "priority",
            "medium"
        ),

        severity=request.form.get(
            "severity",
            "medium"
        ),


        organization=request.form.get(
            "organization"
        ),

        department=request.form.get(
            "department"
        ),


        lead_investigator=request.form.get(
            "lead_investigator"
        ),


        status=request.form.get(
            "status",
            "open"
        ),


        tags=request.form.get(
            "tags"
        ),


        remarks=request.form.get(
            "remarks"
        )

    )


    db.session.add(
        new_case
    )

    db.session.commit()


    # Generate CX-YYYY-0001
    new_case.generate_case_number()


    db.session.commit()


    return redirect(
        url_for(
            "cases.list_cases"
        )
    )