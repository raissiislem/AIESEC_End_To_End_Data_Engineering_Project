select
    cast(row_number() over (order by stage_order) as integer) as stage_key,
    stage_name,
    cast(stage_order as integer) as stage_order
from "aiesec_dw"."silver"."stage_lookup"