import os
import time

from pymongo import MongoClient, ReadPreference
from pymongo.errors import ServerSelectionTimeoutError

MONGO_REPLICA_URI = os.getenv("MONGO_REPLICA_URI", "")
DB_NAME = os.getenv("DB_NAME", "GreenCoop")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "ObsProEtAmateur")
ENABLE_REPLICA_TESTS = os.getenv("ENABLE_REPLICA_TESTS", "false").lower() == "true"


def test_read_secondary():
    client = MongoClient(
        MONGO_REPLICA_URI,
        read_preference=ReadPreference.SECONDARY,
        serverSelectionTimeoutMS=5000,
    )
    collection = client[DB_NAME][COLLECTION_NAME]

    start = time.perf_counter()
    count = collection.count_documents({})
    elapsed_ms = (time.perf_counter() - start) * 1000

    print(f"test_read_secondary: count={count} time_ms={elapsed_ms:.2f}")


def main():
    if ENABLE_REPLICA_TESTS:
        print("test_read_secondary: start")
        if not MONGO_REPLICA_URI:
            print("test_read_secondary: missing MONGO_REPLICA_URI")
            print("INFO: replica set not configured -> test_read_secondary skipped")
            return
        try:
            test_read_secondary()
        except ServerSelectionTimeoutError as exc:
            print(f"test_read_secondary: error: {exc}")
            raise SystemExit(1)
    else:
        print("INFO: replica set not configured -> test_read_secondary skipped")


if __name__ == "__main__":
    main()
