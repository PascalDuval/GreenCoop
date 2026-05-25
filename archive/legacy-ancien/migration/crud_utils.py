# migration/crud_utils.py

import json
from pathlib import Path
from pymongo import MongoClient


def get_collection(uri="mongodb://mongodb:27017", db_name="GreenCoop", collection="ObsProEtAmateur"):
    client = MongoClient(uri)
    db = client[db_name]
    return db[collection]

def export_collection_to_jsonl(collection, output_path):
    data = collection.find({})
    with open(output_path, "w", encoding="utf-8") as f:
        for doc in data:
            doc.pop("_id", None)
            json.dump(doc, f, ensure_ascii=False)
            f.write("\n")
    print(f"✅ Export terminé : {output_path}")

def import_jsonl_to_collection(collection, input_path):
    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        docs = [json.loads(line.strip()) for line in lines]
        if docs:
            collection.insert_many(docs)
            print(f"✅ {len(docs)} documents insérés depuis {input_path}")
        else:
            print(f"⚠️ Aucun document trouvé dans {input_path}")

def clear_collection(collection):
    deleted = collection.delete_many({})
    print(f"🗑️ {deleted.deleted_count} documents supprimés de la collection.")

def count_documents(collection):
    count = collection.count_documents({})
    print(f"📊 {count} documents dans la collection.")
    return count
