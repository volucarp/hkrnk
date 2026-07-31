# Daily Delta Runbook

This runbook describes the daily OpenAQ delta process for New York City and Jersey City.

The process downloads a small lookback window, uses dlt to load the measurements into Oracle, deduplicates the append-only raw data in dbt, and runs the incremental marts:

```text
OpenAQ daily archive files
        |
        v
scripts/run_daily_delta.py
        |
        +--> dlt --> Oracle RAW_OPENAQ_MEASUREMENTS_DLT (append-only)
        |
        +--> dbt staging view (canonical deduplication)
        |
        +--> incremental daily marts
```

## One-Time Setup

From the project directory:

```bash
cd /Users/Shared/repos/hkrnk/openaq_oracle_dbt
/Users/Shared/apps/miniforge3/envs/lpy/bin/python -m pip install -r requirements.txt
```

Create `.env` from [.env.example](/Users/Shared/repos/hkrnk/openaq_oracle_dbt/.env.example), fill in the OpenAQ and Oracle values, and load it into the current shell:

```bash
set -a
source .env
set +a
```

The Oracle database user must be allowed to create and update the raw table and the dbt target objects. `TNS_ADMIN` must point to the Autonomous Database wallet directory when using a wallet TNS alias.

The dlt loader is configured in [config/dlt_ingestion.yml](/Users/Shared/repos/hkrnk/openaq_oracle_dbt/config/dlt_ingestion.yml). It defines the pipeline name, raw table, local pipeline-state directory, append disposition, and measurement key. Credentials remain in environment variables and are not stored in that file.

Discover the target locations once, or repeat discovery when monitoring locations change:

```bash
/Users/Shared/apps/miniforge3/envs/lpy/bin/python scripts/discover_locations.py \
  --config config/cities.yml \
  --output seeds/openaq_target_locations.csv
```

## Run A Daily Delta

The default command processes yesterday and the two preceding days. The lookback is intentional because OpenAQ archive files can be patched after they are first published.

```bash
/Users/Shared/apps/miniforge3/envs/lpy/bin/python scripts/run_daily_delta.py
```

To run a specific processing date:

```bash
/Users/Shared/apps/miniforge3/envs/lpy/bin/python scripts/run_daily_delta.py \
  --run-date 2026-07-22
```

To change the lookback window to seven days:

```bash
/Users/Shared/apps/miniforge3/envs/lpy/bin/python scripts/run_daily_delta.py \
  --run-date 2026-07-22 \
  --lookback-days 7
```

The downloaded CSV is retained under `data/daily/` with a date-range filename. That directory is ignored by git.

## Load One File With dlt

To load an already-downloaded normalized CSV without running the downloader or dbt:

```bash
/Users/Shared/apps/miniforge3/envs/lpy/bin/python scripts/load_daily_with_dlt.py \
  --csv data/daily/openaq_measurements_20260720_20260722.csv \
  --config config/dlt_ingestion.yml
```

dlt creates and maintains `RAW_OPENAQ_MEASUREMENTS_DLT` plus its `_dlt_*` metadata tables in `DBT_ORACLE_RAW_SCHEMA`. Its local working state is kept under `data/dlt_pipelines/`.

## Reruns And Deduplication

The dlt loader deliberately writes the raw table using `append`. dlt's SQLAlchemy `merge` disposition requires a second staging schema, while an Autonomous Database application user normally owns only one schema.

The dbt staging view therefore selects the latest row for each measurement key:

```text
city_name + location_id + sensor_id + measured_at + parameter_name
```

Rerunning a file may add another copy to the append-only raw table, but the latest `loaded_at` row is the only one exposed to the dbt marts. The analytical output remains idempotent and a later corrected measurement wins.

For comparison, the previous native loader remains available. It performs an Oracle `MERGE` directly into `RAW_OPENAQ_MEASUREMENTS`:

```bash
/Users/Shared/apps/miniforge3/envs/lpy/bin/python scripts/run_daily_delta.py \
  --run-date 2026-07-22 \
  --loader native
```

The runner passes the corresponding raw table identifier to dbt automatically.

## How The dbt Incremental Models Work

The three daily marts use `materialized='incremental'` and `incremental_strategy='merge'`:

- `int_daily_city_parameter` merges by city, date, parameter, and unit.
- `mart_city_air_quality_daily` merges by city and date.
- `mart_station_parameter_daily` merges by city, station, date, parameter, and unit.

On the first run, dbt builds the complete tables. On later runs, each model filters source rows from the latest target date minus `daily_lookback_days`, then merges the recalculated aggregates into the target table.

The runner passes the same lookback value to dbt that it uses for the archive download. It also passes `RAW_OPENAQ_MEASUREMENTS_DLT` as the configured dbt source table. The staging model remains a deduplicating view; the daily aggregate marts are the incremental tables.

## Backfills And Full Refreshes

For a historical backfill or a change to model logic, run the daily process with a larger lookback and rebuild dbt:

```bash
/Users/Shared/apps/miniforge3/envs/lpy/bin/python scripts/run_daily_delta.py \
  --run-date 2026-07-01 \
  --lookback-days 30 \
  --full-refresh
```

Use `--full-refresh` sparingly because it rebuilds the selected dbt models from all rows in the raw table.

To test ingestion without running dbt:

```bash
/Users/Shared/apps/miniforge3/envs/lpy/bin/python scripts/run_daily_delta.py \
  --run-date 2026-07-22 \
  --skip-dbt
```

## Scheduling

Run the command once per day after the OpenAQ archive files for the previous day are expected to be available. A scheduler such as cron, GitHub Actions, Airflow, or OCI Data Integration can invoke the same command. Keep the lookback enabled even when the job is scheduled daily so late archive corrections are reprocessed.
