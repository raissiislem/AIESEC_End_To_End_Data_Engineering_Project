select
    row_number() over (order by stage_order) as stage_key,
    stage_name,
    stage_order
from {{ ref('stage_lookup') }}