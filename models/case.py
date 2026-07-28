from database.db import db
from datetime import datetime


class Case(db.Model):

    __tablename__ = "cases"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # Human readable case number
    case_number = db.Column(
        db.String(50),
        unique=True,
        index=True
    )

    case_name = db.Column(
        db.String(100),
        nullable=False
    )

    description = db.Column(
        db.Text
    )


    # Incident Classification

    incident_type = db.Column(
        db.String(100)
    )

    priority = db.Column(
        db.String(50),
        default="medium"
    )

    severity = db.Column(
        db.String(50),
        default="medium"
    )


    # Organization Details

    organization = db.Column(
        db.String(255)
    )

    department = db.Column(
        db.String(255)
    )


    # Investigation

    lead_investigator = db.Column(
        db.String(255)
    )


    status = db.Column(
        db.String(50),
        default="open"
    )


    incident_date = db.Column(
        db.DateTime,
        nullable=True
    )


    tags = db.Column(
        db.String(500)
    )


    remarks = db.Column(
        db.Text
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


    closed_at = db.Column(
        db.DateTime,
        nullable=True
    )


    # -----------------------------
    # Helpers
    # -----------------------------

    def generate_case_number(self):

        year = self.created_at.year if self.created_at else datetime.utcnow().year

        self.case_number = (
            f"CX-{year}-{self.id:04d}"
        )


    def __repr__(self):

        return (
            f"<Case "
            f"{self.case_number} "
            f"{self.case_name}>"
        )