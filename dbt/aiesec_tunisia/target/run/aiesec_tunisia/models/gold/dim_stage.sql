
  
    

  create  table "aiesec_dw"."silver"."dim_stage__dbt_tmp"
  
  
    as
  
  (
    select
    row_number() over (order by stage_order) as stage_key,
    stage_name,
    stage_order
from "aiesec_dw"."silver"."stage_lookup"
  );
  