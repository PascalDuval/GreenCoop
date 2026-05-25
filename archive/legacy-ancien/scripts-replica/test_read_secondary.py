# scripts-replica/test_read_secondary.py

from pymongo import MongoClient, ReadPreference
from pymongo.errors import ServerSelectionTimeoutError
import sys

uri = "mongodb://analyste:readonly123@mongo1:27017,mongo2:27017,mongo3:27017/GreenCoop?replicaSet=rsGreenCoop"

try:
    client = MongoClient(uri, read_preference=ReadPreference.SECONDARY, serverSelectionTimeoutMS=3000)
    db = client["GreenCoop"]
    collection = db["ObsProEtAmateur"]

    # Exécuter une requête simple
    count = collection.count_documents({})
    print(f"✅ Lecture réussie sur un SECONDARY — total documents : {count}")

except ServerSelectionTimeoutError as e:
    print(f"❌ Erreur : impossible de lire depuis un SECONDARY\n{e}")
    sys.exit(1)
