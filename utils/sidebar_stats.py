from flask import g
from sqlalchemy import func

from database.db import db

from models.case import Case
from models.evidence import Evidence
from models.event import Event
from models.incident import Incident
from models.memory_ioc import MemoryIOC
from models.memory_network import MemoryNetwork
from models.memory_process import MemoryProcess


# =========================================================
# SIDEBAR STATISTICS
#
# Counters for the analysis sidebar.
#
#   case_id = None  ->  overall totals, summed across every case
#                       (used on the global /cases page)
#
#   case_id = <id>  ->  the counts for that single case
#                       (used on the in-case analysis pages)
#
# Computed lazily (only when a template asks for them) and
# cached per scope for the lifetime of the request.
# =========================================================

def sidebar_stats(case_id=None):

    try:
        case_id = int(case_id) if case_id not in (None, "") else None

    except (TypeError, ValueError):
        case_id = None


    cache = getattr(g, "_sidebar_stats", None)

    if cache is None:
        cache = g._sidebar_stats = {}

    if case_id in cache:
        return cache[case_id]


    def scoped(model):

        query = model.query

        if case_id is not None:
            query = query.filter_by(case_id=case_id)

        return query


    stats = {

        # The Cases tab always links to the global list,
        # so its badge stays a global total.
        "cases":
            Case.query.count(),

        "open_cases":
            Case.query
            .filter(func.lower(Case.status) == "open")
            .count(),

        "scoped":
            case_id is not None,

        # Names the sidebar heading inside a case. Read from the
        # scope itself, so every in-case page gets it whether or
        # not the route passed a `case` object to the template.
        "case_name":
            db.session.query(Case.case_name)
            .filter(Case.id == case_id)
            .scalar()
            if case_id is not None else None,

        "evidence":
            scoped(Evidence).count(),

        "events":
            scoped(Event).count(),

        # The timeline only plots events that carry a timestamp
        "timeline":
            scoped(Event)
            .filter(Event.timestamp.isnot(None))
            .count(),

        "incidents":
            scoped(Incident).count(),

        # What the memory pages actually list: the extracted
        # processes, network connections and IOCs.
        "memory":
            scoped(MemoryProcess).count()
            + scoped(MemoryNetwork).count()
            + scoped(MemoryIOC).count()

    }


    cache[case_id] = stats

    return stats
