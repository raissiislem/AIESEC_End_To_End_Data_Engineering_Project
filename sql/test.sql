-- AIESEC DW data quality checks
-- Run with: docker exec -i aiesec_postgres psql -U aiesec -d aiesec_dw -f /docker-entrypoint-initdb.d/test.sql
-- or from the host: psql -h localhost -U aiesec -d aiesec_dw -f sql/test.sql

-- 1) Bronze should have exactly 14 raw rows per month (1 row per LC)
SELECT
    period_start,
    COUNT(*) AS raw_rows_per_month
FROM bronze.raw_performance
GROUP BY period_start
HAVING COUNT(*) <> 14
ORDER BY period_start;

-- 2) Duplicate bronze rows by month + LC should be zero
SELECT
    period_start,
    raw_lc_name,
    COUNT(*) AS dupes
FROM bronze.raw_performance
GROUP BY period_start, raw_lc_name
HAVING COUNT(*) > 1
ORDER BY period_start, raw_lc_name;

-- 3) Missing months in bronze compared with expected monthly coverage (Jan 2023 to Sep 2026)
WITH expected_months AS (
    SELECT generate_series(date '2023-01-01', date '2026-09-01', interval '1 month')::date AS month_start
),
actual_months AS (
    SELECT DISTINCT period_start::date AS month_start
    FROM bronze.raw_performance
)
SELECT e.month_start AS missing_month
FROM expected_months e
LEFT JOIN actual_months a ON a.month_start = e.month_start
WHERE a.month_start IS NULL
ORDER BY e.month_start;

-- 4) Silver should be bronze_count * 46 metrics (one row per stage/program metric)
SELECT
    (SELECT COUNT(*) FROM bronze.raw_performance) AS bronze_rows,
    (SELECT COUNT(*) FROM silver.performance) AS silver_rows,
    (SELECT COUNT(*) FROM bronze.raw_performance) * 46 AS expected_silver_rows;

-- 5) Gold fact table should match the silver rows after dimension joins (same record count)
SELECT
    (SELECT COUNT(*) FROM silver.performance) AS expected_gold_rows,
    (SELECT COUNT(*) FROM gold.fact_performance) AS actual_gold_rows;

-- 6) Gold should not contain null foreign keys
SELECT COUNT(*) AS null_fk_rows
FROM gold.fact_performance
WHERE lc_key IS NULL
   OR date_key IS NULL
   OR direction_key IS NULL
   OR product_key IS NULL
   OR stage_key IS NULL;

-- 7) Date key check: normal months should have 644 fact rows (= 14 LCs x 46 metrics)
SELECT
    date_key,
    COUNT(*) AS fact_rows_per_date_key
FROM gold.fact_performance
GROUP BY date_key
HAVING COUNT(*) <> 644
ORDER BY date_key;

-- 8) Duplicate bronze_id within gold is expected because one bronze row expands to 46 metrics.
-- This query should only be used to explain duplicates, not as a data error.
SELECT
    performance_id,
    COUNT(*) AS metric_rows_per_bronze_record
FROM gold.fact_performance
GROUP BY performance_id
HAVING COUNT(*) > 1
ORDER BY performance_id
LIMIT 20;

-- 9) Golden dimension completeness check (fact rows should join to all dimensions)
SELECT COUNT(*) AS unmatched_fact_rows
FROM gold.fact_performance f
LEFT JOIN gold.dim_lc l ON l.lc_key = f.lc_key
LEFT JOIN gold.dim_date d ON d.date_key = f.date_key
LEFT JOIN gold.dim_direction dir ON dir.direction_key = f.direction_key
LEFT JOIN gold.dim_product p ON p.product_key = f.product_key
LEFT JOIN gold.dim_stage s ON s.stage_key = f.stage_key
WHERE l.lc_key IS NULL
   OR d.date_key IS NULL
   OR dir.direction_key IS NULL
   OR p.product_key IS NULL
   OR s.stage_key IS NULL;
