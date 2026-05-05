"""
透過 yfinance 抓取選擇權資料。

用法：
  python options_fetcher.py              # 抓全部 25 檔，印摘要
  python options_fetcher.py AAPL MSFT   # 只抓指定標的
"""
import sys
import yfinance as yf
import pandas as pd
from universe import get_top50_symbols

AVAILABLE = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL",
    "META", "TSLA", "JPM", "V", "UNH",
    "XOM", "COST", "NFLX", "JNJ", "ABBV",
    "WMT", "BAC", "CVX", "AMD", "KO",
    "CSCO", "PEP", "WFC", "GE", "GS",
]


def fetch_options(symbol: str) -> dict[str, pd.DataFrame]:
    """
    回傳 dict：
      "expirations" : list[str]           所有到期日
      "calls"       : pd.DataFrame        最近一個到期日的 calls
      "puts"        : pd.DataFrame        最近一個到期日的 puts
    """
    ticker = yf.Ticker(symbol)
    exps = ticker.options
    if not exps:
        return {}
    chain = ticker.option_chain(exps[0])
    return {
        "expirations": list(exps),
        "calls": chain.calls.copy(),
        "puts": chain.puts.copy(),
    }


def fetch_all_options(symbols: list[str]) -> dict[str, dict]:
    results = {}
    for sym in symbols:
        print(f"  {sym} ...", end=" ")
        data = fetch_options(sym)
        if data:
            n_exp = len(data["expirations"])
            n_calls = len(data["calls"])
            n_puts = len(data["puts"])
            print(f"{n_exp} expirations, {n_calls} calls, {n_puts} puts")
            results[sym] = data
        else:
            print("no data")
    return results


def build_iv_matrix(results: dict[str, dict]) -> pd.DataFrame:
    """
    以最近到期日的 ATM 附近隱含波動率，建立一個簡單摘要 DataFrame。
    index = symbol，columns = strike / iv_call / iv_put / oi_call / oi_put
    """
    rows = []
    for sym, data in results.items():
        calls = data["calls"]
        puts = data["puts"]
        if calls.empty:
            continue
        # 找 ATM（volume 最大的 strike）
        atm = calls.loc[calls["volume"].fillna(0).idxmax()]
        row = {
            "symbol": sym,
            "expiration": data["expirations"][0],
            "atm_strike": atm["strike"],
            "iv_call": round(atm["impliedVolatility"], 4),
            "oi_call": int(atm["openInterest"]) if pd.notna(atm["openInterest"]) else 0,
        }
        # 對應 put
        put_match = puts[puts["strike"] == atm["strike"]]
        if not put_match.empty:
            row["iv_put"] = round(put_match.iloc[0]["impliedVolatility"], 4)
            row["oi_put"] = int(put_match.iloc[0]["openInterest"]) if pd.notna(put_match.iloc[0]["openInterest"]) else 0
        rows.append(row)

    return pd.DataFrame(rows).set_index("symbol")


if __name__ == "__main__":
    symbols = sys.argv[1:] if len(sys.argv) > 1 else AVAILABLE
    print(f"抓取 {len(symbols)} 檔選擇權資料...\n")
    results = fetch_all_options(symbols)

    print("\n--- ATM 隱含波動率摘要 ---")
    summary = build_iv_matrix(results)
    print(summary.to_string())
    summary.to_csv("options_summary.csv")
    print("\n已存檔：options_summary.csv")
