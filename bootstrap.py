"""Bootstrap default analyst user and folders."""

import os
from app import create_app
from database.db import db
from models.user import User


def main():
    app = create_app()
    with app.app_context():
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)
        os.makedirs(os.path.join(os.path.dirname(__file__), "instance"), exist_ok=True)

        if not User.query.filter_by(username="admin").first():
            db.session.add(User(username="analyst", password="analyst123", role="analyst"))
            db.session.commit()
            print("Created default user: analyst / analyst123")
        else:
            print("Default user already exists")


if __name__ == "__main__":
    main()
