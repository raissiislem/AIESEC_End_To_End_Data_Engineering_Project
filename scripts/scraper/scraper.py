import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime


BASE_URL = "https://core.aiesec.org.eg/analytics/1559/LC19/"


# -----------------------------
# 1. SESSION + CSRF
# -----------------------------
session = requests.Session()

res = session.get(BASE_URL)
soup = BeautifulSoup(res.text, "lxml")

csrf_tag = soup.find("input", {"name": "csrfmiddlewaretoken"})
if not csrf_tag:
    raise Exception("CSRF token not found")

csrf = csrf_tag["value"]
print("CSRF:", csrf)


# -----------------------------
# 2. POST REQUEST
# -----------------------------
payload = {
    "csrfmiddlewaretoken": csrf,
    "start_date": "01/01/2023",
    "end_date": "01/31/2023",
}

headers = {
    "Referer": BASE_URL,
    "User-Agent": "Mozilla/5.0"
}

res = session.post(
    "https://core.aiesec.org.eg/analytics/1559/TEMP/",
    data=payload,
    headers=headers
)

print("Status:", res.status_code)
print("URL:", res.url)


soup = BeautifulSoup(res.text, "lxml")

tables = soup.find_all("table")
print("Tables found:", len(tables))


# -----------------------------
# 3. SMART TABLE DETECTION
# -----------------------------
def is_main_lc_table(table):
    text = table.get_text(separator=" ").lower()

    return (
        "entity" in text and
        "sign" in text and
        "applicant" in text and
        "accepted" in text and
        "approved" in text and
        "realized" in text
    )


main_table = None

for t in tables:
    if is_main_lc_table(t):
        main_table = t
        break

if main_table is None:
    raise Exception("No valid LC performance table found")


# -----------------------------
# 4. EXTRACT ROWS (data rows only, skip headers)
# -----------------------------
tbody = main_table.find("tbody")

if tbody is None:
    raise Exception("No <tbody> found in main table — inspect HTML structure")

rows = tbody.find_all("tr")

data = []

for r in rows:
    cols = [c.get_text(strip=True) for c in r.find_all("td")]  # td only, not th

    if len(cols) == 0:
        continue

    data.append(cols)

print("Raw rows extracted:", len(data))


# -----------------------------
# 5. NORMALIZE COLUMN LENGTHS
# -----------------------------
max_len = max(len(r) for r in data)

cleaned = []
for r in data:
    r = r + [None] * (max_len - len(r))
    cleaned.append(r)


# -----------------------------
# 6. BUILD DATAFRAME
# -----------------------------
df = pd.DataFrame(cleaned)


# -----------------------------
# 7. ADD METADATA (BRONZE READY)
# -----------------------------
df["scrape_id"] = "manual_run_" + datetime.now().strftime("%Y%m%d%H%M%S")
df["scraped_at"] = datetime.now()
df["period_start"] = payload["start_date"]
df["period_end"] = payload["end_date"]


# -----------------------------
# 8. SAVE RAW FILE
# -----------------------------
output_path = f"data/raw/core_{datetime.now().strftime('%Y_%m_%d_%H_%M')}.csv"
df.to_csv(output_path, index=False)

print("\nDONE")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("Saved:", output_path)