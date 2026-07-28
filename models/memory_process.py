from database.db import db


class MemoryProcess(db.Model):

    __tablename__ = "memory_processes"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    case_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )


    pid = db.Column(
        db.Integer
    )


    ppid = db.Column(
        db.Integer
    )


    process_name = db.Column(
        db.String(255)
    )


    username = db.Column(
        db.String(255)
    )


    path = db.Column(
        db.Text
    )


    command_line = db.Column(
        db.Text
    )


    risk = db.Column(
        db.String(50),
        default="low"
    )


    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )