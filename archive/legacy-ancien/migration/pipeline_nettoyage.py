# migration/pipeline_nettoyage.py

import json
from pathlib import Path
import pandas as pd

INPUT_FILE = Path("data/observations_flat.json")
OUTPUT_FILE = Path("data/observations_timeseries.jsonl")

def load_data():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def control_quality(data):
    print(f"🔎 Début des contrôles sur {len(data)} observations...")
    df = pd.DataFrame(data)

    if "dh_utc" not in df.columns or df["dh_utc"].isna().any():
        raise ValueError("❌ Champ 'dh_utc' absent ou vide")

    # Exemple de nettoyage simple : suppression des doublons
    df = df.drop_duplicates(subset=["station_id", "dh_utc"])

    # Optionnel : trier
    df = df.sort_values(by="dh_utc")

    print(f"✅ {len(df)} observations après nettoyage et contrôle")
    return df.to_dict(orient="records")

def export_jsonl(data, path):
    with open(path, "w", encoding="utf-8") as f:
        for entry in data:
            json.dump(entry, f, ensure_ascii=False)
            f.write("\n")
    print(f"📄 Export JSONL vers : {path}")

def run_cleaning():
    try:
        data = load_data()
        cleaned = control_quality(data)
        export_jsonl(cleaned, OUTPUT_FILE)
    except Exception as e:
        print(f"❌ Erreur dans le pipeline de nettoyage : {e}")

if __name__ == "__main__":
    run_cleaning()
