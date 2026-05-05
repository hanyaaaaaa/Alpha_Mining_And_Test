# 美股市值前 50（不含 BRK-B 等特殊格式），每季手動更新一次即可
TOP50 = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL",
    "META", "TSLA", "AVGO", "JPM", "LLY",
    "V", "UNH", "XOM", "MA", "COST",
    "HD", "NFLX", "PG", "JNJ", "ABBV",
    "WMT", "BAC", "CRM", "ORCL", "MRK",
    "CVX", "AMD", "KO", "CSCO", "PEP",
    "TMO", "ACN", "LIN", "WFC", "MCD",
    "IBM", "GE", "QCOM", "TXN", "NOW",
    "INTU", "AMGN", "PM", "ISRG", "CAT",
    "GS", "SPGI", "BLK", "RTX", "DE",
]


def get_top50_symbols() -> list[str]:
    return TOP50


if __name__ == "__main__":
    syms = get_top50_symbols()
    print(f"Top {len(syms)} symbols:")
    print(syms)
