from sqlalchemy import func

from database.db import db

from models.case import Case
from models.evidence import Evidence
from models.event import Event
from models.incident import Incident
from models.memory_ioc import MemoryIOC
from models.memory_network import MemoryNetwork
from models.memory_process import MemoryProcess

from utils.timezone import to_ist


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


def _case_colours(cases):
    """{case_id: palette colour}, in the order the cases are given.

    Everything fits the palette, or the tail past slot 7 shares the
    neutral colour it will be folded into.
    """

    folded = len(cases) > MAX_SLICES

    return {

        case.id: (
            OTHER_COLOR
            if folded and index >= MAX_SLICES - 1
            else CASE_PALETTE[index]
        )

        for index, case in enumerate(cases)

    }


def _cases_newest_first():

    return (
        Case.query
        .order_by(
            Case.created_at.desc(),
            Case.id.desc()
        )
        .all()
    )


def case_chips():
    """{case_id: the label a cross-case row wears}.

    Every global view identifies a row's case the same way — same
    name, same number, same palette colour it has in the dashboard
    charts.
    """

    cases = _cases_newest_first()

    colours = _case_colours(cases)

    return {

        case.id: {

            "id": case.id,

            "color": colours[case.id],

            "name": case.case_name or ("Case #%s" % case.id),

            "number": case.case_number or ("#%s" % case.id),

            "status": (case.status or "open").lower()

        }

        for case in cases

    }


def chip_for(chips, case_id):
    """The chip for a case, inventing one for an orphaned row.

    A row whose case was deleted still lists, rather than breaking
    the page it appears on.
    """

    return chips.get(case_id, {

        "id": case_id,
        "color": OTHER_COLOR,
        "name": "Case #%s" % case_id,
        "number": "#%s" % case_id,
        "status": "unknown"

    })


