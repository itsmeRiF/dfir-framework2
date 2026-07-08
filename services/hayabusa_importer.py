import csv

from models.event import Event
from database.db import db



def import_hayabusa_csv(
        csv_file,
        case_id
):


    count = 0


    with open(
        csv_file,
        encoding="utf-8"
    ) as f:


        reader = csv.DictReader(f)


        for row in reader:


            event = Event(

                case_id=case_id,

                timestamp=row.get(
                    "Timestamp"
                ),

                channel=row.get(
                    "Channel"
                ),

                event_id=row.get(
                    "EventID"
                ),

                severity=row.get(
                    "Level"
                ),

                rule_title=row.get(
                    "RuleTitle"
                ),

                computer=row.get(
                    "Computer"
                ),

                details=row.get(
                    "Details"
                )

            )


            db.session.add(event)

            count += 1



    db.session.commit()


    return count
