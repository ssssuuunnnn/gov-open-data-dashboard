# 政府開放資料儀表板

以政府開放資料建置的靜態網站，整理四個長照/老人福利相關資料集為互動式儀表板，可直接部署於 GitHub Pages。

## 資料集

| 頁面 | 資料集名稱 | 提供機關 | 說明 |
|---|---|---|---|
| `abc/` | 長照ABC據點 | 衛生福利部 | 全國 A/B/C 三級長照據點，含經緯度座標，於地圖上呈現，並提供縣市／鄉鎮／類別／關鍵字篩選與統計圖表 |
| `lane/` | 巷弄長照站 | 彰化縣政府社會處 | 彰化縣各鄉鎮巷弄長照站清單，提供鄉鎮篩選、關鍵字搜尋與統計圖表 |
| `tyc-elder/` | 桃園市老人福利機構一覽表 | 桃園市政府社會局 | 桃園市私立老人福利機構（養護/長照/安養）清單，提供鄉鎮市區／收容對象／評鑑成績／關鍵字篩選與統計圖表 |
| `specialty/` | 臺北市長照專業服務特約單位 | 臺北市政府衛生局 | 臺北市居家護理所、物理／職能治療所等長照專業服務特約單位清單，標示是否提供8項專業服務能力（復能照護、營養照護、進食與吞嚥照護等），提供服務區域／服務能力／關鍵字篩選與統計圖表。**資料來源僅為公告頁面的 PDF 附件、非開放資料 CSV/API**，需人工下載更新，詳見下方「更新資料」說明 |

原始資料下載網址：
- https://ltcpap.mohw.gov.tw/publish/abc.csv
- https://email.chcg.gov.tw/df/pufnpn5i5741iy9efkn2rrz5ga6uhb
- https://opendata.tycg.gov.tw/api/dataset/536bb44b-b9f1-4336-ad26-34b9e25b3a68/resource/3d7e3b4c-8bc5-47c4-85a9-eec70415b189/download
- https://health.gov.taipei/News_Content.aspx?n=F0D7A5A451D2493C&sms=549F98C9E5942A2B&s=9138F86B8A3CBF69　（公告頁面，PDF 需手動下載，見下方說明）

授權方式：政府資料開放授權條款-第1版

## 網站架構

```
index.html          首頁，連結至四個儀表板
abc/index.html       長照ABC據點地圖儀表板（Leaflet 地圖 + Chart.js 圖表 + 篩選表格）
abc/app.js
lane/index.html      巷弄長照站儀表板（Chart.js 圖表 + 篩選表格）
lane/app.js
tyc-elder/index.html 桃園市老人福利機構一覽表儀表板（Chart.js 圖表 + 篩選表格，無地圖）
tyc-elder/app.js
specialty/index.html 臺北市長照專業服務特約單位儀表板（Chart.js 圖表 + 篩選表格，無地圖）
specialty/app.js
assets/style.css     共用樣式
assets/table.js       共用分頁表格元件
data/abc.json         長照ABC據點資料（由 scripts/build_data.py 產生）
data/lane.json        巷弄長照站資料（由 scripts/build_data.py 產生）
data/tyc-elder.json   桃園市老人福利機構一覽表資料（由 scripts/build_data.py 產生）
data/tyc-elder.js     同上資料的內嵌 JS 版本（window.TYC_ELDER_DATA），供 tyc-elder 頁面以
                       <script> 標籤直接載入，不透過 fetch()，避免任何網路/快取時序問題
data/specialty.json   臺北市長照專業服務特約單位資料（由 scripts/build_data.py 解析 PDF 產生）
data/specialty.js     同上資料的內嵌 JS 版本（window.SPECIALTY_DATA），供 specialty 頁面以
                       <script> 標籤直接載入
data/source/          長照專業服務特約單位來源 PDF（人工下載存放於此，供 build_data.py 解析）
data/meta.json        資料筆數與更新時間
scripts/build_data.py 資料下載與轉換腳本
```

