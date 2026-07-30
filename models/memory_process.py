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
        db.Integer,
        index=True
    )


    ppid = db.Column(
        db.Integer,
        index=True
    )


    process_name = db.Column(
        db.String(255),
        index=True
    )


    # Filled automatically after parsing
    parent_name = db.Column(
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


    created_time = db.Column(
        db.String(100)
    )


    exit_time = db.Column(
        db.String(100)
    )


    thread_count = db.Column(
        db.Integer,
        default=0
    )


    handle_count = db.Column(
        db.Integer,
        default=0
    )


    wow64 = db.Column(
        db.Boolean,
        default=False
    )


    session_id = db.Column(
        db.Integer
    )


    risk = db.Column(
        db.String(50),
        default="low"
    )


    risk_reason = db.Column(
        db.Text
    )


    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )