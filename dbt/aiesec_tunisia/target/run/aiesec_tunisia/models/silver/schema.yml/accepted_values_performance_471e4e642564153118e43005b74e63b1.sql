select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    

with all_values as (

    select
        stage as value_field,
        count(*) as n_records

    from "aiesec_dw"."silver"."performance"
    group by stage

)

select *
from all_values
where value_field not in (
    'sign_ups','applicants','accepted','approved','realized','finished','completed'
)



      
    ) dbt_internal_test