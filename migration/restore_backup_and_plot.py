import json
import matplotlib.pyplot as plt
import pandas as pd

from migration.config import BACKUP_FILE, FIELD_DATETIME, FIELD_TEMP, VISUAL_FILE
from migration.ts_crud import TimeSeriesManager
from migration.utils import time_call


def restore_from_backup(manager):
    print("Restoring data from JSONL backup...")
    with open(BACKUP_FILE, "r", encoding="utf-8") as handle:
        docs = [json.loads(line) for line in handle if line.strip()]
    _, elapsed_ms = time_call("restore.replace_all", manager.replace_all, docs)
    print(f"restored_docs: {len(docs)}")
    return elapsed_ms


def plot_temperatures(manager):
    print("Plotting temperatures by time...")
    rows, _ = time_call(
        "plot.read",
        manager.read,
        {},
        0,
        {FIELD_DATETIME: 1, FIELD_TEMP: 1, "_id": 0},
        [(FIELD_DATETIME, 1)],
    )
    df = pd.DataFrame(rows)
    df[FIELD_DATETIME] = pd.to_datetime(df[FIELD_DATETIME], errors="coerce")
    df = df.dropna().sort_values(FIELD_DATETIME)

    if df.empty:
        print("plot.skip_empty: no data")
        return

    plt.figure(figsize=(10, 5))
    plt.plot(df[FIELD_DATETIME], df[FIELD_TEMP], marker="o", linestyle="-")
    plt.title("Temperature by hour")
    plt.xlabel("UTC time")
    plt.ylabel("Temperature (C)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(VISUAL_FILE)
    print(f"plot.saved: {VISUAL_FILE}")


if __name__ == "__main__":
    manager = TimeSeriesManager()
    try:
        manager.ping()
        restore_from_backup(manager)
        plot_temperatures(manager)
        print("restore_and_plot: done")
    except Exception as exc:
        print(f"restore_and_plot: error: {exc}")
    finally:
        manager.close()
