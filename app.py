from flask import Flask, redirect, url_for
from config import Config
from database.db import db
import os
from routes.auth import auth_bp, login_manager
from routes.dashboard import dashboard_bp
from routes.cases import cases_bp
from routes.evidence import evidence_bp
from routes.events import events_bp
from routes.timeline import timeline_bp
from routes.incidents import incident_bp
from routes.analysis import analysis_bp
##adding new routes -fingersCrossed
from routes.memory import memory_bp
from routes.registry import registry_bp
from routes.prefetch import prefetch_bp
from routes.browser import browser_bp
from routes.jumplist import jumplist_bp
from routes.mft import mft_bp
from routes.usn import usn_bp
from routes.srum import srum_bp
from routes.recyclebin import recyclebin_bp
from routes.reports import reports_bp

def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
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
## yahan new blueprints ko register karre.. yahan bhi fingers crossed!
    app.register_blueprint(memory_bp)
    app.register_blueprint(registry_bp)
    app.register_blueprint(prefetch_bp)
    app.register_blueprint(browser_bp)
    app.register_blueprint(jumplist_bp)
    app.register_blueprint(mft_bp)
    app.register_blueprint(usn_bp)
    app.register_blueprint(srum_bp)
    app.register_blueprint(recyclebin_bp)
    app.register_blueprint(reports_bp)
    with app.app_context():
        db.create_all()

    @app.route("/")
    def index():
        return redirect(url_for("auth.login"))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=1338, use_reloader=False)
