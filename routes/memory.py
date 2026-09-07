from flask import Blueprint, render_template, request
from flask_login import login_required

from models.case import Case
from models.memory_process import MemoryProcess
from models.memory_network import MemoryNetwork
from models.memory_ioc import MemoryIOC
from sqlalchemy import or_

from utils import case_stats


memory_bp = Blueprint(
    "memory",
    __name__
)


@memory_bp.route("/memory/<int:case_id>")
@login_required
def memory_analysis(case_id):

    case = Case.query.get_or_404(case_id)

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
            i.severity,
            i.description[:100]
        )
        

        if key in seen:
            continue

        seen.add(key)
        unique_iocs.append(i)

    iocs = unique_iocs


    # Headline counts for the tiles. "Risky" and "high severity" use
    # the same severity scale the rest of the product renders.
    risky_count = sum(
        1
        for p in processes
        if case_stats.severity_rank(p.risk) <= 1
    )

    high_iocs = sum(
        1
        for i in iocs
        if case_stats.severity_rank(i.severity) <= 1
    )

    host_count = len({
        n.local_address.split(":")[0]
        for n in networks
        if n.local_address
    })


    return render_template(
        "analysis/memory.html",

        case=case,

        case_id=case_id,

        processes=processes,

        networks=networks,

        iocs=iocs,

        process_count=len(processes),

        network_count=len(networks),

        ioc_count=len(iocs),

        risky_count=risky_count,

        high_iocs=high_iocs,

        host_count=host_count
    )