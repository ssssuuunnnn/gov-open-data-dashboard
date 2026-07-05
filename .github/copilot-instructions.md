# Copilot 專案指引 — 長照據點開放資料儀表板

本文件協助 AI 編碼助理（GitHub Copilot 等）快速理解本專案架構與慣例，以便後續開發能維持一致性。

## 專案性質

純靜態網站（無後端、無建置工具/bundler），直接部署於 GitHub Pages。目前收錄兩個政府開放資料集，
各自對應一個獨立的儀表板頁面，並以共用的首頁導覽。**新增第三個資料集時，請完整複製既有的一組模式**
（見下方「新增資料集的標準流程」）。

## 目錄結構與職責

```
index.html               首頁，卡片式導覽連結到各資料集頁面，讀取 data/meta.json 顯示筆數/更新時間
assets/style.css         全站共用樣式（CSS 變數、卡片、篩選列、統計卡、表格、分頁樣式）
assets/table.js          共用元件 createPagedTable()：分頁 + 排序表格，各頁面 app.js 皆會用到
abc/index.html + app.js  長照ABC據點頁面（含 Leaflet 地圖 + MarkerCluster + Chart.js 圖表）
lane/index.html + app.js 巷弄長照站頁面（無座標資料，僅 Chart.js 圖表，無地圖）
data/abc.json            長照ABC據點資料（build_data.py 產生，勿手動編輯）
data/lane.json            巷弄長照站資料（build_data.py 產生，勿手動編輯）
data/meta.json            兩資料集的筆數、來源網址、產生時間（build_data.py 產生）
scripts/build_data.py     資料下載 + 清理 + 轉換腳本（唯一應該修改資料內容的地方）
README.md                 專案說明、部署步驟、資料更新方式
```

沒有 `package.json`、沒有前端框架、沒有 CSS 前處理器、沒有 bundler。所有 JS 皆為原生瀏覽器可直接執行的
script，透過 `<script src="...">` 標籤引入，不使用 ES module import/export、不使用 build step。**新增程式碼時
請維持這個「零建置」原則**，除非使用者明確要求導入框架。

## 資料流（重要：這是本專案最核心的架構決策）

1. 原始資料來源為政府單位提供的 CSV 下載網址，**沒有 CORS 標頭**，瀏覽器無法直接 fetch，因此不能在前端
   直接打原始網址。
2. 原始 CSV 的地理欄位（如「縣市」「地址縣市」）是行政區代碼（例如 `67000`），不是中文名稱；中文名稱藏在
   地址欄位（如「地址全址」）的開頭。
3. `scripts/build_data.py` 負責：下載 CSV → 用 `urllib` 讀取（`utf-8-sig` 解碼）→ 用正規表達式
   `^(..[市縣])(.*?[市區鄉鎮])` 從地址欄位解析出縣市／鄉鎮市區中文名稱 → 轉成**欄位陣列 + rows 陣列**的
   精簡 JSON（不是 array of objects，是 `{fields: [...], rows: [[...], [...]]}`，用意是避免 3 萬多筆資料
   重複儲存欄位名稱造成檔案過大）→ 寫入 `data/*.json`。
4. 前端 `app.js` 讀取 JSON 後，用 `fields` 陣列把每個 `row` 陣列轉回物件（見 `rowToObj()` function），
   之後所有篩選/圖表/表格邏輯都基於物件陣列操作。
5. **新增欄位時**：修改 `build_data.py` 的 `fields` 清單與對應的 row 組裝邏輯，同時要同步更新對應 `app.js`
   的欄位使用位置（篩選條件、表格欄位定義、圖表統計）。
6. 重新產生資料：`python3 scripts/build_data.py`（會覆寫 `data/*.json`，需要網路連線下載原始 CSV）。

### 資料量與效能考量

- `abc.json` 約 3.1 萬筆、~8MB（GitHub Pages 會自動 gzip 壓縮到 ~1.6MB），是目前最大的資料檔。
- 地圖渲染有效能保護機制：篩選結果超過 8,000 筆時會等距抽樣顯示於地圖（見 `abc/app.js` 的
  `renderMap()` 內 `cap = 8000` 邏輯），但統計卡片與表格一律以完整篩選結果計算，不會被抽樣影響。
- 表格一律走 `assets/table.js` 的分頁元件（預設 pageSize 25），不要在畫面上一次全部渲染大量 `<tr>`。
- Leaflet 地圖使用 `preferCanvas: true` 及 `L.markerClusterGroup` + `L.circleMarker` 以支撐大量標記點。

## 前端頁面共同模式（app.js 慣例）

每個資料集頁面的 `app.js` 都遵循相同結構，新增頁面時建議照抄：

