from database.db import db
from datetime import datetime


class Evidence(db.Model):

    __tablename__ = "evidence"

    id = db.Column(db.Integer, primary_key=True)

    case_id = db.Column(db.Integer, db.ForeignKey("cases.id"))

    filename = db.Column(db.String(255), nullable=False)

    filepath = db.Column(db.String(500), nullable=False)

    artifact_type = db.Column(db.String(50), default="evtx")

    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
