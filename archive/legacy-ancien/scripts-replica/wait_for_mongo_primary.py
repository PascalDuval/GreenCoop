# wait_for_mongo_primary.py

import time
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

MONGO_URI = "mongodb://mongo1:27017/?replicaSet=rsGreenCoop"

MAX_RETRIES = 30
WAIT_SECONDS = 5


def is_primary(client):
    try:
        status = client.admin.command("replSetGetStatus")
        my_state = status.get("myState")
        # 1 = PRIMARY
        return my_state == 1
    except Exception as e:
        print(f"⏳ MongoDB pas encore prêt : {e}")
        return False


if __name__ == "__main__":
    print("🔍 Vérification que MongoDB est en état PRIMARY...")

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            client = MongoClient(
                MONGO_URI,
                serverSelectionTimeoutMS=2000
            )

            if is_primary(client):
                print("✅ MongoDB est PRIMARY (rsGreenCoop)")
                exit(0)

            print(f"⏳ Tentative {attempt}/{MAX_RETRIES} : pas encore PRIMARY")

        except ServerSelectionTimeoutError as e:
            print(f"⏳ MongoDB injoignable : {e}")

        time.sleep(WAIT_SECONDS)

    print("❌ MongoDB n'est pas devenu PRIMARY après plusieurs tentatives.")
    exit(1)
