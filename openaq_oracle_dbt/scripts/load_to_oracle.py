#!/usr/bin/env python3
"""Load normalized OpenAQ CSV rows into an Oracle raw table."""

from __future__ import annotations

import argparse
import csv
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


IDENTIFIER = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--table", default="RAW_OPENAQ_MEASUREMENTS")
    parser.add_argument("--schema", default=os.getenv("DBT_ORACLE_RAW_SCHEMA"))
    parser.add_argument("--batch-size", type=int, default=1000)
    parser.add_argument("--replace", action="store_true")
    return parser.parse_args()


def validate_identifier(value: str, label: str) -> str:
    if not IDENTIFIER.match(value):
        raise ValueError(f"Invalid Oracle {label}: {value!r}")
    return value.upper()


def qualified_name(schema: str | None, table: str) -> str:
    table_name = validate_identifier(table, "table name")
    if not schema:
        return table_name
    schema_name = validate_identifier(schema, "schema name")
    return f"{schema_name}.{table_name}"


def oracle_connection() -> Any:
    import oracledb

    user = os.getenv("DBT_ORACLE_USER")
    password = os.getenv("DBT_ORACLE_PASSWORD")
    dsn = os.getenv("ORACLE_DSN") or os.getenv("DBT_ORACLE_TNS_NAME")
    if not user or not password or not dsn:
        raise RuntimeError(
            "Set DBT_ORACLE_USER, DBT_ORACLE_PASSWORD, and either "
            "ORACLE_DSN or DBT_ORACLE_TNS_NAME."
        )
    return oracledb.connect(user=user, password=password, dsn=dsn)


def is_oracle_error_code(exc: Exception, code: int) -> bool:
    error = exc.args[0] if exc.args else None
    return getattr(error, "code", None) == code


def create_table(cursor: Any, table_name: str) -> None:
    ddl = f"""
    CREATE TABLE {table_name} (
        city_name VARCHAR2(100) NOT NULL,
        location_id NUMBER NOT NULL,
        sensor_id NUMBER NOT NULL,
        location_name VARCHAR2(255),
        measured_at TIMESTAMP WITH TIME ZONE NOT NULL,
        latitude NUMBER,
        longitude NUMBER,
        parameter_name VARCHAR2(50) NOT NULL,
        unit_name VARCHAR2(50),
        measurement_value NUMBER,
        source_file VARCHAR2(500),
        loaded_at TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL
    )
    """
    try:
        cursor.execute(ddl)
    except Exception as exc:
        if not is_oracle_error_code(exc, 955):
            raise


def create_index(cursor: Any, table_name: str, table: str) -> None:
    index_name = validate_identifier(f"IX_{table}_01", "index name")
    try:
        cursor.execute(
            f"""
            CREATE INDEX {index_name}
            ON {table_name} (city_name, parameter_name, measured_at)
            """
        )
    except Exception as exc:
        if not is_oracle_error_code(exc, 955):
            raise


def create_unique_index(cursor: Any, table_name: str) -> None:
    """Make repeated loads of the same measurement address the same row."""
    try:
        cursor.execute(
            f"""
            CREATE UNIQUE INDEX UX_RAW_OPENAQ_MEAS_01
            ON {table_name} (
                city_name,
                location_id,
                sensor_id,
                measured_at,
                parameter_name
            )
            """
        )
    except Exception as exc:
        if not is_oracle_error_code(exc, 955):
            raise


def parse_number(value: str) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def parse_int(value: str) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def parse_timestamp(value: str) -> datetime:
    if not value:
        raise ValueError("measured_at is required")
    cleaned = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(cleaned)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def row_values(row: dict[str, str]) -> tuple[Any, ...]:
    return (
        row["city_name"],
        parse_int(row["location_id"]),
        parse_int(row["sensor_id"]),
        row.get("location_name"),
        parse_timestamp(row["measured_at"]),
        parse_number(row.get("latitude", "")),
        parse_number(row.get("longitude", "")),
        row["parameter_name"].lower(),
        row.get("unit_name"),
        parse_number(row.get("measurement_value", "")),
        row.get("source_file"),
    )


def main() -> int:
    args = parse_args()
    table_name = qualified_name(args.schema, args.table)
    table = validate_identifier(args.table, "table name")

    merge_sql = f"""
    MERGE INTO {table_name} target
    USING (
        SELECT
            :1 AS city_name,
            :2 AS location_id,
            :3 AS sensor_id,
            :4 AS location_name,
            :5 AS measured_at,
            :6 AS latitude,
            :7 AS longitude,
            :8 AS parameter_name,
            :9 AS unit_name,
            :10 AS measurement_value,
            :11 AS source_file
        FROM dual
    ) incoming
    ON (
        target.city_name = incoming.city_name
        AND target.location_id = incoming.location_id
        AND target.sensor_id = incoming.sensor_id
        AND target.measured_at = incoming.measured_at
        AND target.parameter_name = incoming.parameter_name
    )
    WHEN MATCHED THEN UPDATE SET
        target.location_name = incoming.location_name,
        target.latitude = incoming.latitude,
        target.longitude = incoming.longitude,
        target.unit_name = incoming.unit_name,
        target.measurement_value = incoming.measurement_value,
        target.source_file = incoming.source_file,
        target.loaded_at = SYSTIMESTAMP
    WHEN NOT MATCHED THEN INSERT (
        city_name,
        location_id,
        sensor_id,
        location_name,
        measured_at,
        latitude,
        longitude,
        parameter_name,
        unit_name,
        measurement_value,
        source_file
    ) VALUES (
        incoming.city_name,
        incoming.location_id,
        incoming.sensor_id,
        incoming.location_name,
        incoming.measured_at,
        incoming.latitude,
        incoming.longitude,
        incoming.parameter_name,
        incoming.unit_name,
        incoming.measurement_value,
        incoming.source_file
    )
    """

    loaded = 0
    with oracle_connection() as connection:
        cursor = connection.cursor()
        create_table(cursor, table_name)
        create_index(cursor, table_name, table)

        if args.replace:
            cursor.execute(f"TRUNCATE TABLE {table_name}")

        create_unique_index(cursor, table_name)

        with Path(args.csv).open("r", newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            batch: list[tuple[Any, ...]] = []
            for row in reader:
                batch.append(row_values(row))
                if len(batch) >= args.batch_size:
                    cursor.executemany(merge_sql, batch)
                    loaded += len(batch)
                    batch.clear()

            if batch:
                cursor.executemany(merge_sql, batch)
                loaded += len(batch)

        connection.commit()

    print(f"Loaded {loaded} rows into {table_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
