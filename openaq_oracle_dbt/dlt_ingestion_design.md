# dlt Daily Ingestion Design

## Purpose

This project ingests OpenAQ daily measurement files for New York City and
Jersey City into Oracle, then uses dbt to expose a canonical measurement
stream and build incremental daily marts.

The dlt implementation is responsible only for loading a normalized CSV into
the Oracle raw layer. It does not download OpenAQ data or transform it into
analytical tables. Those responsibilities remain separate so that a file can
be replayed without downloading it again.

```text
OpenAQ public AWS archive
        |
        v
scripts/download_archive.py
        |
        v
normalized CSV in data/daily/
        |
        v
scripts/load_daily_with_dlt.py
        |
        v
Oracle RAW_OPENAQ_MEASUREMENTS_DLT (append-only)
        |
        v
dbt staging deduplication and incremental marts
```

## Components

| Component | Responsibility |
| --- | --- |
| `scripts/run_daily_delta.py` | Operational entry point. Downloads a lookback window, invokes dlt, and runs dbt. |
| `scripts/download_archive.py` | Downloads and normalizes archive measurements for the configured target locations. |
| `scripts/load_daily_with_dlt.py` | Loads one normalized CSV into Oracle with dlt. |
| `config/dlt_ingestion.yml` | Controls the dlt pipeline name, raw table, write behavior, local state directory, and measurement key. |
| `models/staging/stg_openaq_measurements.sql` | Deduplicates the append-only raw table before dbt marts consume it. |

The target locations are maintained in `seeds/openaq_target_locations.csv`.
Run `scripts/discover_locations.py` when that list needs to be refreshed.

## Prerequisites

Use the project Python environment and install dependencies once:

```bash
cd /Users/Shared/repos/hkrnk/openaq_oracle_dbt

/Users/Shared/apps/miniforge3/envs/lpy/bin/python -m pip install -r requirements.txt
```

Create `.env` from `.env.example`, then load it into the shell:

```bash
set -a
source .env
set +a
```

The relevant settings are:

| Setting | Used by | Purpose |
| --- | --- | --- |
| `OPENAQ_API_KEY` | downloader | Authenticates requests to OpenAQ. |
| `DBT_ORACLE_USER` | dlt and dbt | Oracle database user. |
| `DBT_ORACLE_PASSWORD` | dlt and dbt | Oracle database password. |
| `DBT_ORACLE_RAW_SCHEMA` | dlt | Existing schema that owns the raw dlt table. |
| `DBT_ORACLE_TNS_NAME` or `ORACLE_DSN` | dlt | Oracle connection address. |
| `TNS_ADMIN` | Oracle driver | Wallet directory when connecting to Autonomous Database with a TNS alias. |

The Oracle user must be able to create and write tables in
`DBT_ORACLE_RAW_SCHEMA`, and dbt must be configured to create its target
objects. dlt creates the raw table and its `_dlt_*` metadata tables when they
do not already exist.

## Entry Point: Daily Pipeline

Use the daily runner for normal scheduled execution. With no arguments it
processes yesterday and the previous two days. The lookback window allows the
pipeline to pick up archive files that were published late or corrected.

```bash
cd /Users/Shared/repos/hkrnk/openaq_oracle_dbt

/Users/Shared/apps/miniforge3/envs/lpy/bin/python scripts/run_daily_delta.py
```

To process a particular date and its two-day lookback:

```bash
/Users/Shared/apps/miniforge3/envs/lpy/bin/python scripts/run_daily_delta.py \
  --run-date 2026-07-22
```

The runner performs these actions in order:

1. Downloads archive data for `run-date - lookback-days` through `run-date`.
2. Writes a normalized CSV under `data/daily/`.
3. Invokes the dlt file loader.
4. Runs `dbt build --select stg_openaq_measurements+` with the same lookback
   and the dlt raw table identifier.

Useful runner options:

