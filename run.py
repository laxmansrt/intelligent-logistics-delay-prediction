"""
run.py
=======
Main entry point for the Logistics BDT application.

Usage:
    python run.py

The app reads all configuration from the .env file (see .env.example).
Make sure MongoDB is running before starting the server.

macOS quick start:
    brew services start mongodb-community
    python run.py
"""

import sys
from pathlib import Path

# Add the project root to sys.path so all packages resolve correctly
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app import create_app
from backend.config import Config
from backend.utils.logger import get_logger

logger = get_logger("run")


def main():
    logger.info("=" * 75)
    logger.info("  BIG DATA CLASSIFICATION AND PREDICTION FOR TRANSPORTATION")
    logger.info("  AND LOGISTICS USING APACHE HIVE")
    logger.info("=" * 75)
    logger.info("Storage mode : %s", Config.STORAGE_MODE)
    logger.info("Spark mode   : %s (%s)", Config.SPARK_MODE, Config.SPARK_MASTER)
    logger.info("MongoDB      : %s / %s", Config.MONGO_URI, Config.MONGO_DB_NAME)
    logger.info("Dashboard    : http://localhost:%s", Config.PORT)
    logger.info("API Health   : http://localhost:%s/api/v1/health", Config.PORT)
    logger.info("-" * 60)

    app = create_app()
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
        use_reloader=Config.DEBUG,
    )


if __name__ == "__main__":
    main()

