import requests
import pandas as pd

FMP_API_KEY = "aeAt9pG7MHDV3jLlzdbkjjEM4PPn8Z43"
BASE_URL = "https://financialmodelingprep.com/stable"

PRICE_FIELDS = {"open", "high", "low", "close", "volume"}
# income-statement 欄位對應（免費方案可用）
FUNDAMENTAL_FIELDS = {
    "revenue": "revenue",
    "netincome": "netIncome",
    "eps": "eps",
    "grossprofit": "grossProfit",
    "opincome": "operatingIncome",
    "ebitda": "ebitda",
}


def fetch_price(symbol: str, start: str, end: str) -> pd.DataFrame:
    resp = requests.get(
        f"{BASE_URL}/historical-price-eod/full",
        headers={"apikey": FMP_API_KEY},
        params={"symbol": symbol, "from": start, "to": end},
    )
    if resp.status_code in (402, 403, 404):
        print(f"    skip {symbol} ({resp.status_code})")
        return pd.DataFrame()
    resp.raise_for_status()
    data = resp.json()
    records = data if isinstance(data, list) else data.get("historical", [])
    if not records:
        return pd.DataFrame()
    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()
    available = [c for c in PRICE_FIELDS if c in df.columns]
    return df[available]


def fetch_fundamentals(symbol: str, period: str = "quarter") -> pd.DataFrame:
    resp = requests.get(
        f"{BASE_URL}/income-statement",
        headers={"apikey": FMP_API_KEY},
        params={"symbol": symbol, "period": period, "limit": 40},
    )
    if resp.status_code in (402, 403, 404):
        print(f"    skip {symbol} ({resp.status_code})")
        return pd.DataFrame()
    resp.raise_for_status()
    data = resp.json()
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()

    col_map = {v: k for k, v in FUNDAMENTAL_FIELDS.items() if v in df.columns}
    df = df[list(col_map.keys())].rename(columns=col_map)
    return df
