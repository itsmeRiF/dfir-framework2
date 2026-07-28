from app import create_app

from modules.events.importer import EventImporter

from models.event import Event


app = create_app()


sample_event = {

    "timestamp": "2026-06-29 10:45:18",

    "source": "Sec",

    "artifact": "evtx",

    "computer": "AlphaM",

    "user": "kioskUser0",

    "event_id": "5379",

    "severity": "low",

    "message": "Credential Manager Enumerated",

    "details": "Test event",

    "rule_id": "test-rule",

    "raw": {

        "RecordID": "725665",

        "ExtraFieldInfo": "Test info"

    }

}


with app.app_context():

    count = EventImporter.import_events(

        [
            sample_event
        ],

        case_id=1

    )


    print(
        "Imported:",
        count
    )


    event = Event.query.first()


    print(
        event.event_id,
        event.rule_title,
        event.computer
    )