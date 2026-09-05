# 全站 PWA 化＋加入應用程式提示 設計

## 背景與目標

使用者要求：「這個專案除了『更新紀錄』以外的所有頁面，都加上 PWA 的功能，並且提示使用者『可以將此頁面
加入應用程式，方便未來持續查詢或找不到頁面』」。

目標：讓每個資料集儀表板頁面（含首頁）都能被瀏覽器辨識為可安裝的 PWA，且各自安裝後仍指向「該頁面自己」
（而非統一導回首頁），並在頁面上顯示一個可關閉的提示橫幅，鼓勵使用者加入主畫面/應用程式清單，方便日後
直接開啟、找不到頁面時也能快速回來查詢。`changelog/index.html` 明確排除在外（維持原樣，不加上述任何
PWA 相關標籤或腳本）。

本專案為零建置靜態網站（無 npm/bundler），所有新增檔案需可直接由瀏覽器讀取，且沿用現有的
「Python 腳本產生靜態產物」慣例（如 `build_data.py` 產生 `data/*.json`）。

## 範圍

- **納入**：首頁 `index.html` ＋現有 53 個資料集頁面 `*/index.html`（不含 `changelog/`）。
- **排除**：`changelog/index.html`（使用者明確指定）。
- 不新增任何 npm 套件、不引入 Workbox 等第三方 PWA 框架，Service Worker 與 manifest 皆手寫/腳本產生
  的純靜態檔案。

## 為什麼每頁需要各自獨立的 manifest（而非全站共用一份）

Web App Manifest 的 `start_url` 是相對於 **manifest 檔案自身的網址**解析，而不是相對於當下頁面網址。
若全站共用同一份 `assets/manifest.webmanifest`，不論使用者在哪個資料集頁面點擊「加入應用程式」，
安裝後的捷徑一律會開回同一個 `start_url`（例如首頁），無法滿足「方便未來持續查詢**此頁面**」的需求。
因此本設計為**每個頁面各自產生一份專屬的 `manifest.webmanifest`**，放在該頁面所在目錄，
`start_url` 指向自己（`index.html` 相對路徑），`name`/`short_name`/`description` 皆對應該頁面內容，
其餘欄位（icons／theme_color／background_color／display／lang）共用相同設定。

## 元件設計

### 1. 圖示：`assets/icon-192.png`、`assets/icon-512.png`

由現有 `assets/favicon.png`（256×256）用 Pillow 等比例縮放/放大產生，供 manifest 的 `icons` 陣列與
`<link rel="apple-touch-icon">` 共用。不重新設計圖像內容，維持與現有 favicon 一致的視覺識別。

### 2. `scripts/generate_pwa_manifests.py`（新增腳本）

一次性/可重複執行的產生腳本，邏輯：
1. 掃描所有 `*/index.html`（不含 `changelog/`）與根目錄 `index.html`。
2. 對每個頁面，解析既有 `<title>`（去除結尾「|郭愷」）與 `<meta name="description">` 取得
   `name`／`description`；`short_name` 由 `name` 截斷（優先在頓號/空白處截斷，上限 12 個中文字）
   自動產生，不需手動維護對照表，確保未來新增資料集頁面時同一支腳本仍可直接套用。
3. 輸出對應目錄下的 `manifest.webmanifest`（JSON），固定內容：
   ```json
   {
     "name": "...",
     "short_name": "...",
     "description": "...",
     "start_url": "./index.html",
     "scope": "./",
     "id": "./index.html",
     "display": "standalone",
     "lang": "zh-Hant-TW",
     "theme_color": "#1f6f5c",
     "background_color": "#ffffff",
     "icons": [
       { "src": "<相對路徑>/assets/icon-192.png", "sizes": "192x192", "type": "image/png" },
       { "src": "<相對路徑>/assets/icon-512.png", "sizes": "512x512", "type": "image/png" }
     ]
   }
   ```
   （首頁的 `<相對路徑>` 為空字串／`assets/...`，子頁面為 `../assets/...`，比照現有 `<link rel="icon">`
   相對路徑慣例。）
4. 每次執行皆完整覆寫（幂等），供日後新增資料集頁面時重新執行即可自動涵蓋新頁面，不需手動補檔。

此腳本與 `build_data.py` 職責不同（不下載政府開放資料），故獨立成一支新腳本，避免 `build_data.py`
（目前已 5000+ 行）承擔不相關職責。

### 3. `assets/sw.js`（共用 Service Worker，單一檔案，`scope: "/"`）

- 監聽 `install`：預先快取一份「跨頁共用靜態資源」清單（`classical-style.css`、`table.js`、
  `analytics.js`、`favicon.png`、`icon-192.png`、`icon-512.png`），版本化快取名稱
  （如 `shell-v1`），避免影響未來各頁 `data/*.json`／`app.js` 的更新。
- 監聽 `activate`：清除舊版本快取名稱，避免快取無限增長。
- 監聽 `fetch`：
  - 對 HTML 頁面與 `data/*.json`／`data/*.js`（政府開放資料，會定期更新）採用
    **network-first，失敗才退回快取**，確保使用者平常都拿到最新資料，只有離線時才顯示上次快取內容。
  - 對其餘靜態資源（css/共用 js/圖示）採用 **cache-first**，減少重複下載。
  - 非 GET 請求或跨網域請求（如 Chart.js CDN、Google Analytics）一律略過，交還瀏覽器預設處理，
    不快取第三方資源。

Service Worker 是滿足 Chrome/Edge「可安裝」判定條件之一（需有 `fetch` handler），同時也讓已安裝的頁面
離線或弱網時仍可開啟上次瀏覽內容，附帶價值但非本次核心需求。

