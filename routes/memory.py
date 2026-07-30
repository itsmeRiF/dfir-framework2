from flask import Blueprint, render_template, request
from flask_login import login_required

from models.memory_process import MemoryProcess
from models.memory_network import MemoryNetwork
from models.memory_ioc import MemoryIOC
from sqlalchemy import or_


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

    
    
    seen = set()
    unique_processes = []

    for p in processes.order_by(MemoryProcess.pid).all():

        key = (
            p.pid,
            p.ppid,
            p.process_name
        )

        if key in seen:
            continue

        seen.add(key)
        unique_processes.append(p)

    processes = unique_processes
    
    



    networks = MemoryNetwork.query.filter_by(
        case_id=case_id
    )

        
        
    if network_search:

        networks = networks.filter(
            or_(
                MemoryNetwork.remote_address.ilike(
                    f"%{network_search}%"
                ),

                MemoryNetwork.local_address.ilike(
                    f"%{network_search}%"
                ),

                MemoryNetwork.process_name.ilike(
                    f"%{network_search}%"
                )
            )
        )    

    
    
    seen = set()
    unique_networks = []

    for n in networks.all():

        key = (
            n.protocol,
            n.local_address,
            n.remote_address,
            n.state,
            n.pid,
            n.process_name
        )

        if key in seen:
            continue

        seen.add(key)
        unique_networks.append(n)

    networks = unique_networks
    
    



    iocs = MemoryIOC.query.filter_by(
        case_id=case_id
    )


    if ioc_search:

        iocs = iocs.filter(
            or_(
                MemoryIOC.indicator.ilike(
                    f"%{ioc_search}%"
                ),

                MemoryIOC.description.ilike(
                    f"%{ioc_search}%"
                ),

                MemoryIOC.severity.ilike(
                    f"%{ioc_search}%"
                )
            )
        )

    
    seen = set()
    unique_iocs = []

    for i in iocs.all():

        key = (
            i.ioc_type,
            i.indicator,
            i.severity
        )

        if key in seen:
            continue

        seen.add(key)
        unique_iocs.append(i)

    iocs = unique_iocs


    print(
        "MEMORY COUNTS:",
        len(processes),
        len(networks),
        len(iocs)
    )
    
    print(
    "CASE:",
    case_id
    )

    print(
        "DB PROCESS:",
        MemoryProcess.query.filter_by(case_id=case_id).count()
    )

    print(
        "DB NETWORK:",
        MemoryNetwork.query.filter_by(case_id=case_id).count()
    )

    print(
        "DB IOC:",
        MemoryIOC.query.filter_by(case_id=case_id).count()
    )
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