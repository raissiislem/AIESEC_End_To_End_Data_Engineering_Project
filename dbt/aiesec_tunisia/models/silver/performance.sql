{% set stage_program_map = [
    ('su', 'sign_ups',  ['total', 'ogv', 'ogta', 'ogte']),
    ('ap', 'applicants', ['total', 'igv', 'igta', 'igte', 'ogv', 'ogta', 'ogte']),
    ('ac', 'accepted',   ['total', 'igv', 'igta', 'igte', 'ogv', 'ogta', 'ogte']),
    ('av', 'approved',   ['total', 'igv', 'igta', 'igte', 'ogv', 'ogta', 'ogte']),
    ('rl', 'realized',   ['total', 'igv', 'igta', 'igte', 'ogv', 'ogta', 'ogte']),
    ('fn', 'finished',   ['total', 'igv', 'igta', 'igte', 'ogv', 'ogta', 'ogte']),
    ('cp', 'completed',  ['total', 'igv', 'igta', 'igte', 'ogv', 'ogta', 'ogte'])
] %}

{% set combos = [] %}
{% for code, stage_name, programs in stage_program_map %}
  {% for program in programs %}
    {% do combos.append((code, stage_name, program)) %}
  {% endfor %}
{% endfor %}

with source as (
    select * from {{ source('bronze', 'raw_performance') }}
)

{% for code, stage_name, program in combos %}
select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    '{{ stage_name }}' as stage,
    '{{ program }}'    as program,
    cast({{ code }}_{{ program }} as integer) as value
from source
{% if not loop.last %}union all{% endif %}
{% endfor %}