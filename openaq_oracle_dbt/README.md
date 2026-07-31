# OpenAQ Oracle dbt Sample

This sample project loads OpenAQ measurements for New York City and Jersey City into Oracle, then uses `dbt-oracle` to build daily air quality marts.

The pipeline is intentionally small and reproducible:

1. Discover OpenAQ monitoring locations inside configured city bounding boxes.
2. Download daily measurement files from the [public OpenAQ AWS archive](https://openaq-data-archive.s3.amazonaws.com/records/csv.gz/), documented in [OpenAQ's AWS archive guide](https://docs.openaq.org/aws/about).
3. Load raw measurements into Oracle Autonomous Database.
4. Run dbt staging and mart models with `dbt-oracle`.

## Data Scope

The city scope lives in [config/cities.yml](/Users/Shared/repos/hkrnk/openaq_oracle_dbt/config/cities.yml).

Current assumptions:

- `New York` means New York City.
- `Jerse City` means Jersey City.
- New York City uses a core NYC bounding box that avoids most New Jersey overlap. If you need Staten Island or a wider NYC metro scope, widen the bbox before discovery.

## Prerequisites

Use the project Python interpreter from the repo instructions:

```bash
/Users/Shared/apps/miniforge3/envs/lpy/bin/python -m pip install -r openaq_oracle_dbt/requirements.txt
```

OpenAQ v3 requires an API key for discovery. The measurement archive download uses public S3 HTTPS URLs after location IDs are known.

Create `.env` from [.env.example](/Users/Shared/repos/hkrnk/openaq_oracle_dbt/.env.example) or export the variables in your shell.

### Get An OpenAQ API Key

1. Create an account at [OpenAQ Explorer](https://explore.openaq.org/register).
2. Open [OpenAQ account settings](https://explore.openaq.org/account) and copy or generate an API key.
3. Put the key in `.env` as `OPENAQ_API_KEY`. Treat it like a password and do not commit or share it.

The discovery script sends this value in the `X-API-Key` request header. OpenAQ's API key instructions are documented in [Managing an OpenAQ API key](https://docs.openaq.org/using-the-api/api-key).

Load the variables into the current terminal before running the scripts:

```bash
set -a
source .env
set +a
```

The `.env` file is ignored by git. The archive download does not need the API key, but the location discovery request does.

The downloader reads files using this archive path pattern:

```text
https://openaq-data-archive.s3.amazonaws.com/records/csv.gz/locationid={location_id}/year={YYYY}/month={MM}/location-{location_id}-{YYYYMMDD}.csv.gz
```

## Hosted Oracle Database

For this sample, the simplest hosted option is an [Oracle Cloud Infrastructure Free Tier](https://www.oracle.com/cloud/free/) account with an [Always Free Autonomous AI Database](https://docs.oracle.com/iaas/Content/FreeTier/freetier.htm). It is suitable for a small learning project and does not expire while it remains an Always Free resource. Oracle currently documents a limit of up to two Always Free Autonomous AI Databases per tenancy, with approximately 20 GB of storage and 30 simultaneous sessions per database. Always Free resources are created in the account's home region, so choose that region carefully during signup. Oracle may require a phone number and payment card for account verification; the card is not charged unless you upgrade or create paid resources.

### Create The Database

1. Sign up for [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/) or sign in to the OCI Console.
2. Open **Oracle Database** and select **Autonomous AI Database**.
3. Click **Create Autonomous AI Database**.
4. Choose a database name, an admin password, and either the **Data Warehouse** or **Transaction Processing** workload. Either workload works for this project.
5. Select **Always Free** and create the database. Wait until its status is **Available**.
6. Create a separate application user for the sample, rather than using `ADMIN`, if you plan to keep the database beyond a short experiment. The user needs permission to create tables, views, indexes, and schemas/models used by dbt. For a first local-only test, `ADMIN` is simpler.

### Download The Wallet

In the database details page, open **Database connection**, choose **Download wallet**, and save the wallet zip file somewhere outside the repository. Unzip it into a private directory, for example:

```bash
mkdir -p "$HOME/.oracle/openaq_wallet"
unzip ~/Downloads/<wallet-file>.zip -d "$HOME/.oracle/openaq_wallet"
export TNS_ADMIN="$HOME/.oracle/openaq_wallet"
```

Protect the wallet files and never commit them. With `python-oracledb` thin mode, the wallet directory supplies the `tnsnames.ora` connection aliases used by `DBT_ORACLE_TNS_NAME`. Oracle's [Python wallet connection guide](https://docs.oracle.com/en-us/iaas/autonomous-database-serverless/doc/connecting-python-mtls.html) describes this connection method.

Set the Oracle values in `.env`, replacing `your_tns_alias` with one of the service names listed in the wallet's `tnsnames.ora` file, such as a `_high`, `_medium`, or `_low` service:

```bash
ORA_PYTHON_DRIVER_TYPE=thin
TNS_ADMIN=/Users/your-user/.oracle/openaq_wallet
DBT_ORACLE_USER=OPENAQ_USER
DBT_ORACLE_PASSWORD='your_database_password'
DBT_ORACLE_SCHEMA=OPENAQ_USER
DBT_ORACLE_RAW_SCHEMA=OPENAQ_USER
DBT_ORACLE_DATABASE=your_database_name
DBT_ORACLE_TNS_NAME=your_tns_alias
```

The sample's raw loader uses `DBT_ORACLE_TNS_NAME` as its DSN. It also accepts an `ORACLE_DSN` environment variable if you use a direct Easy Connect or TLS connection instead. Oracle documents both wallet and walletless Python connections in [Connect Python applications to Autonomous AI Database](https://docs.oracle.com/en/cloud/paas/autonomous-database/serverless/adbsb/connecting-python.html).

## Run The ELT

For the repeatable daily lookback process, see [README-daily.md](/Users/Shared/repos/hkrnk/openaq_oracle_dbt/README-daily.md).

From this directory:

```bash
cd /Users/Shared/repos/hkrnk/openaq_oracle_dbt
```

Discover target locations:

```bash
/Users/Shared/apps/miniforge3/envs/lpy/bin/python scripts/discover_locations.py \
  --config config/cities.yml \
  --output seeds/openaq_target_locations.csv
```

Download a small starter window:

```bash
/Users/Shared/apps/miniforge3/envs/lpy/bin/python scripts/download_archive.py \
  --locations-csv seeds/openaq_target_locations.csv \
  --start-date 2025-06-01 \
  --end-date 2025-06-07 \
  --output data/openaq_measurements.csv
```

Load raw rows into Oracle with dlt:

```bash
/Users/Shared/apps/miniforge3/envs/lpy/bin/python scripts/load_daily_with_dlt.py \
  --csv data/openaq_measurements.csv \
  --config config/dlt_ingestion.yml
```

The original native Oracle loader remains available for comparison:

```bash
/Users/Shared/apps/miniforge3/envs/lpy/bin/python scripts/load_to_oracle.py \
  --csv data/openaq_measurements.csv \
  --replace
```

Run dbt:

```bash
dbt seed
dbt run
dbt test
```

## Oracle Connection

`dbt-oracle` supports thin mode, which avoids installing Oracle Instant Client for common Autonomous Database connections.

Recommended environment:

```bash
export ORA_PYTHON_DRIVER_TYPE=thin
export DBT_ORACLE_USER=OPENAQ_USER
export DBT_ORACLE_PASSWORD='...'
export DBT_ORACLE_SCHEMA=OPENAQ_USER
export DBT_ORACLE_RAW_SCHEMA=OPENAQ_USER
export DBT_ORACLE_DATABASE='<database_name>'
export DBT_ORACLE_TNS_NAME='<tns_alias_from_wallet>'
```

Copy [profiles.yml.example](/Users/Shared/repos/hkrnk/openaq_oracle_dbt/profiles.yml.example) to `~/.dbt/profiles.yml`, or merge the profile into your existing dbt profiles file.

## Models

- `stg_openaq_measurements`: normalized raw measurements for the two configured cities.
- `int_daily_city_parameter`: daily city/parameter summary table.
- `mart_city_air_quality_daily`: city-level daily comparison mart with pollutant columns.
- `mart_station_parameter_daily`: station-level daily parameter rollups.

The default raw source for dbt is `RAW_OPENAQ_MEASUREMENTS_DLT`. When using the native loader directly, run dbt with `--vars '{"raw_table_identifier": "RAW_OPENAQ_MEASUREMENTS"}'`.

## Notes

- OpenAQ archive files are written after the local day ends and may be patched later.
- Some location/day combinations do not have files. The downloader skips HTTP 404s and reports counts.
- Start with one week of data, then widen the date range after the load and dbt models work.
