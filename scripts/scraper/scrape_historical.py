import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import calendar
import time
import os

BASE_URL = "https://core.aiesec.org.eg/analytics/1559/LC19/"
POST_URL = "https://core.aiesec.org.eg/analytics/1559/TEMP/"


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


def scrape_month(session, year, month, retries=2):
    start_date = f"{month:02d}/01/{year}"
    last_day = calendar.monthrange(year, month)[1]
    end_date = f"{month:02d}/{last_day:02d}/{year}"

    headers = {"Referer": BASE_URL, "User-Agent": "Mozilla/5.0"}

    main_table = None

    for attempt in range(1, retries + 2):
        try:
            csrf = get_fresh_csrf(session)  # fresh token every attempt, every month
            payload = {
                "csrfmiddlewaretoken": csrf,
                "start_date": start_date,
                "end_date": end_date,
            }
            res = session.post(POST_URL, data=payload, headers=headers, timeout=60)
        except requests.exceptions.RequestException as e:
            print(f"  attempt {attempt}: request failed ({type(e).__name__}: {e}), retrying...")
            time.sleep(5)
            continue

        soup = BeautifulSoup(res.text, "lxml")
        tables = soup.find_all("table")

        main_table = None
        for t in tables:
            if is_main_lc_table(t):
                main_table = t
                break

        if main_table is not None:
            break

        print(f"  attempt {attempt}: table not found (status {res.status_code}, {len(tables)} tables on page), retrying...")
        time.sleep(3)

    if main_table is None:
        print(f"  ⚠ No table found for {start_date} - {end_date} after {retries + 1} attempts, skipping")
        return None

    tbody = main_table.find("tbody")
    if tbody is None:
        print(f"  ⚠ No <tbody> found for {start_date} - {end_date}, skipping")
        return None

    rows = tbody.find_all("tr")
    data = []
    for r in rows:
        cols = [c.get_text(strip=True) for c in r.find_all("td")]
        if len(cols) == 0:
            continue
        data.append(cols)

    if not data:
        print(f"  ⚠ Empty table for {start_date} - {end_date}, skipping")
        return None

    max_len = max(len(r) for r in data)
    cleaned = [r + [None] * (max_len - len(r)) for r in data]

    df = pd.DataFrame(cleaned)
    df["scrape_id"] = f"historical_{year}_{month:02d}_" + datetime.now().strftime("%Y%m%d%H%M%S")
    df["scraped_at"] = datetime.now()
    df["period_start"] = start_date
    df["period_end"] = end_date

    return df


# -----------------------------
# MAIN LOOP: Jan 2023 -> Jun 2026
# -----------------------------
session = requests.Session()

periods = []
for year in range(2023, 2027):
    for month in range(1, 13):
        if year == 2026 and month > 6:
            break
        periods.append((year, month))

print(f"Total months in range: {len(periods)}")

os.makedirs("data/raw", exist_ok=True)

failed_months = []

for year, month in periods:
    output_path = f"data/raw/core_{year}_{month:02d}.csv"

    print(f"Scraping {year}-{month:02d}...")  # no skip-if-exists this time — we're rebuilding everything

    try:
        df = scrape_month(session, year, month)
    except Exception as e:
        print(f"  ✗ Unexpected error on {year}-{month:02d}: {type(e).__name__}: {e}")
        failed_months.append((year, month))
        continue

    if df is not None:
        df.to_csv(output_path, index=False)
        print(f"  ✔ Saved {output_path} ({len(df)} rows)")
    else:
        failed_months.append((year, month))

    time.sleep(1)

print("\nDONE.")
if failed_months:
    print(f"Months that still need attention: {failed_months}")
else:
    print("All months scraped successfully.")