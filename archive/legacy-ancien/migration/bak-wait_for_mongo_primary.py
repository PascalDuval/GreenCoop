# wait_for_mongo_primary.py

import time
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

MONGO_URI = "mongodb://mongodb:27017/"
REPLICA_SET = "rsGreenCoop"

MAX_RETRIES = 20
WAIT_SECONDS = 5

def is_primary(client):
    try:
        ismaster = client.admin.command("isMaster")
        return ismaster.get("ismaster", False)
    except Exception as e:
        print(f"⏳ MongoDB pas encore prêt : {e}")
        return False

if __name__ == "__main__":
    print("🔍 Vérification que MongoDB est en état PRIMARY...")
    for attempt in range(MAX_RETRIES):
        try:
            client = MongoClient(MONGO_URI, replicaset=REPLICA_SET, serverSelectionTimeoutMS=2000)
            if is_primary(client):
                print("✅ MongoDB est PRIMARY, on peut démarrer.")
                exit(0)
        except ConnectionFailure:
            print("❌ Connexion échouée à MongoDB.")
        time.sleep(WAIT_SECONDS)

    print("❌ MongoDB n'est pas devenu PRIMARY après plusieurs tentatives.")
    exit(1)
