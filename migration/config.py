import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27027")
MONGO_REPLICA_URI = os.getenv(
    "MONGO_REPLICA_URI",
    "mongodb://analyste:readonly123@localhost:27027,localhost:27028,localhost:27029/"
    "GreenCoop?replicaSet=rsGreenCoop",
)

DB_NAME = os.getenv("DB_NAME", "GreenCoop")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "ObsProEtAmateur")

BACKUP_FILE = os.getenv(
    "BACKUP_FILE",
    os.path.join(DATA_DIR, "backup_ObsProEtAmateur.jsonl"),
)
VISUAL_FILE = os.getenv(
    "VISUAL_FILE",
    os.path.join(DATA_DIR, "visualisation_temp.png"),
)

# Field names from backup_ObsProEtAmateur.jsonl, kept ASCII via escapes.
FIELD_DATETIME = "dh_utc"
FIELD_STATION_ID = "station_id"
FIELD_TEMP = "temp\u00e9rature_\u00b0C"
FIELD_HUMIDITY = "humidit\u00e9_%"
FIELD_PRESSURE = "pression_hPa"
FIELD_WIND_MEAN = "vent_moyen_km/h"
