
  
    

  create  table "aiesec_dw"."gold"."dim_direction__dbt_tmp"
  
  
    as
  
  (
    select
    row_number() over (order by direction_code) as direction_key,
    direction_code,
    direction_name
from "aiesec_dw"."silver"."direction_lookup"
  );
  