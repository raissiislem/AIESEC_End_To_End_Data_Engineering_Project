import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "database": "aiesec_dw",
    "user": "aiesec",
    "password": "aiesec",
    "port": 5432
}

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS gold.fact_prediction (
    prediction_id   BIGSERIAL PRIMARY KEY,
    lc_key          INTEGER NOT NULL REFERENCES gold.dim_lc(lc_key),
    date_key        INTEGER NOT NULL REFERENCES gold.dim_date(date_key),
    stage_key       INTEGER NOT NULL REFERENCES gold.dim_stage(stage_key),
    predicted_value INTEGER NOT NULL,
    lower_bound     INTEGER,
    upper_bound     INTEGER,
    model_version   TEXT,
    generated_at    TIMESTAMP NOT NULL
);
"""

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    print("Creating table 'gold.fact_prediction' (if not exists)...")
    cur.execute(CREATE_TABLE_SQL)
    conn.commit()
    cur.close()
    conn.close()
    print("✔ gold.fact_prediction ready.")

if __name__ == "__main__":
    main()