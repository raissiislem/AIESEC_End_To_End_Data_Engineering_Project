{% set stage_program_map = [
    ('su', 'sign_ups',  ['ogv', 'ogta', 'ogte']),
    ('ap', 'applicants', ['igv', 'igta', 'igte', 'ogv', 'ogta', 'ogte']),
    ('ac', 'accepted',   ['igv', 'igta', 'igte', 'ogv', 'ogta', 'ogte']),
    ('av', 'approved',   ['igv', 'igta', 'igte', 'ogv', 'ogta', 'ogte']),
    ('rl', 'realized',   ['igv', 'igta', 'igte', 'ogv', 'ogta', 'ogte']),
    ('fn', 'finished',   ['igv', 'igta', 'igte', 'ogv', 'ogta', 'ogte']),
    ('cp', 'completed',  ['igv', 'igta', 'igte', 'ogv', 'ogta', 'ogte'])
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