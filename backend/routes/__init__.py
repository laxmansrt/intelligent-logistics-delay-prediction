"""
backend/routes/__init__.py
===========================
Registers all API blueprints with the Flask application.

Adding a new module:
    1. Create backend/routes/my_module.py with a Blueprint named my_module_bp
    2. Import and add it to BLUEPRINTS below
    3. It will be auto-registered under /api/v1/
"""

from flask import Flask
from backend.routes.health import health_bp
from backend.routes.upload import upload_bp
from backend.routes.predict import predict_bp
from backend.routes.shipments import shipments_bp
from backend.routes.analytics import analytics_bp
from backend.routes.jobs import jobs_bp

# List all blueprints and their URL prefixes
BLUEPRINTS = [
    (health_bp, "/api/v1"),
    (upload_bp, "/api/v1"),
    (predict_bp, "/api/v1"),
    (shipments_bp, "/api/v1"),
    (analytics_bp, "/api/v1"),
    (jobs_bp, "/api/v1"),
]


def register_routes(app: Flask) -> None:
    """Register all API blueprints with the given Flask app."""
    for blueprint, url_prefix in BLUEPRINTS:
        app.register_blueprint(blueprint, url_prefix=url_prefix)

