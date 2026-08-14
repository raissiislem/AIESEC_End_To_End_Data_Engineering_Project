
  
    

  create  table "aiesec_dw"."gold"."dim_date__dbt_tmp"
  
  
    
  
  (
    date_key integer primary key,
    date date,
    year integer,
    month integer,
    quarter integer
    
    )
 ;
    insert into "aiesec_dw"."gold"."dim_date__dbt_tmp" (
      date_key, date, year, month, quarter
    )
  
  (
    
    select date_key, date, year, month, quarter
    from (
        with calendar as (
    select
        generate_series(
            date '2023-01-01',
            (date_trunc('month', current_date) + interval '12 months')::date,
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
    ) as model_subq
  );
  