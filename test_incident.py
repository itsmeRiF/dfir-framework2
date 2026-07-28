from app import create_app

from models.event import Event

from modules.engine.incident_service import IncidentService


app = create_app()


with app.app_context():


    events = Event.query.filter_by(
        case_id=1
    ).all()


    data = []


    for e in events:

        data.append({

            "event_id": e.event_id,

            "timestamp": e.timestamp,

            "rule_title": e.rule_title,

            "severity": e.severity,

            "channel": e.channel

        })


    incidents = IncidentService.generate(
        1,
        data
    )


    print(
        "Created:",
        len(incidents)
    )


    for i in incidents:

        print(
            i.title,
            i.severity,
            i.event_count
        )