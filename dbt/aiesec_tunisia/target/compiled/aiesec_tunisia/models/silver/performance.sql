



  
    
  
    
  
    
  

  
    
  
    
  
    
  
    
  
    
  
    
  

  
    
  
    
  
    
  
    
  
    
  
    
  

  
    
  
    
  
    
  
    
  
    
  
    
  

  
    
  
    
  
    
  
    
  
    
  
    
  

  
    
  
    
  
    
  
    
  
    
  
    
  

  
    
  
    
  
    
  
    
  
    
  
    
  


with source as (
    select * from "aiesec_dw"."bronze"."raw_performance"
)


select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'sign_ups' as stage,
    'ogv'    as program,
    cast(su_ogv as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'sign_ups' as stage,
    'ogta'    as program,
    cast(su_ogta as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'sign_ups' as stage,
    'ogte'    as program,
    cast(su_ogte as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'applicants' as stage,
    'igv'    as program,
    cast(ap_igv as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'applicants' as stage,
    'igta'    as program,
    cast(ap_igta as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'applicants' as stage,
    'igte'    as program,
    cast(ap_igte as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'applicants' as stage,
    'ogv'    as program,
    cast(ap_ogv as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'applicants' as stage,
    'ogta'    as program,
    cast(ap_ogta as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'applicants' as stage,
    'ogte'    as program,
    cast(ap_ogte as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'accepted' as stage,
    'igv'    as program,
    cast(ac_igv as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'accepted' as stage,
    'igta'    as program,
    cast(ac_igta as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'accepted' as stage,
    'igte'    as program,
    cast(ac_igte as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'accepted' as stage,
    'ogv'    as program,
    cast(ac_ogv as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'accepted' as stage,
    'ogta'    as program,
    cast(ac_ogta as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'accepted' as stage,
    'ogte'    as program,
    cast(ac_ogte as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'approved' as stage,
    'igv'    as program,
    cast(av_igv as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'approved' as stage,
    'igta'    as program,
    cast(av_igta as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'approved' as stage,
    'igte'    as program,
    cast(av_igte as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'approved' as stage,
    'ogv'    as program,
    cast(av_ogv as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'approved' as stage,
    'ogta'    as program,
    cast(av_ogta as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'approved' as stage,
    'ogte'    as program,
    cast(av_ogte as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'realized' as stage,
    'igv'    as program,
    cast(rl_igv as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'realized' as stage,
    'igta'    as program,
    cast(rl_igta as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'realized' as stage,
    'igte'    as program,
    cast(rl_igte as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'realized' as stage,
    'ogv'    as program,
    cast(rl_ogv as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'realized' as stage,
    'ogta'    as program,
    cast(rl_ogta as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'realized' as stage,
    'ogte'    as program,
    cast(rl_ogte as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'finished' as stage,
    'igv'    as program,
    cast(fn_igv as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'finished' as stage,
    'igta'    as program,
    cast(fn_igta as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'finished' as stage,
    'igte'    as program,
    cast(fn_igte as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'finished' as stage,
    'ogv'    as program,
    cast(fn_ogv as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'finished' as stage,
    'ogta'    as program,
    cast(fn_ogta as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'finished' as stage,
    'ogte'    as program,
    cast(fn_ogte as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'completed' as stage,
    'igv'    as program,
    cast(cp_igv as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'completed' as stage,
    'igta'    as program,
    cast(cp_igta as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'completed' as stage,
    'igte'    as program,
    cast(cp_igte as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'completed' as stage,
    'ogv'    as program,
    cast(cp_ogv as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'completed' as stage,
    'ogta'    as program,
    cast(cp_ogta as integer) as value
from source
union all

select
    id              as bronze_id,
    scrape_id,
    period_start,
    period_end,
    scraped_at,
    raw_lc_name     as lc_name,
    'completed' as stage,
    'ogte'    as program,
    cast(cp_ogte as integer) as value
from source

