with calendar as (
    select
        generate_series(
            date '2023-01-01',
            date '2026-12-01',
            interval '1 month'
        )::date as date
)

select
    cast(row_number() over (order by date) as integer) as date_key,
    date,
    cast(extract(year from date)    as integer) as year,
    cast(extract(month from date)   as integer) as month,
    cast(extract(quarter from date) as integer) as quarter
from calendar