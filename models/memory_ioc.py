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


    # IOC Classification

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
        db.String(50),
        default="medium"
    )


    # =========================
    # Memory Specific Fields
    # =========================


    pid = db.Column(
        db.Integer,
        nullable=True
    )


    process_name = db.Column(
        db.String(255),
        nullable=True
    )


    offset = db.Column(
        db.String(100),
        nullable=True
    )


    address = db.Column(
        db.String(100),
        nullable=True
    )


    finding = db.Column(
        db.Text,
        nullable=True
    )


    # Short analyst description

    description = db.Column(
        db.Text
    )


    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )