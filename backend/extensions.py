"""
backend/extensions.py
======================
Initialises shared Flask extensions and the MongoDB client.
Using this module avoids circular imports between app.py and routes.

BDT Concept: MongoDB is a NoSQL document store ideal for heterogeneous
logistics records where schema evolves frequently.
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Global MongoDB client and database references.
# They are set by init_db() after the Flask app is created.
mongo_client: MongoClient | None = None
db = None  # pymongo.database.Database


def init_db(app) -> bool:
    """
    Initialise the MongoDB connection using settings from the Flask app config.

    Called once from app.py during app creation.
    Returns True on success, False if connection fails.

    The connection uses a short serverSelectionTimeoutMS so the app starts
    quickly even if MongoDB is unavailable — routes will return 503 in that case.
    """
    global mongo_client, db

    mongo_uri: str = app.config.get("MONGO_URI", "mongodb://localhost:27017/")
    db_name: str = app.config.get("MONGO_DB_NAME", "logistics_bdt")

    try:
        mongo_client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=3000,  # 3 second timeout
        )
        # Force a connection check
        mongo_client.admin.command("ping")
        db = mongo_client[db_name]
        logger.info("MongoDB connected → database: '%s'", db_name)
        return True

    except (ConnectionFailure, ServerSelectionTimeoutError) as exc:
        logger.warning(
            "MongoDB connection failed: %s. "
            "The app will start but database features will be unavailable. "
            "Start MongoDB with: brew services start mongodb-community",
            exc,
        )
        return False


def get_db():
    """
    Return the active database handle.
    Raises RuntimeError if init_db() was never called or failed.
    """
    if db is None:
        raise RuntimeError(
            "Database not initialised. "
            "Check that MongoDB is running and MONGO_URI is correct."
        )
    return db


def get_collection(name: str):
    """Convenience wrapper to get a named collection from the active database."""
    return get_db()[name]

