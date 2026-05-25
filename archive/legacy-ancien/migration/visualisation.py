# visualisation.py

import pandas as pd
import matplotlib.pyplot as plt
from pymongo import MongoClient

# Connexion MongoDB
client = MongoClient("mongodb://mongodb:27017/")
db = client["GreenCoop"]
coll = db["ObsProEtAmateur"]

# Charger dans DataFrame
cursor = coll.find({}, {"dh_utc": 1, "température_°C": 1, "_id": 0})
df = pd.DataFrame(list(cursor))
df["dh_utc"] = pd.to_datetime(df["dh_utc"])
df = df.sort_values("dh_utc")

# Tracer
plt.figure(figsize=(12, 5))
plt.plot(df["dh_utc"], df["température_°C"], marker="o")
plt.title("Température heure par heure")
plt.xlabel("Date/Heure")
plt.ylabel("Température (°C)")
plt.grid(True)
plt.tight_layout()
plt.savefig("/home/jovyan/app/data/visualisation_temp.png")
print("✅ Visualisation sauvegardée dans data/visualisation_temp.png")
