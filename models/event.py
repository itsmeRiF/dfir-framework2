from database.db import db
from datetime import datetime


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)

    case_id = db.Column(db.Integer, db.ForeignKey("cases.id"), index=True)

    timestamp = db.Column(db.DateTime, index=True)

    computer = db.Column(db.String(255), index=True)
    channel = db.Column(db.String(100))

    event_id = db.Column(db.String(50), index=True)
    record_id = db.Column(db.String(50))

    rule_title = db.Column(db.String(255), index=True)
    rule_id = db.Column(db.String(255))

    severity = db.Column(db.String(50), index=True)

    details = db.Column(db.Text)
    extra_info = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
