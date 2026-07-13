select
    row_number() over (order by product_code) as product_key,
    product_code,
    product_name
from "aiesec_dw"."silver"."product_lookup"