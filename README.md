# 政府開放資料儀表板

以政府開放資料建置的靜態網站，整理十八個長照/老人福利/身心障礙相關資料集為互動式儀表板，可直接部署於 GitHub Pages。

## 資料集

| 頁面 | 資料集名稱 | 提供機關 | 說明 |
|---|---|---|---|
| `abc/` | 長照ABC據點 | 衛生福利部 | 全國 A/B/C 三級長照據點，含經緯度座標，於地圖上呈現，並提供縣市／鄉鎮／類別／關鍵字篩選與統計圖表 |
| `lane/` | 巷弄長照站 | 彰化縣政府社會處 | 彰化縣各鄉鎮巷弄長照站清單，提供鄉鎮篩選、關鍵字搜尋與統計圖表 |
| `tyc-elder/` | 桃園市老人福利機構一覽表 | 桃園市政府社會局 | 桃園市私立老人福利機構（養護/長照/安養）清單，提供鄉鎮市區／收容對象／評鑑成績／關鍵字篩選與統計圖表 |
| `specialty/` | 臺北市長照專業服務特約單位 | 臺北市政府衛生局 | 臺北市居家護理所、物理／職能治療所等長照專業服務特約單位清單，標示是否提供8項專業服務能力（復能照護、營養照護、進食與吞嚥照護等），提供服務區域／服務能力／關鍵字篩選與統計圖表。**資料來源僅為公告頁面的 PDF 附件、非開放資料 CSV/API**，需人工下載更新，詳見下方「更新資料」說明 |
| `kcg-homecare/` | 銀髮族服務-居家長照機構 | 高雄市政府社會局 | 高雄市居家式服務類長期照顧服務機構清單，含經緯度座標，於地圖上呈現，並提供行政區／服務時段／關鍵字篩選與統計圖表 |
| `hsc-ltc/` | 新竹縣長照機構名冊 | 新竹縣政府社會處 | 新竹縣居家服務、日間照顧、小規模多機能、家庭托顧、團體家屋等長照機構清單，提供鄉鎮市區／服務類型／關鍵字篩選與統計圖表 |
| `yl-ltc/` | 宜蘭縣立案老人長期照顧及安養機構名冊 | 宜蘭縣政府 | 宜蘭縣養護型、長期照護型等立案老人長期照顧及安養機構清單，提供鄉鎮市區／機構類型／關鍵字篩選與統計圖表 |
| `hccg-elder/` | 新竹市老人福利機構一覽表 | 新竹市政府社會處 | 新竹市立案老人福利機構清單，含經緯度座標，於地圖上呈現，並提供行政區／收容對象／關鍵字篩選與統計圖表 |
| `tn-homecare-nursing/` | 臺南市居家護理機構 | 臺南市政府衛生局 | 臺南市各行政區居家護理所清單（114年度），提供行政區／關鍵字篩選與統計圖表 |
| `tc-nursing/` | 臺中市一般護理之家清冊 | 臺中市政府衛生局 | 臺中市各行政區一般護理之家清單，含一般床／呼吸器依賴床許可與開放床數、評鑑結果、督考結果，提供行政區／關鍵字篩選與統計圖表 |
| `ntpc-nursing/` | 新北市一般護理之家清冊 | 新北市政府衛生局 | 新北市各行政區一般護理之家清單，含地址、聯絡人、電話、開放床數、機構應配置護理人員數，提供行政區／關鍵字篩選與統計圖表 |
| `chiayi-ltc/` | 嘉義縣立案長照及護理之家機構一覽 | 嘉義縣政府長期照護管理中心 | 合併嘉義縣立案住宿長照機構名單與護理之家名單，收錄機構類型、機構名稱、鄉鎮市、地址、電話、負責人、許可／開業床數，提供機構類型／鄉鎮市／關鍵字篩選與統計圖表。**資料來源為使用者提供之本機 CSV、無公開下載網址**，需人工更新，詳見下方「更新資料」說明 |
| `pingtung-ltc/` | 屏東縣老人長期照顧機構 | 屏東縣政府社會處 | 屏東縣老人長期照顧機構清單，收錄機構名稱、地址、電話，機構類型（養護型／失智型／未標示）由機構名稱解析而來，鄉鎮市由地址欄位解析，提供鄉鎮市／機構類型／關鍵字篩選與統計圖表，無經緯度座標 |
| `tc-transport/` | 臺中市失能者交通接送服務 | 臺中市政府衛生局 | 協助中重度失能者滿足以就醫及使用長期照顧服務為主要目的之交通服務需求，收錄辦理單位名稱、連絡電話、地址、服務區域，含經緯度座標（由原始 TWD97 TM2 平面座標換算），於地圖上呈現，並提供服務區域（多選）／辦理單位所在行政區／關鍵字篩選與統計圖表 |
| `tyltc/` | 桃園市長期照護專業服務特約單位 | 桃園市政府衛生局 | 桃園市居家護理所、物理／職能治療所等長期照護專業服務特約單位清單，收錄機構名稱、負責人、電話、傳真、電子郵件、地址與最後更新時間；「服務類型」由機構名稱關鍵字啟發式推斷（非官方分類），部分機構地址位於新北市、臺北市等鄰近縣市，提供縣市／鄉鎮市區／服務類型／關鍵字篩選與統計圖表，無經緯度座標 |
| `tyc-denture/` | 桃園市長者裝置活動假牙合約醫療院所 | 桃園市政府衛生局 | 桃園市長者裝置活動假牙補助合約醫療院所（牙醫診所/醫院）清單，收錄特約單位名稱、區別、地址、電話，並整理補助對象、補助基準（部分/半口/全口活動假牙、假牙維修）與申請流程說明；「機構類型」由名稱關鍵字啟發式推斷（非官方分類），提供行政區／機構類型／關鍵字篩選與統計圖表，無經緯度座標 |
| `tyc-disability-hospitals/` | 桃園市身心障礙類別、向度之鑑定醫院名冊 | 桃園市政府衛生局 | 桃園市身心障礙「鑑定類別（第一類～第八類）×鑑定向度×17家醫院」勾選矩陣，本站展開為長格式（約623筆），收錄鑑定類別、向度、相關疾病類別、可鑑定醫院與備註條件（如年齡/疾病限制），提供鑑定類別／向度／醫院／關鍵字篩選與統計圖表，無地址、電話、經緯度座標 |
| `tyc-placement/` | 桃園市失能老人接受長期照顧機構服務暨老人保護安置機構名冊 | 桃園市政府社會局 | 115-116年失能老人公費安置機構簽約名冊，收錄約123筆機構名稱、電話、地址，機構多數位於桃園市但亦有少數位於新竹縣、花蓮縣、彰化縣、新北市、臺南市等縣市；「機構類型」由機構名稱結尾括號中以「型」結尾的文字解析（非官方分類），提供縣市／鄉鎮市區／機構類型／關鍵字篩選與統計圖表，無經緯度座標 |

