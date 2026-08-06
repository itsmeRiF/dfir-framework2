from sqlalchemy import func

from database.db import db

from models.case import Case
from models.evidence import Evidence
from models.event import Event
from models.incident import Incident
from models.memory_ioc import MemoryIOC
from models.memory_network import MemoryNetwork
from models.memory_process import MemoryProcess


# The Memory tab counts what the memory pages list: extracted
# processes, network connections and IOCs.
MEMORY_MODELS = (MemoryProcess, MemoryNetwork, MemoryIOC)


# =========================================================
# GLOBAL (ALL-CASES) STATISTICS
#
# Powers /analysis/dashboard/ — the same numbers the sidebar
# tabs show, rolled up across every case and broken down per
# case for the charts.
# =========================================================


# Categorical slots, in the fixed order that keeps neighbouring
# hues apart for colour-blind readers. A case keeps its slot in
# every chart, so the colour identifies the case and never its
# rank. Past 8 cases the tail folds into a neutral "Other".
CASE_PALETTE = [
    "#2a78d6",   # blue
    "#eb6834",   # orange
    "#1baf7a",   # aqua
    "#eda100",   # yellow
    "#e87ba4",   # magenta
    "#008300",   # green
    "#4a3aa7",   # violet
    "#e34948",   # red
]

OTHER_COLOR = "#898781"

# Slices a pie can carry before the tail is folded together.
MAX_SLICES = len(CASE_PALETTE)


def _counts_by_case(model, *filters):
    """{case_id: row count} for one model, optionally filtered."""

    query = db.session.query(
        model.case_id,
        func.count(model.id)
    )

    for condition in filters:
        query = query.filter(condition)

    return dict(
        query.group_by(model.case_id).all()
    )


def totals():
    """Headline numbers — one per sidebar tab."""

    cases = Case.query.count()

    open_cases = (
        Case.query
        .filter(func.lower(Case.status) == "open")
        .count()
    )

    return {

        "cases": cases,

        "open_cases": open_cases,

        "closed_cases": cases - open_cases,

        "evidence": Evidence.query.count(),

        "events": Event.query.count(),

        # The timeline only plots events that carry a timestamp
        "timeline":
            Event.query
            .filter(Event.timestamp.isnot(None))
            .count(),

        "incidents": Incident.query.count(),

        "memory": sum(
            model.query.count()
            for model in MEMORY_MODELS
        )

    }


def per_case():
    """One row per case carrying every sidebar-tab count."""

    cases = (
        Case.query
        .order_by(
            Case.created_at.desc(),
            Case.id.desc()
        )
        .all()
    )

    evidence = _counts_by_case(Evidence)
    events = _counts_by_case(Event)
    timeline = _counts_by_case(Event, Event.timestamp.isnot(None))
    incidents = _counts_by_case(Incident)

    memory = {}

    for model in MEMORY_MODELS:
        for case_id, count in _counts_by_case(model).items():
            memory[case_id] = memory.get(case_id, 0) + count

    # Everything fits the palette, or the tail past slot 7 shares
    # the neutral colour it will be folded into.
    folded = len(cases) > MAX_SLICES

    rows = []

    for index, case in enumerate(cases):

        if folded and index >= MAX_SLICES - 1:
            colour = OTHER_COLOR
        else:
            colour = CASE_PALETTE[index]

        rows.append({

            "id": case.id,

            "color": colour,

            "name": case.case_name or ("Case #%s" % case.id),

            "number": case.case_number or ("#%s" % case.id),

            "status": (case.status or "open").lower(),

            "evidence": evidence.get(case.id, 0),

            "events": events.get(case.id, 0),

            "timeline": timeline.get(case.id, 0),

            "incidents": incidents.get(case.id, 0),

            "memory": memory.get(case.id, 0)

        })

    return rows


def top_rules(limit=8):
    """Most frequently triggered detection rules, across all cases."""

    rows = (
        db.session.query(
            Event.rule_title,
            func.count(Event.id)
        )
        .filter(Event.rule_title.isnot(None))
        .group_by(Event.rule_title)
        .order_by(func.count(Event.id).desc())
        .limit(limit)
        .all()
    )

    return [
        {"label": title, "count": hits}
        for title, hits in rows
    ]


def top_hosts(limit=8):
    """Noisiest machines, across all cases."""

    rows = (
        db.session.query(
            Event.computer,
            func.count(Event.id)
        )
        .filter(Event.computer.isnot(None))
        .group_by(Event.computer)
        .order_by(func.count(Event.id).desc())
        .limit(limit)
        .all()
    )

    return [
        {"label": computer, "count": hits}
        for computer, hits in rows
    ]


def overview():
    """Everything the all-cases dashboard renders."""

    return {
        "totals": totals(),
        "cases": per_case(),
        "palette": CASE_PALETTE,
        "max_slices": MAX_SLICES,
        "other_color": OTHER_COLOR,
        "top_rules": top_rules(),
        "top_hosts": top_hosts()
    }
