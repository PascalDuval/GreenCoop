# pipeline_migration.py

import pandas as pd
import json
from pathlib import Path
import re
from datetime import datetime, timezone
from ts_crud import TimeSeriesManager  # ✅ correct

# === 📁 Chemins ===
json_path = Path("data/Data_Source1_011024-071024.json")
xlsx_lm = Path("data/WeatherUndergroundLaMadeleineFR.xlsx")
xlsx_ic = Path("data/WeatherUndergroundIchtegemBE.xlsx")
output_path = Path("data/observations_flat.json")

# === 🧰 Helpers ===
def safe_str(x):
    s = str(x).replace("\xa0", " ").strip() if x is not None else None
    return s if s else None

def safe_float(x):
    s = safe_str(x)
    if s:
        s = s.replace(",", ".")
        m = re.search(r"-?\d+(\.\d+)?", s)
        return float(m.group(0)) if m else None
    return None

def safe_int(x):
    val = safe_float(x)
    return int(val) if val is not None else None

def parse_date(sheet_name):
    try:
        return pd.to_datetime(sheet_name, dayfirst=True).strftime("%Y-%m-%d")
    except:
        return None

def parse_time_to_hms(val):
    try:
        return pd.to_datetime(val).strftime("%H:%M:%S")
    except:
        return None

def make_dh_utc(date, time):
    return f"{date}T{time}Z" if date and time else None

# === 🔧 Stations ===
stations_amateurs = {
    "ILAMAD25": {
        "station_id": "ILAMAD25",
        "station_name": "La Madeleine",
        "ville": "La Madeleine",
        "latitude": 50.659,
        "longitude": 3.07,
        "elevation": 23,
        "hardware": "other",
        "software": "EasyWeatherPro_V5.1.6",
        "type_station": "amateur",
        "source": "Weather Underground (PWS amateur)"
    },
    "IICHTE19": {
        "station_id": "IICHTE19",
        "station_name": "WeerstationBS",
        "ville": "Ichtegem",
        "latitude": 51.092,
        "longitude": 2.999,
        "elevation": 15,
        "hardware": "other",
        "software": "EasyWeatherV1.6.6",
        "type_station": "amateur",
        "source": "Weather Underground (PWS amateur)"
    }
}

# === 📊 Nettoyage Excel ===
def clean_excel(path, station_id):
    xls = pd.ExcelFile(path)
    data = []
    for sheet in xls.sheet_names:
        date = parse_date(sheet)
        df = xls.parse(sheet)
        df.columns = [str(c).strip() for c in df.columns]
        for _, row in df.iterrows():
            hms = parse_time_to_hms(row.get("Time"))
            dh_utc = make_dh_utc(date, hms)
            if dh_utc:
                rec = {
                    "dh_utc": dh_utc,
                    "température_°C": safe_float(row.get("Temperature")),
                    "point_de_rosée_°C": safe_float(row.get("Dew Point")),
                    "humidité_%": safe_int(row.get("Humidity")),
                    "pression_hPa": round(safe_float(row.get("Pressure")) * 33.8639, 2)
                        if row.get("Pressure") else None,
                    "vent_direction": safe_str(row.get("Wind")),
                    "vent_moyen_km/h": safe_float(row.get("Speed")),
                    "vent_rafales_km/h": safe_float(row.get("Gust")),
                    "pluie_taux_mm/h": safe_float(row.get("Precip. Rate.")),
                    "pluie_cumulee_mm": safe_float(row.get("Precip. Accum.")),
                    "indice_uv": safe_int(row.get("UV")),
                    "rayonnement_solaire_W/m²": safe_float(row.get("Solar"))
                }
                rec.update(stations_amateurs[station_id])
                data.append(rec)
    return data

# === 📄 Lecture JSON Pro ===
def load_json_data():
    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    stations_meta = {
        st["id"]: {
            "station_id": st["id"],
            "station_name": st.get("name"),
            "latitude": st.get("latitude"),
            "longitude": st.get("longitude"),
            "elevation": st.get("elevation"),
            "type_station": "pro",
            "source": st.get("license", {}).get("source")
        } for st in json_data["stations"]
    }

    json_obs = []
    for st_id, entries in json_data.get("hourly", {}).items():
        if st_id == "_params":
            continue
        for entry in entries:
            dh = pd.to_datetime(entry.get("dh_utc"), errors="coerce", utc=True)
            if pd.isna(dh):
                continue
            json_obs.append({
                "dh_utc": dh.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "température_°C": safe_float(entry.get("temperature")),
                "point_de_rosée_°C": safe_float(entry.get("point_de_rosee")),
                "humidité_%": safe_int(entry.get("humidite")),
                "pression_hPa": safe_float(entry.get("pression")),
                "vent_direction": safe_str(entry.get("vent_direction")),
                "vent_moyen_km/h": safe_float(entry.get("vent_moyen")),
                "vent_rafales_km/h": safe_float(entry.get("vent_rafales")),
                "pluie_taux_mm/h": safe_float(entry.get("taux_precipitation")),
                "pluie_cumulee_mm": safe_float(entry.get("pluie_accumulee")),
                "pluie_1h_mm": safe_float(entry.get("pluie_1h")),
                "pluie_3h_mm": safe_float(entry.get("pluie_3h")),
                **stations_meta.get(st_id, {})
            })
    return json_obs

# === 🚀 Exécution principale ===
def run_migration():
    print("▶️ Démarrage de la migration...")

    try:
        all_data = (
            load_json_data()
            + clean_excel(xlsx_lm, "ILAMAD25")
            + clean_excel(xlsx_ic, "IICHTE19")
        )

        cleaned = [{k: v for k, v in d.items() if v is not None} for d in all_data]

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(cleaned, f, indent=2, ensure_ascii=False)

        print(f"✅ {len(cleaned)} observations exportées vers {output_path}")

        # ✅ Conversion BSON datetime pour Mongo Time Series
        for doc in cleaned:
            if "dh_utc" in doc:
                doc["dh_utc"] = datetime.fromisoformat(
                    doc["dh_utc"].replace("Z", "+00:00")
                ).astimezone(timezone.utc)

        # ✅ Insertion MongoDB Time Series
        manager = TimeSeriesManager()
        inserted_count = manager.insert(cleaned)
        print(f"✅ {inserted_count} documents insérés dans MongoDB")

    except Exception as e:
        print(f"❌ Erreur pendant la migration : {e}")

# === Point d’entrée script
if __name__ == "__main__":
    run_migration()
