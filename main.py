"""
用法範例：
  python main.py --price close,volume,returns --days 365
  python main.py --price close --fundamental revenue,eps,netincome --days 1260
  python main.py --fundamental revenue,eps,grossprofit,opincome,ebitda
"""
import argparse
import os
import pandas as pd

from universe import get_top50_symbols
from matrix_builder import build_price_matrices, build_fundamental_matrices

PRICE_CHOICES = {"open", "high", "low", "close", "volume", "returns"}
FUNDAMENTAL_CHOICES = {"pe", "pb", "roe", "roa", "de", "eps"}


def parse_args():
    parser = argparse.ArgumentParser(description="Build alpha matrices from FMP data")
    parser.add_argument("--price", default="", help="Price fields: close,volume,returns,open,high,low")
    parser.add_argument("--fundamental", default="", help="Fundamental fields: pe,pb,roe,roa,de,eps")
    parser.add_argument("--days", type=int, default=365 * 5, help="History window in days (default 1825)")
    parser.add_argument("--output", default="matrices", help="Output directory (default: matrices/)")
    return parser.parse_args()


def main():
    args = parse_args()

    price_fields = [f.strip() for f in args.price.split(",") if f.strip()] if args.price else []
    fund_fields = [f.strip() for f in args.fundamental.split(",") if f.strip()] if args.fundamental else []

    if not price_fields and not fund_fields:
        print("請指定至少一個欄位，例如：--price close,volume 或 --fundamental pe,roe")
        return

    os.makedirs(args.output, exist_ok=True)

    symbols = get_top50_symbols()
    print(f"\n Universe: {len(symbols)} 檔標的")
    print(f" 價量欄位: {price_fields}")
    print(f" 基本面欄位: {fund_fields}")
    print(f" 天數範圍: {args.days} 天\n")

    all_matrices: dict[str, pd.DataFrame] = {}

    if price_fields:
        # returns 需要先建 close
        fetch_fields = list(set(price_fields) - {"returns"})
        if "returns" in price_fields and "close" not in fetch_fields:
            fetch_fields.append("close")
        price_mats = build_price_matrices(symbols, args.days, fetch_fields)
        if "returns" in price_fields:
            price_mats["returns"] = price_mats["close"].pct_change(axis=1)
        all_matrices.update(price_mats)

    trading_days = None
    if fund_fields:
        if all_matrices:
            trading_days = next(iter(all_matrices.values())).columns
        else:
            # 沒有價量 matrix 時，用第一個有資料的標的交易日
            from fetcher import fetch_price
            from datetime import date, timedelta
            end = date.today()
            start = end - timedelta(days=args.days)
            ref = fetch_price(symbols[0], start.isoformat(), end.isoformat())
            trading_days = ref.index

        fund_mats = build_fundamental_matrices(symbols, fund_fields, trading_days)
        all_matrices.update(fund_mats)

    print("\n--- 輸出結果 ---")
    for name, mat in all_matrices.items():
        path = os.path.join(args.output, f"{name}.csv")
        mat.to_csv(path)
        n, m = mat.shape
        print(f"  {name:10s}  shape={n}×{m}  -> {path}")

    print("\n完成。")


if __name__ == "__main__":
    main()
