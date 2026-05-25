import pandas as pd
import matplotlib.pyplot as plt
from pymongo import MongoClient
import time
import json

# === 🔧 Connexion MongoDB via le nom du service Docker
client = MongoClient("mongodb://mongo1:27017/?replicaSet=rsGreenCoop")
db = client["GreenCoop"]
collection = db["ObsProEtAmateur"]

# === 🔁 Restauration de la base
def restore_from_backup():
    backup_path = "data/back/backup_ObsProEtAmateur.jsonl"
    with open(backup_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        docs = [json.loads(line) for line in lines]
        collection.drop()
        collection.insert_many(docs)
    print(f"✅ Base restaurée avec {len(docs)} documents.")

# === 🧪 Tests d’accessibilité (vitesse)
def test_accessibility():
    print("🚦 Test d'accessibilité (vitesse requêtes)...")
    start = time.time()
    _ = collection.find_one()
    print(f"⏱️ Test 1 - Accès premier document : {round((time.time() - start)*1000, 2)} ms")

    start = time.time()
    list(collection.find().limit(1000))
    print(f"⏱️ Test 2 - Accès 1000 documents : {round((time.time() - start)*1000, 2)} ms")

# === 🧪 Test lecture depuis SECONDARY
def test_secondary_read():
    print("🔄 Test de lecture depuis un nœud SECONDARY...")
    try:
        secondary_client = MongoClient(
            "mongodb://mongo2:27017/?replicaSet=rsGreenCoop",
            readPreference='secondaryPreferred'
        )
        secondary_coll = secondary_client["GreenCoop"]["ObsProEtAmateur"]
        doc = secondary_coll.find_one()
        if doc:
            print("✅ Lecture depuis SECONDARY réussie.")
        else:
            print("❌ Aucun document lu depuis SECONDARY.")
    except Exception as e:
        print(f"❌ Erreur lecture SECONDARY : {e}")

# === ✅ Tests d’intégrité
def test_integrity():
    print("🔍 Tests d’intégrité...")

    # Test 1 : dh_utc bien formattés
    cursor = collection.find({"dh_utc": {"$exists": True}})
    invalid_dates = [doc for doc in cursor if "T" not in doc["dh_utc"]]
    print(f"❗ Documents avec dh_utc mal formaté : {len(invalid_dates)}")

    # Test 2 : valeurs aberrantes de température
    high_temp = collection.count_documents({"température_°C": {"$gt": 50}})
    low_temp = collection.count_documents({"température_°C": {"$lt": -30}})
    print(f"🌡️ Températures > 50°C : {high_temp} | < -30°C : {low_temp}")

# === 📈 Visualisation : Températures heure par heure
def plot_temperatures():
    print("📊 Visualisation des températures heure par heure...")

    df = pd.DataFrame(list(collection.find({}, {"_id": 0, "dh_utc": 1, "température_°C": 1})))
    df["dh_utc"] = pd.to_datetime(df["dh_utc"], errors="coerce")
    df = df.dropna().sort_values("dh_utc")

    plt.figure(figsize=(10, 5))
    plt.plot(df["dh_utc"], df["température_°C"], marker='o', linestyle='-')
    plt.xlabel("Heure")
    plt.ylabel("Température (°C)")
    plt.title("Températures heure par heure")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("data/visualisation_temp.png")
    print("📷 Visualisation enregistrée dans data/visualisation_temp.png")

# === ▶️ MAIN
if __name__ == "__main__":
    restore_from_backup()
    test_accessibility()
    test_secondary_read()
    test_integrity()
    plot_temperatures()
