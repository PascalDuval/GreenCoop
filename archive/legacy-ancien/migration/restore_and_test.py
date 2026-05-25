# restore_and_test.py

import pymongo
import pandas as pd
from pathlib import Path
import json

# --- Connexion MongoDB
client = pymongo.MongoClient("mongodb://mongodb:27017/")
db = client["GreenCoop"]
collection = db["ObsProEtAmateur"]

# --- Restauration si collection vide
backup_path = Path("data/back/backup_ObsProEtAmateur.jsonl")
if collection.count_documents({}) == 0:
    print("📦 Restauration à partir du backup JSONL...")
    with open(backup_path, "r", encoding="utf-8") as f:
        docs = [json.loads(line) for line in f]
    collection.insert_many(docs)
    print(f"✅ {len(docs)} documents restaurés.")
else:
    print("✅ Collection déjà remplie.")

# --- 🔍 Accessibilité : Tests Data Science (exemples)
df = pd.DataFrame(collection.find())

print("\n🔎 Tests d'accessibilité (Data Science):")
# 1. Données disponibles pour plusieurs stations
nb_stations = df['station_id'].nunique()
print(f"✔️ {nb_stations} stations uniques détectées.")

# 2. Plage temporelle correcte
df["dh_utc"] = pd.to_datetime(df["dh_utc"])
start, end = df["dh_utc"].min(), df["dh_utc"].max()
print(f"✔️ Période de données : {start} → {end}")

# 3. Températures disponibles
if "température_°C" in df.columns and df["température_°C"].notna().sum() > 0:
    print(f"✔️ Températures disponibles sur {df['température_°C'].notna().sum()} observations.")
else:
    print("❌ Aucune température détectée.")

# --- ✅ Contrôles d'intégrité inspirés de pipeline_nettoyage
print("\n🔍 Contrôles d'intégrité :")
nb_total = len(df)
df_clean = df.drop_duplicates(subset=["station_id", "dh_utc"])
nb_clean = len(df_clean)

print(f"✔️ Suppression de doublons : {nb_total - nb_clean} doublon(s) détecté(s).")
missing_dh_utc = df["dh_utc"].isna().sum()
print(f"✔️ dh_utc manquants : {missing_dh_utc}")
print(f"✅ Données prêtes pour visualisation.")

# --- 📊 Requête de visualisation : Température heure par heure
df_visu = df_clean[["dh_utc", "température_°C"]].dropna().sort_values("dh_utc")
print("\n📈 Aperçu des températures heure par heure :")
print(df_visu.head(10).to_string(index=False))
