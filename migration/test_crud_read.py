from migration.config import FIELD_STATION_ID
from migration.ts_crud import TimeSeriesManager
from migration.utils import time_call


def test_read_sample(manager):
    print("test_crud_read: start")
    rows, _ = time_call("crud.read", manager.read, {}, 5)
    print(f"test_crud_read: rows={len(rows)}")
    if rows:
        station = rows[0].get(FIELD_STATION_ID, "n/a")
        print(f"test_crud_read: sample_station={station}")
    print("test_crud_read: done")


if __name__ == "__main__":
    manager = TimeSeriesManager()
    try:
        manager.ping()
        test_read_sample(manager)
    except Exception as exc:
        print(f"test_crud_read: explain: {exc}")
    finally:
        manager.close()
