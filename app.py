from flask import Flask, render_template, redirect, url_for
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
