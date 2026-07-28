from database.db import db
from datetime import datetime


class MemoryAnalysis(db.Model):

    __tablename__ = "memory_analysis"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    case_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )


    process_count = db.Column(
        db.Integer,
        default=0
    )


    network_count = db.Column(
        db.Integer,
        default=0
    )


    malfind_count = db.Column(
        db.Integer,
        default=0
    )


    dll_count = db.Column(
        db.Integer,
        default=0
    )


    driver_count = db.Column(
        db.Integer,
        default=0
    )


    service_count = db.Column(
        db.Integer,
        default=0
    )


    risk_score = db.Column(
        db.Integer,
        default=0
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )