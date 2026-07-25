# tyc-placement 機構 Google Map Popup 設計

## 背景與目標

`tyc-placement/index.html`（桃園市失能老人接受長期照顧機構服務暨老人保護安置機構名冊）目前只有機構名稱、
地址、電話等文字資料，沒有經緯度座標、也沒有地圖呈現。使用者希望點擊某個機構後，能立即看到該機構的
Google Map 資訊，不需要離開頁面（不像現有的「地址」超連結是另開分頁跳到 Google Maps 搜尋）。

## 範圍

僅套用於 `tyc-placement/index.html` + `tyc-placement/app.js` 這一個頁面。不影響其他資料集頁面的既有行為
（現有的地址欄位超連結、電話 `tel:` 連結維持不變）。

共用元件（Modal 樣式與開合邏輯）以可重用的方式實作於 `assets/`，供未來其他頁面視需要採用，但本次不強制
套用到其他頁面。

## 使用者互動設計

1. 表格「機構名稱」欄位改為可點擊樣式（底線 + 游標為手指），點擊觸發跳出 popup（其餘欄位如地址、電話
   的既有超連結行為不變，不會被 popup 取代）。
2. Popup（modal）內容：
   - 標題列：機構名稱 + 關閉按鈕（×）。
   - 內嵌 `<iframe>`：`https://www.google.com/maps?q=<encodeURIComponent(地址)>&output=embed`
     （Google Maps 免金鑰 embed 網址，不需 Google API Key，可互動：縮放/拖曳/切換街景）。
   - 文字資訊列：地址、電話（沿用既有 `phoneLink()` 產生的 `tel:` 連結）、機構類型（若有值才顯示）。
   - 底部按鈕：「在 Google Maps 開啟」，連到既有 `addressLink()` 產生的網址，`target="_blank"` 開新分頁。
3. 關閉方式：點擊 × 按鈕、點擊遮罩背景（modal 外側區域）、或按 `Esc` 鍵，三種皆可關閉。
4. 若地址欄位為空字串（理論上目前資料集不會發生），機構名稱維持純文字、不綁定點擊事件，避免開啟空白地圖。

## 技術設計

### 新檔案：`assets/map-popup.js`

提供一個全域函式 `openMapPopup({ name, address, phone, type })`：
- 首次呼叫時動態建立 modal 的 DOM 結構（遮罩層 `.map-popup-overlay` + 內容框 `.map-popup-box`），
  之後重複使用同一組 DOM，只更新內容（避免重複建立/GC 負擔）。
- 開啟時才設定 `iframe.src`；關閉時清空 `iframe.src = ""`，停止地圖持續載入/佔用資源。
- 所有動態文字內容透過既有專案慣例的 `escapeHtml()` 轉義後插入，避免 XSS（在 `map-popup.js` 內部自帶
  一份 `escapeHtml()`，不依賴呼叫端提供，維持模組獨立、零外部依賴）。
- 監聽 `Esc` 鍵與遮罩點擊以關閉；內容框本身的點擊需要 `stopPropagation()`，避免點擊內容框誤觸背景關閉。

### 樣式：`assets/style.css` 新增區塊

新增 `.map-popup-overlay`（固定定位、半透明黑色背景、`display:none` 預設隱藏，開啟時切換為
`display:flex` 置中內容）、`.map-popup-box`（白底卡片、圓角、最大寬度限制、內部捲動）、
`.map-popup-close`（右上角關閉按鈕）、`.map-popup-iframe`（固定比例的地圖 iframe 容器）等 class，
沿用專案既有的 CSS 變數（`--color-*`、圓角、陰影）維持視覺風格一致。

### `tyc-placement/index.html`

在 `</body>` 前，`app.js` 之前加入 `<script src="../assets/map-popup.js"></script>`。

### `tyc-placement/app.js`

- 表格欄位定義中，「機構名稱」欄位改用 `render` 函式輸出可點擊樣式的 `<span>`（非 `<a>`，因為不是外部
  連結、是觸發 popup 的按鈕語意，會加上 `role="button"` 與 `tabindex="0"` 供鍵盤可及性）。
- 在 `createPagedTable` 之後，透過事件代理（在 `table-container` 上監聽 `click`，比照
  `assets/analytics.js` 的事件代理寫法）偵測點擊到機構名稱 `span`，取出該列資料後呼叫
  `openMapPopup({ name: r.name, address: r.address, phone: r.phone, type: r.type })`。
  （不使用 `createPagedTable` 既有的 `onRowClick` 選項，因為需求是「只點機構名稱」而非整列，
  `onRowClick` 是整列觸發，語意不符。）

## 錯誤處理

- 若 `window.google` 或任何外部資源載入失敗不影響本功能，因為 embed 網址是純 iframe src、不依賴
  JS SDK。
- 若 `address` 為空字串，`openMapPopup` 直接不執行（呼叫端已先行判斷不綁定點擊事件，屬雙重防呆）。

## 測試 / 驗證方式

- `node -c assets/map-popup.js`、`node -c tyc-placement/app.js` 語法檢查。
- 本機 `python3 -m http.server` 開啟頁面，實際點擊機構名稱確認 popup 正確顯示地圖/資訊，
  確認點擊遮罩／×／Esc 皆可關閉，確認地址/電話欄位既有超連結行為不受影響。
