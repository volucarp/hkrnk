#!/usr/bin/env python3
"""Discover OpenAQ locations for configured city bounding boxes."""

from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path
from typing import Any

import requests
import yaml


OPENAQ_LOCATIONS_URL = "https://api.openaq.org/v3/locations"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/cities.yml")
    parser.add_argument("--output", default="seeds/openaq_target_locations.csv")
    parser.add_argument("--api-key", default=os.getenv("OPENAQ_API_KEY"))
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--monitors-only", action="store_true")
    return parser.parse_args()


def bbox_string(city: dict[str, Any]) -> str:
    bbox = city["bbox"]
    return ",".join(
        str(bbox[key]) for key in ("min_lon", "min_lat", "max_lon", "max_lat")
    )


def sensor_summary(location: dict[str, Any]) -> tuple[str, str]:
    sensors: list[str] = []
    parameters: list[str] = []
    for sensor in location.get("sensors") or []:
        sensor_id = sensor.get("id")
        parameter = (sensor.get("parameter") or {}).get("name")
        if sensor_id is not None:
            sensors.append(str(sensor_id))
        if parameter:
            parameters.append(str(parameter).lower())
    return "|".join(sorted(set(sensors))), "|".join(sorted(set(parameters)))


def fetch_locations(
    api_key: str,
    city: dict[str, Any],
    limit: int,
    monitors_only: bool,
) -> list[dict[str, Any]]:
    headers = {"X-API-Key": api_key}
    page = 1
    rows: list[dict[str, Any]] = []

    while True:
        params: dict[str, Any] = {
            "iso": "US",
            "bbox": bbox_string(city),
            "limit": limit,
            "page": page,
            "order_by": "id",
            "sort_order": "asc",
        }
        if monitors_only:
            params["monitor"] = "true"

        response = requests.get(
            OPENAQ_LOCATIONS_URL, headers=headers, params=params, timeout=60
        )
        response.raise_for_status()
        payload = response.json()
        results = payload.get("results") or []
        rows.extend(results)

        found = payload.get("meta", {}).get("found")
        if not results or len(results) < limit:
            break
        if isinstance(found, int) and page * limit >= found:
            break
        page += 1

    return rows


def flatten_location(city: dict[str, Any], location: dict[str, Any]) -> dict[str, Any]:
    sensor_ids, parameters = sensor_summary(location)
    coordinates = location.get("coordinates") or {}
    owner = location.get("owner") or {}
    provider = location.get("provider") or {}
    country = location.get("country") or {}
    first = location.get("datetimeFirst") or {}
    last = location.get("datetimeLast") or {}

    return {
        "city_name": city["city_name"],
        "city_slug": city["city_slug"],
        "location_id": location.get("id"),
        "location_name": location.get("name"),
        "locality": location.get("locality"),
        "country_code": country.get("code"),
        "latitude": coordinates.get("latitude"),
        "longitude": coordinates.get("longitude"),
        "is_mobile": location.get("isMobile"),
        "is_monitor": location.get("isMonitor"),
        "owner_name": owner.get("name"),
        "provider_name": provider.get("name"),
        "datetime_first_utc": first.get("utc"),
        "datetime_last_utc": last.get("utc"),
        "sensor_ids": sensor_ids,
        "parameters": parameters,
    }


def main() -> int:
    args = parse_args()
    if not args.api_key:
        print("OPENAQ_API_KEY is required for location discovery.", file=sys.stderr)
        return 2

    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as fh:
        config = yaml.safe_load(fh)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "city_name",
        "city_slug",
        "location_id",
        "location_name",
        "locality",
        "country_code",
        "latitude",
        "longitude",
        "is_mobile",
        "is_monitor",
        "owner_name",
        "provider_name",
        "datetime_first_utc",
        "datetime_last_utc",
        "sensor_ids",
        "parameters",
    ]

    seen: set[int] = set()
    written = 0
    with output_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()

        for city in config.get("cities", []):
            locations = fetch_locations(
                args.api_key, city, limit=args.limit, monitors_only=args.monitors_only
            )
            for location in locations:
                location_id = location.get("id")
                if location_id is None or location_id in seen:
                    continue
                seen.add(int(location_id))
                writer.writerow(flatten_location(city, location))
                written += 1

    print(f"Wrote {written} locations to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