def chip_options(chips, used_ids):
    """Chips for a filter dropdown — only cases actually on the page."""

    return [
        chip
        for case_id, chip in chips.items()
        if case_id in used_ids
    ]


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

    cases = _cases_newest_first()

    evidence = _counts_by_case(Evidence)
    events = _counts_by_case(Event)
    timeline = _counts_by_case(Event, Event.timestamp.isnot(None))
    incidents = _counts_by_case(Incident)

    memory = {}

    for model in MEMORY_MODELS:
        for case_id, count in _counts_by_case(model).items():
            memory[case_id] = memory.get(case_id, 0) + count

    colours = _case_colours(cases)

    rows = []

    for case in cases:

        rows.append({

            "id": case.id,

            "color": colours[case.id],

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


# =========================================================
# ALL-CASES EVIDENCE REPOSITORY
#
# Powers /analysis/evidence/ — every artifact ever uploaded,
# newest first, each row carrying the case it belongs to.
# =========================================================

def evidence_repository():

    chips = case_chips()

    items = (
        Evidence.query
        .order_by(
            Evidence.uploaded_at.desc(),
            Evidence.id.desc()
        )
        .all()
    )

    rows = [

        {
            "evidence": item,
            "case": chip_for(chips, item.case_id)
        }

        for item in items

    ]

    def status_count(name):

        return sum(
            1
            for item in items
            if (item.status or "").lower() == name
        )

    totals = {

        "evidence": len(items),

        "queued": status_count("queued"),

        "processing": status_count("processing"),

        "completed": status_count("completed"),

        "failed": status_count("failed"),

        "size_mb": round(
            sum(item.filesize or 0 for item in items) / (1024 * 1024),
            2
        ),

        "cases": len(chips),

        "cases_with_evidence": len({
            item.case_id for item in items
        })

    }

    # Filter dropdowns list only what is actually on the page.
    artifact_types = sorted({
        item.artifact_type
        for item in items
        if item.artifact_type
    })

    filter_cases = chip_options(
        chips,
        {item.case_id for item in items}
    )

    return {
        "rows": rows,
        "totals": totals,
        "artifact_types": artifact_types,
        "filter_cases": filter_cases
    }


# =========================================================
# ALL-CASES TIMELINE
#
# Powers /analysis/timeline/ — daily activity for every case
# on one axis, so investigations can be lined up against each
# other. Only the timestamp column is read: the chart needs
# nothing else, and there can be a lot of events.
# =========================================================

def timeline_overview(start=None, end=None, recent_limit=100):

    chips = case_chips()

    query = (
        db.session.query(
            Event.case_id,
            Event.timestamp
        )
        .filter(Event.timestamp.isnot(None))
    )

    if start:
        query = query.filter(Event.timestamp >= start)

    if end:
        query = query.filter(Event.timestamp <= end)

    stamps = query.all()

    # {day: {case_id: count}} — the stacked bars.
    days = {}

    # Per-case span, for the breakdown table.
    spans = {}

    for case_id, when in stamps:

        # Bucketed by IST day, because IST is what every timestamp
        # on the page is rendered in.
        day = to_ist(when).strftime("%Y-%m-%d")

        days.setdefault(day, {})
        days[day][case_id] = days[day].get(case_id, 0) + 1

        span = spans.setdefault(case_id, {
            "events": 0,
            "first": when,
            "last": when
        })

        span["events"] += 1
        span["first"] = min(span["first"], when)
        span["last"] = max(span["last"], when)

    labels = sorted(days)

    used_ids = set(spans)

    # One series per case, aligned to the shared day axis.
    series = [
        {
            "id": chip["id"],
            "name": chip["name"],
            "color": chip["color"],
            "values": [
                days[day].get(chip["id"], 0)
                for day in labels
            ]
        }
        for chip in chip_options(chips, used_ids)
    ]

    rows = sorted(
        (
            {
                "case": chip_for(chips, case_id),
                "events": span["events"],
                "first": span["first"],
                "last": span["last"],
                "days": to_ist(span["last"]).date().toordinal()
                - to_ist(span["first"]).date().toordinal() + 1
            }
            for case_id, span in spans.items()
        ),
        key=lambda row: row["events"],
        reverse=True
    )

    busiest = max(
        (
            (day, sum(counts.values()))
            for day, counts in days.items()
        ),
        key=lambda item: item[1],
        default=(None, 0)
    )

    recent_query = (
        Event.query
        .filter(Event.timestamp.isnot(None))
    )

    if start:
        recent_query = recent_query.filter(Event.timestamp >= start)

    if end:
        recent_query = recent_query.filter(Event.timestamp <= end)

    recent = [

        {
            "event": event,
            "case": chip_for(chips, event.case_id)
        }

        for event in (
            recent_query
            .order_by(Event.timestamp.desc(), Event.id.desc())
            .limit(recent_limit)
            .all()
        )

    ]

    return {

        "labels": labels,

        "series": series,

        "rows": rows,

        "recent": recent,

        "recent_limit": recent_limit,

        "filter_cases": chip_options(chips, used_ids),

        "totals": {

            "events": len(stamps),

            "days": len(labels),

            "cases": len(spans),

            "first": min(
                (span["first"] for span in spans.values()),
                default=None
            ),

            "last": max(
                (span["last"] for span in spans.values()),
                default=None
            ),

            "busiest_day": busiest[0],

            "busiest_count": busiest[1]

        }

    }


# =========================================================
# ALL-CASES INCIDENTS
#
# Powers /analysis/incidents/ — every correlated detection
# raised in any case, worst first.
# =========================================================

SEVERITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "med": 2,
    "low": 3,
    "informational": 4,
    "information": 4,
    "info": 4
}


def _severity_rank(value):

    return SEVERITY_ORDER.get(
        (value or "").lower().strip(),
        5
    )


def incident_overview():

    chips = case_chips()

    incidents = Incident.query.all()

    rows = sorted(
        (
            {
                "incident": incident,
                "case": chip_for(chips, incident.case_id),
                "severity": (incident.severity or "unknown").lower()
            }
            for incident in incidents
        ),
        key=lambda row: (
            _severity_rank(row["severity"]),
            -(row["incident"].event_count or 0)
        )
    )

    def severity_count(*names):

        return sum(
            1
            for row in rows
            if row["severity"] in names
        )

    totals = {

        "incidents": len(rows),

        "critical": severity_count("critical"),

        "high": severity_count("high"),

        "medium": severity_count("medium", "med"),

        "low": severity_count("low"),

        "events": sum(
            row["incident"].event_count or 0
            for row in rows
        ),

        "cases_affected": len({
            row["incident"].case_id
            for row in rows
        })

    }

    return {

        "rows": rows,

        "totals": totals,

        "filter_cases": chip_options(
            chips,
            {row["incident"].case_id for row in rows}
        ),

        "severities": sorted(
            {row["severity"] for row in rows},
            key=_severity_rank
        )

    }


# =========================================================
# ALL-CASES MEMORY
#
# Powers /analysis/memory/ — the processes, connections and
# IOCs the memory pages list, pooled across every case.
#
# Repeated captures of the same host write the same row more
# than once, so each table is de-duplicated per case exactly
# as the per-case memory page does it.
# =========================================================

# Rows a single table renders before the tail is left to the
# per-case page.
MEMORY_ROW_CAP = 1000


def _dedup(items, key):

    seen = set()

    unique = []

    for item in items:

        signature = key(item)

        if signature in seen:
            continue

        seen.add(signature)
        unique.append(item)

    return unique


def memory_overview(row_cap=MEMORY_ROW_CAP):

    chips = case_chips()

    processes = _dedup(
        MemoryProcess.query
        .order_by(MemoryProcess.case_id, MemoryProcess.pid)
        .all(),
        lambda p: (p.case_id, p.pid, p.ppid, p.process_name)
    )

    networks = _dedup(
        MemoryNetwork.query
        .order_by(MemoryNetwork.case_id, MemoryNetwork.id)
        .all(),
        lambda n: (
            n.case_id,
            n.protocol,
            n.local_address,
            n.remote_address,
            n.state,
            n.pid,
            n.process_name
        )
    )

    iocs = _dedup(
        MemoryIOC.query
        .order_by(MemoryIOC.case_id, MemoryIOC.id)
        .all(),
        lambda i: (
            i.case_id,
            i.ioc_type,
            i.indicator,
            i.severity,
            (i.description or "")[:100]
        )
    )

    # Worst first — an analyst opening this page is looking for
    # the risky rows, not row 1 of case 1.
    iocs.sort(key=lambda i: _severity_rank(i.severity))

    processes.sort(key=lambda p: _severity_rank(p.risk))

    def table(items):

        return {

            "rows": [
                {
                    "item": item,
                    "case": chip_for(chips, item.case_id)
                }
                for item in items[:row_cap]
            ],

            "total": len(items),

            "hidden": max(len(items) - row_cap, 0)

        }

    used_ids = {
        item.case_id
        for group in (processes, networks, iocs)
        for item in group
    }

    return {

        "processes": table(processes),

        "networks": table(networks),

        "iocs": table(iocs),

        "filter_cases": chip_options(chips, used_ids),

        "totals": {

            "processes": len(processes),

            "networks": len(networks),

            "iocs": len(iocs),

            "risky_processes": sum(
                1
                for item in processes
                if _severity_rank(item.risk) <= 1
            ),

            "high_iocs": sum(
                1
                for item in iocs
                if _severity_rank(item.severity) <= 1
            ),

            "cases_with_memory": len(used_ids)

        }

    }


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