原始資料下載網址：
- https://ltcpap.mohw.gov.tw/publish/abc.csv
- https://email.chcg.gov.tw/df/pufnpn5i5741iy9efkn2rrz5ga6uhb
- https://opendata.tycg.gov.tw/api/dataset/536bb44b-b9f1-4336-ad26-34b9e25b3a68/resource/3d7e3b4c-8bc5-47c4-85a9-eec70415b189/download
- https://health.gov.taipei/News_Content.aspx?n=F0D7A5A451D2493C&sms=549F98C9E5942A2B&s=9138F86B8A3CBF69　（公告頁面，PDF 需手動下載，見下方說明）
- https://data.kcg.gov.tw/File/DirectDownload/59ac925f-10dd-42f7-a540-ab6c4218b93d
- https://ws.hsinchu.gov.tw/001/Upload/1/opendata/8774/283/b14a70a1-784c-4586-babf-ade99a7e8277.json
- https://opendataap2.e-land.gov.tw/./resource/files/2019-12-03/a91e966d8b5b07d1e9bb8c3a767e9d1f.json
- https://odws.hccg.gov.tw/001/Upload/25/opendataback/9059/33/b253c75b-9e30-42d5-81bd-eb1f37e74af2.json
- https://data.tainan.gov.tw/File/ResourceCsvDownload/4de27549-893c-4e8e-8644-538a35076607
- https://newdatacenter.taichung.gov.tw/api/v1/no-auth/resource.download?rid=af086949-239b-41ef-8316-5c12dd26a672
- https://data.ntpc.gov.tw/api/datasets/467cb02f-1f94-4fa1-a440-4f08575cf181/csv?page=0&size=100
- https://ltccenter.cyhg.gov.tw/cp.aspx?n=F7AEF7883C88532B　（公告頁面，非開放資料 CSV/API，資料由使用者提供本機 CSV，見下方說明）
- https://www-ws.pthg.gov.tw/Upload/2015pthg/0/relfile/0/0/886f59e6-23b6-4de3-a04a-4de087bdf9b8.csv
- https://newdatacenter.taichung.gov.tw/api/v1/no-auth/resource.download?rid=96251524-861c-4b92-9401-590444adcb8f
- https://opendata.tycg.gov.tw/api/dataset/2e087011-3a3d-4ae1-9038-19b2f3f43a9a/resource/cc33a2eb-c1cf-47f1-b6f7-d4b37ba4c797/download　（BIG5(cp950) 編碼）
- https://opendata.tycg.gov.tw/api/dataset/c0c21e97-fc4a-4b65-aa31-0550b4a007b6/resource/433a97d4-c947-4ecd-9e9f-a1860f8cc0d5/download
- https://opendata.tycg.gov.tw/api/dataset/628c2789-10f8-4c73-bafc-58dac276fa6f/resource/a2b6559b-9265-4854-b1be-97c0f8cde3a6/download
- https://opendata.tycg.gov.tw/api/dataset/d771e458-6e10-45c0-9ec0-83fd820266b5/resource/f7339a27-6360-4a34-a7ec-11f5dc0b2135/download　（BIG5(cp950) 編碼）

