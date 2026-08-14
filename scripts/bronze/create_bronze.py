import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "database": "aiesec_dw",
    "user": "aiesec",
    "password": "aiesec",
    "port": 5432
}

CREATE_SCHEMA_SQL = "CREATE SCHEMA IF NOT EXISTS bronze;"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS bronze.raw_performance (
    id              SERIAL PRIMARY KEY,
    raw_lc_name     TEXT,
    period_start    TEXT,
    period_end      TEXT,

    su_total TEXT, su_ogv TEXT, su_ogta TEXT, su_ogte TEXT,

    ap_total TEXT, ap_igv TEXT, ap_igta TEXT, ap_igte TEXT, ap_ogv TEXT, ap_ogta TEXT, ap_ogte TEXT,
    ac_total TEXT, ac_igv TEXT, ac_igta TEXT, ac_igte TEXT, ac_ogv TEXT, ac_ogta TEXT, ac_ogte TEXT,
    av_total TEXT, av_igv TEXT, av_igta TEXT, av_igte TEXT, av_ogv TEXT, av_ogta TEXT, av_ogte TEXT,
    rl_total TEXT, rl_igv TEXT, rl_igta TEXT, rl_igte TEXT, rl_ogv TEXT, rl_ogta TEXT, rl_ogte TEXT,
    fn_total TEXT, fn_igv TEXT, fn_igta TEXT, fn_igte TEXT, fn_ogv TEXT, fn_ogta TEXT, fn_ogte TEXT,
    cp_total TEXT, cp_igv TEXT, cp_igta TEXT, cp_igte TEXT, cp_ogv TEXT, cp_ogta TEXT, cp_ogte TEXT,

    scrape_id       TEXT NOT NULL,
    scraped_at      TIMESTAMP NOT NULL
);
"""

def load_current_month_file(cur, file_path, metric_columns, final_columns, expected_cols):
    df = pd.read_csv(file_path)
    if len(df.columns) != expected_cols:
        raise ValueError(f"Expected {expected_cols} columns, got {len(df.columns)}")

    rename_map = {"1": "raw_lc_name"}
    for i, name in enumerate(metric_columns):
        rename_map[str(i + 2)] = name
    df = df.rename(columns=rename_map)
    df = df[final_columns]

    period_start = df["period_start"].iloc[0]  # same for every row in this file

    # Delete any existing rows for this exact period_start (this month's prior snapshot)
    cur.execute("DELETE FROM bronze.raw_performance WHERE period_start = %s", (period_start,))

    insert_query = f"""
        INSERT INTO bronze.raw_performance ({", ".join(final_columns)})
        VALUES ({", ".join(["%s"] * len(final_columns))})
    """
    for _, row in df.iterrows():
        cur.execute(insert_query, tuple(row.values))

    return len(df)

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    print("Creating schema 'bronze' (if not exists)...")
    cur.execute(CREATE_SCHEMA_SQL)

    print("Creating table 'bronze.raw_performance' (if not exists)...")
    cur.execute(CREATE_TABLE_SQL)

    conn.commit()
    cur.close()
    conn.close()

    print("✔ Bronze schema/table ready.")

if __name__ == "__main__":
    main()