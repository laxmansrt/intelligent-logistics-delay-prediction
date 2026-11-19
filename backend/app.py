"""
backend/app.py
==============
Flask application factory.

Using the factory pattern (create_app()) makes it easy to:
  - Create the app with different configs for testing vs production
  - Avoid circular imports
  - Initialise extensions in the right order

BDT Concept: This is the central hub that ties together the Flask web
server, MongoDB database, and all processing modules.
"""

from flask import Flask, jsonify
from flask_cors import CORS
from backend.config import Config
from backend.extensions import init_db
from backend.routes import register_routes
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def create_app() -> Flask:
    """
    Application factory.
    Returns a fully configured Flask application instance.

    Usage:
        app = create_app()
        app.run(...)
    """
    app = Flask(
        __name__,
        # Serve HTML templates from frontend/templates/
        template_folder="../frontend/templates",
        # Serve static files (CSS, JS, images) from frontend/static/
        static_folder="../frontend/static",
        static_url_path="/static",
    )

    # ── Load configuration ────────────────────────────────
    app.config["SECRET_KEY"] = Config.SECRET_KEY
    app.config["DEBUG"] = Config.DEBUG
    app.config["MAX_CONTENT_LENGTH"] = Config.MAX_CONTENT_LENGTH
    app.config["MONGO_URI"] = Config.MONGO_URI
    app.config["MONGO_DB_NAME"] = Config.MONGO_DB_NAME
    app.config["UPLOAD_FOLDER"] = str(Config.RAW_DIR)

    # ── Create required directories ───────────────────────
    Config.ensure_directories()

    # ── CORS (allow frontend on same host during development) ──
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ── Database ──────────────────────────────────────────
    db_ok = init_db(app)
    if not db_ok:
        logger.warning(
            "Starting without MongoDB. Run: brew services start mongodb-community"
        )

    # ── Register API routes ───────────────────────────────
    register_routes(app)

    # ── Frontend Template Routes ──────────────────────────
    @app.route("/")
    def index():
        from flask import render_template
        return render_template("index.html")

    @app.route("/shipments-page")
    def shipments_page():
        from flask import render_template
        return render_template("shipments.html")

    @app.route("/predict-page")
    def predict_page():
        from flask import render_template
        return render_template("predict.html")

    @app.route("/analytics-page")
    def analytics_page():
        from flask import render_template
        return render_template("analytics.html")

    @app.route("/processing-page")
    def processing_page():
        from flask import render_template
        return render_template("processing.html")

    @app.route("/model-page")
    def model_page():
        from flask import render_template
        return render_template("model.html")

    @app.route("/hive-page")
    def hive_page():
        from flask import render_template
        return render_template("hive.html")

    @app.route("/upload-page")
    def upload_page():
        from flask import render_template
        return render_template("upload.html")

    # ── Global error handlers ─────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "success": False,
            "error": "NotFound",
            "message": str(e),
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({
            "success": False,
            "error": "MethodNotAllowed",
            "message": str(e),
        }), 405

    @app.errorhandler(413)
    def file_too_large(e):
        return jsonify({
            "success": False,
            "error": "FileTooLarge",
            "message": f"File exceeds the {Config.MAX_UPLOAD_MB} MB limit.",
        }), 413

    @app.errorhandler(500)
    def internal_error(e):
        logger.error("Internal server error: %s", e)
        return jsonify({
            "success": False,
            "error": "InternalServerError",
            "message": "An unexpected error occurred. Check the server logs.",
        }), 500

    logger.info(
        "Flask app created | storage=%s | spark=%s | db=%s",
        Config.STORAGE_MODE,
        Config.SPARK_MODE,
        Config.MONGO_DB_NAME,
    )
    return app