授權方式：政府資料開放授權條款-第1版

## 網站架構

```
index.html          首頁，連結至十八個儀表板與更新紀錄頁
llms.txt             全站給 LLM 閱讀的摘要（含各資料集頁面連結與說明），依 llmstxt.org 慣例放在網站根目錄
changelog/index.html 網站更新紀錄頁（純靜態文字，供 SEO 與使用者查看網站更新歷程）
abc/index.html       長照ABC據點地圖儀表板（Leaflet 地圖 + Chart.js 圖表 + 篩選表格）
abc/app.js
lane/index.html      巷弄長照站儀表板（Chart.js 圖表 + 篩選表格）
lane/app.js
tyc-elder/index.html 桃園市老人福利機構一覽表儀表板（Chart.js 圖表 + 篩選表格，無地圖）
tyc-elder/app.js
specialty/index.html 臺北市長照專業服務特約單位儀表板（Chart.js 圖表 + 篩選表格，無地圖）
specialty/app.js
kcg-homecare/index.html 銀髮族服務-居家長照機構地圖儀表板（Leaflet 地圖 + Chart.js 圖表 + 篩選表格）
kcg-homecare/app.js
hsc-ltc/index.html   新竹縣長照機構名冊儀表板（Chart.js 圖表 + 篩選表格，無地圖）
hsc-ltc/app.js
yl-ltc/index.html    宜蘭縣立案老人長期照顧及安養機構名冊儀表板（Chart.js 圖表 + 篩選表格，無地圖）
yl-ltc/app.js
hccg-elder/index.html 新竹市老人福利機構一覽表地圖儀表板（Leaflet 地圖 + Chart.js 圖表 + 篩選表格）
hccg-elder/app.js
tn-homecare-nursing/index.html 臺南市居家護理機構儀表板（Chart.js 圖表 + 篩選表格，無地圖）
tn-homecare-nursing/app.js
tc-nursing/index.html 臺中市一般護理之家清冊儀表板（Chart.js 圖表 + 篩選表格，無地圖）
tc-nursing/app.js
ntpc-nursing/index.html 新北市一般護理之家清冊儀表板（Chart.js 圖表 + 篩選表格，無地圖）
ntpc-nursing/app.js
chiayi-ltc/index.html 嘉義縣立案長照及護理之家機構一覽儀表板（Chart.js 圖表 + 篩選表格，無地圖）
chiayi-ltc/app.js
pingtung-ltc/index.html 屏東縣老人長期照顧機構儀表板（Chart.js 圖表 + 篩選表格，無地圖）
pingtung-ltc/app.js
tc-transport/index.html 臺中市失能者交通接送服務地圖儀表板（Leaflet 地圖 + Chart.js 圖表 + 篩選表格）
tc-transport/app.js
tyltc/index.html     桃園市長期照護專業服務特約單位儀表板（Chart.js 圖表 + 篩選表格，無地圖）
tyltc/app.js
tyc-denture/index.html 桃園市長者裝置活動假牙合約醫療院所儀表板（Chart.js 圖表 + 篩選表格，無地圖；
                       頁面上方另有補助制度說明靜態卡片）
tyc-denture/app.js
tyc-disability-hospitals/index.html 桃園市身心障礙類別、向度之鑑定醫院名冊儀表板（Chart.js 圖表 +
                       篩選表格，無地圖；原始資料為勾選矩陣，本站展開為長格式）
tyc-disability-hospitals/app.js
tyc-placement/index.html 桃園市失能老人接受長期照顧機構服務暨老人保護安置機構名冊儀表板（Chart.js
                       圖表 + 篩選表格，無地圖）
tyc-placement/app.js
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
data/kcg-homecare.json 銀髮族服務-居家長照機構資料（由 scripts/build_data.py 產生）
data/kcg-homecare.js   同上資料的內嵌 JS 版本（window.KCG_HOMECARE_DATA），供 kcg-homecare 頁面以
                       <script> 標籤直接載入，因來源網址無 CORS 標頭，不透過 fetch()
data/hsc-ltc.json     新竹縣長照機構名冊資料（由 scripts/build_data.py 產生）
data/hsc-ltc.js       同上資料的內嵌 JS 版本（window.HSC_LTC_DATA），供 hsc-ltc 頁面以
                       <script> 標籤直接載入，因來源網址無 CORS 標頭，不透過 fetch()
data/yl-ltc.json      宜蘭縣立案老人長期照顧及安養機構名冊資料（由 scripts/build_data.py 產生）
data/yl-ltc.js        同上資料的內嵌 JS 版本（window.YL_LTC_DATA），供 yl-ltc 頁面以
                       <script> 標籤直接載入，因來源網址無 CORS 標頭，不透過 fetch()
data/hccg-elder.json  新竹市老人福利機構一覽表資料（由 scripts/build_data.py 產生）
data/hccg-elder.js    同上資料的內嵌 JS 版本（window.HCCG_ELDER_DATA），供 hccg-elder 頁面以
                       <script> 標籤直接載入，因來源網址無 CORS 標頭，不透過 fetch()
data/tn-homecare-nursing.json  臺南市居家護理機構資料（由 scripts/build_data.py 產生）
data/tn-homecare-nursing.js    同上資料的內嵌 JS 版本（window.TN_HOMECARE_NURSING_DATA），供
                       tn-homecare-nursing 頁面以 <script> 標籤直接載入，因來源網址無 CORS 標頭，不透過 fetch()
data/tc-nursing.json  臺中市一般護理之家清冊資料（由 scripts/build_data.py 產生）
data/tc-nursing.js    同上資料的內嵌 JS 版本（window.TC_NURSING_DATA），供 tc-nursing 頁面以
                       <script> 標籤直接載入，避免依賴外部網址即時可用性
data/ntpc-nursing.json 新北市一般護理之家清冊資料（由 scripts/build_data.py 產生）
data/ntpc-nursing.js   同上資料的內嵌 JS 版本（window.NTPC_NURSING_DATA），供 ntpc-nursing 頁面以
                       <script> 標籤直接載入，因來源網址 CORS 僅允許 data.ntpc.gov.tw 網域，不透過 fetch()
data/chiayi-ltc.json  嘉義縣立案長照及護理之家機構一覽資料（由 scripts/build_data.py 讀取本機 CSV 產生）
data/chiayi-ltc.js    同上資料的內嵌 JS 版本（window.CHIAYI_LTC_DATA），供 chiayi-ltc 頁面以
                       <script> 標籤直接載入，因無公開下載網址，不透過 fetch()
data/pingtung-ltc.json 屏東縣老人長期照顧機構資料（由 scripts/build_data.py 產生）
data/pingtung-ltc.js   同上資料的內嵌 JS 版本（window.PINGTUNG_LTC_DATA），供 pingtung-ltc 頁面以
                       <script> 標籤直接載入，因來源網址無 CORS 標頭，不透過 fetch()
data/tc-transport.json 臺中市失能者交通接送服務資料（由 scripts/build_data.py 產生，含座標換算）
data/tc-transport.js   同上資料的內嵌 JS 版本（window.TC_TRANSPORT_DATA），供 tc-transport 頁面以
                       <script> 標籤直接載入，避免依賴外部網址即時可用性
data/tyltc.json       桃園市長期照護專業服務特約單位資料（由 scripts/build_data.py 產生，BIG5(cp950) 解碼）
data/tyltc.js         同上資料的內嵌 JS 版本（window.TYLTC_DATA），供 tyltc 頁面以
                       <script> 標籤直接載入，因來源網址無 CORS 標頭，不透過 fetch()
data/tyc-denture.json 桃園市長者裝置活動假牙合約醫療院所資料（由 scripts/build_data.py 產生）
data/tyc-denture.js   同上資料的內嵌 JS 版本（window.TYC_DENTURE_DATA），供 tyc-denture 頁面以
                       <script> 標籤直接載入，因來源網址無 CORS 標頭，不透過 fetch()
data/tyc-disability-hospitals.json 桃園市身心障礙類別、向度之鑑定醫院名冊資料（由
                       scripts/build_data.py 展開矩陣為長格式產生；資料量小，前端以一般 fetch()
                       讀取，不輸出內嵌 JS 版本）
data/tyc-placement.json 桃園市失能老人接受長期照顧機構服務暨老人保護安置機構名冊資料（由
                       scripts/build_data.py 產生，BIG5(cp950) 解碼）
data/tyc-placement.js  同上資料的內嵌 JS 版本（window.TYC_PLACEMENT_DATA），供 tyc-placement
                       頁面以 <script> 標籤直接載入，因來源網址無 CORS 標頭，不透過 fetch()
data/source/          長照專業服務特約單位來源 PDF（人工下載存放於此，供 build_data.py 解析）
data/meta.json        資料筆數與更新時間
scripts/build_data.py 資料下載與轉換腳本
scripts/sources/chiayi-ltc/  嘉義縣立案長照及護理之家機構一覽的原始 CSV（institutions.csv／
                       nursing-homes.csv，人工提供，無公開下載網址，需人工更新後重跑 build_data.py）
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

不帶參數執行會重新下載十六份 CSV/JSON（長照ABC據點、巷弄長照站、桃園市老人福利機構一覽表、
銀髮族服務-居家長照機構、新竹縣長照機構名冊、宜蘭縣立案老人長期照顧及安養機構名冊、
新竹市老人福利機構一覽表、臺南市居家護理機構、臺中市一般護理之家清冊、新北市一般護理之家清冊、
屏東縣老人長期照顧機構、臺中市失能者交通接送服務、桃園市長期照護專業服務特約單位、
桃園市長者裝置活動假牙合約醫療院所、桃園市身心障礙類別、向度之鑑定醫院名冊、
桃園市失能老人接受長期照顧機構服務暨老人保護安置機構名冊）並覆寫對應
`data/*.json`；同時嘗試解析
`data/source/tp-ltc-specialty-*.pdf`
（若存在）產生 `data/specialty.json`／`data/specialty.js`，並讀取 `scripts/sources/chiayi-ltc/` 下的
本機 CSV 產生 `data/chiayi-ltc.json`／`data/chiayi-ltc.js`。這是**完整流程**，會對外發送多個網路請求且較耗時，
**僅在明確需要全面更新所有資料集時才執行**；建議依資料集「更新頻率」（每1月 / 每1年 / 不定期）
定期執行後再部署，平常開發（例如新增單一資料集頁面）不需要、也不應該每次都跑全部。

### 只更新單一資料集

新增或調整單一資料集時（例如剛寫好一個新的 `build_xxx()`），可指定資料集 key 只重跑該資料集，
不會影響其他資料集既有的 `data/*.json`／`.js`，也不會覆寫 `data/meta.json` 中其他資料集的紀錄：

```bash
python3 scripts/build_data.py chiayi-ltc          # 只重新產生嘉義縣立案長照及護理之家機構一覽
python3 scripts/build_data.py pingtung-ltc        # 只重新產生屏東縣老人長期照顧機構
python3 scripts/build_data.py tc-transport        # 只重新產生臺中市失能者交通接送服務
python3 scripts/build_data.py tyc-placement       # 只重新產生桃園市失能老人長照暨老人保護安置機構名冊
python3 scripts/build_data.py tc-nursing ntpc-nursing   # 可同時指定多個，以空白分隔
python3 scripts/build_data.py --help              # 列出所有可用的資料集 key
```

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
3. 執行 `python3 scripts/build_data.py specialty` 只重新產生 `data/specialty.json`／`data/specialty.js`。
4. 建議抽樣核對幾筆機構名稱、地址與服務能力是否正確解析（PDF 表格跨頁與換行清理邏輯詳見
   `scripts/build_data.py` 的 `build_specialty()`）。

### 更新「嘉義縣立案長照及護理之家機構一覽」

此資料集**沒有開放資料 CSV/API**，來源為[嘉義縣政府長期照護管理中心](https://ltccenter.cyhg.gov.tw/cp.aspx?n=F7AEF7883C88532B)網站，
資料由使用者以本機 CSV 提供，因此無法由腳本自動下載，需手動維護：

1. 取得最新版「嘉義縣立案住宿長照機構名單」與「嘉義縣護理之家名單」CSV（UTF-8 編碼）。
2. 分別覆蓋 `scripts/sources/chiayi-ltc/institutions.csv`（住宿長照機構）與
   `scripts/sources/chiayi-ltc/nursing-homes.csv`（護理之家），維持原有欄位名稱與順序。
3. 執行 `python3 scripts/build_data.py chiayi-ltc` 只重新產生 `data/chiayi-ltc.json`／`data/chiayi-ltc.js`。
4. 建議抽樣核對幾筆機構名稱、鄉鎮市解析與床數是否正確（地址解析邏輯詳見
   `scripts/build_data.py` 的 `build_chiayi_ltc()` 與 `_chiayi_township()`）。

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
- 首頁與各資料集頁面皆內嵌 `schema.org` JSON-LD 結構化資料（`WebSite` / `Dataset`），標示資料提供機關、授權方式與原始下載網址，利於搜尋引擎理解資料集內容。**每次新增資料集頁面時，務必同步在首頁 `index.html` 的
  `WebSite` JSON-LD 的 `hasPart` 陣列新增對應 `Dataset` 條目（name/description/url/license/creator），並更新
  `dateModified`，否則搜尋引擎讀到的結構化資料會與實際頁面數量不一致。**
- 根目錄提供 `robots.txt` 與 `sitemap.xml`，並加入 `favicon.png`/`favicon.ico`。
- 根目錄 `llms.txt`（依 [llmstxt.org](https://llmstxt.org/) 慣例）提供全站 Markdown 摘要，列出各資料集頁面
  連結與簡介；每個資料集頁面資料夾下另有一份專屬 `<dataset>/llms.txt`，說明該資料集的提供機關、原始資料
  來源、授權方式與筆數，供 LLM 快速理解單一資料集內容。**新增資料集頁面時，記得同步在根目錄 `llms.txt` 的
  「資料集頁面」清單新增一筆條目，並在該資料集資料夾新增對應的 `llms.txt`。**
- 加入 `<noscript>` 提示文字，因本站內容需 JavaScript 動態載入 JSON 資料才能顯示。
- 若更換部署網域，請同步更新 `robots.txt`、`sitemap.xml` 及各頁面內的 canonical／og:url／JSON-LD 網址。
- `changelog/index.html` 為純靜態的網站更新紀錄頁，記錄各資料集/功能上線時間，內嵌 `WebPage` + `ItemList`
  結構化資料，供搜尋引擎判斷網站的更新頻率與內容新鮮度；**每次新增資料集或重大功能變更時，請同步在此頁
  新增一筆條目**，並更新 `dateModified`。

## 技術說明

- 純靜態網站，無需後端，前端使用原生 JavaScript + [Leaflet](https://leafletjs.com/)（含 MarkerCluster 群聚顯示 3 萬筆座標點）+ [Chart.js](https://www.chartjs.org/)。
- 「長照ABC據點」資料實際筆數約 3.1 萬筆（開放資料平台詮釋資料標示的 1000 筆為估計值，非實際資料量）。
- 地圖為兼顧效能，篩選結果超過 8,000 筆時會等距抽樣顯示，統計數字與表格仍以完整篩選結果為準。
- 「臺北市長照專業服務特約單位」無地圖與經緯度座標，且原始 PDF 因來源字型 cmap 對應問題，部分常見漢字
  被替換成外觀相同的 Unicode CJK 部首符號，`build_data.py` 已內建還原對照表；服務區域欄位可能為「全區」
  或多個行政區組合，前端篩選與統計圖表會將「全區」展開計入全部12個行政區。
- 「銀髮族服務-居家長照機構」資料約115筆，來源網址無 CORS 標頭，改以內嵌式 JS（`window.KCG_HOMECARE_DATA`）
  載入；因筆數遠低於 abc 資料集，地圖不做抽樣上限處理，僅沿用 MarkerCluster 群聚顯示。
- 「新竹縣長照機構名冊」資料約55筆，無經緯度座標，來源網址無 CORS 標頭，改以內嵌式 JS
  （`window.HSC_LTC_DATA`）載入；原始資料地址欄位有「新鋪鎮」typo（新竹縣無此行政區），已於
  `build_data.py` 自動修正為「新埔鎮」再解析鄉鎮市區。
- 「宜蘭縣立案老人長期照顧及安養機構名冊」資料約39筆，無經緯度座標，來源網址無 CORS 標頭，改以內嵌式
  JS（`window.YL_LTC_DATA`）載入；機構類型由機構名稱結尾括號文字（如「(養護型)」）解析而來，無標示者
  歸類為「未標示」；部分地址缺少「宜蘭縣」前綴，`build_data.py` 會依已知鄉鎮市區名稱嘗試補上，仍有1筆
  因地址資訊不足（僅門牌未含鄉鎮名）無法辨識行政區，鄉鎮市區欄位留空。
- 「新竹市老人福利機構一覽表」資料約8筆，來源網址無 CORS 標頭，改以內嵌式 JS
  （`window.HCCG_ELDER_DATA`）載入；原始資料已內建經緯度座標不需地理編碼，地址已含完整「新竹市OO區」
  字首可直接解析行政區；「編號」欄位有跳號（例如缺7號）、「立案日期」欄位格式不一致（部分夾雜
  「設立/變更負責人」等敘述文字），皆屬原始資料狀態，前端僅原文顯示不做日期排序/運算。
- 「臺南市居家護理機構」DCAT 罕見地同時列出104~114年度共9個版本的 distribution，欄位隨年度不同；
  選用114年度 CSV 下載網址（機構名稱、機構代碼、行政區、地址、負責人、電話、分機），因其欄位最完整
  且為最新資料，但**不含經緯度**，故本頁僅提供表格＋統計圖表，不含地圖。「行政區」原始欄位為數字代碼
  （無對照表），改由「地址」欄位以既有 `parse_county_district()` 解析出中文行政區名稱；「電話」與
  「分機」欄位常互斥出現（其中一欄為空，另一欄可能放手機號碼），前端合併為單一「聯絡電話」欄位顯示
  （格式為「電話 轉 分機」，若電話為空則直接顯示分機欄位內容）。來源網址無 CORS 標頭，改以內嵌式 JS
  （`window.TN_HOMECARE_NURSING_DATA`）載入。
- 「嘉義縣立案長照及護理之家機構一覽」合併使用者提供的「嘉義縣立案住宿長照機構名單」（2筆）與
  「嘉義縣護理之家名單」（15筆）共17筆資料，以 `category` 欄位分類呈現於同一頁面；**無經緯度座標**，
  故不含地圖，僅提供機構類型／鄉鎮市篩選、關鍵字搜尋、統計圖表與分頁表格。此資料集**沒有公開下載
  網址**，原始 CSV 已存放於 `scripts/sources/chiayi-ltc/`，供未來人工更新資料使用，詳見上方「更新
  嘉義縣立案長照及護理之家機構一覽」說明。住宿長照機構原始資料無「負責人」「核准開業日期」欄位，
  於前端表格顯示為「—」；「核准開業日期」為民國年字串（如「88.3.22」），原文照登不轉換為西元年。
- 「屏東縣老人長期照顧機構」資料約56筆，原始欄位僅 name／address／phone 三欄，**無經緯度座標**，
  故不含地圖，僅提供鄉鎮市／機構類型篩選、關鍵字搜尋、統計圖表與分頁表格；來源網址無 CORS 標頭，
  改以內嵌式 JS（`window.PINGTUNG_LTC_DATA`）載入。多數地址未含「屏東縣」前綴（僅鄉鎮市名稱開頭），
  `build_data.py` 依屏東縣33個鄉鎮市清單補上前綴後再解析，仍有1筆因地址資訊不足（僅門牌未含鄉鎮名）
  無法辨識鄉鎮市，鄉鎮市欄位留空；機構類型由機構名稱結尾括號文字（如「(養護型)」）解析而來，無標示者
  歸類為「未標示」，與宜蘭縣資料集處理方式一致。
- 「臺中市失能者交通接送服務」資料約47筆，原始欄位為辦理單位／連絡電話／地址／X坐標／Y坐標／
  服務區域；X/Y 坐標為 **TWD97 TM2 平面座標（EPSG:3826）**而非經緯度，`build_data.py` 的
  `twd97_to_wgs84()` 用標準橫麥卡托投影反算公式自行換算為 WGS84 經緯度，未新增任何外部套件依賴；
  地址已含完整「臺中市OO區」字首可直接解析辦理單位所在行政區；「服務區域」欄位以「、」分隔多個行政區
  （少數為「全區」代表服務臺中市全部行政區），前端拆解為陣列供服務區域多選篩選（勾選任一行政區時，
  「全區」單位恆視為符合）；「連絡電話」欄位格式不一，混雜市話/手機並偶夾帶「分機」文字，原文照登，
  前端另行解析組成 tel: 連結；地址於表格中另提供 Google Maps 搜尋連結，點選開新分頁瀏覽該地址位置；
  來源網址與「臺中市一般護理之家清冊」同平台，仍依專案慣例改以內嵌式 JS
  （`window.TC_TRANSPORT_DATA`）載入。
- 「桃園市長期照護專業服務特約單位」資料約115筆，原始 CSV **編碼為 BIG5(cp950)**（與本專案其他
  資料集慣用的 utf-8-sig 不同，`fetch()` 已支援自訂編碼參數處理）；「地址」為特約單位（辦理單位）
  本身的地址，約18%機構位於新北市、臺北市、基隆市、新竹市等桃園市以外縣市（服務桃園市民但機構設址
  於外縣市），縣市／鄉鎮市區皆由地址欄位解析，地址以「桃園市」開頭者用固定13區清單比對，其餘縣市
  改用通用地址解析規則；**無經緯度座標**，故不含地圖，僅提供縣市／鄉鎮市區／服務類型／關鍵字篩選、
  統計卡與圖表。「服務類型」為本站依機構名稱關鍵字（如「居家式服務類機構」「職能治療所」「物理
  治療所」「護理之家」「日間照顧」等）啟發式推斷，**非衛生局官方分類欄位**，僅供篩選與圖表參考；
  「連絡電話」欄位偶有跨行的多組號碼/分機備註，前端與建置腳本皆合併為單行顯示；來源網址無 CORS
  標頭，改以內嵌式 JS（`window.TYLTC_DATA`）載入。
- 「桃園市長者裝置活動假牙合約醫療院所」資料約155筆，原始欄位為編號／特約單位名稱／區別／地址／
  電話；「區別」欄位本身即為乾淨的桃園市鄉鎮市區中文名稱（如「八德區」），**不需**從地址欄位解析，
  比「桃園市老人福利機構一覽表」更單純；少數地址欄位（如編號140）本身多帶「桃園市」字首屬原始資料
  不一致，原文照登不修正；**無經緯度座標**，故不含地圖，僅提供行政區／機構類型／關鍵字篩選、統計卡
  與圖表。頁面上方另加一張補助制度說明靜態卡片（目的／補助對象／補助基準四項金額／申請流程五步驟／
  注意事項），內容整理自桃園市政府衛生局公告，**非資料集欄位**，純為靜態文字說明，不影響下方
  篩選/圖表/表格運作。「機構類型」（醫院／診所）為本站依「特約單位名稱」是否含「醫院」二字啟發式
  推斷，**非官方分類欄位**，僅供篩選與圖表參考；來源網址與同平台的桃園市老人福利機構一覽表／桃園市
  長期照護專業服務特約單位一致，CORS 僅允許 opendata.tycg.gov.tw 網域，改以內嵌式 JS
  （`window.TYC_DENTURE_DATA`）載入。
- 「桃園市身心障礙類別、向度之鑑定醫院名冊」原始格式並非機構名冊，而是「鑑定類別（第一類～第八類）
  ×鑑定向度×17家醫院」的勾選矩陣（CSV），儲存格值為「V」（可鑑定）、空白（不可鑑定）或「V+備註」
  （有條件可鑑定，如「僅鑑定失智症」「限18歲以上民眾」「無鑑定智能障礙」）；原始 CSV 使用合併儲存格，
  「新制鑑定類別」「新制鑑定向度」欄位僅在分組第一列填值，本腳本以 forward-fill 還原完整分組；含一筆
  特例「整體心理功能：發展遲緩」不屬於「第X類」編號格式，獨立於分組之外處理；檔案結尾有「更新日期：
  112.1.19」備註列，非資料列，本腳本偵測後略過。本站將矩陣展開為長格式（category／dimension／item／
  disease／hospital／note），只保留有勾選的組合，共約623筆，以套用既有分頁表格元件，並提供鑑定
  類別／向度／醫院／關鍵字篩選、統計卡與圖表（醫院排行、類別分布）。**無地址、電話、經緯度座標**，
  故不含地圖，也不套用地址/電話超連結慣例；來源網址與同平台的其他 opendata.tycg.gov.tw 資料集一致，
  CORS 僅允許該平台網域，改由建置腳本於伺服器端下載，但資料量小，前端以一般 `fetch()` 讀取本地靜態
  json 即可，不需另外輸出內嵌 JS 版本。


