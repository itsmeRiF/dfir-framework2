from database.db import db
from datetime import datetime


class Evidence(db.Model):

    __tablename__ = "evidence"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    case_id = db.Column(
        db.Integer,
        db.ForeignKey("cases.id"),
        nullable=False,
        index=True
    )

    # ----------------------------------
    # File Information
    # ----------------------------------

    filename = db.Column(
        db.String(255),
        nullable=False
    )

    original_filename = db.Column(
        db.String(255)
    )

    filepath = db.Column(
        db.String(500),
        nullable=False
    )

    filesize = db.Column(
        db.BigInteger,
        default=0
    )

    # ----------------------------------
    # Artifact
    # ----------------------------------

    artifact_type = db.Column(
        db.String(100),
        index=True
    )

    parser = db.Column(
        db.String(100)
    )

    status = db.Column(
        db.String(50),
        default="Queued"
    )

    # ----------------------------------
    # Hashes
    # ----------------------------------

    md5 = db.Column(
        db.String(32),
        index=True
    )

    sha1 = db.Column(
        db.String(40),
        index=True
    )

    sha256 = db.Column(
        db.String(64),
        unique=True,
        index=True
    )

    sha512 = db.Column(
        db.String(128)
    )

    # ----------------------------------
    # Timestamps
    # ----------------------------------

    uploaded_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
    started_at = db.Column(
        db.DateTime,
        nullable=True
    )

    completed_at = db.Column(
        db.DateTime,
        nullable=True
    )

    error_message = db.Column(
        db.Text,
        nullable=True
    )
    
    
    
    

    # ----------------------------------
    # Helpers
    # ----------------------------------

    @property
    def extension(self):

        if "." not in self.filename:
            return ""

        return self.filename.rsplit(".", 1)[1].lower()

    @property
    def size_mb(self):

        return round(
            self.filesize / (1024 * 1024),
            2
        )

    def to_dict(self):

        return {

            "id": self.id,

            "case_id": self.case_id,

            "filename": self.filename,

            "original_filename": self.original_filename,

            "filepath": self.filepath,

            "artifact_type": self.artifact_type,

            "parser": self.parser,

            "status": self.status,

            "filesize": self.filesize,

            "md5": self.md5,

            "sha1": self.sha1,

            "sha256": self.sha256,

            "sha512": self.sha512,

            "uploaded_at": self.uploaded_at.isoformat()
            if self.uploaded_at else None
            
            

        }

    def __repr__(self):

        return (
            f"<Evidence "
            f"id={self.id} "
            f"file='{self.filename}' "
            f"type='{self.artifact_type}'>"
        )