select
    row_number() over (order by direction_code) as direction_key,
    direction_code,
    direction_name
from {{ ref('direction_lookup') }}