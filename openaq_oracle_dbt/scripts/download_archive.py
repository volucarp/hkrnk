#!/usr/bin/env python3
"""Download OpenAQ archive files for discovered locations."""

from __future__ import annotations

import argparse
import csv
import gzip
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable

import requests


ARCHIVE_ROOT = "https://openaq-data-archive.s3.amazonaws.com"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--locations-csv", default="seeds/openaq_target_locations.csv")
    parser.add_argument("--start-date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--end-date", required=True, help="YYYY-MM-DD, inclusive")
    parser.add_argument("--output", default="data/openaq_measurements.csv")
    parser.add_argument("--max-locations", type=int, default=None)
    return parser.parse_args()


def date_range(start: date, end: date) -> Iterable[date]:
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def archive_url(location_id: str, day: date) -> str:
    year = day.strftime("%Y")
    month = day.strftime("%m")
    ymd = day.strftime("%Y%m%d")
    return (
        f"{ARCHIVE_ROOT}/records/csv.gz/locationid={location_id}/"
        f"year={year}/month={month}/location-{location_id}-{ymd}.csv.gz"
    )


def load_locations(path: Path, max_locations: int | None) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if max_locations is not None:
        rows = rows[:max_locations]
    return rows


def normalized_measurement(
    city: dict[str, str], source_file: str, row: dict[str, str]
) -> dict[str, str]:
    sensor_id = row.get("sensor_id") or row.get("sensors_id") or row.get("sensorsId")
    unit_name = row.get("unit") or row.get("units") or row.get("unit_name")
    return {
        "city_name": city["city_name"],
        "location_id": row.get("location_id") or city["location_id"],
        "sensor_id": sensor_id or "",
        "location_name": row.get("location") or city.get("location_name") or "",
        "measured_at": row.get("datetime") or "",
        "latitude": row.get("lat") or city.get("latitude") or "",
        "longitude": row.get("lon") or city.get("longitude") or "",
        "parameter_name": row.get("parameter") or "",
        "unit_name": unit_name or "",
        "measurement_value": row.get("value") or "",
        "source_file": source_file,
    }


def main() -> int:
    args = parse_args()
    start = datetime.strptime(args.start_date, "%Y-%m-%d").date()
    end = datetime.strptime(args.end_date, "%Y-%m-%d").date()
    if end < start:
        raise ValueError("--end-date must be on or after --start-date")

    locations = load_locations(Path(args.locations_csv), args.max_locations)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "city_name",
        "location_id",
        "sensor_id",
        "location_name",
        "measured_at",
        "latitude",
        "longitude",
        "parameter_name",
        "unit_name",
        "measurement_value",
        "source_file",
    ]

    downloaded = 0
    missing = 0
    measurements = 0

    with output.open("w", newline="", encoding="utf-8") as out_fh:
        writer = csv.DictWriter(out_fh, fieldnames=fieldnames)
        writer.writeheader()

        for location in locations:
            location_id = location["location_id"]
            for day in date_range(start, end):
                url = archive_url(location_id, day)
                response = requests.get(url, timeout=120)
                if response.status_code == 404:
                    missing += 1
                    continue
                response.raise_for_status()
                downloaded += 1

                content = gzip.decompress(response.content).decode("utf-8")
                rows = csv.DictReader(content.splitlines())
                for row in rows:
                    writer.writerow(normalized_measurement(location, url, row))
                    measurements += 1

    print(
        "Downloaded "
        f"{downloaded} files, skipped {missing} missing files, "
        f"wrote {measurements} measurements to {output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

