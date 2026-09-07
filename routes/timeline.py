from flask import Blueprint, render_template, request
from datetime import datetime
import json

from models.case import Case
from models.event import Event

from utils.timezone import format_ist, to_ist


timeline_bp = Blueprint(
    "timeline",
    __name__
)


# Rows the table renders. The chart still plots every event in range —
# only the table is capped, because ten thousand rows of DOM make the
# page crawl. Narrow the range, or use the event explorer, for the rest.
ROW_CAP = 500


@timeline_bp.route("/timeline/<int:case_id>")
def timeline(case_id):

    case = Case.query.get_or_404(case_id)

    start = request.args.get("start")

    end = request.args.get("end")


    query = Event.query.filter_by(
        case_id=case_id
    )


    def parse(value):
        """A malformed range is ignored rather than raising a 500."""

        if not value:
            return None

        try:
            return datetime.fromisoformat(value)

        except ValueError:
            return None


    start_at = parse(start)

    end_at = parse(end)


    if start_at:

        query = query.filter(
            Event.timestamp >= start_at
        )


    if end_at:

        query = query.filter(
            Event.timestamp <= end_at
        )


    events = query.order_by(
        Event.timestamp.asc()
    ).all()


    # Graph Data — bucketed by IST day, matching how every timestamp
    # on the page is rendered.

    freq = {}

    hosts = set()

    for e in events:

        if e.computer:
            hosts.add(e.computer)

        if not e.timestamp:
            continue

        day = to_ist(e.timestamp).strftime("%Y-%m-%d")

        freq[day] = freq.get(day, 0) + 1


    days = sorted(freq)

    busiest = max(
        freq.items(),
        key=lambda item: item[1],
        default=(None, 0)
    )


    stats = {

        "events": len(events),

        "days": len(days),

        "first": days[0] if days else None,

        "last": days[-1] if days else None,

        "busiest": (
            "%s · %s" % (busiest[0], "{:,}".format(busiest[1]))
            if busiest[0] else None
        ),

        "hosts": len(hosts),

    }


    graph_labels = json.dumps(days)

    graph_values = json.dumps(
        [freq[day] for day in days]
    )


    # The most recent slice, still shown oldest-first so the table
    # reads chronologically like the chart above it.
    visible = events[-ROW_CAP:]

    hidden = len(events) - len(visible)


    # Dropdowns list only what is actually in the table.

    severities = sorted({
        (e.severity or "informational").lower()
        for e in visible
    })

    channels = sorted({
        e.channel
        for e in visible
        if e.channel
    })


    return render_template(

        "analysis/timeline.html",

        events=visible,

        hidden=hidden,

        row_cap=ROW_CAP,

        case=case,

        case_id=case_id,

        stats=stats,

        severities=severities,

        channels=channels,

        format_ist=format_ist,

        start=start or "",

        end=end or "",

        graph_labels=graph_labels,

        graph_values=graph_values

    )
