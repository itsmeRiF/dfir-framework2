from database.db import db
from datetime import datetime


class Case(db.Model):

    __tablename__ = "cases"

    id = db.Column(db.Integer, primary_key=True)

    case_name = db.Column(db.String(100), nullable=False)

    description = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    status = db.Column(db.String(20), default="open")
