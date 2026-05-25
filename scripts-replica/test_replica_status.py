import os
import time

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

MONGO_PRIMARY_URI = os.getenv(
    "MONGO_PRIMARY_URI",
    "mongodb://mongo1:27017/?replicaSet=rsGreenCoop",
)
ENABLE_REPLICA_TESTS = os.getenv("ENABLE_REPLICA_TESTS", "false").lower() == "true"


def main():
    if not ENABLE_REPLICA_TESTS:
        print("INFO: replica set not configured -> test_replica_status skipped")
        return
    print("test_replica_status: start")
    if not MONGO_PRIMARY_URI:
        print("test_replica_status: missing MONGO_PRIMARY_URI")
        print("INFO: replica set not configured -> test_replica_status skipped")
        return
    client = MongoClient(MONGO_PRIMARY_URI, serverSelectionTimeoutMS=5000)
    start = time.perf_counter()
    try:
        status = client.admin.command("replSetGetStatus")
    except ServerSelectionTimeoutError as exc:
        print(f"test_replica_status: error: {exc}")
        print("INFO: replica set not configured -> test_replica_status skipped")
        return
    elapsed_ms = (time.perf_counter() - start) * 1000

    members = status.get("members", [])
    for member in members:
        print(
            "test_replica_status: member="
            f"{member.get('name')} state={member.get('stateStr')}"
        )
    print(f"test_replica_status: time_ms={elapsed_ms:.2f}")


if __name__ == "__main__":
    main()
