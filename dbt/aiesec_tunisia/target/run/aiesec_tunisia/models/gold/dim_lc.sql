
  
    

  create  table "aiesec_dw"."gold"."dim_lc__dbt_tmp"
  
  
    
  
  (
    lc_key integer primary key,
    lc_name text
    
    )
 ;
    insert into "aiesec_dw"."gold"."dim_lc__dbt_tmp" (
      lc_key, lc_name
    )
  
  (
    
    select lc_key, lc_name
    from (
        with distinct_lc as (
    select distinct lc_name
    from "aiesec_dw"."silver"."performance"
)

select
    cast(row_number() over (order by lc_name) as integer) as lc_key,
    lc_name
from distinct_lc
    ) as model_subq
  );
  