{{ config(materialized='view') }}

with source as (
    select
        city_name,
        location_id,
        sensor_id,
        location_name,
        measured_at,
        latitude,
        longitude,
        lower(parameter_name) as parameter_name,
        unit_name,
        measurement_value,
        source_file,
        loaded_at
    from {{ source('raw', 'raw_openaq_measurements') }}
), deduplicated as (

    select
        source.*,
        row_number() over (
            partition by
                city_name,
                location_id,
                sensor_id,
                measured_at,
                parameter_name
            order by loaded_at desc, source_file desc
        ) as ingestion_row_number
    from source
)

select
    city_name,
    location_id,
    sensor_id,
    location_name,
    cast((measured_at at time zone 'UTC') as timestamp) as measured_at_utc,
    cast(trunc(cast((measured_at at time zone 'UTC') as date)) as date) as measurement_date,
    latitude,
    longitude,
    parameter_name,
    case parameter_name
        when 'pm25' then 'PM2.5'
        when 'pm10' then 'PM10'
        when 'no2' then 'Nitrogen dioxide'
        when 'o3' then 'Ozone'
        when 'so2' then 'Sulfur dioxide'
        when 'co' then 'Carbon monoxide'
        else parameter_name
    end as parameter_display_name,
    unit_name,
    measurement_value,
    source_file,
    loaded_at
from deduplicated
where city_name in ('New York City', 'Jersey City')
  and ingestion_row_number = 1
  and measurement_value is not null
  and parameter_name in ('pm25', 'pm10', 'no2', 'o3', 'so2', 'co')
