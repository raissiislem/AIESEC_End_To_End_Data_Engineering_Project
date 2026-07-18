import pandas as pd
import psycopg2
from datetime import datetime
from prophet import Prophet
import warnings

warnings.filterwarnings("ignore")  # Prophet is chatty with harmless convergence warnings

DB_CONFIG = {
    "host": "localhost",
    "database": "aiesec_dw",
    "user": "aiesec",
    "password": "aiesec",
    "port": 5432
}

MIN_MONTHS_WITH_ACTIVITY = 12   # skip series with less history than this
FORECAST_MONTHS = 6             # Jul-Dec 2026
MODEL_VERSION = "prophet_v1"


def load_training_data(conn):
    query = """
        SELECT
            l.lc_name,
            s.stage_name,
            d.date,
            f.value
        FROM gold.fact_performance f
        JOIN gold.dim_lc l         ON f.lc_key = l.lc_key
        JOIN gold.dim_stage s      ON f.stage_key = s.stage_key
        JOIN gold.dim_direction dr ON f.direction_key = dr.direction_key
        JOIN gold.dim_product p    ON f.product_key = p.product_key
        JOIN gold.dim_date d       ON f.date_key = d.date_key
        WHERE dr.direction_code = 'total'
        AND p.product_code = 'total'
        ORDER BY l.lc_name, s.stage_name, d.date
    """
    return pd.read_sql(query, conn)


def load_dim_lookup(conn, table, key_col, name_col):
    query = f"SELECT {key_col}, {name_col} FROM gold.{table}"
    df = pd.read_sql(query, conn)
    return dict(zip(df[name_col], df[key_col]))


def get_future_date_keys(conn):
    query = """
        SELECT date_key, date
        FROM gold.dim_date
        WHERE date >= '2026-07-01' AND date <= '2026-12-01'
        ORDER BY date
    """
    df = pd.read_sql(query, conn)
    return dict(zip(df["date"].astype(str), df["date_key"]))


def forecast_series(df_series):
    """df_series must have columns: ds, y"""
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
    )
    model.fit(df_series)

    future = model.make_future_dataframe(periods=FORECAST_MONTHS, freq="MS")
    forecast = model.predict(future)

    return forecast.tail(FORECAST_MONTHS)[["ds", "yhat", "yhat_lower", "yhat_upper"]]


def main():
    conn = psycopg2.connect(**DB_CONFIG)

    print("Loading training data...")
    df = load_training_data(conn)
    print(f"  {len(df)} rows loaded, covering {df['lc_name'].nunique()} LCs x {df['stage_name'].nunique()} stages")

    lc_lookup = load_dim_lookup(conn, "dim_lc", "lc_key", "lc_name")
    stage_lookup = load_dim_lookup(conn, "dim_stage", "stage_key", "stage_name")
    future_date_lookup = get_future_date_keys(conn)

    if len(future_date_lookup) != FORECAST_MONTHS:
        raise ValueError(
            f"Expected {FORECAST_MONTHS} future date rows in gold.dim_date, found {len(future_date_lookup)}. "
            "Did you rebuild dim_date with the full calendar?"
        )

    results = []
    skipped = []

    for (lc_name, stage_name), group in df.groupby(["lc_name", "stage_name"]):
        months_with_activity = (group["value"] > 0).sum()

        if months_with_activity < MIN_MONTHS_WITH_ACTIVITY:
            skipped.append((lc_name, stage_name, months_with_activity))
            continue

        series = group[["date", "value"]].rename(columns={"date": "ds", "value": "y"})

        try:
            forecast = forecast_series(series)
        except Exception as e:
            print(f"  ✗ Failed to forecast {lc_name} / {stage_name}: {e}")
            skipped.append((lc_name, stage_name, "error"))
            continue

        lc_key = lc_lookup.get(lc_name)
        stage_key = stage_lookup.get(stage_name)

        for _, row in forecast.iterrows():
            date_str = row["ds"].strftime("%Y-%m-%d")
            date_key = future_date_lookup.get(date_str)

            if date_key is None:
                print(f"  ⚠ No date_key found for {date_str}, skipping this row")
                continue

            results.append((
                lc_key,
                date_key,
                stage_key,
                max(0, round(row["yhat"])),          # predictions shouldn't go negative
                max(0, round(row["yhat_lower"])),
                max(0, round(row["yhat_upper"])),
                MODEL_VERSION,
                datetime.now()
            ))

    print(f"\nForecasted {len(results)} predictions, skipped {len(skipped)} series (insufficient history or error)")
    if skipped:
        print("Skipped series:", skipped)

    if not results:
        print("No predictions to insert. Exiting.")
        return

    cur = conn.cursor()
    insert_query = """
        INSERT INTO gold.fact_prediction (
            lc_key, date_key, stage_key,
            predicted_value, lower_bound, upper_bound,
            model_version, generated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cur.executemany(insert_query, results)
    conn.commit()
    cur.close()
    conn.close()

    print(f"✔ Inserted {len(results)} predictions into gold.fact_prediction")


if __name__ == "__main__":
    main()