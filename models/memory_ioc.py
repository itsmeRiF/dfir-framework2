from database.db import db


class MemoryIOC(db.Model):

    __tablename__ = "memory_iocs"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    case_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )


    ioc_type = db.Column(
        db.String(50)
    )


    indicator = db.Column(
        db.Text
    )


    source = db.Column(
        db.String(100)
    )


    severity = db.Column(
        db.String(50)
    )


    description = db.Column(
        db.Text
    )


    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )