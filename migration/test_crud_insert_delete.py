from datetime import datetime

from migration.config import FIELD_DATETIME, FIELD_STATION_ID, FIELD_TEMP
from migration.ts_crud import TimeSeriesManager
from migration.utils import time_call


def test_insert_delete(manager):
    print("test_crud_insert_delete: start")

    test_doc = {
        FIELD_STATION_ID: "TEST_STATION",
        FIELD_DATETIME: datetime.utcnow().isoformat(),
        FIELD_TEMP: 99.9,
    }

    inserted_id, _ = time_call("crud.insert", manager.insert, test_doc)
    deleted_result, _ = time_call("crud.delete", manager.delete, {"_id": inserted_id})
    print(
        "test_crud_insert_delete: "
        f"inserted_id={inserted_id} deleted={deleted_result.deleted_count}"
    )

    print("test_crud_insert_delete: done")


if __name__ == "__main__":
    manager = TimeSeriesManager()
    try:
        manager.ping()
        test_insert_delete(manager)
    except Exception as exc:
        print(f"test_crud_insert_delete: explain: {exc}")
    finally:
        manager.close()
