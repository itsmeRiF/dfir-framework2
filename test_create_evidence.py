from app import create_app

from database.db import db
from models.evidence import Evidence


app = create_app()


with app.app_context():

    evidence = Evidence(

        case_id=1,

        filename="2_Security.evtx",

        original_filename="2_Security.evtx",

        filepath=r"K:\CyberX-DFIR-framework2\dfir-framework2\uploads\2_Security.evtx",

        filesize=20975616,

        artifact_type="evtx",

        parser="hayabusa",

        status="Queued"

    )


    db.session.add(
        evidence
    )

    db.session.commit()


    print(
        "Created Evidence ID:",
        evidence.id
    )