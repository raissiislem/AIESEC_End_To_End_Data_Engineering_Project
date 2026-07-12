import pandas as pd
import psycopg2
import glob
import os
from datetime import datetime

DB_CONFIG = {
    "host": "localhost",
    "database": "aiesec_dw",
    "user": "aiesec",
    "password": "aiesec",
    "port": 5432
}

# 1. Auto-detect the latest scraped file
raw_files = glob.glob("data/raw/core_*.csv")
if not raw_files:
    raise FileNotFoundError("No CSV files found in data/raw/")
file_path = max(raw_files, key=os.path.getmtime)
print("Loading file:", file_path)

df = pd.read_csv(file_path)

print("Columns:", df.columns.tolist())
print("Total columns:", len(df.columns))

# 2. Sanity check column count BEFORE inserting anything
# 48 positional metric/name columns (0-47) + scrape_id + scraped_at + period_start + period_end
expected_cols = 52
if len(df.columns) != expected_cols:
    raise ValueError(
        f"Expected {expected_cols} columns, got {len(df.columns)}. "
        f"Columns found: {df.columns.tolist()}"
    )

# 3. Explicit column mapping — position -> real name
metric_columns = [
    "su_total", "su_ogv", "su_ogta", "su_ogte",  # su_total = the OGX column

    "ap_total", "ap_igv", "ap_igta", "ap_igte", "ap_ogv", "ap_ogta", "ap_ogte",
    "ac_total", "ac_igv", "ac_igta", "ac_igte", "ac_ogv", "ac_ogta", "ac_ogte",
    "av_total", "av_igv", "av_igta", "av_igte", "av_ogv", "av_ogta", "av_ogte",
    "rl_total", "rl_igv", "rl_igta", "rl_igte", "rl_ogv", "rl_ogta", "rl_ogte",
    "fn_total", "fn_igv", "fn_igta", "fn_igte", "fn_ogv", "fn_ogta", "fn_ogte",
    "cp_total", "cp_igv", "cp_igta", "cp_igte", "cp_ogv", "cp_ogta", "cp_ogte",
]  # 46 names, matching CSV columns "2" through "47"

# CSV column "1" = LC name, columns "2".."47" = the 46 metrics above
rename_map = {"1": "raw_lc_name"}
for i, name in enumerate(metric_columns):
    rename_map[str(i + 2)] = name

df = df.rename(columns=rename_map)

# 4. Keep only the columns we actually want, in the right order — drops column "0" (blank) automatically
final_columns = ["raw_lc_name", "period_start", "period_end"] + metric_columns + ["scrape_id", "scraped_at"]
df = df[final_columns]

# 5. Insert
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

insert_query = f"""
    INSERT INTO bronze.raw_performance (
        {", ".join(final_columns)}
    )
    VALUES ({", ".join(["%s"] * len(final_columns))})
"""

for _, row in df.iterrows():
    cur.execute(insert_query, tuple(row.values))

conn.commit()
cur.close()
conn.close()

print(f"✔ Bronze load completed successfully — {len(df)} rows inserted from {file_path}")