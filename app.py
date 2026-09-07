from flask import Flask, render_template, redirect, request, url_for
from flask_login import current_user
from modules.parser.registry import register_parsers
from config import Config
from database.db import db
import os
from flask_migrate import Migrate
from routes.auth import auth_bp, login_manager
from routes.dashboard import dashboard_bp
from routes.cases import cases_bp
from routes.evidence import evidence_bp
from routes.events import events_bp
from routes.timeline import timeline_bp
from routes.incidents import incident_bp
from routes.analysis import analysis_bp
from routes.event_detail import event_detail_bp
from routes.incidents import incident_bp
from routes.memory import memory_bp
from utils.sidebar_stats import sidebar_stats


# The only things an unauthenticated request may reach: the login
# form itself and the assets that page needs to render.
PUBLIC_ENDPOINTS = {
    "auth.login",
    "static"
}


def create_app():

    app = Flask(__name__)
    
    app.config.from_object(Config)
    register_parsers()

    db.init_app(app)

    migrate = Migrate(
        app,
        db
    )
    login_manager.init_app(app)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(cases_bp)
    app.register_blueprint(evidence_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(timeline_bp)
    app.register_blueprint(incident_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(event_detail_bp)
    app.register_blueprint(memory_bp)
    @app.before_request
    def require_login():
        # Case data is behind the login page everywhere, rather than
        # per route: a view added later is protected by default, and
        # forgetting a decorator cannot expose one.
        #
        # Unmatched URLs are guarded too, so which routes exist is
        # not something a logged-out visitor can probe.

        if request.endpoint in PUBLIC_ENDPOINTS:
            return None

        if current_user.is_authenticated:
            return None

        return login_manager.unauthorized()

    @app.context_processor
    def inject_sidebar_stats():
        # Exposed as a callable so the counts are only queried
        # when a template actually renders the sidebar.
        return {"sidebar_stats": sidebar_stats}

    with app.app_context():
        db.create_all()

    @app.route("/")
    def index():
        return redirect(url_for("auth.login"))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=1338)
