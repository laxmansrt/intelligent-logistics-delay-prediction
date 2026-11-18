"""
scripts/init_db.py
===================
One-time MongoDB database initialisation script.

What it does:
    1. Connects to MongoDB using the config in .env
    2. Creates all collections (MongoDB auto-creates on first insert,
       but we do it explicitly to set options)
    3. Creates all indexes for optimal query performance
    4. Inserts a system metadata document

Usage:
    python scripts/init_db.py

Run this once after:
    - First cloning the project
    - Wiping the database
    - Changing the index structure
"""

import sys
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import Config
from database.mongo_client import get_database, ALL_COLLECTIONS
from database.indexes import create_all_indexes
from backend.utils.logger import get_logger

logger = get_logger("init_db")


def main():
    print("=" * 60)
    print("  MongoDB Database Initialisation")
    print(f"  URI: {Config.MONGO_URI}")
    print(f"  DB:  {Config.MONGO_DB_NAME}")
    print("=" * 60)

    db = get_database()
    if db is None:
        print("\n❌ Cannot connect to MongoDB.")
        print("   Make sure MongoDB is running:")
        print("   macOS:  brew services start mongodb-community")
        print("   Linux:  sudo systemctl start mongod")
        sys.exit(1)

    print("\n✓ Connected to MongoDB")

    # Create collections explicitly
    existing = db.list_collection_names()
    for col_name in ALL_COLLECTIONS:
        if col_name not in existing:
            db.create_collection(col_name)
            print(f"  Created collection: {col_name}")
        else:
            print(f"  Collection exists:  {col_name}")

    # Create indexes
    print("\nCreating indexes...")
    created = create_all_indexes(db)
    for col_name, indexes in created.items():
        print(f"  {col_name}: {len(indexes)} indexes")

    # Insert system metadata
    meta = db["system_meta"] if "system_meta" in db.list_collection_names() \
           else db.create_collection("system_meta")

    db["system_meta"].replace_one(
        {"_id": "init"},
        {
            "_id": "init",
            "project": "Intelligent Logistics Delay Prediction — BDT",
            "initialized_at": datetime.now(timezone.utc).isoformat(),
            "mongo_db": Config.MONGO_DB_NAME,
            "collections": ALL_COLLECTIONS,
        },
        upsert=True,
    )

    print("\n✅ Database initialisation complete.")
    print(f"   Database: {Config.MONGO_DB_NAME}")
    print(f"   Collections: {len(ALL_COLLECTIONS)}")
    print("\nNext steps:")
    print("  python run.py                          # start the app")
    print("  POST /api/v1/upload/load-sample        # load sample data")
    print("  python scripts/generate_sample_data.py # regenerate samples")


if __name__ == "__main__":
    main()

