import pandas as pd
import psycopg2
import glob
import os

DB_CONFIG = {
    "host": "localhost",
    "database": "aiesec_dw",
    "user": "aiesec",
    "password": "aiesec",
    "port": 5432
}

metric_columns = [
    "su_total", "su_ogv", "su_ogta", "su_ogte",

    "ap_total", "ap_igv", "ap_igta", "ap_igte", "ap_ogv", "ap_ogta", "ap_ogte",
    "ac_total", "ac_igv", "ac_igta", "ac_igte", "ac_ogv", "ac_ogta", "ac_ogte",
    "av_total", "av_igv", "av_igta", "av_igte", "av_ogv", "av_ogta", "av_ogte",
    "rl_total", "rl_igv", "rl_igta", "rl_igte", "rl_ogv", "rl_ogta", "rl_ogte",
    "fn_total", "fn_igv", "fn_igta", "fn_igte", "fn_ogv", "fn_ogta", "fn_ogte",
    "cp_total", "cp_igv", "cp_igta", "cp_igte", "cp_ogv", "cp_ogta", "cp_ogte",
]  # 46 names, matching CSV columns "2" through "47"

final_columns = ["raw_lc_name", "period_start", "period_end"] + metric_columns + ["scrape_id", "scraped_at"]

expected_cols = 52  # 48 positional (0-47) + scrape_id + scraped_at + period_start + period_end


def load_file(cur, file_path):
    df = pd.read_csv(file_path)

    if len(df.columns) != expected_cols:
        print(f"  ✗ Skipping {file_path}: expected {expected_cols} columns, got {len(df.columns)}")
        return 0

    rename_map = {"1": "raw_lc_name"}
    for i, name in enumerate(metric_columns):
        rename_map[str(i + 2)] = name

    df = df.rename(columns=rename_map)
    df = df[final_columns]

    # Prevent duplicate raw rows when the same month is reloaded or a backfill is rerun.
    if "period_start" in df.columns and not df.empty:
        period_start = df["period_start"].iloc[0]
        cur.execute("DELETE FROM bronze.raw_performance WHERE period_start = %s", (period_start,))

    # Drop any duplicate row within the same file before insert.
    df = df.drop_duplicates(subset=["raw_lc_name", "period_start", "scrape_id"], keep="last")

    insert_query = f"""
        INSERT INTO bronze.raw_performance (
            {", ".join(final_columns)}
        )
        VALUES ({", ".join(["%s"] * len(final_columns))})
    """

    for _, row in df.iterrows():
        cur.execute(insert_query, tuple(row.values))

    return len(df)


def main():
    raw_files = sorted(glob.glob("data/raw/core_*.csv"))
    if not raw_files:
        raise FileNotFoundError("No CSV files found in data/raw/")

    print(f"Found {len(raw_files)} files to load.")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    total_rows = 0
    skipped_files = []

    for file_path in raw_files:
        print(f"Loading {file_path}...")
        try:
            rows_loaded = load_file(cur, file_path)
            total_rows += rows_loaded
            print(f"  ✔ {rows_loaded} rows")
        except Exception as e:
            print(f"  ✗ Failed on {file_path}: {type(e).__name__}: {e}")
            skipped_files.append(file_path)
            conn.rollback()  # undo any partial insert from this file, don't corrupt the transaction
            continue

    conn.commit()
    cur.close()
    conn.close()

    print(f"\n✔ Bronze load completed — {total_rows} total rows inserted from {len(raw_files)} files.")
    if skipped_files:
        print(f"Files skipped due to errors: {skipped_files}")


if __name__ == "__main__":
    main()