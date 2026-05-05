import requests
import pandas as pd
from datetime import date, timedelta

FMP_API_KEY = "aeAt9pG7MHDV3jLlzdbkjjEM4PPn8Z43"
BASE_URL = "https://financialmodelingprep.com/stable"


def fetch_history(symbol: str, start: str, end: str) -> pd.DataFrame:
    url = f"{BASE_URL}/historical-price-eod/full"
    resp = requests.get(
        url,
        headers={"apikey": FMP_API_KEY},
        params={"symbol": symbol, "from": start, "to": end},
    )
    resp.raise_for_status()
    data = resp.json()
    records = data if isinstance(data, list) else data.get("historical", [])
    df = pd.DataFrame(records)[["date", "close", "volume", "open", "high", "low"]]
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()
    return df


def build_matrix(
    symbols: list[str],
    days: int = 365 * 5,
    fields: list[str] = None,
) -> dict[str, pd.DataFrame]:
    """
    回傳 dict，key 為欄位名稱（close / volume / ...），
    value 為 DataFrame，shape = (n_symbols, m_days)，
    index = symbol，columns = date。
    """
    if fields is None:
        fields = ["close", "volume"]

    end = date.today()
    start = end - timedelta(days=days)
    start_str, end_str = start.isoformat(), end.isoformat()

    raw: dict[str, pd.DataFrame] = {}
    for sym in symbols:
        print(f"  fetching {sym} ...")
        raw[sym] = fetch_history(sym, start_str, end_str)

    # 取所有標的共有的交易日
    common_dates = raw[symbols[0]].index
    for sym in symbols[1:]:
        common_dates = common_dates.intersection(raw[sym].index)
    common_dates = common_dates.sort_values()

    matrices: dict[str, pd.DataFrame] = {}
    for field in fields:
        mat = pd.DataFrame(
            {sym: raw[sym].loc[common_dates, field] for sym in symbols},
            index=common_dates,
        ).T  # shape: (n_symbols, m_days)
        mat.index.name = "symbol"
        matrices[field] = mat

    return matrices


if __name__ == "__main__":
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]
    print(f"建立 {len(symbols)} 檔標的的 matrix ...\n")

    matrices = build_matrix(symbols, days=365 * 5, fields=["close", "volume"])

    for field, mat in matrices.items():
        n, m = mat.shape
        print(f"\n[{field}] shape = {n} × {m}  (symbols × days)")
        print(mat.iloc[:, -5:].to_string())  # 顯示最後 5 天

        mat.to_csv(f"matrix_{field}.csv")
        print(f"  -> 已存檔：matrix_{field}.csv")
