
  
    

  create  table "aiesec_dw"."silver"."fact_performance__dbt_tmp"
  
  
    as
  
  (
    with perf as (
    select * from "aiesec_dw"."silver"."performance"
),

program_map as (
    select * from "aiesec_dw"."silver"."program_map"
)

select
    perf.bronze_id                          as performance_id,
    lc.lc_key,
    dt.date_key,
    dir.direction_key,
    prod.product_key,
    stg.stage_key,
    perf.value,
    perf.scrape_id,
    perf.scraped_at
from perf
left join program_map                      pm   on perf.program = pm.program_code
left join "aiesec_dw"."silver"."dim_lc"        lc   on perf.lc_name = lc.lc_name
left join "aiesec_dw"."silver"."dim_date"      dt   on to_date(perf.period_start, 'MM/DD/YYYY') = dt.date
left join "aiesec_dw"."silver"."dim_direction" dir  on pm.direction_code = dir.direction_code
left join "aiesec_dw"."silver"."dim_product"   prod on pm.product_code = prod.product_code
left join "aiesec_dw"."silver"."dim_stage"     stg  on perf.stage = stg.stage_name
  );
  