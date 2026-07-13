with distinct_dates as (
    select distinct to_date(period_start, 'MM/DD/YYYY') as date
    from "aiesec_dw"."silver"."performance"
)

select
    row_number() over (order by date) as date_key,
    date,
    extract(year from date)    as year,
    extract(month from date)   as month,
    extract(quarter from date) as quarter
from distinct_dates