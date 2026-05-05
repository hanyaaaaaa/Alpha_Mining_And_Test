import requests
from datetime import date, timedelta

FMP_API_KEY = "aeAt9pG7MHDV3jLlzdbkjjEM4PPn8Z43"
BASE_URL = "https://financialmodelingprep.com/stable"

def fetch_aapl_5y():
    end_date = date.today()
    start_date = end_date - timedelta(days=365 * 5)

    url = f"{BASE_URL}/historical-price-eod/full"
    headers = {"apikey": FMP_API_KEY}
    params = {
        "symbol": "AAPL",
        "from": start_date.isoformat(),
        "to": end_date.isoformat(),
    }

    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    data = resp.json()

    records = data if isinstance(data, list) else data.get("historical", [])
    print(f"{'Date':<12} {'Close':>10} {'Volume':>15}")
    print("-" * 40)
    for r in records[:10]:
        print(f"{r['date']:<12} {r['close']:>10.2f} {r['volume']:>15,}")
    print(f"\n共 {len(records)} 筆資料（{start_date} ~ {end_date}）")
    return records

if __name__ == "__main__":
    fetch_aapl_5y()