```bash
# Reprocess seven previous days as well as the run date.
/Users/Shared/apps/miniforge3/envs/lpy/bin/python scripts/run_daily_delta.py \
  --run-date 2026-07-22 \
  --lookback-days 7

# Validate archive download and Oracle ingestion without dbt.
/Users/Shared/apps/miniforge3/envs/lpy/bin/python scripts/run_daily_delta.py \
  --run-date 2026-07-22 \
  --skip-dbt

# Rebuild the selected dbt models after a historical backfill or model change.
/Users/Shared/apps/miniforge3/envs/lpy/bin/python scripts/run_daily_delta.py \
  --run-date 2026-07-22 \
  --lookback-days 30 \
  --full-refresh
```

## Entry Point: Load One Existing File

Use the dlt loader directly to replay a normalized file that already exists.
This command does not call OpenAQ and does not run dbt.

```bash
cd /Users/Shared/repos/hkrnk/openaq_oracle_dbt

/Users/Shared/apps/miniforge3/envs/lpy/bin/python scripts/load_daily_with_dlt.py \
  --csv data/daily/openaq_measurements_20260720_20260722.csv
```

By default, the loader reads `config/dlt_ingestion.yml` and uses
`DBT_ORACLE_RAW_SCHEMA`. Override either for an alternate configuration or
existing target schema:

```bash
/Users/Shared/apps/miniforge3/envs/lpy/bin/python scripts/load_daily_with_dlt.py \
  --csv /absolute/path/to/openaq_measurements.csv \
  --config config/dlt_ingestion.yml \
  --schema OPENAQ_USER
```

After a direct file load, run dbt to update the downstream models:

```bash
dbt build --select stg_openaq_measurements+ \
  --vars '{"daily_lookback_days": 2, "raw_table_identifier": "RAW_OPENAQ_MEASUREMENTS_DLT"}'
```

## dlt Configuration

The current configuration is:

```yaml
pipeline_name: openaq_daily_file
table_name: raw_openaq_measurements_dlt
write_disposition: append
pipelines_dir: data/dlt_pipelines
primary_key:
  - city_name
  - location_id
  - sensor_id
  - measured_at
  - parameter_name
```

`pipelines_dir` stores dlt's local pipeline state. It is intentionally under
`data/`, which is ignored by git. Do not commit that state or database
credentials.

The loader converts CSV values to appropriate Python values before handing
them to dlt: numeric identifiers become integers, values and coordinates
become decimals, and timestamps become timezone-aware datetimes. This avoids
loading measurements as untyped strings.

## Reruns, Duplicates, and Idempotency

The dlt raw table is append-only. Reprocessing the same daily file may add
another physical copy of the same measurement to
`RAW_OPENAQ_MEASUREMENTS_DLT`.

The dbt staging view makes the analytical result idempotent. It partitions
raw rows by this natural measurement key:

```text
city_name + location_id + sensor_id + measured_at + parameter_name
```

It keeps the row with the latest `loaded_at` value, then the incremental dbt
marts merge recalculated daily aggregates. A rerun therefore does not produce
duplicate measurements in the marts, and a later corrected archive record
wins over an earlier one.

The raw layer uses `append` deliberately. dlt's SQLAlchemy `merge` behavior
needs a separate staging dataset/schema. A typical Oracle Autonomous Database
application user owns one schema, so adding another solely for dlt merge would
require extra database administration and privileges. The append plus dbt
deduplication pattern works within the normal single-schema setup.

## Operational Notes

- Schedule `scripts/run_daily_delta.py` once daily after the prior day's
  archive files are expected to be available.
- Keep a nonzero lookback window in scheduled runs.
- Use `--skip-dbt` when diagnosing raw ingestion separately from dbt.
- Use a direct loader invocation to replay a retained file without making any
  OpenAQ API calls.
- The legacy native Oracle `MERGE` implementation remains available for
  comparison with `scripts/run_daily_delta.py --loader native`. It loads
  `RAW_OPENAQ_MEASUREMENTS`, so the runner passes the corresponding dbt source
  table automatically.
