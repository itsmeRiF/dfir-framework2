from flask import Blueprint, render_template, request
from flask_login import login_required

from models.memory_process import MemoryProcess
from models.memory_network import MemoryNetwork
from models.memory_ioc import MemoryIOC


memory_bp = Blueprint(
    "memory",
    __name__
)


@memory_bp.route("/memory/<int:case_id>")
@login_required
def memory_analysis(case_id):

    process_search = request.args.get(
        "process",
        ""
    ).strip()


    network_search = request.args.get(
        "network",
        ""
    ).strip()


    ioc_search = request.args.get(
        "ioc",
        ""
    ).strip()



    processes = MemoryProcess.query.filter_by(
        case_id=case_id
    )


    if process_search:

        processes = processes.filter(
            MemoryProcess.process_name.ilike(
                f"%{process_search}%"
            )
        )


    processes = processes.order_by(
        MemoryProcess.pid
    ).all()



    networks = MemoryNetwork.query.filter_by(
        case_id=case_id
    )


    if network_search:

        networks = networks.filter(
            MemoryNetwork.remote_address.ilike(
                f"%{network_search}%"
            )
        )


    networks = networks.all()



    iocs = MemoryIOC.query.filter_by(
        case_id=case_id
    )


    if ioc_search:

        iocs = iocs.filter(
            MemoryIOC.indicator.ilike(
                f"%{ioc_search}%"
            )
        )


    iocs = iocs.all()



    return render_template(
        "analysis/memory.html",

        case_id=case_id,

        processes=processes,

        networks=networks,

        iocs=iocs,

        process_count=len(processes),

        network_count=len(networks),

        ioc_count=len(iocs)
    )