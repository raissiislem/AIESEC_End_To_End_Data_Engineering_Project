
  
    

  create  table "aiesec_dw"."gold"."dim_stage__dbt_tmp"
  
  
    
  
  (
    stage_key integer primary key,
    stage_name text,
    stage_order integer
    
    )
 ;
    insert into "aiesec_dw"."gold"."dim_stage__dbt_tmp" (
      stage_key, stage_name, stage_order
    )
  
  (
    
    select stage_key, stage_name, stage_order
    from (
        select
    cast(row_number() over (order by stage_order) as integer) as stage_key,
    stage_name,
    cast(stage_order as integer) as stage_order
from "aiesec_dw"."silver"."stage_lookup"
    ) as model_subq
  );
  