from app import create_app

from models.evidence import Evidence

from modules.engine.evidence_worker import EvidenceWorker


app = create_app()


with app.app_context():

    evidence = Evidence.query.first()

    if not evidence:

        print(
            "No evidence found"
        )

    else:

        result = EvidenceWorker.process(
            evidence
        )

        print(
            result
        )