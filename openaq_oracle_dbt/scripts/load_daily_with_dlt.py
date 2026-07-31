#!/usr/bin/env python3
"""Load a normalized daily OpenAQ CSV into Oracle with dlt."""

from __future__ import annotations

import argparse
import csv
import os
import re
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterator

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
IDENTIFIER = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load one normalized OpenAQ daily CSV into Oracle using dlt."
    )
    parser.add_argument("--csv", required=True, help="Normalized OpenAQ CSV file.")
    parser.add_argument(
        "--config",
        default="config/dlt_ingestion.yml",
        help="dlt ingestion configuration, relative to the project root.",
    )
    parser.add_argument(
        "--schema",
        default=os.getenv("DBT_ORACLE_RAW_SCHEMA"),
        help="Existing Oracle schema; defaults to DBT_ORACLE_RAW_SCHEMA.",
    )
    return parser.parse_args()


def project_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def validate_identifier(value: str, label: str) -> str:
    if not IDENTIFIER.match(value):
        raise ValueError(f"Invalid {label}: {value!r}")
    return value


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        config = yaml.safe_load(fh) or {}

    required = {"pipeline_name", "table_name", "write_disposition", "primary_key"}
    missing = sorted(required - config.keys())
    if missing:
        raise ValueError(f"Missing dlt configuration keys: {', '.join(missing)}")
    if config["write_disposition"] != "append":
        raise ValueError(
            "Oracle daily ingestion must use append. dlt merge requires a second "
            "Oracle staging schema; dbt performs canonical deduplication instead."
        )

    validate_identifier(str(config["pipeline_name"]), "dlt pipeline name")
    validate_identifier(str(config["table_name"]), "Oracle table name")
    if not isinstance(config["primary_key"], list) or not config["primary_key"]:
        raise ValueError("primary_key must be a non-empty list")
    for column in config["primary_key"]:
        validate_identifier(str(column), "primary key column")
    return config


def required_value(row: dict[str, str], column: str) -> str:
    value = row.get(column, "").strip()
    if not value:
        raise ValueError(f"CSV column {column!r} is required")
    return value


def optional_decimal(value: str | None) -> Decimal | None:
    if value is None or not value.strip():
        return None
    return Decimal(value)


def parse_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def normalized_row(
    row: dict[str, str], loaded_at: datetime
) -> dict[str, Any]:
    return {
        "city_name": required_value(row, "city_name"),
        "location_id": int(required_value(row, "location_id")),
        "sensor_id": int(required_value(row, "sensor_id")),
        "location_name": row.get("location_name") or None,
        "measured_at": parse_timestamp(required_value(row, "measured_at")),
        "latitude": optional_decimal(row.get("latitude")),
        "longitude": optional_decimal(row.get("longitude")),
        "parameter_name": required_value(row, "parameter_name").lower(),
        "unit_name": row.get("unit_name") or None,
        "measurement_value": optional_decimal(row.get("measurement_value")),
        "source_file": row.get("source_file") or None,
        "loaded_at": loaded_at,
    }


def iter_csv_rows(path: Path) -> Iterator[dict[str, Any]]:
    loaded_at = datetime.now(timezone.utc)
    with path.open("r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for line_number, row in enumerate(reader, start=2):
            try:
                yield normalized_row(row, loaded_at)
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"Invalid row at {path}:{line_number}: {exc}") from exc


def oracle_engine() -> Any:
    try:
        import oracledb
        import sqlalchemy as sa
    except ImportError as exc:
        raise RuntimeError(
            "Install the project requirements to use dlt ingestion: "
            "python -m pip install -r requirements.txt"
        ) from exc

    user = os.getenv("DBT_ORACLE_USER")
    password = os.getenv("DBT_ORACLE_PASSWORD")
    dsn = os.getenv("ORACLE_DSN") or os.getenv("DBT_ORACLE_TNS_NAME")
    if not user or not password or not dsn:
        raise RuntimeError(
            "Set DBT_ORACLE_USER, DBT_ORACLE_PASSWORD, and either "
            "ORACLE_DSN or DBT_ORACLE_TNS_NAME."
        )

    def connect() -> Any:
        return oracledb.connect(user=user, password=password, dsn=dsn)

    return sa.create_engine("oracle+oracledb://", creator=connect)


def main() -> int:
    args = parse_args()
    csv_path = project_path(args.csv)
    config_path = project_path(args.config)
    config = load_config(config_path)
    if not args.schema:
        raise RuntimeError("Set DBT_ORACLE_RAW_SCHEMA or pass --schema")
    schema = validate_identifier(args.schema, "Oracle schema")

    try:
        import dlt
    except ImportError as exc:
        raise RuntimeError(
            "dlt is not installed. Install the project requirements first."
        ) from exc

    table_name = str(config["table_name"])
    pipelines_dir = project_path(
        str(config.get("pipelines_dir", "data/dlt_pipelines"))
    )
    resource = dlt.resource(
        iter_csv_rows(csv_path),
        name=table_name,
        primary_key=[str(column) for column in config["primary_key"]],
        write_disposition=str(config["write_disposition"]),
    )

    engine = oracle_engine()
    try:
        destination = dlt.destinations.sqlalchemy(engine)
        pipeline = dlt.pipeline(
            pipeline_name=str(config["pipeline_name"]),
            destination=destination,
            dataset_name=schema,
            pipelines_dir=str(pipelines_dir),
        )
        load_info = pipeline.run(resource)
        load_info.raise_on_failed_jobs()
        print(load_info)
    finally:
        engine.dispose()

    print(f"dlt loaded {csv_path} into {schema}.{table_name.upper()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
