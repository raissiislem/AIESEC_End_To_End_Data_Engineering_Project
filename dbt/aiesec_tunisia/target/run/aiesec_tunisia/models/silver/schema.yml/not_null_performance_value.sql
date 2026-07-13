select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select value
from "aiesec_dw"."silver"."performance"
where value is null



      
    ) dbt_internal_test