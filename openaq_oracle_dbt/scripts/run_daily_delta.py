#!/usr/bin/env python3
"""Run an idempotent OpenAQ daily lookback load and dbt build."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected YYYY-MM-DD") from exc


def default_run_date() -> date:
    return date.today() - timedelta(days=1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Download an OpenAQ lookback window, load it into Oracle, "
            "and run incremental dbt models."
        )
    )
    parser.add_argument(
        "--run-date",
        type=parse_date,
        default=default_run_date(),
        help="Last date to process, YYYY-MM-DD; defaults to yesterday.",
    )
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=2,
        help="Also reprocess this many days before --run-date.",
    )
    parser.add_argument(
        "--locations-csv",
        default="seeds/openaq_target_locations.csv",
        help="Discovered OpenAQ locations CSV, relative to the project root.",
    )
    parser.add_argument(
        "--output-dir",
        default="data/daily",
        help="Directory for downloaded daily CSV files, relative to the project root.",
    )
    parser.add_argument("--max-locations", type=int, default=None)
    parser.add_argument(
        "--loader",
        choices=("dlt", "native"),
        default="dlt",
        help="Raw ingestion implementation; defaults to dlt.",
    )
    parser.add_argument(
        "--dlt-config",
        default="config/dlt_ingestion.yml",
        help="dlt ingestion configuration, relative to the project root.",
    )
    parser.add_argument(
        "--skip-dbt",
        action="store_true",
        help="Stop after the Oracle load; useful for testing ingestion only.",
    )
    parser.add_argument(
        "--full-refresh",
        action="store_true",
        help="Run dbt with --full-refresh after loading the delta.",
    )
    return parser.parse_args()


def project_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def run(command: list[str]) -> None:
    print("$ " + " ".join(command))
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def dlt_table_identifier(config_path: Path) -> str:
    with config_path.open("r", encoding="utf-8") as fh:
        config = yaml.safe_load(fh) or {}
    table_name = config.get("table_name")
    if not table_name:
        raise ValueError(f"table_name is required in {config_path}")
    return str(table_name).upper()


def main() -> int:
    args = parse_args()
    if args.lookback_days < 0:
        raise ValueError("--lookback-days must be zero or greater")

    start_date = args.run_date - timedelta(days=args.lookback_days)
    end_date = args.run_date
    output = project_path(args.output_dir) / (
        f"openaq_measurements_{start_date:%Y%m%d}_{end_date:%Y%m%d}.csv"
    )
    locations_csv = project_path(args.locations_csv)

    download_command = [
        sys.executable,
        str(PROJECT_ROOT / "scripts" / "download_archive.py"),
        "--locations-csv",
        str(locations_csv),
        "--start-date",
        start_date.isoformat(),
        "--end-date",
        end_date.isoformat(),
        "--output",
        str(output),
    ]
    if args.max_locations is not None:
        download_command.extend(["--max-locations", str(args.max_locations)])
    run(download_command)

    if args.loader == "dlt":
        dlt_config = project_path(args.dlt_config)
        raw_table_identifier = dlt_table_identifier(dlt_config)
        run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "load_daily_with_dlt.py"),
                "--csv",
                str(output),
                "--config",
                str(dlt_config),
            ]
        )
    else:
        raw_table_identifier = "RAW_OPENAQ_MEASUREMENTS"
        run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "load_to_oracle.py"),
                "--csv",
                str(output),
            ]
        )

    if args.skip_dbt:
        print(
            f"Loaded {raw_table_identifier}; skipped dbt build (--skip-dbt)."
        )
        return 0

    dbt_command = shutil.which("dbt")
    if not dbt_command:
        raise RuntimeError(
            "dbt was not found on PATH. Activate the project environment or "
            "rerun with --skip-dbt."
        )
    dbt_args = [
        dbt_command,
        "build",
        "--select",
        "stg_openaq_measurements+",
        "--vars",
        json.dumps(
            {
                "daily_lookback_days": args.lookback_days,
                "raw_table_identifier": raw_table_identifier,
            }
        ),
    ]
    if args.full_refresh:
        dbt_args.append("--full-refresh")
    run(dbt_args)
    print(
        f"Daily delta complete with {args.loader} for {start_date} through {end_date}. "
        f"Downloaded file: {output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
