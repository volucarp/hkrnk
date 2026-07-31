{{
    config(
        materialized='incremental',
        incremental_strategy='merge',
        unique_key=[
            'city_name',
            'location_id',
            'measurement_date',
            'parameter_name',
            'unit_name'
        ],
        on_schema_change='fail'
    )
}}

with source_data as (

    select *
    from {{ ref('stg_openaq_measurements') }}

    {% if is_incremental() %}
        where measurement_date >= (
            select coalesce(max(measurement_date), date '1900-01-01')
                   - {{ var('daily_lookback_days', 2) }}
            from {{ this }}
        )
    {% endif %}

), aggregated as (

select
    city_name,
    location_id,
    location_name,
    latitude,
    longitude,
    measurement_date,
    parameter_name,
    parameter_display_name,
    coalesce(unit_name, 'unknown') as unit_name,
    count(*) as observation_count,
    avg(measurement_value) as avg_value,
    min(measurement_value) as min_value,
    max(measurement_value) as max_value
from source_data
group by
    city_name,
    location_id,
    location_name,
    latitude,
    longitude,
    measurement_date,
    parameter_name,
    parameter_display_name,
    coalesce(unit_name, 'unknown')

)

select * from aggregated
