# 🌍 AIESEC End-to-End Data Engineering Project

A complete data engineering pipeline that extracts AIESEC performance metrics from the public core portal, stores them in a PostgreSQL warehouse, transforms them with dbt, and prepares them for analytics dashboards such as Power BI.

This project demonstrates an end-to-end ELT flow for historical and current-month operational reporting, with a bronze-silver-gold data warehouse model and automated orchestration using Airflow.

## ✨ Project purpose

The project collects AIESEC local committee performance data, including KPIs such as:

- sign ups
- applicants
- accepted
- approved
- realized
- finished
- completed

The data is collected by period, by local committee, and by performance category, then modeled into a star schema that can be consumed by BI tools and forecasting jobs.

## 🏗️ Architecture overview

The project follows a layered analytics architecture:

1. Data extraction
   - Python scraper scripts request data from the AIESEC core portal
   - raw monthly CSV files are saved under the data/raw folder

2. Bronze layer
   - raw scraped data is loaded into PostgreSQL in the bronze schema
   - raw rows keep the original source structure and metadata such as scrape_id and scraped_at

3. Silver layer
   - dbt transforms the bronze data into a clean normalized structure
   - one row is created per metric value using stage and program dimensions

4. Gold layer
   - business dimensions and fact tables are created in the gold schema
   - the warehouse is shaped for analytics and dashboarding

5. Consumption layer
   - tables can be used directly in Power BI, Excel, or ML/forecasting workflows

## 🧠 Technical stack

- Python for scraping and ETL logic
- Pandas for CSV handling and transformation
- PostgreSQL 15 as the analytics warehouse
- dbt for ELT modeling
- Airflow for orchestration and scheduled runs
- Docker Compose for local environment setup
- pgAdmin for database inspection

## 📁 Repository structure

```text
AIESEC_End_To_End_Data_Engineering_Project/
├── .env
├── docker-compose.yml
├── requirements.txt
├── requirements-airflow.txt
├── README.md
├── dags/
│   └── daily_scrape_and_load.py
├── airflow/
│   └── Dockerfile
├── data/
│   └── raw/
├── dbt/
│   └── aiesec_tunisia/
│       ├── dbt_project.yml
│       ├── models/
│       ├── seeds/
│       └── target/
├── dbt_profiles/
│   └── profiles.yml
├── logs/
├── scripts/
│   ├── bronze/
│   ├── ml/
│   └── scraper/
├── sql/
│   ├── init/
│   └── test.sql
└── modelisation/
    └── Architecture.drawio
```

## 🔄 Data flow

### 1) Scraping
The scripts in scripts/scraper use requests and BeautifulSoup to fetch monthly performance tables from the AIESEC portal.

Relevant files include:

- scrape_historical.py
- scrape_current_month.py
- repair.py
- utils.py
- config.py

### 2) CSV storage
The raw CSVs are saved in data/raw as files like:

- core_2023_01.csv
- core_2024_05.csv
- core_2026_06.csv

### 3) Bronze ingestion
The bronze loader reads each CSV and loads it into bronze.raw_performance.

This preserves the original scraped data and stores metadata such as:

- raw_lc_name
- period_start
- period_end
- metric columns
- scrape_id
- scraped_at

### 4) Silver modeling
The silver model transforms raw bronze rows into a cleaner, normalized structure.

Each row becomes a metric observation such as:

- stage = accepted
- program = igta
- value = 18

This makes it easier to aggregate and query the records for analytics.

### 5) Gold modeling
The gold layer creates the business dimensions and fact table:

- dim_date
- dim_lc
- dim_stage
- dim_direction
- dim_product
- fact_performance

This creates a star schema suitable for Power BI dashboards and KPI reporting.

## 🗄️ Warehouse model logic

The design follows a typical star schema:

- fact_performance stores performance values
- date, product, direction, stage, and LC dimension tables provide context
- fact rows connect through keys like date_key, lc_key, stage_key, product_key, and direction_key

The main fact table is built by joining performance metric rows to the relevant dimensions in the gold layer.

## 📊 Data quality checks performed

The project includes a validation file at [sql/test.sql](sql/test.sql) to verify:

- raw monthly row counts
- duplicate bronze rows
- missing months
- null foreign keys in gold
- date-key consistency
- expected fact row counts per month

I also identified and fixed a real issue: August 2026 had duplicated raw rows, which inflated `date_key = 44` to 1,288 rows instead of the expected 644.

The fix was to deduplicate the raw monthly inserts before loading to bronze and then rebuild the dbt models.

## 🚀 How to run the project

### Start the environment

```bash
docker compose up -d
```

### Run dbt models

```bash
docker exec -i aiesec_dbt sh -lc "cd /usr/app/dbt && dbt run --profiles-dir /root/.dbt --project-dir /usr/app/dbt"
```

### Run warehouse validation checks

```bash
psql -h localhost -U aiesec -d aiesec_dw -f sql/test.sql
```

### Access the tools

- PostgreSQL: localhost:5432
- pgAdmin: http://localhost:5050
- Airflow: http://localhost:8080

## 📌 Notes

This project is more than a scraper. It is a full analytics engineering workflow that turns web data into trusted reporting assets.

It is designed for:

- ETL/ELT logic
- warehouse modeling
- data quality validation
- BI consumption
- future forecasting and ML use cases

## ⭐ Project rating

I would absolutely star this project because it demonstrates a complete end-to-end data pipeline from raw web extraction to a warehouse model ready for Power BI and analytics.

It is a strong portfolio project for:

- data engineering
- analytics engineering
- Python + SQL + dbt work
- modern warehouse design
- business intelligence preparation

## 🙌 Summary

This project collects AIESEC operational data, transforms it into a reliable star-schema warehouse, validates its quality, and prepares it for reporting and future analytics use.
