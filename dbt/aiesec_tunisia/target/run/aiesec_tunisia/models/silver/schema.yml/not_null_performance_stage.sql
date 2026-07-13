select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select stage
from "aiesec_dw"."silver"."performance"
where stage is null



      
    ) dbt_internal_test