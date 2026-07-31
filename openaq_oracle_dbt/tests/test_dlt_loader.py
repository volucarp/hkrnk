from __future__ import annotations

import sys
import unittest
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import load_daily_with_dlt as loader


class DltLoaderTests(unittest.TestCase):
    def test_ingestion_config_is_valid(self) -> None:
        config = loader.load_config(PROJECT_ROOT / "config" / "dlt_ingestion.yml")

        self.assertEqual(config["write_disposition"], "append")
        self.assertEqual(config["table_name"], "raw_openaq_measurements_dlt")
        self.assertIn("measured_at", config["primary_key"])

    def test_normalized_row_has_typed_values(self) -> None:
        loaded_at = datetime(2026, 7, 22, tzinfo=timezone.utc)
        row = loader.normalized_row(
            {
                "city_name": "New York City",
                "location_id": "42",
                "sensor_id": "84",
                "location_name": "Test station",
                "measured_at": "2026-07-21T12:30:00Z",
                "latitude": "40.7",
                "longitude": "-74.0",
                "parameter_name": "PM25",
                "unit_name": "ug/m3",
                "measurement_value": "8.5",
                "source_file": "test.csv.gz",
            },
            loaded_at,
        )

        self.assertEqual(row["location_id"], 42)
        self.assertEqual(row["measurement_value"], Decimal("8.5"))
        self.assertEqual(row["parameter_name"], "pm25")
        self.assertEqual(row["measured_at"].tzinfo, timezone.utc)
        self.assertEqual(row["loaded_at"], loaded_at)

    def test_required_measurement_key_is_validated(self) -> None:
        with self.assertRaisesRegex(ValueError, "sensor_id"):
            loader.normalized_row(
                {
                    "city_name": "Jersey City",
                    "location_id": "42",
                    "sensor_id": "",
                    "measured_at": "2026-07-21T12:30:00Z",
                    "parameter_name": "pm25",
                },
                datetime.now(timezone.utc),
            )


if __name__ == "__main__":
    unittest.main()
