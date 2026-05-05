import pandas as pd
from datetime import date, timedelta
from fetcher import fetch_price, fetch_fundamentals, FUNDAMENTAL_FIELDS


def _common_trading_days(raw: dict[str, pd.DataFrame]) -> pd.DatetimeIndex:
    valid = [df.index for df in raw.values() if not df.empty]
    if not valid:
        return pd.DatetimeIndex([])
    dates = valid[0]
    for idx in valid[1:]:
        dates = dates.intersection(idx)
    return dates.sort_values()


def build_price_matrices(
    symbols: list[str],
    days: int,
    fields: list[str],
) -> dict[str, pd.DataFrame]:
    end = date.today()
    start = end - timedelta(days=days)
    start_str, end_str = start.isoformat(), end.isoformat()

    raw: dict[str, pd.DataFrame] = {}
    for sym in symbols:
        print(f"  [price] {sym}")
        raw[sym] = fetch_price(sym, start_str, end_str)

    trading_days = _common_trading_days(raw)

    matrices: dict[str, pd.DataFrame] = {}
    for field in fields:
        rows = {}
        for sym, df in raw.items():
            if df.empty or field not in df.columns:
                continue
            rows[sym] = df.loc[df.index.isin(trading_days), field]
        if rows:
            mat = pd.DataFrame(rows, index=trading_days).T
            mat.index.name = "symbol"
            # 衍生欄位
            if field == "returns":
                close_mat = matrices.get("close")
                if close_mat is not None:
                    mat = close_mat.pct_change(axis=1)
            matrices[field] = mat

    # 若要 returns 但 close 已建好
    if "returns" in fields and "returns" not in matrices and "close" in matrices:
        matrices["returns"] = matrices["close"].pct_change(axis=1)

    return matrices


def build_fundamental_matrices(
    symbols: list[str],
    fields: list[str],
    trading_days: pd.DatetimeIndex,
) -> dict[str, pd.DataFrame]:
    raw: dict[str, pd.DataFrame] = {}
    for sym in symbols:
        print(f"  [fundamental] {sym}")
        raw[sym] = fetch_fundamentals(sym)

    matrices: dict[str, pd.DataFrame] = {}
    for field in fields:
        rows = {}
        for sym, df in raw.items():
            if df.empty or field not in df.columns:
                continue
            # reindex 到交易日，forward-fill 季度值到每個交易日
            s = df[field].reindex(trading_days, method="ffill")
            rows[sym] = s
        if rows:
            mat = pd.DataFrame(rows, index=trading_days).T
            mat.index.name = "symbol"
            matrices[field] = mat

    return matrices
