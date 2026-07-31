{{
    config(
        materialized='incremental',
        incremental_strategy='merge',
        unique_key=['city_name', 'measurement_date'],
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

)

select
    city_name,
    measurement_date,
    count(*) as total_observations,
    count(distinct location_id) as reporting_locations,
    avg(case when parameter_name = 'pm25' then measurement_value end) as avg_pm25,
    avg(case when parameter_name = 'pm10' then measurement_value end) as avg_pm10,
    avg(case when parameter_name = 'no2' then measurement_value end) as avg_no2,
    avg(case when parameter_name = 'o3' then measurement_value end) as avg_o3,
    avg(case when parameter_name = 'so2' then measurement_value end) as avg_so2,
    avg(case when parameter_name = 'co' then measurement_value end) as avg_co
from source_data
group by
    city_name,
    measurement_date
