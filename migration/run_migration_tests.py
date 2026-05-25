import time

from migration.test_crud_insert_delete import test_insert_delete
from migration.test_crud_read import test_read_sample
from migration.test_integrity import test_outliers
from migration.ts_crud import TimeSeriesManager


def run_step(label, func):
    print(f"migration.step.start: {label}")
    start = time.perf_counter()
    try:
        func()
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000
        print(
            f"migration.step.result: {label} status=error time_ms={elapsed_ms:.2f}"
            f" error={exc}"
        )
        raise
    elapsed_ms = (time.perf_counter() - start) * 1000
    print(f"migration.step.result: {label} status=ok time_ms={elapsed_ms:.2f}")


def main():
    print("migration.tests: start")
    overall_start = time.perf_counter()
    manager = TimeSeriesManager()
    try:
        manager.ping()
        run_step("test_integrity", lambda: test_outliers(manager))
        run_step("test_crud_read", lambda: test_read_sample(manager))
        run_step("test_crud_insert_delete", lambda: test_insert_delete(manager))
    finally:
        manager.close()
    overall_ms = (time.perf_counter() - overall_start) * 1000
    print(f"migration.tests: done time_ms={overall_ms:.2f}")


if __name__ == "__main__":
    main()