1. `state` 物件：`{ all, fields, filtered, ... }` 保存全部資料與目前篩選結果。
2. `els` 物件：集中存放所有會用到的 DOM 節點參照。
3. `rowToObj(row)`：把 JSON 的 row 陣列轉成物件（依 `state.fields`）。
4. `populateSelect(select, values)`：動態產生下拉選單選項（依實際資料內容而非寫死清單）。
5. `applyFilters()`：讀取所有篩選條件（下拉選單、checkbox、關鍵字 input）過濾 `state.all` 得到
   `state.filtered`，然後呼叫 `renderAll()`。
6. `renderAll()` → 依序呼叫 `renderStats()`（統計卡片）、`renderCharts()`（Chart.js 圖表，記得先
   `destroy()` 舊圖表實例再建立新的，避免記憶體洩漏/圖表疊加）、`table.setData(state.filtered)`。
7. 篩選條件變動時的事件綁定都在檔案底部；文字輸入框用 `debounce()`（250ms）避免每個按鍵都觸發全量重算。
8. 資料以 `Promise.all([fetch(data/xxx.json), fetch(data/meta.json)])` 載入，失敗時要在
   `#table-container` 顯示錯誤訊息（`.loading` class）。

## 樣式慣例（assets/style.css）

- 使用 CSS 變數（`:root` 定義顏色、圓角、陰影），新增顏色請沿用既有變數命名風格（`--color-*`, `--cat-*`）。
- 類別徽章（A/B/C 據點等級）固定用 `.badge.a/.b/.c` class 對應 `--cat-a/b/c` 顏色，圖表也共用相同色碼
  （見 `app.js` 中的 `catColor` 常數），**如果新增分類請同時更新 CSS 與 JS 兩處色碼，保持視覺一致**。
- 版面共用 class：`.card`（白底卡片）、`.stat-grid` / `.stat-card`（統計卡片列）、`.filters`（篩選列）、
  `.grid-2`（左右兩欄，響應式在 900px 以下變單欄）、`.chart-box`、`.table-wrap` + `table.data-table`。

## 外部依賴（皆透過 CDN，未 vendor 進repo）

- Leaflet 1.9.4 + Leaflet.markercluster 1.5.3（僅 `abc/` 頁面使用，因為只有這個資料集有經緯度座標）
- Chart.js 4.4.4（兩頁都用）
- 皆用 `unpkg.com` / `cdn.jsdelivr.net` 引入，沒有離線備援。若目標環境無法連外網，需改為將檔案下載並
  放進 `assets/vendor/` 後改本地路徑引用。

## 新增資料集的標準流程

1. 在 `scripts/build_data.py` 新增一個 `build_xxx()` function：下載來源 CSV/JSON、解析必要欄位、
   輸出 `{fields, rows}` 結構（如需要分類色碼對照表，仿照 `CATEGORY_LABELS` 額外附加）。
2. 在 `main()` 中呼叫該 function，寫出 `data/xxx.json`，並在 `meta` dict 補上對應的
   `{count, source, title}`。
3. 新增 `xxx/index.html`（複製 `abc/index.html` 或 `lane/index.html` 當範本，視是否有經緯度資料決定
   要不要含地圖）與 `xxx/app.js`（複製對應頁面的 JS，改資料欄位、篩選條件、圖表定義）。
4. 在首頁 `index.html` 的 `.home-grid` 新增一張 `.home-card` 連結新頁面，並在頁尾 script 補上筆數顯示。
5. 更新 `README.md` 的資料集表格與目錄結構說明。
6. 執行 `python3 scripts/build_data.py` 產生資料，並用 `python3 -m http.server` 本機預覽驗證後再部署。

## 部署

- GitHub Pages 由 repo 設定直接以根目錄 `/` 部署 `main` 分支，沒有 CI/CD workflow、沒有 Actions build
  流程。**資料更新是手動流程**：本機跑 `build_data.py` → commit 新的 `data/*.json` → push。
- 若未來要自動化，可考慮加入 GitHub Actions 排程（依「更新頻率」欄位 cron）執行 `build_data.py` 並自動
  commit，但目前尚未實作，新增時請先與使用者確認排程頻率與 commit 權限設定。

## 已知限制 / 待改進事項

- `data/abc.json` 中約 6 筆資料因原始地址格式無法解析出縣市名稱（county 為空字串），篩選下拉選單會有
  極少數資料游離在「全部」之外，屬原始資料品質問題，非程式錯誤。
- `lane/` 資料集無經緯度，嘗試以 Nominatim 地理編碼加座標曾因該服務阻擋請求而放棄，如未來要加地圖需另尋
  穩定的地理編碼服務或申請 API 金鑰。
- 目前沒有自動化測試；修改 `build_data.py` 或 `app.js` 後請至少用 `node -c` 檢查語法，並啟動
  `python3 -m http.server` 手動走過篩選/圖表/表格互動流程再視為完成。