由於原始資料來源伺服器未開放跨網域（CORS）存取（僅允許來源平台自己的網域），且欄位中的「縣市」「鄉鎮市區」
為行政區代碼而非中文名稱（或需另行比對行政區清單），因此以 Python 腳本於建置階段下載 CSV、解析地址還原
縣市／鄉鎮名稱，並轉換為精簡的 JSON 供前端讀取，避免瀏覽器直接請求原始網址因 CORS 被擋下，同時大幅縮小
檔案大小。「臺北市長照專業服務特約單位」則因來源僅提供 PDF 附件（無開放資料 CSV/API），改為以
[pdfplumber](https://github.com/jsvine/pdfplumber) 解析本機存放的 PDF 表格。

## 更新資料

```bash
python3 scripts/build_data.py
```

會重新下載三份 CSV（長照ABC據點、巷弄長照站、桃園市老人福利機構一覽表）並覆寫對應 `data/*.json`；
同時嘗試解析 `data/source/tp-ltc-specialty-*.pdf`（若存在）產生 `data/specialty.json`／`data/specialty.js`。
建議依資料集「更新頻率」（每1月 / 每1年 / 不定期）定期執行後再部署。

執行前請先安裝 PDF 解析用的額外相依套件（僅 `specialty` 資料集需要，其他資料集僅用標準庫）：

```bash
python3 -m pip install pdfplumber
```

### 更新「臺北市長照專業服務特約單位」

此資料集**沒有開放資料 CSV/API**，臺北市政府衛生局僅於公告頁面提供 PDF 附件，因此無法由腳本自動下載，
需手動維護：

1. 到[長照服務特約專區公告頁面](https://health.gov.taipei/News_Content.aspx?n=F0D7A5A451D2493C&sms=549F98C9E5942A2B&s=9138F86B8A3CBF69)下載最新版 PDF。
2. 將檔案存成 `data/source/tp-ltc-specialty-<公告日期，例如20260430>.pdf`（腳本會自動抓取
   `data/source/` 目錄下符合此檔名規則、依檔名排序最新的一份 PDF）。
3. 執行 `python3 scripts/build_data.py` 重新產生 `data/specialty.json`／`data/specialty.js`。
4. 建議抽樣核對幾筆機構名稱、地址與服務能力是否正確解析（PDF 表格跨頁與換行清理邏輯詳見
   `scripts/build_data.py` 的 `build_specialty()`）。

## 本機預覽

```bash
python3 -m http.server 8000
# 開啟 http://localhost:8000
```

## 部署到 GitHub Pages

1. 將本專案推送到 GitHub repository。
2. 到 repository 的 Settings → Pages，Source 選擇 `main` 分支、根目錄 `/`。
3. 儲存後幾分鐘即可透過 `https://<你的帳號>.github.io/<repo名稱>/` 瀏覽。

## SEO 優化

- 每頁皆有獨立的 `<title>` 與 `meta description`／`keywords`，並設定 `canonical` 網址避免重複內容問題。
- 加入 Open Graph 與 Twitter Card 標籤（含共用分享圖 `assets/og-image.png`），讓連結分享到社群平台時有預覽圖。
- 首頁與各資料集頁面皆內嵌 `schema.org` JSON-LD 結構化資料（`WebSite` / `Dataset`），標示資料提供機關、授權方式與原始下載網址，利於搜尋引擎理解資料集內容。
- 根目錄提供 `robots.txt` 與 `sitemap.xml`，並加入 `favicon.png`/`favicon.ico`。
- 加入 `<noscript>` 提示文字，因本站內容需 JavaScript 動態載入 JSON 資料才能顯示。
- 若更換部署網域，請同步更新 `robots.txt`、`sitemap.xml` 及各頁面內的 canonical／og:url／JSON-LD 網址。

## 技術說明

- 純靜態網站，無需後端，前端使用原生 JavaScript + [Leaflet](https://leafletjs.com/)（含 MarkerCluster 群聚顯示 3 萬筆座標點）+ [Chart.js](https://www.chartjs.org/)。
- 「長照ABC據點」資料實際筆數約 3.1 萬筆（開放資料平台詮釋資料標示的 1000 筆為估計值，非實際資料量）。
- 地圖為兼顧效能，篩選結果超過 8,000 筆時會等距抽樣顯示，統計數字與表格仍以完整篩選結果為準。
- 「臺北市長照專業服務特約單位」無地圖與經緯度座標，且原始 PDF 因來源字型 cmap 對應問題，部分常見漢字
  被替換成外觀相同的 Unicode CJK 部首符號，`build_data.py` 已內建還原對照表；服務區域欄位可能為「全區」
  或多個行政區組合，前端篩選與統計圖表會將「全區」展開計入全部12個行政區。

