from flask import g
from sqlalchemy import func

from models.case import Case
from models.evidence import Evidence
from models.event import Event
from models.incident import Incident
from models.memory import MemoryAnalysis


# =========================================================
# SIDEBAR STATISTICS
#
# Overall counters rolled up across *every* case, used by the
# analysis sidebar. Computed lazily (only when a template asks
# for them) and cached for the lifetime of the request.
# =========================================================

def sidebar_stats():

    cached = getattr(g, "_sidebar_stats", None)

    if cached is not None:
        return cached


    stats = {

        "cases":
            Case.query.count(),

        "open_cases":
            Case.query
            .filter(func.lower(Case.status) == "open")
            .count(),

        "evidence":
            Evidence.query.count(),

        "events":
            Event.query.count(),

        # The timeline only plots events that carry a timestamp
        "timeline":
            Event.query
            .filter(Event.timestamp.isnot(None))
            .count(),

        "incidents":
            Incident.query.count(),

        "memory":
            MemoryAnalysis.query.count()

    }


    g._sidebar_stats = stats

    return stats
