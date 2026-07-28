from flask import Blueprint, render_template

from database.db import db

from models.case import Case
from models.memory import MemoryAnalysis
from models.memory_process import MemoryProcess
from models.memory_network import MemoryNetwork
from models.memory_ioc import MemoryIOC



memory_bp = Blueprint(
    "memory",
    __name__
)



# =========================================================
# MEMORY ANALYSIS DASHBOARD
# =========================================================

@memory_bp.route(
    "/analysis/memory/<int:case_id>"
)
def memory_dashboard(case_id):


    case = Case.query.get_or_404(
        case_id
    )



    # -----------------------------------------
    # Memory Summary
    # -----------------------------------------

    memory_summary = MemoryAnalysis.query.filter_by(
        case_id=case_id
    ).first()



    if memory_summary:

        summary = {

            "processes":
                memory_summary.process_count or 0,


            "network":
                memory_summary.network_count or 0,


            "malfind":
                memory_summary.malfind_count or 0,


            "dlls":
                memory_summary.dll_count or 0,


            "drivers":
                memory_summary.driver_count or 0,


            "services":
                memory_summary.service_count or 0

        }


    else:

        summary = {

            "processes":0,
            "network":0,
            "malfind":0,
            "dlls":0,
            "drivers":0,
            "services":0

        }




    # -----------------------------------------
    # Processes
    # -----------------------------------------

    processes = (

        MemoryProcess.query
        .filter_by(
            case_id=case_id
        )
        .order_by(
            MemoryProcess.pid
        )
        .all()

    )




    # -----------------------------------------
    # Network Connections
    # -----------------------------------------

    networks = (

        MemoryNetwork.query
        .filter_by(
            case_id=case_id
        )
        .all()

    )




    # -----------------------------------------
    # IoC
    # -----------------------------------------

    iocs = (

        MemoryIOC.query
        .filter_by(
            case_id=case_id
        )
        .order_by(
            MemoryIOC.severity
        )
        .all()

    )




    # -----------------------------------------
    # Risk Calculation
    # -----------------------------------------

    risk_score = 0


    if memory_summary:

        risk_score += (
            memory_summary.malfind_count or 0
        ) * 10



    risk_score += len(iocs) * 5




    return render_template(

        "memory/dashboard.html",

        case=case,

        case_id=case_id,

        memory=summary,

        processes=processes,

        networks=networks,

        iocs=iocs,

        risk_score=risk_score

    )