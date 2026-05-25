# ts_crud.py
from pymongo import MongoClient
from datetime import datetime
import pandas as pd

class TimeSeriesManager:
    def __init__(self, db_name="GreenCoop", collection_name="ObsProEtAmateur", uri="mongodb://localhost:27017/"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        print(f"✅ Connecté à {db_name}.{collection_name}")

    # ✅ Créer un ou plusieurs documents
    def insert(self, docs):
        if isinstance(docs, dict):
            result = self.collection.insert_one(docs)
            return result.inserted_id
        elif isinstance(docs, list):
            result = self.collection.insert_many(docs)
            return result.inserted_ids
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
        df = pd.DataFrame(data)
        return df