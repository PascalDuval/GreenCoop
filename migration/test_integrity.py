from migration.config import FIELD_HUMIDITY, FIELD_PRESSURE, FIELD_TEMP, FIELD_WIND_MEAN
from migration.ts_crud import TimeSeriesManager
from migration.utils import time_call


COHERENCE_RULES = {
    FIELD_TEMP: {"min": -30, "max": 50},
    FIELD_HUMIDITY: {"min": 0, "max": 100},
    FIELD_PRESSURE: {"min": 900, "max": 1100},
    FIELD_WIND_MEAN: {"min": 0, "max": 200},
}


def test_outliers(manager):
    print("test_integrity: start")
    for field, rules in COHERENCE_RULES.items():
        too_low, _ = time_call(
            f"integrity.count_low.{field}",
            manager.count,
            {field: {"$lt": rules["min"]}},
        )
        too_high, _ = time_call(
            f"integrity.count_high.{field}",
            manager.count,
            {field: {"$gt": rules["max"]}},
        )
        print(
            f"integrity.field: {field} low={too_low} high={too_high} "
            f"range=({rules['min']},{rules['max']})"
        )
    print("test_integrity: done")


if __name__ == "__main__":
    manager = TimeSeriesManager()
    try:
        manager.ping()
        test_outliers(manager)
    except Exception as exc:
        print(f"test_integrity: explain: {exc}")
    finally:
        manager.close()
