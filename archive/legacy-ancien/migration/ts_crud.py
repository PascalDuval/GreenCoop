# ts_crud.py

from pymongo import MongoClient, errors
from datetime import datetime
import pandas as pd

class TimeSeriesManager:
    def __init__(self, db_name="GreenCoop", collection_name="ObsProEtAmateur", uri="mongodb://mongodb:27017/"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

        # ✅ Vérifie et crée la collection time-series si elle n'existe pas
        if collection_name not in self.db.list_collection_names():
            try:
                self.db.create_collection(
                    collection_name,
                    timeseries={
                        "timeField": "dh_utc",
                        "metaField": "station_id",
                        "granularity": "hours"
                    }
                )
                print(f"✅ Collection time-series '{collection_name}' créée.")
            except errors.CollectionInvalid:
                print(f"⚠️ Collection '{collection_name}' existe déjà.")
        
        self.collection = self.db[collection_name]
        print(f"✅ Connecté à {db_name}.{collection_name}")

    # ✅ Insertion unique ou multiple
    def insert(self, docs):
        if isinstance(docs, dict):
            result = self.collection.insert_one(docs)
            return 1
        elif isinstance(docs, list):
            result = self.collection.insert_many(docs)
            return len(result.inserted_ids)
        else:
            raise ValueError("❌ Format non reconnu pour l'insertion.")

    # 🔍 Lire les documents avec un filtre
    def read(self, filter_query={}, limit=10):
        return list(self.collection.find(filter_query).limit(limit))

    # 📝 Corriger une mesure = Delete + Insert
    def correct_measure(self, filter_query, new_doc):
        deleted = self.collection.delete_many(filter_query)
        inserted = self.collection.insert_one(new_doc)
        print(f"✅ Correction : {deleted.deleted_count} supprimé(s), 1 inséré.")
        return inserted.inserted_id

    # 🗑️ Supprimer par station_id
    def delete_by_station(self, station_id):
        deleted = self.collection.delete_many({"station_id": station_id})
        print(f"🗑️ {deleted.deleted_count} document(s) supprimé(s) pour station_id = {station_id}")
        return deleted.deleted_count

    # 📊 Charger les données dans un DataFrame
    def to_dataframe(self, filter_query={}):
        data = list(self.collection.find(filter_query))
        if not data:
            print("⚠️ Aucun document trouvé.")
            return pd.DataFrame()
        return pd.DataFrame(data)
