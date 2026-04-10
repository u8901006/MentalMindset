# MentalMindset

每日自動彙整心理學研究文獻，從 PubMed 搜尋、Crossref 補充 metadata，產生繁體中文日報。

## 輸出

- `reports/YYYY-MM-DD.md` — Markdown 日報
- `reports/YYYY-MM-DD.json` — 結構化 JSON
- `reports/YYYY-MM-DD.html` — 網頁版日報
- `index.html` — 歷史日報索引頁

## 自動化

GitHub Actions 每日 06:00 UTC 執行，也可手動觸發。流程：安裝 pytest → 執行測試 → 產生日報 → 提交 `reports/` 與 `index.html`。
