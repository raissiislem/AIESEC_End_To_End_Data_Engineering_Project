import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import calendar
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


def scrape_range(session, start_date, end_date, retries=2):
    headers = {"Referer": BASE_URL, "User-Agent": "Mozilla/5.0"}
    main_table = None

    for attempt in range(1, retries + 2):
        try:
            csrf = get_fresh_csrf(session)
            payload = {
                "csrfmiddlewaretoken": csrf,
                "start_date": start_date,
                "end_date": end_date,
            }
            res = session.post(POST_URL, data=payload, headers=headers, timeout=60)
        except requests.exceptions.RequestException as e:
            print(f"  attempt {attempt}: request failed ({type(e).__name__}: {e}), retrying...")
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

        print(f"  attempt {attempt}: table not found, retrying...")

    if main_table is None:
        raise Exception(f"No table found for {start_date} - {end_date} after {retries + 1} attempts")

    tbody = main_table.find("tbody")
    if tbody is None:
        raise Exception(f"No <tbody> found for {start_date} - {end_date}")

    rows = tbody.find_all("tr")
    data = []
    for r in rows:
        cols = [c.get_text(strip=True) for c in r.find_all("td")]
        if len(cols) == 0:
            continue
        data.append(cols)

    if not data:
        raise Exception(f"Empty table for {start_date} - {end_date}")

    max_len = max(len(r) for r in data)
    cleaned = [r + [None] * (max_len - len(r)) for r in data]

    df = pd.DataFrame(cleaned)
    df["scrape_id"] = "daily_current_month_" + datetime.now().strftime("%Y%m%d%H%M%S")
    df["scraped_at"] = datetime.now()
    df["period_start"] = start_date
    df["period_end"] = end_date

    return df


def main():
    today = datetime.now()
    year, month = today.year, today.month

    start_date = f"{month:02d}/01/{year}"
    end_date = today.strftime("%m/%d/%Y")  # today, not end of month — this month is still in progress

    print(f"Scraping current month so far: {start_date} to {end_date}")

    session = requests.Session()
    df = scrape_range(session, start_date, end_date)

    os.makedirs("data/raw", exist_ok=True)
    # NOTE: fixed filename per month, not per scrape-timestamp — always overwrites today's version
    output_path = f"data/raw/core_{year}_{month:02d}_current.csv"
    df.to_csv(output_path, index=False)

    print(f"✔ Saved {output_path} ({len(df)} rows)")
    return output_path


if __name__ == "__main__":
    main()