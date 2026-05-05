# Alpha Mining And Test

## 改進紀錄

<!-- 每次改進後在此新增一條記錄，格式如下 -->
<!-- - YYYY-MM-DD：改進了什麼 -->
- 2026-05-05：新增 `aapl_price_volume.py`，透過 FMP API 抓取 AAPL 5 年日頻價量資料（收盤價 + 成交量），共 1254 筆
- 2026-05-05：新增 `build_matrix.py`，支援多標的批次拉取，輸出 n×m matrix（symbols × days），欄位可選 close/volume/open/high/low，並存成 CSV
- 2026-05-05：重構為四模組架構（`universe.py` / `fetcher.py` / `matrix_builder.py` / `main.py`），支援 CLI 參數驅動，可同時輸出價量（close/volume/returns）與基本面（revenue/eps/ebitda 等）多張 matrix；免費方案可用 25 檔標的