### 4. `assets/pwa-install.js`（共用安裝提示橫幅腳本）

- 用 `document.currentScript.src` 動態算出 `assets/` 目錄的絕對網址，據此推導同目錄的 `sw.js` 網址，
  呼叫 `navigator.serviceWorker.register(swURL)`（不論頁面深度皆可運作，不需依賴呼叫端傳入相對路徑）。
- 監聽 `window.addEventListener("beforeinstallprompt", ...)`：
  - `event.preventDefault()` 保留事件（`deferredPrompt`）。
  - 若使用者先前已在**這一頁**按下「不用了」（`localStorage` 記錄 key 為
    `pwaInstallDismissed:<pathname>`），則不再顯示，避免每次造訪都打擾。
  - 否則動態注入一個橫幅 DOM（`.pwa-install-banner`，固定於頁面底部，樣式加入
    `assets/style.css`／或者內嵌於腳本注入的 `<style>`，因為要顯示於「所有頁面」，比照
    `assets/style.css` 現況為未使用檔案，選擇改寫進本次真正共用的 `assets/classical-style.css`
    更符合實際套用範圍，避免再新增一份全站都要引入的 CSS 檔），文字為使用者指定的完整提示句：
    「可以將此頁面加入應用程式，方便未來持續查詢或找不到頁面」，並提供兩個按鈕：
    - 「加入」：呼叫 `deferredPrompt.prompt()`，取得使用者選擇結果後關閉橫幅（不論同意或取消）。
    - 「不用了」：關閉橫幅並寫入上述 `localStorage` 旗標。
- 監聽 `window.addEventListener("appinstalled", ...)`：安裝完成後主動關閉橫幅（若還開著）。
- 若瀏覽器/裝置回報已在「standalone」模式執行（`window.matchMedia('(display-mode: standalone)').matches`
  或 iOS 的 `navigator.standalone === true`），代表已經是安裝後開啟，直接不註冊橫幅邏輯（不需要提示
  已經裝過的使用者）。
- **iOS Safari 不支援 `beforeinstallprompt`**：此瀏覽器不會觸發上述事件，因此不會顯示任何橫幅
  （不额外做 iOS 手動「加入主畫面」教學圖文，避免範圍膨脹；如日後有需求可另開一個獨立的小型加強項目）。

### 5. 各頁面 `<head>`／`</head>` 前新增的標籤（由批次腳本自動插入，不手動逐一編輯 54 個檔案）

```html
<link rel="manifest" href="manifest.webmanifest" />
<meta name="theme-color" content="#1f6f5c" />
<link rel="apple-touch-icon" href="{相對路徑}assets/icon-192.png" />
```
與 `</body>` 前新增：
```html
<script src="{相對路徑}assets/pwa-install.js" defer></script>
```
（用 `defer` 避免阻塞頁面渲染；橫幅由腳本自行注入 DOM，不需要頁面預留容器元素，因此可用單一批次
腳本 `scripts/apply_pwa_tags.py` 對 54 個 `index.html` 做字串插入，不需要逐頁手動修改既有版面。）

## 資料流與現有慣例的相容性

- 不影響任何現有 `app.js` 的篩選／圖表／表格邏輯。
- 不影響 `robots.txt`／`sitemap.xml`（manifest／sw.js 不需要另外列入 sitemap）。
- `changelog/index.html` 完全不改動（不含 manifest、sw 註冊、安裝橫幅）。
- Service Worker 快取的「共用靜態資源」清單需與 `assets/` 實際檔案同步；未來若新增/更名共用資源，
  需同步更新 `assets/sw.js` 內的預快取清單（於檔案內註解說明維護方式）。

## 驗證方式

1. `python3 scripts/generate_pwa_manifests.py` 產生 54 份 `manifest.webmanifest`，抽查其中 3-5 份
   `name`/`short_name`/`start_url` 是否正確對應各自頁面。
2. `python3 scripts/apply_pwa_tags.py` 後，用 `grep` 確認 54 個目標頁面皆含
   `rel="manifest"`／`pwa-install.js`，且 `changelog/index.html` 未被修改。
3. 用 Pillow 產生的 `icon-192.png`／`icon-512.png` 檔案存在且尺寸正確。
4. 本機 `python3 -m http.server` 開啟任一資料集頁面，開發者工具 Application 分頁確認
   Service Worker 已註冊、Manifest 內容正確、Lighthouse PWA 可安裝性檢查通過（若環境可執行）。
5. 手動確認安裝提示橫幅文字、按鈕行為（「加入」觸發 `deferredPrompt.prompt()`；「不用了」寫入
   localStorage 後重新整理不再顯示）。因 Chrome 的 `beforeinstallprompt` 需要瀏覽器判定頁面符合
   可安裝資格才會觸發，本機測試環境不一定會觸發，此步驟為盡力驗證，非必要條件。

## 已知限制

- iOS Safari 不觸發 `beforeinstallprompt`，該裝置使用者不會看到安裝橫幅（僅能靠瀏覽器選單手動
  「加入主畫面」，本次不額外做手動教學提示）。
- `short_name` 為腳本自動截斷產生，非人工逐頁挑選最精簡的顯示名稱，長度上限 12 字，多數情況可接受，
  少數頁面截斷後可能不夠精簡，屬可接受的自動化取捨。
- 512×512 圖示由 256×256 的 `favicon.png`放大而成，非重新繪製的高解析度素材，畫質可能略為模糊，
  但足以滿足 PWA 安裝圖示的基本需求。
