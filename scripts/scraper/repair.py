import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import calendar
import time
import os
import psycopg2
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ── Config ────────────────────────────────────────────────────────
BASE_URL = "https://core.aiesec.org.eg/analytics/1559/LC19/"
POST_URL = "https://core.aiesec.org.eg/analytics/1559/TEMP/"

DB_CONFIG = {
    "host": "localhost",   # run this outside Docker, so localhost
    "database": "aiesec_dw",
    "user": "aiesec",
    "password": "aiesec",
    "port": 5432
}

# ── Helpers (same as your existing scraper) ───────────────────────
def is_main_lc_table(table):
    text = table.get_text(separator=" ").lower()
    return (
        "entity" in text and "sign" in text and "applicant" in text and
        "accepted" in text and "approved" in text and "realized" in text
    )

def get_fresh_csrf(session):
    res = session.get(BASE_URL, timeout=30)
    soup = BeautifulSoup(res.text, "lxml")
    tag = soup.find("input", {"name": "csrfmiddlewaretoken"})
    if not tag:
        raise Exception("CSRF token not found")
    return tag["value"]

# ── Step 1: Find which months are missing from Bronze ─────────────
def get_missing_months():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Get all months currently in Bronze
    cur.execute("""
        SELECT DISTINCT period_start
        FROM bronze.raw_performance
        ORDER BY period_start
    """)
    existing = set(row[0] for row in cur.fetchall())
    cur.close()
    conn.close()

    print(f"Months already in Bronze: {len(existing)}")

    # Build expected month list: Jan 2023 → current month
    today = datetime.now()
    expected = []
    for year in range(2023, today.year + 1):
        for month in range(1, 13):
            if year == today.year and month > today.month:
                break
            # Format matches what's in your DB (MM/DD/YYYY)
            period_start = f"{month:02d}/01/{year}"
            expected.append((year, month, period_start))

    print(f"Expected months total: {len(expected)}")

    # Find missing
    missing = [
        (year, month)
        for year, month, period_start in expected
        if period_start not in existing
    ]

    print(f"Missing months: {len(missing)}")
    for y, m in missing:
        print(f"  - {y}-{m:02d}")

    return missing

# ── Step 2: Scrape one month ──────────────────────────────────────
def scrape_month(session, year, month, retries=2):
    start_date = f"{month:02d}/01/{year}"
    last_day = calendar.monthrange(year, month)[1]
    end_date = f"{month:02d}/{last_day:02d}/{year}"
    headers = {"Referer": BASE_URL, "User-Agent": "Mozilla/5.0"}

    for attempt in range(1, retries + 2):
        try:
            csrf = get_fresh_csrf(session)
            payload = {
                "csrfmiddlewaretoken": csrf,
                "start_date": start_date,
                "end_date": end_date,
            }
            res = session.post(POST_URL, data=payload, headers=headers, timeout=60)
        except Exception as e:
            print(f"  attempt {attempt}: {e}, retrying...")
            time.sleep(5)
            continue

        soup = BeautifulSoup(res.text, "lxml")
        for t in soup.find_all("table"):
            if is_main_lc_table(t):
                tbody = t.find("tbody")
                if not tbody:
                    continue
                rows = tbody.find_all("tr")
                data = []
                for r in rows:
                    cols = [c.get_text(strip=True) for c in r.find_all("td")]
                    if cols:
                        data.append(cols)
                if not data:
                    continue

                max_len = max(len(r) for r in data)
                cleaned = [r + [None] * (max_len - len(r)) for r in data]
                df = pd.DataFrame(cleaned)
                df["scrape_id"] = f"backfill_{year}_{month:02d}_" + datetime.now().strftime("%Y%m%d%H%M%S")
                df["scraped_at"] = datetime.now()
                df["period_start"] = start_date
                df["period_end"] = end_date
                return df

        print(f"  attempt {attempt}: table not found, retrying...")
        time.sleep(3)

    print(f"  ⚠ Could not scrape {year}-{month:02d}")
    return None

# ── Step 3: Load into Bronze (idempotent) ─────────────────────────
def load_into_bronze(df):
    if df is None or df.empty:
        return 0

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    period_start = df["period_start"].iloc[0]

    # Delete existing rows for this month first — makes it safe to re-run
    cur.execute(
        "DELETE FROM bronze.raw_performance WHERE period_start = %s",
        (period_start,)
    )
    deleted = cur.rowcount
    if deleted > 0:
        print(f"  Removed {deleted} existing rows for {period_start}")

    # Save to CSV first (your existing load_file reads from CSV)
    os.makedirs("data/raw", exist_ok=True)
    period = period_start.replace("/", "_")
    path = f"data/raw/backfill_{period}.csv"
    df.to_csv(path, index=False)

    # Use your existing load_file function
    from bronze.load_bronze import load_file
    rows = load_file(cur, path)

    conn.commit()
    cur.close()
    conn.close()

    print(f"  ✔ Loaded {rows} rows for {period_start}")
    return rows

# ── Main ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Backfill Missing Months ===\n")

    missing = get_missing_months()

    if not missing:
        print("\n✅ Bronze is complete — no missing months.")
    else:
        session = requests.Session()
        failed = []

        for year, month in missing:
            print(f"\nScraping {year}-{month:02d}...")
            df = scrape_month(session, year, month)

            if df is not None:
                print(f"  Got {len(df)} rows from website")
                load_into_bronze(df)
            else:
                failed.append((year, month))

            time.sleep(2)

        print("\n=== Done ===")
        if failed:
            print(f"Still missing (website returned no data): {failed}")
        else:
            print("All missing months filled successfully.")

    # Final verification
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT period_start, COUNT(*) as row_count
        FROM bronze.raw_performance
        GROUP BY period_start
        HAVING COUNT(*) != 14
    """)
    problems = cur.fetchall()
    cur.close()
    conn.close()

    if problems:
        print(f"\n⚠ Months still not having 14 rows: {problems}")
    else:
        print("\n✅ All months verified — every month has exactly 14 rows.")