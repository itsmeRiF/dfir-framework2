from database.db import db


class MemoryNetwork(db.Model):

    __tablename__ = "memory_networks"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    case_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )


    protocol = db.Column(
        db.String(20)
    )


    local_address = db.Column(
        db.String(100)
    )


    remote_address = db.Column(
        db.String(100)
    )


    state = db.Column(
        db.String(50)
    )


    pid = db.Column(
        db.Integer
    )


    process_name = db.Column(
        db.String(255)
    )


    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )