import requests
import pandas as pd
import time

API_KEY = "3l4nEbnBekOTEAxeD7tV0SZMUXoxiREZ"

TICKERS = ["AAPL", "NVDA", "TSLA", "AMZN", "META"]
LIMIT_YEARS = 5


def get_json(url):
    r = requests.get(url)
    data = r.json()

    # API issues
    if "Note" in data:
        raise Exception("⚠️ API rate limit hit. Try again later.")
    if "Information" in data:
        raise Exception(f"⚠️ {data['Information']}")
    if "Error Message" in data:
        raise Exception(f"❌ API error: {data['Error Message']}")

    return data


def to_number(x):
    if x in [None, "None", ""]:
        return None
    return float(x)


rows = []

for ticker in TICKERS:
    print(f"Fetching {ticker}...")

    income_url = f"https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={ticker}&apikey={API_KEY}"
    bs_url = f"https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={ticker}&apikey={API_KEY}"

    income_data = get_json(income_url)
    time.sleep(3)
    bs_data = get_json(bs_url)
    time.sleep(3)

    income_reports = income_data.get("annualReports", [])[:LIMIT_YEARS]
    bs_reports = bs_data.get("annualReports", [])[:LIMIT_YEARS]

    # Map Balance Sheet by Year
    bs_by_year = {}
    for b in bs_reports:
        year = b["fiscalDateEnding"][:4]
        bs_by_year[year] = b

    for inc in income_reports:
        year = inc["fiscalDateEnding"][:4]
        bs = bs_by_year.get(year, {})

        rows.append({
            "Company": ticker,
            "Year": int(year),

            "Revenue": to_number(inc.get("totalRevenue")),
            "NetIncome": to_number(inc.get("netIncome")),

            "TotalAssets": to_number(bs.get("totalAssets")),
            "TotalLiabilities": to_number(bs.get("totalLiabilities")),
            "Equity": to_number(bs.get("totalShareholderEquity")),

            "CurrentAssets": to_number(bs.get("totalCurrentAssets")),
            "CurrentLiabilities": to_number(bs.get("totalCurrentLiabilities")),
        })

df = pd.DataFrame(rows)

if df.empty:
    print("❌ No data collected. API might be limited right now.")
else:
    df = df.sort_values(["Company", "Year"], ascending=[True, True])
    df.to_csv("financials_powerbi.csv", index=False)

    print("\n✅ Saved file: financials_powerbi.csv")
    print(df["Company"].value_counts())
    print(df.tail(10))
