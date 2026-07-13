
  
    

  create  table "aiesec_dw"."silver"."dim_lc__dbt_tmp"
  
  
    as
  
  (
    with distinct_lc as (
    select distinct lc_name
    from "aiesec_dw"."silver"."performance"
)

select
    row_number() over (order by lc_name) as lc_key,
    lc_name
from distinct_lc
  );
  