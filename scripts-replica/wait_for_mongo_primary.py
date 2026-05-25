import os
import time

from pymongo import MongoClient

mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")

print(f"🔍 Connexion à MongoDB via {mongo_uri}")

while True:
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
        client.admin.command("ping")
        print("✅ MongoDB est prêt")
        break
    except Exception as e:
        print(f"⏳ MongoDB pas encore prêt : {e}")
        time.sleep(2)
