import os
import time

from pymongo import MongoClient, ReadPreference
from pymongo.errors import ServerSelectionTimeoutError


ENABLE_REPLICA_TESTS = os.getenv("ENABLE_REPLICA_TESTS", "false").lower() == "true"
MONGO_PRIMARY_URI = os.getenv(
    "MONGO_PRIMARY_URI",
    "mongodb://mongo1:27017/?replicaSet=rsGreenCoop",
)
MONGO_PRIMARY_ADMIN_URI = os.getenv(
    "MONGO_PRIMARY_ADMIN_URI",
    "mongodb://admin:admin123@mongo1:27017/admin?replicaSet=rsGreenCoop",
)
MONGO_REPLICA_URI = os.getenv(
    "MONGO_REPLICA_URI",
    "mongodb://analyste:readonly123@mongo1:27017,mongo2:27017,mongo3:27017/"
    "GreenCoop?replicaSet=rsGreenCoop",
)
MONGO_CLONE_SECONDARY_URI = os.getenv(
    "MONGO_CLONE_SECONDARY_URI",
    "mongodb://analyste:readonly123@mongo3:27017/GreenCoop?directConnection=true",
)
DB_NAME = os.getenv("DB_NAME", "GreenCoop")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "ObsProEtAmateur")

FIELD_CITY = "ville"
FIELD_DATETIME = "dh_utc"
FIELD_TEMP = "temp\u00e9rature_\u00b0C"


def run_step(label, func):
    print(f"replica.step.start: {label}")
    start = time.perf_counter()
    try:
        result = func()
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000
        print(
            f"replica.step.result: {label} status=error time_ms={elapsed_ms:.2f}"
            f" error={exc}"
        )
        raise
    elapsed_ms = (time.perf_counter() - start) * 1000
    print(f"replica.step.result: {label} status=ok time_ms={elapsed_ms:.2f}")
    return result


def test_replica_status():
    client = MongoClient(MONGO_PRIMARY_URI, serverSelectionTimeoutMS=5000)
    status = client.admin.command("replSetGetStatus")
    members = status.get("members", [])
    for member in members:
        print(
            "replica.member: name="
            f"{member.get('name')} state={member.get('stateStr')}"
        )


def test_primary_admin_access():
    client = MongoClient(MONGO_PRIMARY_ADMIN_URI, serverSelectionTimeoutMS=5000)
    dbs = client.admin.command("listDatabases")
    db_names = [db.get("name") for db in dbs.get("databases", [])]
    print(f"primary.admin: databases={len(db_names)} sample={db_names[:3]}")


def test_secondary_read():
    client = MongoClient(
        MONGO_REPLICA_URI,
        read_preference=ReadPreference.SECONDARY,
        serverSelectionTimeoutMS=5000,
    )
    collection = client[DB_NAME][COLLECTION_NAME]
    count = collection.count_documents({})
    print(f"secondary.read: count={count}")


def test_clone_secondary_readonly():
    client = MongoClient(
        MONGO_CLONE_SECONDARY_URI,
        read_preference=ReadPreference.SECONDARY,
        serverSelectionTimeoutMS=5000,
    )
    collection = client[DB_NAME][COLLECTION_NAME]
    match = {FIELD_CITY: "Lille"}
    pipeline = [
        {"$match": match},
        {
            "$group": {
                "_id": None,
                "count": {"$sum": 1},
                "min_temp": {"$min": f"${FIELD_TEMP}"},
                "max_temp": {"$max": f"${FIELD_TEMP}"},
                "first_time": {"$min": f"${FIELD_DATETIME}"},
                "last_time": {"$max": f"${FIELD_DATETIME}"},
            }
        },
    ]
    result = list(collection.aggregate(pipeline))
    if not result:
        print("clone.secondary.readonly: Lille no data")
        return
    stats = result[0]
    print(
        "clone.secondary.readonly: "
        f"Lille count={stats.get('count')} min_temp={stats.get('min_temp')} "
        f"max_temp={stats.get('max_temp')} "
        f"first={stats.get('first_time')} last={stats.get('last_time')}"
    )


def main():
    if not ENABLE_REPLICA_TESTS:
        print("INFO: replica tests skipped (ENABLE_REPLICA_TESTS=false)")
        return
    print("replica.tests: start")
    overall_start = time.perf_counter()
    try:
        run_step("replica_status", test_replica_status)
        run_step("primary_admin_access", test_primary_admin_access)
        run_step("secondary_read", test_secondary_read)
        run_step("clone_secondary_readonly", test_clone_secondary_readonly)
    except ServerSelectionTimeoutError as exc:
        print(f"replica.tests: error: {exc}")
        raise SystemExit(1)
    overall_ms = (time.perf_counter() - overall_start) * 1000
    print(f"replica.tests: done time_ms={overall_ms:.2f}")


if __name__ == "__main__":
    main()
