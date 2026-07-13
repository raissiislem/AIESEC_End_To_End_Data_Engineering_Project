select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select bronze_id
from "aiesec_dw"."silver"."performance"
where bronze_id is null



      
    ) dbt_internal_test