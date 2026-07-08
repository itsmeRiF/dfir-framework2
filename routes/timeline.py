from flask import Blueprint, render_template, request
from models.event import Event
from datetime import datetime
import json


timeline_bp = Blueprint(
    "timeline",
    __name__
)



@timeline_bp.route("/timeline/<int:case_id>")
def timeline(case_id):


    start=request.args.get("start")

    end=request.args.get("end")


    query = Event.query.filter_by(
        case_id=case_id
    )


    if start:

        query=query.filter(
            Event.timestamp >= datetime.fromisoformat(start)
        )


    if end:

        query=query.filter(
            Event.timestamp <= datetime.fromisoformat(end)
        )


    events=query.order_by(
        Event.timestamp.asc()
    ).all()



    # Graph Data

    freq={}


    for e in events:

        if not e.timestamp:
            continue

        day = e.timestamp.strftime("%Y-%m-%d")

        freq[day] = freq.get(day,0) + 1

    graph_labels=json.dumps(
        list(freq.keys())
    )


    graph_values=json.dumps(
        list(freq.values())
    )



    return render_template(

        "timeline.html",

        events=events,

        case_id=case_id,

        start=start or "",

        end=end or "",

        graph_labels=graph_labels,

        graph_values=graph_values

    )
