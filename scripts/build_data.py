#!/usr/bin/env python3
"""
下載並轉換政府開放資料集為前端可用的 JSON。

資料來源：
1. 長照ABC據點  https://ltcpap.mohw.gov.tw/publish/abc.csv
2. 巷弄長照站    https://email.chcg.gov.tw/df/pufnpn5i5741iy9efkn2rrz5ga6uhb
3. 桃園市老人福利機構一覽表  https://opendata.tycg.gov.tw/api/dataset/536bb44b-b9f1-4336-ad26-34b9e25b3a68/resource/3d7e3b4c-8bc5-47c4-85a9-eec70415b189/download
   （來源網址的 CORS 標頭僅允許 opendata.tycg.gov.tw 網域，前端無法直接 fetch，
   需由本腳本於伺服器端下載；另附加 google_rating／google_review_count／google_place_id 三欄，
   為 2026-07-26 用 scripts/fetch_google_ratings.py --dataset tyc-elder 一次性呼叫 Google Places
   API (Legacy) Text Search 人工核對後，整理成 data/source/tyc-elder-google-ratings.json 供
   build_tyc_elder() 讀取合併，非政府開放資料且未來不會重新抓取，詳見該函式與來源 JSON 說明）
4. 臺北市長照專業服務特約單位  https://health.gov.taipei/News_Content.aspx?n=F0D7A5A451D2493C&sms=549F98C9E5942A2B&s=9138F86B8A3CBF69
   （此資料集**非開放資料 CSV/API**，臺北市政府衛生局僅以公告頁面附加 PDF 附件釋出，因此無法在
   本腳本自動下載，須將衛生局公告的最新 PDF 手動存成 data/source/tp-ltc-specialty-*.pdf 後才能
   重新解析。詳見 build_specialty() 與 README「更新資料」章節）
5. 銀髮族服務-居家長照機構（高雄市）  https://data.kcg.gov.tw/File/DirectDownload/59ac925f-10dd-42f7-a540-ab6c4218b93d
   （來源網址無 CORS 標頭，前端無法直接 fetch，改由本腳本於伺服器端下載）
6. 新竹縣長照機構名冊  https://ws.hsinchu.gov.tw/001/Upload/1/opendata/8774/283/b14a70a1-784c-4586-babf-ade99a7e8277.json
   （來源網址無 CORS 標頭，前端無法直接 fetch，改由本腳本於伺服器端下載；原始地址欄位有「新鋪鎮」
   應為「新埔鎮」的錯字，本腳本會自動修正後再解析鄉鎮市區）
7. 宜蘭縣立案老人長期照顧及安養機構名冊  https://opendataap2.e-land.gov.tw/./resource/files/2019-12-03/a91e966d8b5b07d1e9bb8c3a767e9d1f.json
   （來源網址無 CORS 標頭，前端無法直接 fetch，改由本腳本於伺服器端下載；部分地址欄位缺少「宜蘭縣」
   前綴，本腳本會嘗試依已知鄉鎮市區名稱補上前綴後再解析；機構類型由機構名稱後綴「(養護型)」等括號
   文字解析而來，無標示者歸類為「未標示」）
8. 新竹市老人福利機構一覽表（DCAT dataset https://data.gov.tw/dataset/8572）
   https://odws.hccg.gov.tw/001/Upload/25/opendataback/9059/33/b253c75b-9e30-42d5-81bd-eb1f37e74af2.json
   （來源網址無 CORS 標頭，前端無法直接 fetch，改由本腳本於伺服器端下載；地址已含完整「新竹市OO區」
   字首可直接解析行政區，且原始資料已內建經緯度不需地理編碼；「編號」欄位有跳號、「立案日期」欄位
   格式不一致，屬原始資料狀態）
9. 臺南市居家護理機構（DCAT dataset https://data.gov.tw/dataset/7626）
   https://data.tainan.gov.tw/File/ResourceCsvDownload/4de27549-893c-4e8e-8644-538a35076607
   （此 DCAT 罕見列出104~114年度共9個版本 distribution，欄位隨年度不同，本腳本選用114年度：
   機構名稱/機構代碼/行政區/地址/負責人/電話/分機，無經緯度座標但地址已含完整「臺南市OO區」字首可
   直接解析行政區；原始「行政區」欄位為數字代碼未提供對照表，本腳本改用地址解析取代；來源網址無
   CORS 標頭，改由本腳本於伺服器端下載，詳見 build_tn_homecare_nursing() 選用理由說明）
10. 臺中市一般護理之家清冊（DCAT dataset https://data.gov.tw/dataset/8572）
    https://newdatacenter.taichung.gov.tw/api/v1/no-auth/resource.download?rid=af086949-239b-41ef-8316-5c12dd26a672
    （CSV，共60筆；「行政區」欄位已是中文名稱，不需從地址解析；無經緯度座標；來源網址本身已允許
    CORS（Access-Control-Allow-Origin: *），但仍依專案慣例由本腳本於伺服器端下載，另輸出內嵌 JS
    版本以避免依賴外部網址即時可用性；「附設日間照顧開放人數」多數為「-」（視為0）、「評鑑結果」／
    「督考結果」欄位偶見同格夾帶兩個年度結果（如「112不合格113不合格」）、「開業日期」為民國年
    字串，皆原文照登不重新拆分/轉換，詳見 build_tc_nursing()）
11. 新北市一般護理之家清冊  https://data.ntpc.gov.tw/datasets/467cb02f-1f94-4fa1-a440-4f08575cf181
    https://data.ntpc.gov.tw/api/datasets/467cb02f-1f94-4fa1-a440-4f08575cf181/csv?page=0&size=100
    （正式分頁 CSV API，共75筆，更新頻率每年；地址已含完整「新北市OO區」字首可直接解析行政區，
    無經緯度座標；來源網址 CORS 標頭僅允許 data.ntpc.gov.tw 網域，改由本腳本於伺服器端下載，
    另輸出內嵌 JS 版本；「聯絡人姓名」欄位來源未做遮蔽處理，忠實照登；「特約類別」欄位實測全數為
    常數值無篩選意義，本腳本不輸出，詳見 build_ntpc_nursing()）
12. 嘉義縣立案長照及護理之家機構一覽（嘉義縣政府長期照護管理中心
    https://ltccenter.cyhg.gov.tw/cp.aspx?n=F7AEF7883C88532B ，人工提供，非開放資料 CSV/API）
    （此資料集由使用者提供兩份本機 CSV：「嘉義縣立案住宿長照機構名單」（2筆，欄位：序號/機構名稱/
    許可床數/開業床數/地址/電話，地址已含「嘉義縣」字首）與「嘉義縣護理之家名單」（15筆，欄位：
    序號/機構名稱/負責人或聯絡人/許可床數/開業床數/核准開業日期/地址/電話，地址多數不含縣名字首，
    僅1筆例外）；因無公開下載網址，原始 CSV 已存放於 scripts/sources/chiayi-ltc/institutions.csv
    與 scripts/sources/chiayi-ltc/nursing-homes.csv，供本腳本讀取，未來如需更新資料需人工以最新
    CSV 覆蓋這兩個檔案後再重新執行本腳本；兩份資料合併為單一資料集並以 category 欄位
    （住宿長照機構／護理之家）分類，鄉鎮市由地址欄位解析（先移除可能存在的「嘉義縣」字首，再比對
    嘉義縣18個鄉鎮市清單）；住宿長照機構因原始欄位無「負責人」「核准開業日期」，該兩欄位留空；
    「核准開業日期」為民國年字串（如「88.3.22」），原文照登不轉換為西元年，詳見 build_chiayi_ltc()）
13. 屏東縣老人長期照顧機構（DCAT dataset https://data.gov.tw/dataset/8572 ，提供機關：屏東縣政府
    社會處）
    https://www-ws.pthg.gov.tw/Upload/2015pthg/0/relfile/0/0/886f59e6-23b6-4de3-a04a-4de087bdf9b8.csv
    （CSV，共57筆，欄位僅 name/address/phone 三欄；地址多數不含「屏東縣」字首（僅鄉鎮市名稱開頭，
    如「竹田鄉六巷村太平路70巷20號」），本腳本先比對屏東縣33個鄉鎮市清單補上「屏東縣」前綴後再解析
    鄉鎮市；機構類型由機構名稱結尾括號文字解析（如「(養護型)」「（養護型）」），無標示者歸類為
    「未標示」，與 build_yl_ltc() 處理方式一致；無經緯度座標；來源網址無 CORS 標頭，改由本腳本於
    伺服器端下載，詳見 build_pingtung_ltc()）
14. 臺中市失能者交通接送服務（DCAT dataset https://data.gov.tw/dataset/8572 ，提供機關：臺中市
    政府衛生局）
    https://newdatacenter.taichung.gov.tw/api/v1/no-auth/resource.download?rid=96251524-861c-4b92-9401-590444adcb8f
    （CSV，欄位：辦理單位/連絡電話/地址/X坐標/Y坐標/服務區域，與 DCAT description 一致；地址已含
    完整「臺中市OO區」字首可用 parse_county_district() 直接解析辦理單位所在行政區；X/Y 坐標為
    **TWD97 TM2 平面座標（EPSG:3826）**而非經緯度，本腳本用 twd97_to_wgs84() 以標準反算公式
    （GRS80 橢球、中央經線121°E、縮放係數0.9999、東移250000）自行換算為 WGS84 經緯度，未新增
    任何外部套件依賴；「服務區域」欄位是以「、」分隔的行政區清單字串，少數為「全區」代表服務臺中市
    全部行政區，本腳本拆解為 serviceAreas 陣列供前端多選篩選（比對時「全區」視為符合任一行政區）；
    「連絡電話」欄位格式不一，混雜市話/手機並偶夾帶「分機」文字（如「(04)23950256分機15」），
    原文照登不重新格式化，前端另行去除非數字字元組成可用的 tel: 連結；來源檔案本身在最後一筆資料的
    「服務區域」欄位處疑似遭伺服器端截斷（結尾停在一個多位元組 UTF-8 字元中間），本腳本會過濾掉
    因此產生的解碼替換字元片段；另有一筆服務區域含「棲棲」錯字（應為「梧棲」），原文照登不修正；
    來源網址與同網域的臺中市一般護理之家清冊相同平台，仍依專案慣例由本腳本於伺服器端下載並輸出內嵌
    JS 版本，詳見 build_tc_transport()）
15. 桃園市長期照護專業服務特約單位（DCAT dataset https://data.gov.tw/dataset/8572 ，
    dataset id 94306，提供機關：桃園市政府衛生局）
    https://opendata.tycg.gov.tw/api/dataset/2e087011-3a3d-4ae1-9038-19b2f3f43a9a/resource/cc33a2eb-c1cf-47f1-b6f7-d4b37ba4c797/download
    （CSV，共約121筆，**編碼為 BIG5(cp950)**，與本專案其他資料集慣用的 utf-8-sig 不同，fetch() 已
    支援自訂 encoding 參數處理此例外；欄位為性質/資源彙整機關/辦理單位/成立日期/立案文號/負責人/
    連絡電話/傳真/電子郵件/地址/服務區域/相關網址/X坐標/Y坐標/備註/最後更新時間，與 DCAT description
    一致，但實測「性質」「成立日期」「立案文號」「服務區域」「相關網址」「X坐標」「Y坐標」「備註」
    全數為空值，**無經緯度座標**，故不含地圖；「地址」為特約單位（辦理單位）本身的地址，約12%機構
    位於新北市/臺北市等桃園市以外縣市（服務桃園市民但機構設址於外縣市），不可假設地址一律在桃園市，
    本腳本先判斷是否以「桃園市」開頭並用既有 TYC_DISTRICTS 固定清單解析行政區，否則改用
    parse_county_district() 一般規則解析其他縣市；「服務類型」欄位為本腳本依「辦理單位」名稱關鍵字
    啟發式推斷（如含「居家式服務類機構」「職能治療所」「物理治療所」「護理之家」「日間照顧」等），
    **非官方分類欄位**，前端會明確標注為推斷值，詳見 build_tyltc() 與 TYLTC_TYPE_RULES）
16. 桃園市長者裝置活動假牙合約醫療院所（DCAT dataset https://data.gov.tw/dataset/8572 ，
    dataset id 26030，提供機關：桃園市政府衛生局）
    https://opendata.tycg.gov.tw/api/dataset/c0c21e97-fc4a-4b65-aa31-0550b4a007b6/resource/433a97d4-c947-4ecd-9e9f-a1860f8cc0d5/download
    （CSV，共約155筆；欄位為編號/特約單位名稱/區別/地址/電話，與 DCAT description 一致；「區別」
    欄位本身即為乾淨的桃園市鄉鎮市區中文名稱（如「八德區」），**不需**從地址欄位解析，比
    build_tyc_elder() 更單純；少數地址欄位（如編號140）本身多帶「桃園市」字首屬原始資料不一致，
    原文照登不修正；無經緯度座標，故不含地圖；本腳本額外依「特約單位名稱」是否含「醫院」二字推斷
    「機構類型」（醫院／診所），**非官方分類欄位**，僅供篩選/圖表參考，詳見 build_tyc_denture()；
    來源網址與同平台其他 opendata.tycg.gov.tw 資料集一致，CORS 僅允許該平台網域，改由本腳本於
    伺服器端下載並額外輸出內嵌 JS 版本）
17. 桃園市身心障礙類別、向度之鑑定醫院名冊（DCAT dataset https://data.gov.tw/dataset/8572 ，
    dataset id 128335，提供機關：桃園市政府衛生局）
    https://opendata.tycg.gov.tw/api/dataset/628c2789-10f8-4c73-bafc-58dac276fa6f/resource/a2b6559b-9265-4854-b1be-97c0f8cde3a6/download
    （CSV，原始格式為「鑑定類別×向度×17家醫院」勾選矩陣，非機構名冊；欄位為 新制鑑定類別／
    新制鑑定向度／新制鑑定向度_名稱／相關疾病類別，加上17個醫院欄位（值為V／空白／V+備註）；
    使用合併儲存格，「新制鑑定類別」「新制鑑定向度」欄位本腳本以 forward-fill 還原完整分組；
    含一筆特例「整體心理功能：發展遲緩」不屬於「第X類」編號格式，獨立於分組之外處理；結尾有
    「更新日期：112.1.19」備註列，本腳本偵測後略過；本腳本將矩陣展開為長格式（category/
    dimension/item/disease/hospital/note，僅保留有勾選的組合，預估400~500筆）以套用既有分頁
    表格元件；無地址、無電話、無經緯度座標，故不含地圖也不套用超連結慣例；來源網址與同平台其他
    opendata.tycg.gov.tw 資料集一致，CORS 僅允許該平台網域，改由本腳本於伺服器端下載，但資料量小
    不需另外輸出內嵌 JS 版本，詳見 build_tyc_disability_hospitals()）
18. 桃園市失能老人接受長期照顧機構服務暨老人保護安置機構名冊（DCAT dataset https://data.gov.tw/dataset/8572 ，
    dataset id 75570，提供機關：桃園市政府社會局；distribution 備註「115-116年失能老人公費安置機構
    簽約名冊」）
    https://opendata.tycg.gov.tw/api/dataset/d771e458-6e10-45c0-9ec0-83fd820266b5/resource/f7339a27-6360-4a34-a7ec-11f5dc0b2135/download
    （CSV，共123筆，**編碼為 BIG5(cp950)**，與 tyltc 相同例外，fetch() 用 encoding="cp950" 下載；
    欄位為編號/機構名稱/電話/地址，與 DCAT description 一致；無經緯度座標，故不含地圖；「機構名稱」
    結尾偶帶括號分類文字，本腳本只擷取以「型」結尾的括號內容作為「機構類型」（如「養護型」
    「長期照護型」），避免誤擷取名稱中其他非分類用途的括號備註（如「（更名前：海森）」「（玉里
    園區）」這類改名/分院備註），無法擷取到「型」結尾括號者歸類「未標示」，**非官方分類欄位**，
    僅供篩選/圖表參考；「地址」多數為「桃園市OO區」，但因屬跨縣市公費安置合約名冊，實測約13筆
    位於新竹縣/花蓮縣/彰化縣/新北市/臺南市等桃園市以外縣市，本腳本比照 build_tyltc() 的作法：地址
    以「桃園市」開頭者用既有 TYC_DISTRICTS 固定清單解析行政區，其餘縣市改用
    parse_county_district(strict=True) 一般規則解析；第92筆地址欄位以引號包住跨行兩筆地址（機構
    行政聯絡地址＋實際所在地地址），CSV 已用 csv.DictReader 正確讀入，原文照登不拆分成兩筆；第3筆
    地址欄位內容誤填為與機構名稱相同的文字（原始資料品質問題，非本腳本解析錯誤），原文照登不修正，
    該筆行政區因文字不含合法鄉鎮市區字尾而解析為空字串；電話欄位格式不一（夾帶空格、「分機」文字、
    「#」分機、聯絡人姓名如「03-8886141#1153葉小姐」），原文照登不重新格式化；來源網址與同平台其他
    opendata.tycg.gov.tw 資料集一致，CORS 僅允許該平台網域，改由本腳本於伺服器端下載並輸出內嵌 JS
    版本，詳見 build_tyc_placement()）

19. 臺北市假牙補助醫療院所名單（DCAT dataset https://data.gov.tw/dataset/8572 ，
    dataset id 129840，提供機關：臺北市政府社會局）
    https://data.taipei/api/dataset/76b8b514-e793-4cca-8dcf-065d5af4b760/resource/d6522c9f-2026-4ab0-9642-65df9218a9bc/download
    （CSV，**編碼為 BIG5(cp950)**，與 tyltc/tyc-placement 同一例外，fetch() 用 encoding="cp950"
    下載；欄位為補助類型/區域/院所名稱/地址/連絡電話，與 DCAT description 一致；實測僅**6筆資料**，
    「補助類型」全數為常數值「假牙補助」無篩選/圖表意義，本腳本仍照原文輸出該欄位但前端不另外
    製作分布圖表；6家院所全為「臺北市立聯合醫院」不同分院，地址已含完整「臺北市OO區」字首可直接用
    parse_county_district(strict=True) 解析行政區（臺北市12個行政區名稱互不含子字串歧義，不需
    像 TYC_DISTRICTS 那樣額外處理）；無經緯度座標，故不含地圖；「區域」欄位本身即為乾淨的臺北市
    行政區中文名稱，與從地址解析出的行政區一致，僅作為交叉驗證，前端仍以地址解析結果為準；來源網址
    data.taipei 平台無 CORS 標頭，改由本腳本於伺服器端下載，因資料量極小仍輸出內嵌 JS 版本以維持
    與其他資料集一致的載入方式，詳見 build_tpe_denture()；本資料集另外附加 rating／review_count
    兩欄，為 2026-07-26 用 scripts/fetch_tpe_denture_ratings.py 一次性呼叫 Google Places API
    (Legacy) Text Search 人工核對後，寫死於 build_tpe_denture() 內的 TPE_DENTURE_GOOGLE_RATINGS
    常數，非政府開放資料且未來不會重新抓取，詳見該常數與函式註解）
20. 桃園市社區安寧療護資源一覽表（DCAT dataset https://data.gov.tw/dataset/8572 ，
    dataset id 45675，提供機關：桃園市政府衛生局）
    https://opendata.tycg.gov.tw/api/dataset/7d03add1-aef5-4bbf-9b1b-7d601abd43a4/resource/5e7907b0-5418-4c36-9723-b6f786ad5871/download
    （CSV，**編碼為 BIG5(cp950)**，與 tyltc/tyc-placement/tpe-denture 同一例外，fetch() 用
    encoding="cp950" 下載；檔案僅62行、**無標準表頭列**，而是用三段「分類標題列」把資料切成三個
    服務類別區塊：「安寧病房,聯繫方式,地址」「安寧共照,聯繫方式,地址」「安寧,居家及社區安寧,」，
    本腳本偵測這三種標題列作為服務類別分段依據（欄位固定 3 欄：機構名稱／電話／地址）；少數資料列
    機構名稱欄位為空、僅有電話（如同一機構的第二支聯絡電話），本腳本會將這類列的電話合併進前一筆
    機構的電話欄位（以「、」分隔），不輸出空名稱的資料列；同一機構常出現在多個服務類別（如「臺北
    榮民總醫院桃園分院」同時提供安寧病房／安寧共照／居家及社區安寧），屬資料集本身設計（一機構可
    對應多種服務），忠實照登為多筆（機構,服務類別）組合，不視為重複資料；地址已含完整「桃園市OO區」
    字首，但共用的 ADDR_RE 對「平鎮區」等名稱中途含「鎮」字的行政區會誤判（截斷成「平鎮」），比照
    build_tyc_elder() 改用桃園市固定13區清單（TYC_DISTRICTS）比對取代 parse_county_district()；
    無經緯度座標，故不含地圖；「居家及社區安寧」
    類別內混雜性質不同的院所（居家護理所／診所／衛生所），原始欄位未區分，本腳本另外依機構名稱關鍵字
    啟發式推斷「機構型態」（含「居家護理所」→居家護理所；含「衛生所」→衛生所；其餘→診所；非居家
    及社區安寧類別留空字串不推斷），**非官方分類欄位**，前端會標注為推斷值；電話欄位格式不一（有無
    括號區碼、夾帶「分機」文字、以「/」分隔多組號碼），原文照登不重新格式化；來源網址與同平台其他
    opendata.tycg.gov.tw 資料集一致，CORS 僅允許該平台網域，改由本腳本於伺服器端下載並輸出內嵌 JS
    版本，詳見 build_tyc_hospice()）

21. 桃園市長照交通接送服務單位（DCAT dataset https://data.gov.tw/dataset/8572 ，
    dataset id 148536，提供機關：桃園市政府社會局）
    https://opendata.tycg.gov.tw/api/dataset/ad10c5d0-b128-4daf-866e-4cfc9a78dadb/resource/e21c957c-1ff5-4c7e-9fcc-7132b96b0033/download
    （CSV，**編碼為 BIG5**，共14筆，欄位：辦理單位/連絡電話/地址/服務區域，與 DCAT description
    一致；「地址」分布多個縣市（桃園市/臺北市/新北市等，服務桃園市民但辦理單位本身設址於外縣市），
    不可假設地址一律在桃園市，改用 parse_county_district() 一般規則解析；少數地址僅以「OO區」
    開頭缺少「桃園市」字首（如「桃園區大興西路二段61號11樓」），本腳本用既有 TYC_DISTRICTS 固定
    清單額外判斷補上「桃園市」；無經緯度座標，故不含地圖；「連絡電話」欄位偶有跨行的多組號碼
    （CSV 已用引號包住換行內容），統一以 " / " 合併成單行，與 build_tyltc() 處理方式一致；
    「服務區域」幾乎全為「桃園市全區」，僅3筆為「復興區(專車)」，資料量小不拆解為陣列；因僅14筆，
    比照 build_tyc_denture() 另輸出內嵌 JS 版本，詳見 build_tyc_transportation()）
22. 看護／照服機構名錄（使用者人工蒐集網路公開資訊，**非政府開放資料**，無提供機關、無官方驗證）
    （此資料集由使用者手動整理目前網路上找得到的私人看護／居家照護機構名單，共27筆，原始 CSV
    已存放於 scripts/sources/caregiver/caregivers.csv，欄位：名稱/網址/收費頁面/聯絡電話/
    服務地區/統一編號；因無公開下載網址、非官方驗證資料，前端頁面會明確標示免責聲明；「服務地區」
    為自由文字且分隔符不一致（「、」「,」「，」「.」「及」「與」等混用，如「雙北及桃園地區，台中」
    「基隆.台北市.新北市.桃園市」），本腳本不強行 split，改用子字串比對偵測文字中出現的縣市
    （見 _caregiver_regions()）：①先比對舊縣名別名（如「台北縣」對應「新北市」）②比對完整縣市
    名稱（如「新竹市」）③比對去除「市／縣」字尾的簡稱（如「新竹」，會同時列出新竹市與新竹縣兩者，
    嘉義同理，屬已知限制僅供參考；「雙北」等模糊描述未展開為個別縣市時不會被偵測到），輸出為
    regions 陣列（可能為空陣列），縣市名稱統一輸出為「臺」的正式寫法；「聯絡電話」欄位偶有多餘
    換行/空白，本腳本會 strip 處理；僅3筆有填「統一編號」，其餘留空字串；未來如需更新資料，需
    人工以最新 CSV 覆蓋 scripts/sources/caregiver/caregivers.csv 後重新執行本腳本，
    詳見 build_caregivers()）
23. 洗腎（透析）接送資源清單（使用者人工蒐集網路公開資訊，**非政府開放資料**，無提供機關、無官方驗證）
    （此資料集由使用者手動整理目前網路上找得到的洗腎/透析民間接送服務單位，共15筆，原始 CSV
    已存放於 scripts/sources/dialysis-transport/dialysis-transport.csv，欄位：名稱/網址/
    聯絡電話/服務地區；因無公開下載網址、非官方驗證資料，前端頁面會明確標示免責聲明；「服務地區」
    欄位極度稀疏（15筆僅5筆有填）故不做縣市正規化篩選，直接保留原始字串；「聯絡電話」欄位偶有
    多餘空白/tab 字元，本腳本會清理後輸出；未來如需更新資料，需人工以最新 CSV 覆蓋
    scripts/sources/dialysis-transport/dialysis-transport.csv 後重新執行本腳本，
    詳見 build_dialysis_transport()。頁面另有一段官方「交通接送服務」BD03/DA01 制度說明文字，
    來源為長期照顧司 1966 長照專區公告頁 https://1966.gov.tw/LTC/cp-6452-69937-207.html
    （建檔日期 111-06-10、更新時間 114-10-23），該頁僅為公告內容非可下載資料，不進入本腳本
    下載流程，僅供頁面引用來源連結）
24. 臺中市失智症服務及資源提供單位（DCAT dataset https://data.gov.tw/dataset/8572 ，dataset id
    108261，提供機關：臺中市政府衛生局）
    https://newdatacenter.taichung.gov.tw/api/v1/no-auth/resource.download?rid=a753a1f2-25d6-469c-9580-83e5e17405cf
    （CSV，共49筆；地址已含完整「臺中市OO區」字首可直接解析行政區；X/Y坐標欄位混雜 WGS84 經緯度
    （41筆）與 TWD97 TM2 平面座標（8筆，數值>1000），本腳本依數值大小判斷格式並用既有
    twd97_to_wgs84() 換算為統一的 WGS84 經緯度；「服務項目」欄位固定僅兩種文字值，對應「失智共同
    照護中心」與「失智社區服務據點」兩類服務單位，轉換為較短的 type 欄位供篩選/圖表使用；來源網址
    無 CORS 標頭，改由本腳本於伺服器端下載，另輸出內嵌 JS 版本，詳見 build_tc_dementia())

用法：
    python3 scripts/build_data.py
輸出：
    data/abc.json
    data/lane.json
    data/tyc-elder.json
    data/tyc-elder.js   (window.TYC_ELDER_DATA，供前端以 <script> 直接載入，避免 fetch 時序問題)
    data/specialty.json
    data/specialty.js   (window.SPECIALTY_DATA，同上，供前端以 <script> 直接載入)
    data/kcg-homecare.json
    data/kcg-homecare.js  (window.KCG_HOMECARE_DATA，同上，供前端以 <script> 直接載入)
    data/hsc-ltc.json
    data/hsc-ltc.js       (window.HSC_LTC_DATA，同上，供前端以 <script> 直接載入)
    data/yl-ltc.json
    data/yl-ltc.js        (window.YL_LTC_DATA，同上，供前端以 <script> 直接載入)
    data/hccg-elder.json
    data/hccg-elder.js    (window.HCCG_ELDER_DATA，同上，供前端以 <script> 直接載入)
    data/tn-homecare-nursing.json
    data/tn-homecare-nursing.js  (window.TN_HOMECARE_NURSING_DATA，同上，供前端以 <script> 直接載入)
    data/tc-nursing.json
    data/tc-nursing.js    (window.TC_NURSING_DATA，同上，供前端以 <script> 直接載入)
    data/ntpc-nursing.json
    data/ntpc-nursing.js  (window.NTPC_NURSING_DATA，同上，供前端以 <script> 直接載入)
    data/chiayi-ltc.json
    data/chiayi-ltc.js    (window.CHIAYI_LTC_DATA，同上，供前端以 <script> 直接載入)
    data/pingtung-ltc.json
    data/pingtung-ltc.js  (window.PINGTUNG_LTC_DATA，同上，供前端以 <script> 直接載入)
    data/tc-transport.json
    data/tc-transport.js  (window.TC_TRANSPORT_DATA，同上，供前端以 <script> 直接載入)
    data/tyltc.json
    data/tyltc.js         (window.TYLTC_DATA，同上，供前端以 <script> 直接載入)
    data/tyc-denture.json
    data/tyc-denture.js   (window.TYC_DENTURE_DATA，同上，供前端以 <script> 直接載入)
    data/tyc-disability-hospitals.json  (資料量小且無 CORS 前端 fetch 需求，不輸出內嵌 JS)
    data/tyc-placement.json
    data/tyc-placement.js  (window.TYC_PLACEMENT_DATA，同上，供前端以 <script> 直接載入)
    data/tpe-denture.json
    data/tpe-denture.js    (window.TPE_DENTURE_DATA，同上，供前端以 <script> 直接載入)
    data/tyc-transport.json
    data/tyc-transport.js  (window.TYC_TRANSPORT_DATA，同上，供前端以 <script> 直接載入)
    data/tyc-hospice.json
    data/tyc-hospice.js    (window.TYC_HOSPICE_DATA，同上，供前端以 <script> 直接載入)
    data/caregiver.json
    data/caregiver.js      (window.CAREGIVER_DATA，同上，供前端以 <script> 直接載入)
    data/dialysis-transport.json
    data/dialysis-transport.js  (window.DIALYSIS_TRANSPORT_DATA，同上，供前端以 <script> 直接載入)
    data/tc-dementia.json
    data/tc-dementia.js    (window.TC_DEMENTIA_DATA，同上，供前端以 <script> 直接載入)
    data/meta.json  (資料更新時間等資訊)

額外相依套件：
    僅 build_specialty() 需要 pdfplumber（`python3 -m pip install pdfplumber`）解析 PDF 表格，
    其餘資料集仍只用標準庫 urllib/csv 下載/解析 CSV。
"""
import argparse
import csv
import glob
import io
import json
import math
import re
import sys
import urllib.request
from datetime import datetime, timezone

ABC_URL = "https://ltcpap.mohw.gov.tw/publish/abc.csv"
LANE_URL = "https://email.chcg.gov.tw/df/pufnpn5i5741iy9efkn2rrz5ga6uhb"
TYC_ELDER_URL = "https://opendata.tycg.gov.tw/api/dataset/536bb44b-b9f1-4336-ad26-34b9e25b3a68/resource/3d7e3b4c-8bc5-47c4-85a9-eec70415b189/download"
SPECIALTY_SOURCE_PAGE = "https://health.gov.taipei/News_Content.aspx?n=F0D7A5A451D2493C&sms=549F98C9E5942A2B&s=9138F86B8A3CBF69"
SPECIALTY_PDF_GLOB = "data/source/tp-ltc-specialty-*.pdf"
KCG_DENTURE_PDF_URL = "https://orgws.kcg.gov.tw/001/KcgOrgUploadFiles/463/RelFile/0/85588/23687658-8121-4268-8bf3-8def3a1e1bf8.pdf"
KCG_DENTURE_MANUAL_JSON = "data/source/kcg-denture-manual.json"
KCG_HOMECARE_URL = "https://data.kcg.gov.tw/File/DirectDownload/59ac925f-10dd-42f7-a540-ab6c4218b93d"
HSC_LTC_URL = "https://ws.hsinchu.gov.tw/001/Upload/1/opendata/8774/283/b14a70a1-784c-4586-babf-ade99a7e8277.json"
HSC_DENTURE_URL = "https://ws.hsinchu.gov.tw/001/Upload/1/opendata/8774/288/d6586e37-bce0-46eb-ae4e-08c5fa41a568.json"
CHC_DENTURE_URL = "https://email.chcg.gov.tw/df/36br48cd4g64iragh4y6dwoy668s3q"
YL_LTC_URL = "https://opendataap2.e-land.gov.tw/./resource/files/2019-12-03/a91e966d8b5b07d1e9bb8c3a767e9d1f.json"
# 115年度宜蘭縣中低收入戶老人假牙裝置補助實施計畫－特約牙醫醫療院所名單（宜蘭縣政府社會處公告 PDF，
# 非 DCAT 開放資料 CSV/API，來源網址本身即為可直接下載的檔案，比照 build_tn_denture() 由本腳本
# 於伺服器端自動下載解析，不需人工存檔）。
YL_DENTURE_PDF_URL = (
    "https://www-ws.e-land.gov.tw/Download.ashx?"
    "u=LzAwMS9VcGxvYWQvNDQ1L3JlbGZpbGUvMTI4MzQvMTMzNDU3LzcyNDJiMDlkLWY2MzYtNDY3Mi04ZjIwLTBkMjlkZTlmN2MwMi5wZGY%3d"
    "&n=MTE15bm05bqm54m557SE6Yar55mC6Zmi5omA5ZCN5ZauKOWQq%2beUs%2biri%2ba1geeoiykgMTE0MTIxOS5wZGY%3d"
)
YL_DENTURE_GOOGLE_RATINGS_FILE = "data/source/yl-denture-google-ratings.json"
HCCG_ELDER_URL = "https://odws.hccg.gov.tw/001/Upload/25/opendataback/9059/33/b253c75b-9e30-42d5-81bd-eb1f37e74af2.json"
TN_HOMECARE_NURSING_URL = "https://data.tainan.gov.tw/File/ResourceCsvDownload/4de27549-893c-4e8e-8644-538a35076607"
TC_NURSING_URL = "https://newdatacenter.taichung.gov.tw/api/v1/no-auth/resource.download?rid=af086949-239b-41ef-8316-5c12dd26a672"
# {page} 佔位符，page 從 0 起算，size=100；資料集目前僅 75 筆一頁即可取完，
# 但保留分頁迴圈以防未來筆數超過 100（見 build_ntpc_nursing()）。
NTPC_NURSING_URL_TEMPLATE = (
    "https://data.ntpc.gov.tw/api/datasets/467cb02f-1f94-4fa1-a440-4f08575cf181/csv"
    "?page={page}&size=100"
)
NTPC_SILVER_HAIR_CLUB_URL = (
    "https://data.ntpc.gov.tw/api/datasets/f531a808-4aab-4e5e-93f0-c34f9ff97a78/csv/file"
)
CHIAYI_LTC_SOURCE_PAGE = "https://ltccenter.cyhg.gov.tw/cp.aspx?n=F7AEF7883C88532B"
CHIAYI_LTC_INSTITUTIONS_CSV = "scripts/sources/chiayi-ltc/institutions.csv"
CHIAYI_LTC_NURSING_CSV = "scripts/sources/chiayi-ltc/nursing-homes.csv"
PINGTUNG_LTC_URL = (
    "https://www-ws.pthg.gov.tw/Upload/2015pthg/0/relfile/0/0/"
    "886f59e6-23b6-4de3-a04a-4de087bdf9b8.csv"
)
TC_TRANSPORT_URL = "https://newdatacenter.taichung.gov.tw/api/v1/no-auth/resource.download?rid=96251524-861c-4b92-9401-590444adcb8f"
TC_DEMENTIA_URL = "https://newdatacenter.taichung.gov.tw/api/v1/no-auth/resource.download?rid=a753a1f2-25d6-469c-9580-83e5e17405cf"
TYLTC_URL = (
    "https://opendata.tycg.gov.tw/api/dataset/2e087011-3a3d-4ae1-9038-19b2f3f43a9a/"
    "resource/cc33a2eb-c1cf-47f1-b6f7-d4b37ba4c797/download"
)
TYC_DENTURE_URL = (
    "https://opendata.tycg.gov.tw/api/dataset/c0c21e97-fc4a-4b65-aa31-0550b4a007b6/"
    "resource/433a97d4-c947-4ecd-9e9f-a1860f8cc0d5/download"
)
TYC_DISABILITY_HOSPITALS_URL = (
    "https://opendata.tycg.gov.tw/api/dataset/628c2789-10f8-4c73-bafc-58dac276fa6f/"
    "resource/a2b6559b-9265-4854-b1be-97c0f8cde3a6/download"
)
TYC_PLACEMENT_URL = (
    "https://opendata.tycg.gov.tw/api/dataset/d771e458-6e10-45c0-9ec0-83fd820266b5/"
    "resource/f7339a27-6360-4a34-a7ec-11f5dc0b2135/download"
)
TPE_DENTURE_URL = (
    "https://data.taipei/api/dataset/76b8b514-e793-4cca-8dcf-065d5af4b760/"
    "resource/d6522c9f-2026-4ab0-9642-65df9218a9bc/download"
)
TYC_TRANSPORT_URL = (
    "https://opendata.tycg.gov.tw/api/dataset/ad10c5d0-b128-4daf-866e-4cfc9a78dadb/"
    "resource/e21c957c-1ff5-4c7e-9fcc-7132b96b0033/download"
)
TYC_HOSPICE_URL = (
    "https://opendata.tycg.gov.tw/api/dataset/7d03add1-aef5-4bbf-9b1b-7d601abd43a4/"
    "resource/5e7907b0-5418-4c36-9723-b6f786ad5871/download"
)
TYC_RESPITE_HOME_URL = (
    "https://opendata.tycg.gov.tw/api/dataset/7ae18138-74f9-4ebb-8b7d-f03d9ddb1ef5/"
    "resource/0b949cb1-bfc3-4d02-8474-35e42a932643/download"
)
TYC_DEMENTIA_HOSPITALS_URL = (
    "https://opendata.tycg.gov.tw/api/dataset/9c47f483-3f6d-4b1a-9a7e-7398d609d646/"
    "resource/e04e10b7-d27a-4480-9489-ab109f928d7f/download"
)
TYC_RESPITE_INST_URL = (
    "https://opendata.tycg.gov.tw/api/dataset/7ae18138-74f9-4ebb-8b7d-f03d9ddb1ef5/"
    "resource/b7c16660-f7ac-4bb6-b639-9c795581f160/download"
)
TN_DENTURE_PDF_URL = (
    "https://health.tainan.gov.tw/warehouse/F8BCB915-C08B-47F3-A731-1C30A3EE61EE/"
    "F_1780645430477e.pdf"
)
# 嘉義市中低收入老人免費裝置假牙合約醫院名單（DCAT dataset https://data.gov.tw/dataset/8572
# https://cms.data.gov.tw/dataset/130486，提供機關：嘉義市政府社會處）。
CHIAYI_DENTURE_LOW_INCOME_URL = (
    "https://data.chiayi.gov.tw/opendata/api/getResource"
    "?oid=79cde0d6-7554-473d-9a0e-4c918afd36ac&rid=7fa5f790-9bfc-4465-83a0-e9007fc2ee18"
)
# 嘉義市115年度一般身分別老人補助裝置假牙合約院所（嘉義市政府社會處長青及社會行政科公告 PDF，
# 非 DCAT 開放資料，無法查得穩定資料集網址，僅有此公告附件連結）。
CHIAYI_DENTURE_LOW_INCOME_ADDED_20260601 = {"杏林牙醫診所", "劍橋牙醫診所", "大明牙醫診所"}
CHIAYI_DENTURE_GENERAL_PDF_URL = (
    "https://icmp-ws.chiayi.gov.tw/Download.ashx"
    "?u=LzAwMS9VcGxvYWQvNDA4L3JlbGZpbGUvOTU1NS83ODI3MDYvMTU3Y2Y5NTgtNGFiYi00ZGQxLTk3MjItMWExYmVhYTFjZTk3LnBkZg%3d%3d"
    "&n=MTE15bm05bqm5LiA6Iis6ICB5Lq65YGH54mZ5ZCI57SE6Zmi5omA5ZCN5YaKLnBkZg%3d%3d"
)
CAREGIVER_CSV = "scripts/sources/caregiver/caregivers.csv"
CAREGIVER_GOOGLE_RATINGS_FILE = "data/source/caregiver-google-ratings.json"

DIALYSIS_TRANSPORT_CSV = "scripts/sources/dialysis-transport/dialysis-transport.csv"

TC_DENTURE_CSV = "scripts/sources/tc-denture/tc-denture.csv"

HL_DENTURE_PDF = "scripts/sources/hl-denture/institution-list.pdf"
HL_DENTURE_GOOGLE_RATINGS_FILE = "data/source/hl-denture-google-ratings.json"

PINGTUNG_DENTURE_PDF = "scripts/sources/pingtung-denture/institution-list.pdf"
PINGTUNG_DENTURE_GOOGLE_RATINGS_FILE = "data/source/pingtung-denture-google-ratings.json"

TPE_DEMENTIA_HOSPITALS_PDF = "scripts/sources/tpe-dementia-hospitals/institution-list.pdf"

# 屏東縣轄1市3鎮28鄉固定清單，供 build_pingtung_denture() 解析地址行政區使用。與 TYC_DISTRICTS
# 用途相同：地址欄位中「屏東市」本身不會再加「屏東縣」字首（如「屏東市自由路270號」），若沿用
# parse_county_district(fallback_county="屏東縣") 會因地址不含字面「屏東縣」三字而解析失敗，
# 故改用固定清單比對（先去除可能存在的「屏東縣」字首，再從清單比對開頭）。
PINGTUNG_DISTRICTS = [
    "屏東市", "潮州鎮", "東港鎮", "恆春鎮",
    "三地門鄉", "霧台鄉", "瑪家鄉", "九如鄉", "里港鄉", "高樹鄉", "鹽埔鄉",
    "長治鄉", "麟洛鄉", "竹田鄉", "內埔鄉", "萬丹鄉", "崁頂鄉", "新埤鄉",
    "南州鄉", "林邊鄉", "琉球鄉", "佳冬鄉", "新園鄉", "枋寮鄉",
    "枋山鄉", "獅子鄉", "車城鄉", "牡丹鄉", "滿州鄉", "來義鄉", "春日鄉", "泰武鄉",
]

# 台灣22縣市清單（正式「臺」寫法），用於從看護機構「服務地區」自由文字欄位以子字串比對方式
# 偵測涵蓋縣市，詳見 build_caregivers()。CAREGIVER_REGION_ALIASES 額外收錄常見「台」簡寫寫法，
# 比對時會先將輸入文字中的「台」正規化為「臺」再比對，故此清單一律使用「臺」。
CAREGIVER_REGIONS = [
    "臺北市", "新北市", "桃園市", "臺中市", "臺南市", "高雄市",
    "基隆市", "新竹市", "新竹縣", "苗栗縣", "彰化縣", "南投縣",
    "雲林縣", "嘉義市", "嘉義縣", "屏東縣", "宜蘭縣", "花蓮縣",
    "臺東縣", "澎湖縣", "金門縣", "連江縣",
]

# 桃園市身心障礙類別、向度之鑑定醫院名冊：17家醫院欄位順序（CSV 表頭欄位名稱，
# 同時也是長格式展開後 hospital 欄位的值），供 build_tyc_disability_hospitals() 使用。
TYC_DISABILITY_HOSPITALS = [
    "衛生福利部桃園醫院",
    "桃園醫院新屋分院",
    "林口長庚紀念醫院",
    "桃園長庚紀念醫院",
    "聯新國際醫院",
    "天晟醫院",
    "天成醫院",
    "聖保祿醫院",
    "臺北榮總桃園分院",
    "居善醫院",
    "衛生福利部桃園療養院",
    "國軍桃園總醫院",
    "敏盛綜合醫院",
    "龍潭敏盛醫院",
    "大園敏盛醫院",
    "怡仁綜合醫院",
    "中壢長榮醫院",
]

# 桃園市長期照護專業服務特約單位「服務類型」啟發式分類規則：依「辦理單位」名稱關鍵字比對，
# 由上到下第一個命中的關鍵字決定分類，非官方分類欄位，僅供篩選/圖表參考用途。
TYLTC_TYPE_RULES = [
    ("居家式服務類機構", "居家式服務類機構"),
    ("職能治療所", "職能治療所"),
    ("物理治療所", "物理治療所"),
    ("護理之家", "護理之家"),
    ("護理站", "護理之家"),
    ("日間照顧", "日間照顧中心"),
    ("治療所", "其他治療所"),
    ("居家", "居家式服務（其他）"),
]

# 宜蘭縣行政區清單，用於補上原始地址欄位缺漏的「宜蘭縣」前綴（部分機構地址僅寫鄉鎮市區名，
# 未包含縣名，例如「羅東鎮站前南路11號」）。
YL_DISTRICTS = [
    "宜蘭市", "羅東鎮", "蘇澳鎮", "頭城鎮", "礁溪鄉", "壯圍鄉", "員山鄉",
    "五結鄉", "冬山鄉", "三星鄉", "大同鄉", "南澳鄉",
]

# 嘉義縣18個鄉鎮市清單，用於從地址欄位解析鄉鎮市（部分機構地址未含「嘉義縣」前綴，
# 例如「竹崎鄉灣橋村石麻園38號」），詳見 build_chiayi_ltc()。
CHIAYI_TOWNSHIPS = [
    "番路鄉", "梅山鄉", "竹崎鄉", "阿里山鄉", "中埔鄉", "大埔鄉", "水上鄉", "鹿草鄉",
    "太保市", "朴子市", "東石鄉", "六腳鄉", "新港鄉", "民雄鄉", "大林鎮", "溪口鄉",
    "義竹鄉", "布袋鎮",
]

# 屏東縣33個鄉鎮市清單，用於從地址欄位解析鄉鎮市（多數機構地址未含「屏東縣」前綴，
# 例如「竹田鄉六巷村太平路70巷20號」），詳見 build_pingtung_ltc()。
PINGTUNG_TOWNSHIPS = [
    "屏東市", "潮州鎮", "東港鎮", "恆春鎮",
    "萬丹鄉", "長治鄉", "麟洛鄉", "九如鄉", "里港鄉", "鹽埔鄉", "高樹鄉", "萬巒鄉",
    "內埔鄉", "竹田鄉", "新埤鄉", "枋寮鄉", "新園鄉", "崁頂鄉", "林邊鄉", "南州鄉",
    "佳冬鄉", "琉球鄉", "車城鄉", "滿州鄉", "枋山鄉", "三地門鄉", "霧台鄉", "瑪家鄉",
    "泰武鄉", "來義鄉", "春日鄉", "獅子鄉", "牡丹鄉",
]

# 服務碼中文全名（8 項專業服務能力，PDF 表頭欄位）
CAPABILITY_LABELS = {
    "ca07": "CA07 復能照護",
    "ca08": "CA08 個別化服務計畫（ISP）擬定與執行",
    "cb01": "CB01 營養照護",
    "cb02": "CB02 進食與吞嚥照護",
    "cb03": "CB03 困擾行為照護",
    "cb04": "CB04 臥床或長期活動受限照護",
    "cc01": "CC01 居家環境安全或無障礙空間規劃",
    "cd02": "CD02 居家護理指導與諮詢",
}

# PDF 內文字因來源字型 cmap 對應問題，部分常見漢字被替換成外觀相同的
# Unicode CJK 部首（Kangxi Radicals / CJK Radicals Supplement）符號，需還原為正常漢字才能顯示。
SPECIALTY_RADICAL_MAP = {
    0x2EA0: "民", 0x2EC4: "西", 0x2F00: "一", 0x2F06: "二", 0x2F08: "人",
    0x2F1D: "口", 0x2F1F: "土", 0x2F20: "士", 0x2F24: "大", 0x2F29: "小",
    0x2F2D: "山", 0x2F3C: "心", 0x2F42: "文", 0x2F47: "日", 0x2F4C: "止",
    0x2F63: "生", 0x2F6F: "石", 0x2F72: "禾", 0x2F8F: "行", 0x2F94: "言",
    0x2FA6: "金", 0x2FBA: "馬",
}

# O_ABC 類別中文說明
CATEGORY_LABELS = {
    "A": "A級 社區整合型服務中心（旗艦店）",
    "B": "B級 複合型服務中心（據點）",
    "C": "C級 巷弄長照站",
}

ADDR_RE = re.compile(r"^(..[市縣])(.*?[市區鄉鎮])")
# 加上「後面不可緊接市/區/鄉/鎮」的否定預查，避免「前鎮區」被非貪婪比對誤判成「前鎮」
# （原 ADDR_RE 在鄉鎮市區名稱中途含有這些字時會提前停止，例如「前鎮區」「平鎮區」）。
ADDR_RE_STRICT = re.compile(r"^(..[市縣])(.*?[市區鄉鎮])(?![市區鄉鎮])")


def fetch(url: str, encoding: str = "utf-8-sig") -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read()
    return raw.decode(encoding, errors="replace")


def fetch_bytes(url: str) -> bytes:
    """與 fetch() 相同，但回傳原始位元組，供二進位格式（如 PDF）解析使用，不做文字解碼。"""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def twd97_to_wgs84(x: float, y: float) -> tuple[float, float]:
    """將 TWD97 TM2 平面座標（EPSG:3826，臺灣政府單位常見的 X/Y 坐標系統）轉換為
    WGS84 經緯度（EPSG:4326）。使用標準橫麥卡托投影反算公式（Redfearn 系列展開），
    GRS80 橢球參數、中央經線 121°E、縮放係數 k0=0.9999、東移(false easting) 250000、
    北移(false northing) 0，為公開通用的地理座標轉換演算法，不依賴任何外部套件。

    回傳 (lat, lng)。
    """
    a = 6378137.0
    b = 6356752.314245
    long0 = math.radians(121)
    k0 = 0.9999
    dx = 250000.0

    e = math.sqrt(1 - (b / a) ** 2)
    x = x - dx
    y = y

    m = y / k0
    mu = m / (a * (1 - e ** 2 / 4 - 3 * e ** 4 / 64 - 5 * e ** 6 / 256))

    e1 = (1 - (1 - e ** 2) ** 0.5) / (1 + (1 - e ** 2) ** 0.5)
    j1 = 3 * e1 / 2 - 27 * e1 ** 3 / 32
    j2 = 21 * e1 ** 2 / 16 - 55 * e1 ** 4 / 32
    j3 = 151 * e1 ** 3 / 96
    j4 = 1097 * e1 ** 4 / 512
    fp = (mu + j1 * math.sin(2 * mu) + j2 * math.sin(4 * mu)
          + j3 * math.sin(6 * mu) + j4 * math.sin(8 * mu))

    e2 = (e * a / b) ** 2
    c1 = e2 * math.cos(fp) ** 2
    t1 = math.tan(fp) ** 2
    r1 = a * (1 - e ** 2) / (1 - e ** 2 * math.sin(fp) ** 2) ** 1.5
    n1 = a / (1 - e ** 2 * math.sin(fp) ** 2) ** 0.5
    d = x / (n1 * k0)

    q1 = n1 * math.tan(fp) / r1
    q2 = d ** 2 / 2
    q3 = (5 + 3 * t1 + 10 * c1 - 4 * c1 ** 2 - 9 * e2) * d ** 4 / 24
    q4 = (61 + 90 * t1 + 298 * c1 + 45 * t1 ** 2 - 3 * c1 ** 2 - 252 * e2) * d ** 6 / 720
    lat = fp - q1 * (q2 - q3 + q4)

    q5 = d
    q6 = (1 + 2 * t1 + c1) * d ** 3 / 6
    q7 = (5 - 2 * c1 + 28 * t1 - 3 * c1 ** 2 + 8 * e2 + 24 * t1 ** 2) * d ** 5 / 120
    lon = long0 + (q5 - q6 + q7) / math.cos(fp)

    return math.degrees(lat), math.degrees(lon)


def parse_county_district(address: str, fallback_county: str = "", strict: bool = False) -> tuple[str, str]:
    m = (ADDR_RE_STRICT if strict else ADDR_RE).match(address or "")
    if m:
        return m.group(1), m.group(2)
    # fallback: try to locate fallback_county text anywhere in the address
    if fallback_county and fallback_county in (address or ""):
        rest = address[address.index(fallback_county) + len(fallback_county):]
        m2 = re.match(r"(.*?[市區鄉鎮])", rest)
        if m2:
            return fallback_county, m2.group(1)
        return fallback_county, ""
    return "", ""


def build_abc():
    print("下載 長照ABC據點 ...", file=sys.stderr)
    text = fetch(ABC_URL)
    reader = csv.DictReader(io.StringIO(text))
    records = []
    county_code_name = {}
    for row in reader:
        addr = row.get("地址全址", "") or ""
        county, district = parse_county_district(addr)
        code = row.get("縣市", "")
        if county and code:
            county_code_name[code] = county
        try:
            lng = float(row.get("經度") or 0)
            lat = float(row.get("緯度") or 0)
        except ValueError:
            lng, lat = 0.0, 0.0
        services = ";".join(s for s in (row.get("特約服務項目", "") or "").split(";") if s)
        cat = (row.get("O_ABC", "") or "").strip()
        records.append([
            row.get("機構名稱", "").strip(),      # 0 name
            row.get("機構代碼", "").strip(),      # 1 code
            cat,                                    # 2 category (A/B/C)
            county,                                 # 3 county
            district,                               # 4 district
            addr,                                   # 5 address
            round(lng, 6),                           # 6 lng
            round(lat, 6),                           # 7 lat
            services,                               # 8 services (';' joined)
            row.get("機構電話", "").strip(),      # 9 phone
            _to_int(row.get("開放床數")),          # 10 bedsOpen
            _to_int(row.get("現有住民")),          # 11 bedsCurrent
            row.get("特約起日", "").strip(),      # 12 contractStart
            row.get("特約迄日", "").strip(),      # 13 contractEnd
            row.get("最後異動時間", "").strip(), # 14 updatedAt
        ])
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["name", "code", "category", "county", "district", "address",
              "lng", "lat", "services", "phone", "bedsOpen", "bedsCurrent",
              "contractStart", "contractEnd", "updatedAt"]
    return {"fields": fields, "categoryLabels": CATEGORY_LABELS, "rows": records}


def build_lane():
    print("下載 巷弄長照站 ...", file=sys.stderr)
    text = fetch(LANE_URL)
    reader = csv.DictReader(io.StringIO(text))
    records = []
    for row in reader:
        addr = (row.get("地址", "") or "").strip()
        # 原始資料偶有錯字（例如「彰化線」）或漏打縣名，統一修正/補上後再解析
        addr_norm = addr.replace("彰化線", "彰化縣")
        if not addr_norm.startswith("彰化"):
            addr_norm = "彰化縣" + addr_norm
        county, district = parse_county_district(addr_norm, fallback_county="彰化縣")
        if not county:
            county = "彰化縣"
        records.append([
            row.get("項目", "").strip(),
            row.get("單位", "").strip(),
            county,
            district,
            addr,
        ])
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["item", "unit", "county", "district", "address"]
    return {"fields": fields, "rows": records}


TYC_DISTRICTS = [
    "桃園區", "中壢區", "平鎮區", "八德區", "楊梅區", "蘆竹區",
    "龜山區", "大溪區", "復興區", "大園區", "觀音區", "新屋區", "龍潭區",
]


TYC_ELDER_GOOGLE_RATINGS_FILE = "data/source/tyc-elder-google-ratings.json"


def build_tyc_elder():
    """桃園市老人福利機構一覽表（桃園市政府開放資料平台，CORS 僅允許該平台網域，改由本腳本下載）。

    額外欄位 google_rating／google_review_count／google_place_id：使用者需求為呈現各機構的
    Google 地圖星等與評論數，且明確表示「一次性資料，之後不會重新抓取」。由於本資料集既有
    `rating` 欄位是桃園市政府「最近1次評鑑成績」（甲/乙/丙），不可與 Google 星等混用同一欄位名，
    故另外開三個 google_ 前綴欄位。

    資料來源：2026-07-26 用 scripts/fetch_google_ratings.py --dataset tyc-elder 一次性呼叫
    Google Places API (Legacy) Text Search，取得 67 筆機構的比對結果後人工核對，整理成
    data/source/tyc-elder-google-ratings.json（key 為「機構名稱」）。人工核對時發現並排除以下
    情況：
    - 「桃園市私立友愛老人長期照顧中心（養護型）」「桃園市私立宥恩老人長期照顧中心（養護型）」
      「桃園市私立友德老人長期照顧中心(養護型)」三筆皆被 API 誤配對到「桃園市私立友緣老人長期
      照顧中心」的 Google 地圖地點（用 Place Details 核對地址後確認地址完全不符，友愛/友德在
      蘆竹區、友緣在龜山區），故排除這三筆，僅保留名稱與地址皆吻合的「友緣」；
    - 2 筆機構 Google 回傳 rating 為 None（無評分資料），亦排除。
    - 「桃園市私立同安老人長期照顧中心(養護型)」與「桃園市私立康健老人長期照顧中心(養護型)」
      經 Place Details 核對地址完全相同（同一棟「新埔七街101號」不同樓層），Google 地圖上是
      同一個地點列表（顯示為「同安/康健」），故兩筆皆保留、共用同一組評分資料。
    查無對照資料的機構，此三欄留空字串，前端顯示為「-」。
    """
    print("下載 桃園市老人福利機構一覽表 ...", file=sys.stderr)
    text = fetch(TYC_ELDER_URL)
    reader = csv.DictReader(io.StringIO(text))
    rows_in = list(reader)

    try:
        with open(TYC_ELDER_GOOGLE_RATINGS_FILE, "r", encoding="utf-8") as f:
            google_ratings = json.load(f)
    except FileNotFoundError:
        google_ratings = {}

    records = []
    for row in rows_in:
        addr = (row.get("地址", "") or "").strip()
        # 地址開頭即為鄉鎮市區（無縣市字首），且共用的 ADDR_RE 對「平鎮區」等
        # 名稱中途含「鎮」字的行政區會誤判，故改用桃園市固定 13 區清單比對。
        district = next((d for d in TYC_DISTRICTS if addr.startswith(d)), "")
        occupants = [s for s in re.split(r"\s+", (row.get("收容對象", "") or "").strip()) if s]
        name = row.get("機構名稱", "").strip()
        g = google_ratings.get(name, {})
        records.append([
            row.get("編號", "").strip(),          # 0 id
            name,                                    # 1 name
            row.get("負責人", "").strip(),        # 2 director
            district,                               # 3 district
            addr,                                   # 4 address
            row.get("電話", "").strip(),          # 5 phone
            ";".join(occupants),                    # 6 occupants (';' joined)
            _to_int(row.get("立案床數")),          # 7 beds
            row.get("最近1次評鑑成績", "").strip(), # 8 rating
            g.get("rating", ""),                    # 9 google_rating（一次性資料，查無留空字串）
            g.get("review_count", ""),              # 10 google_review_count（同上）
            g.get("place_id", ""),                   # 11 google_place_id（同上，用於評論連結）
        ])
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["id", "name", "director", "district", "address", "phone",
              "occupants", "beds", "rating", "google_rating", "google_review_count", "google_place_id"]
    return {"fields": fields, "rows": records}


def build_kcg_homecare():
    """銀髮族服務-居家長照機構（高雄市政府社會局，來源網址無 CORS 標頭，改由本腳本下載）。

    來源 CSV 欄位為 id、lat、lng、informaddress、hlink、informtel、servItem、servTime、
    dataOrg、doOrg、text；經檢查 hlink／doOrg 全數為空字串，不具資訊價值故不收錄。
    """
    print("下載 銀髮族服務-居家長照機構 ...", file=sys.stderr)
    text = fetch(KCG_HOMECARE_URL)
    reader = csv.DictReader(io.StringIO(text))
    records = []
    for row in reader:
        addr = (row.get("informaddress", "") or "").strip()
        _county, district = parse_county_district(addr, strict=True)
        # 電話欄位偶有跨行的多組號碼/分機備註，統一以 " / " 合併成單行
        phone_lines = [p.strip() for p in (row.get("informtel", "") or "").splitlines() if p.strip()]
        phone = " / ".join(phone_lines)
        try:
            lng = float(row.get("lng") or 0)
            lat = float(row.get("lat") or 0)
        except ValueError:
            lng, lat = 0.0, 0.0
        records.append([
            row.get("id", "").strip(),            # 0 id
            row.get("text", "").strip(),           # 1 name
            district,                                # 2 district
            addr,                                    # 3 address
            phone,                                   # 4 phone
            row.get("servItem", "").strip(),       # 5 servItem
            row.get("servTime", "").strip(),       # 6 servTime
            round(lng, 6),                           # 7 lng
            round(lat, 6),                           # 8 lat
        ])
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["id", "name", "district", "address", "phone",
              "servItem", "servTime", "lng", "lat"]
    return {"fields": fields, "rows": records}


def build_hsc_ltc():
    """新竹縣長照機構名冊（新竹縣政府社會處，來源網址無 CORS 標頭，改由本腳本下載）。

    來源為 JSON 陣列，欄位為編號、服務類型、機構名稱、郵遞區號、地址、電話、分機；
    原始地址欄位有「新鋪鎮」應為「新埔鎮」的錯字（新竹縣僅有「新埔鎮」），此處先修正後再解析鄉鎮市區。
    """
    print("下載 新竹縣長照機構名冊 ...", file=sys.stderr)
    text = fetch(HSC_LTC_URL)
    rows_in = json.loads(text)
    records = []
    for row in rows_in:
        addr = (row.get("地址", "") or "").strip().replace("新鋪鎮", "新埔鎮")
        _county, district = parse_county_district(addr)
        phone = (row.get("電話", "") or "").strip()
        ext = (row.get("分機", "") or "").strip()
        if ext:
            phone = f"{phone} 轉 {ext}"
        records.append([
            row.get("編號", "").strip(),           # 0 id
            row.get("服務類型", "").strip(),       # 1 servType
            row.get("機構名稱", "").strip(),       # 2 name
            row.get("郵遞區號", "").strip(),       # 3 zipcode
            district,                                 # 4 district
            addr,                                     # 5 address
            phone,                                    # 6 phone
        ])
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["id", "servType", "name", "zipcode", "district", "address", "phone"]
    return {"fields": fields, "rows": records}


def _hsc_denture_type(name: str) -> str:
    return "醫院" if "醫院" in name else "牙醫診所"


def build_hsc_denture():
    """新竹縣中低收入老人補助裝置假牙特約醫療院所（DCAT dataset id 109330，
    https://data.gov.tw/dataset/8572，提供機關：新竹縣政府社會處）。

    來源：HSC_DENTURE_URL（JSON 格式，共4種格式中選用 JSON，因 CSV 為 BIG5 編碼較麻煩、JSON 為
    UTF-8 且欄位與 description 一致），來源網址無 CORS 標頭，改由本腳本於伺服器端下載。

    實測欄位：名稱／負責人／郵遞區號33／地址／電話，共**僅7筆**（美利堅牙醫診所、湖口仁慈醫院(地區)、
    范牙醫診所、柏齡牙醫診所、啟清牙醫診所、田牙醫診所、台北榮民總醫院新竹分院(地區)），資料量小屬
    原始公告名冊範圍，如實呈現非解析遺漏。

    地址欄位格式為「郵遞區號＋鄉鎮市名稱＋路名門牌」（如「310004竹東鎮仁愛路250號」），**不含「新竹縣」
    字首**，與同網域 build_hsc_ltc() 的來源（地址已含「新竹縣」字首）不同；本函式先用正規表達式移除
    開頭的郵遞區號數字，再補上「新竹縣」前綴後用 parse_county_district(fallback_county="新竹縣")
    解析鄉鎮市，比照 build_lane() 的 fallback 模式；表格顯示仍保留原始地址文字（含郵遞區號開頭），
    僅在轉 Google Maps 連結時才使用補上「新竹縣」的完整地址。

    「機構類型」由 _hsc_denture_type() 依名稱是否含「醫院」關鍵字啟發式判斷（如「湖口仁慈醫院(地區)」
    「台北榮民總醫院新竹分院(地區)」歸類「醫院」），其餘歸類「牙醫診所」，非官方分類欄位。無經緯度
    座標，故本頁不含地圖。
    """
    print("下載 新竹縣中低收入老人補助裝置假牙特約醫療院所 ...", file=sys.stderr)
    text = fetch(HSC_DENTURE_URL)
    rows_in = json.loads(text)
    records = []
    for i, row in enumerate(rows_in, start=1):
        addr = (row.get("地址", "") or "").strip()
        addr_no_zip = re.sub(r"^\d+", "", addr)
        addr_norm = "新竹縣" + addr_no_zip
        _county, district = parse_county_district(addr_norm, fallback_county="新竹縣")
        name = row.get("名稱", "").strip()
        records.append([
            i,                              # 0 id
            district,                        # 1 district
            name,                            # 2 name
            _hsc_denture_type(name),         # 3 type
            row.get("負責人", "").strip(), # 4 owner
            addr,                            # 5 address
            row.get("電話", "").strip(),   # 6 phone
        ])
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["id", "district", "name", "type", "owner", "address", "phone"]
    return {"fields": fields, "rows": records}


CHC_DENTURE_GOOGLE_RATINGS_FILE = "data/source/chc-denture-google-ratings.json"

TC_DENTURE_GOOGLE_RATINGS_FILE = "data/source/tc-denture-google-ratings.json"


def build_chc_denture():
    """彰化縣補助65歲以上老人裝置全口假牙契約診所名冊（DCAT dataset id 31787，
    https://data.gov.tw/dataset/8572，提供機關：彰化縣政府社會處長青福利科，承辦：謝社工
    04-7532353）。

    來源 CHC_DENTURE_URL 僅提供一種格式（CSV），且該 CSV 為 **BIG5 編碼**（非本專案常見的 UTF-8），
    需以 fetch(url, encoding="big5") 解碼；來源網址無 CORS 標頭，改由本腳本於伺服器端下載。

    實測欄位：診所名稱／電話／地址縣市／地址，共 **109 筆**，診所名稱無重複。「地址縣市」欄位實測
    109 筆恆為常數 "10007"（縣市代碼），無篩選意義，本函式不輸出此欄位。

    「地址」欄位格式為「鄉鎮市名稱＋路名門牌」（如「彰化市三民路49號」「鹿港鎮民權路...」），**不含
    「彰化縣」字首**，且彰化縣轄下26鄉鎮市皆為市/鎮/鄉，無「區」層級，故不使用共用的
    parse_county_district()（其 fallback 模式需比對 fallback_county 文字本身存在於地址中，但此處
    地址完全不含「彰化縣」三字，無法比對），改用簡化正規表達式 `^(.{2,3}[市鎮鄉])` 直接從地址開頭
    抽取鄉鎮市名稱，county 固定為「彰化縣」。實測涵蓋23個鄉鎮市（彰化縣共26鄉鎮市，其餘3個鄉鎮市
    無契約診所，如實呈現不強行補列）。

    資料本身無機構類型／分類欄位，且109筆診所名稱皆為「XX牙醫診所」「XX牙科診所」型態，未見「醫院」
    關鍵字案例（與 hsc-denture／chiayi-denture 不同），故本資料集不新增推斷 type 欄位。無經緯度
    座標，故本頁不含地圖。

    額外欄位 google_rating／google_review_count／google_place_id：使用者需求為呈現各診所的
    Google 地圖星等與評論數，且明確表示為一次性資料，之後不會重新抓取。資料來源：2026-08-05 用
    scripts/fetch_google_ratings.py --dataset chc-denture 一次性呼叫 Google Places API (Legacy)
    Text Search，109 筆全數比對成功（status=OK），整理成
    data/source/chc-denture-google-ratings.json（key 為「診所名稱」）。人工核對時特別確認以下
    容易誤判的案例，皆核對地址後確認比對正確：
    - 「彰化秀傳紀念醫院」「彰化基督教醫院」「鹿港基督教醫院」「彰濱秀傳紀念醫院」「衛生福利部彰化
      醫院」「二林基督教醫院」「道周醫院」等機構的 Google 地點名稱為英文（如「Show Chwan Memorial
      Hospital」「Farlin Hospital」），核對 Place Details 回傳地址與原始資料地址完全一致，確認為
      同一地點，僅顯示名稱不同。
    - 「秀安牙醫診所(聯合)」與「秀欣牙醫診所(聯合)」地址與電話完全相同（秀水鄉彰水路二段510號，
      (04)7687207），Google 地圖上為同一地點（顯示為「秀欣聯合牙醫診所」），比照 tyc-elder 案例
      的處理方式，兩筆皆保留、共用同一組評分資料。
    查無對照資料的診所，此三欄留空字串，前端顯示為「-」（本次 109 筆全數有對照資料，故實務上不會
    出現空值，僅為程式穩健性保留）。
    """
    print("下載 彰化縣補助65歲以上老人裝置全口假牙契約診所名冊 ...", file=sys.stderr)
    text = fetch(CHC_DENTURE_URL, encoding="big5")
    reader = csv.DictReader(io.StringIO(text))

    try:
        with open(CHC_DENTURE_GOOGLE_RATINGS_FILE, "r", encoding="utf-8") as f:
            google_ratings = json.load(f)
    except FileNotFoundError:
        google_ratings = {}

    records = []
    for i, row in enumerate(reader, start=1):
        addr = (row.get("地址", "") or "").strip()
        m = re.match(r"^(.{2,3}[市鎮鄉])", addr)
        district = m.group(1) if m else ""
        name = (row.get("診所名稱", "") or "").strip()
        g = google_ratings.get(name, {})
        records.append([
            i,                                    # 0 id
            district,                              # 1 district
            name,                                   # 2 name
            addr,                                   # 3 address
            (row.get("電話", "") or "").strip(),   # 4 phone
            g.get("rating", ""),                    # 5 google_rating（一次性資料，查無留空字串）
            g.get("review_count", ""),              # 6 google_review_count（同上）
            g.get("place_id", ""),                   # 7 google_place_id（同上，用於評論連結）
        ])
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["id", "district", "name", "address", "phone",
              "google_rating", "google_review_count", "google_place_id"]
    return {"fields": fields, "rows": records}


def build_tc_denture():
    """臺中市115年度65歲以上銀髮族假牙裝置補助計畫合約院所名單（臺中市政府衛生局公告，
    「假牙裝置補助管理暨查詢系統」相關計畫）。

    **資料來源特殊性（務必先讀）**：此名單無公開的機器可讀下載網址（非 DCAT CSV/API、亦非可直接
    fetch 的公告 PDF），使用者係手動於 Google 試算表（原始檔名「65歲以上銀髮族假牙裝置補助計畫合約
    院所名單-統計至115年07月30日」）匯出為 CSV 後提供，故本函式**讀取本地已清理過的 CSV 檔案**
    （TC_DENTURE_CSV = scripts/sources/tc-denture/tc-denture.csv，已移除原始檔案第一列的標題文字，
    保留表頭列＋281筆資料列），比照 build_caregivers()／build_dialysis_transport() 的作法，非向遠端
    URL 下載。日後如需更新（如次年度116年版），需人工取得新版試算表匯出 CSV 覆蓋此檔案後，重新執行
    `python3 scripts/build_data.py tc-denture`，**無法自動重新抓取**。

    實測欄位：編號、區域、診所名稱、地址、電話，共 **281 筆**，編號為 1~281 連續整數無缺漏無重複。
    「區域」欄位本身已是乾淨的「臺中市OO區」去除縣市字首後的行政區名稱（如「中區」「東區」），與地址
    欄位開頭一致，直接當作 district 使用，不需另外解析；county 固定為「臺中市」（不存於資料欄位，
    比照 chc-denture／chiayi-denture 僅存 district，前端寫死顯示「臺中市」）。涵蓋臺中市29個行政區
    （太平區/大甲區/大安區/大里區/大肚區/大雅區/北屯區/北區/南屯區/南區/和平區/后里區/沙鹿區/烏日區/
    石岡區/神岡區/清水區/潭子區/東勢區/東區/梧棲區/西屯區/西區/豐原區/霧峰區/龍井區/中區 等，實測未見
    新社區、外埔區資料，如實呈現不強行補列）。無官方「機構類型」分類欄位，且原始資料未要求分類，不比照
    build_tyc_denture()/build_kcg_denture() 做啟發式推斷。無經緯度座標，故本頁不含地圖。

    額外欄位 google_rating／google_review_count／google_place_id：比照 tyc-denture／chc-denture／
    tyc-elder 的作法，呈現各診所的 Google 地圖星等與評論數，且為一次性資料、之後不會重新抓取。2026-
    08-06 用 `scripts/fetch_google_ratings.py --dataset tc-denture` 一次性呼叫 Google Places API
    (Legacy) Text Search，281 筆全數比對成功（status=OK），整理成
    data/source/tc-denture-google-ratings.json（key 為「診所名稱」）。人工核對時特別抽查「比對名稱
    與原始名稱差異較大」的案例（21 筆純英譯名稱如「Cheng Ching Hospital」「Taichung Veterans
    General Hospital」，以及 3 筆中文名稱不同的案例），逐筆以 Place Details 回傳地址核對門牌號碼：
    - 21 筆英譯名稱：地址門牌完全一致，確認為同一地點，僅顯示名稱為英文。
    - 「汎宇牙醫診所」比對到「dentict Hospital 聯強牙醫診所」、「沙鹿張牙醫診所」比對到「張牙醫
      診所」：地址門牌完全一致，確認為同一地點（可能為診所更名或多醫師掛牌），予以保留。
    - 「東興陳牙醫診所」比對到「陳尚德牙醫診所」：原始地址「南屯路二段616號」與 Google 回傳地址
      「南屯路二段663號」門牌不符，判定為**不同地點的誤配對**，予以排除，此筆三欄留空字串。
    因此最終 280 筆（281 筆扣除上述誤配對 1 筆）有對照資料，1 筆查無/排除資料此三欄留空字串，
    前端顯示為「-」。
    """
    print("讀取 臺中市65歲以上銀髮族假牙裝置補助計畫合約院所 本地 CSV ...", file=sys.stderr)
    with open(TC_DENTURE_CSV, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    try:
        with open(TC_DENTURE_GOOGLE_RATINGS_FILE, "r", encoding="utf-8") as f:
            google_ratings = json.load(f)
    except FileNotFoundError:
        google_ratings = {}

    records = []
    for row in rows:
        rid = (row.get("編號", "") or "").strip()
        if not rid.isdigit():
            continue  # 跳過非資料列（防禦性處理，正式資料應皆為純數字編號）
        name = (row.get("診所名稱", "") or "").strip()
        g = google_ratings.get(name, {})
        records.append([
            int(rid),                               # 0 id
            (row.get("區域", "") or "").strip(),    # 1 district
            name,                                    # 2 name
            (row.get("地址", "") or "").strip(),    # 3 address
            (row.get("電話", "") or "").strip(),    # 4 phone
            g.get("rating", ""),                     # 5 google_rating（一次性資料，查無留空字串）
            g.get("review_count", ""),               # 6 google_review_count（同上）
            g.get("place_id", ""),                    # 7 google_place_id（同上，用於評論連結）
        ])
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["id", "district", "name", "address", "phone",
              "google_rating", "google_review_count", "google_place_id"]
    return {"fields": fields, "rows": records}


def _hl_denture_type(name: str) -> str:
    if "醫院" in name:
        return "醫院"
    if "衛生所" in name:
        return "衛生所"
    return "牙醫診所"


def build_hl_denture():
    """花蓮縣115年度65歲以上長者假牙補助實施計畫－合約醫療院所公開名單（花蓮縣政府社會處公告）。

    **資料來源特殊性（務必先讀）**：使用者手動提供三份本機 PDF（皆非公開可下載之開放資料 CSV/API，
    亦非有效可直接 fetch 的公告網址），已複製存放於 scripts/sources/hl-denture/：
    - institution-list.pdf：機構名單（原檔名「202606051032215377261.pdf」），本函式解析對象
    - flowchart.pdf：附件四申請流程圖，已另用 pdftoppm 轉存為 hl-denture/flowchart.jpg（比照
      yl-denture／chiayi-denture 的做法），供前端頁面內嵌顯示，本函式不處理該圖片
    - qa.pdf：醫療院所申請假牙補助常見問答（Q&A），內容為純文字說明（5大類約20題），已人工整理
      寫入 hl-denture/index.html 的 FAQ 區塊，本函式不解析此檔案
    日後如需更新名單，需人工取得新版 PDF 覆蓋 institution-list.pdf 後重新執行
    `python3 scripts/build_data.py hl-denture`，**無法自動重新下載**。

    表格表頭為「區域、編號、醫事機構名稱、電話、地址」，共 37 筆，編號 1~37 連續無缺漏。原始表格
    「區域」欄位為合併儲存格樣式（僅該區域第一列有值，同區域後續列為空/None），本函式做「向下延續」
    （forward-fill）處理，取每列實際所屬區域文字。「醫事機構名稱」欄位多筆因原始表格跨行斷字含換行
    符號（如「佛教慈濟醫療財團法人花\n蓮慈濟醫院」），本函式移除換行符號後還原成完整名稱。

    county／district 一律用 parse_county_district() 由「地址」欄位解析而來，不直接採用/寫死表格的
    「區域」欄位文字，因為：(1) 第37筆「合諧牙醫診所」地址為「臺東縣池上鄉忠孝路365號」，是跨縣市
    特約診所（區域欄位本身也直接寫「臺東縣」而非鄉鎮市名稱），如比照 yl-denture 對跨縣市案例的處理
    原則，忠實呈現實際地址對應的縣市／鄉鎮市，不強行歸類為花蓮縣；(2) 其餘36筆地址皆已含完整
    「花蓮縣OO市/鄉/鎮」字首，可直接解析，兩者結果一致，僅第37筆會不同。

    「機構類型」由 _hl_denture_type() 依名稱是否含「醫院」「衛生所」關鍵字啟發式判斷，其餘歸類
    「牙醫診所」，非官方分類欄位。無經緯度座標，故本頁不含地圖。

    額外欄位 google_rating／google_review_count／google_place_id：使用者需求為呈現各院所的 Google
    地圖星等與評論數，且明確表示為一次性資料，之後不會重新抓取。資料來源：2026-08-08 用
    scripts/fetch_google_ratings.py --dataset hl-denture 一次性呼叫 Google Places API (Legacy)
    Text Search，37 筆全數比對成功（status=OK），整理成
    data/source/hl-denture-google-ratings.json（key 為「醫事機構名稱」）。人工核對時特別確認以下
    容易誤判的案例，皆用 Place Details 核對地址後確認比對正確：
    - 醫院類機構多筆顯示英文地點名稱（如「衛生福利部花蓮醫院」比對到「Hualien Hospital, Ministry
      of Health and Welfare」、「衛生福利部玉里醫院」比對到「Yuli Hospital, Ministry of Health and
      Welfare」等），核對 Place Details 回傳地址與原始地址一致，確認為同一機構。
    - 「天祥牙醫診所」比對到「天祥牙科」、「政安牙醫診所」比對到「Jengan's Dental Clinic」、
      「微笑牙醫診所」比對到「Smiles-Dental」：皆核對地址門牌一致，確認僅顯示名稱不同，非誤配對。
    查無對照資料的院所，此三欄留空字串，前端顯示為「-」（本次 37 筆全數有對照資料，故實務上不會
    出現空值，僅為程式穩健性保留）。
    """
    print("讀取 花蓮縣65歲以上長者假牙補助合約醫療院所名單 本地 PDF ...", file=sys.stderr)
    import pdfplumber  # 延遲載入：僅此資料集需要，避免其他資料集重跑時強制安裝

    try:
        with open(HL_DENTURE_GOOGLE_RATINGS_FILE, "r", encoding="utf-8") as f:
            google_ratings = json.load(f)
    except FileNotFoundError:
        google_ratings = {}

    records = []
    with pdfplumber.open(HL_DENTURE_PDF) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                current_region = ""
                for row in table:
                    row = row + [""] * (5 - len(row))
                    region_col, rid, name, phone, addr = row[:5]
                    rid = (rid or "").strip()
                    if not rid.isdigit():
                        continue  # 跳過表頭列（編號欄為「編號」文字）
                    if region_col and region_col.strip():
                        current_region = region_col.strip()
                    name = (name or "").replace("\n", "").strip()
                    phone = (phone or "").replace("\n", "").strip()
                    addr = (addr or "").replace("\n", "").strip()
                    county, district = parse_county_district(addr, fallback_county="花蓮縣")
                    g = google_ratings.get(name, {})
                    records.append([
                        int(rid),                     # 0 id
                        county or "",                  # 1 county
                        district or current_region,    # 2 district
                        name,                          # 3 name
                        _hl_denture_type(name),        # 4 type
                        addr,                           # 5 address
                        phone,                          # 6 phone
                        g.get("rating", ""),                # 7 google_rating（一次性資料，查無留空字串）
                        g.get("review_count", ""),          # 8 google_review_count（同上）
                        g.get("place_id", ""),               # 9 google_place_id（同上，用於評論連結）
                    ])
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["id", "county", "district", "name", "type", "address", "phone",
              "google_rating", "google_review_count", "google_place_id"]
    return {"fields": fields, "rows": records}


def _pingtung_denture_district(address: str) -> str:
    """從屏東縣假牙補助地址解析行政區，見 PINGTUNG_DISTRICTS 常數說明。"""
    rest = address[3:] if address.startswith("屏東縣") else address
    for d in sorted(PINGTUNG_DISTRICTS, key=len, reverse=True):
        if rest.startswith(d):
            return d
    return ""


def _pingtung_denture_type(name: str) -> str:
    if "醫院" in name:
        return "醫院"
    if "衛生所" in name:
        return "衛生所"
    if "醫療站" in name or "服務中心" in name or "活動中心" in name:
        return "醫療站"
    return "牙醫診所"


def build_pingtung_denture():
    """115年屏東縣補助長者假牙裝置合作醫療院所名冊（屏東縣政府衛生局醫政科公告，115.3.18更新）。

    **資料來源特殊性（務必先讀）**：使用者手動提供本機 PDF（非公開可下載之開放資料 CSV/API，亦非
    有效可直接 fetch 的公告網址），已複製存放於 PINGTUNG_DENTURE_PDF
    （scripts/sources/pingtung-denture/institution-list.pdf）。此 PDF 文字為可選取的一般文字
    （非向量繪製曲線圖形），pdfplumber 可直接用 extract_tables() 取得乾淨表格，不需比照
    build_kcg_denture() 的「渲染成圖片 + AI 視覺閱讀」流程。日後如需更新名冊，需人工取得新版 PDF
    覆蓋 institution-list.pdf 後重新執行 `python3 scripts/build_data.py pingtung-denture`，
    **無法自動重新下載**。

    PDF 共2頁，內含**3個表格**（pdfplumber 因跨頁與版面切斷偵測為3個 table 物件，但邏輯上是連續的
    2大段落）：
    - 第1段「醫療院所」：序號1~59，欄位「序號、醫療院所、地址、電話」，含4家醫院
      （衛生福利部屏東醫院、屏東榮民總醫院、國軍高雄總醫院屏東分院附設民眾診療服務處、
      屏基醫療財團法人屏東基督教醫院、恆基醫療財團法人恆春基督教醫院、衛生福利部恆春旅遊醫院）
      與大量牙醫診所。
    - 第2段「醫療站」：序號1~7（PDF 內獨立重新從1編號），欄位同上，涵蓋牙科醫療站、鄉衛生所、
      活動中心、公共服務中心等非典型診所據點（如「禮納里公共服務中心」「滿州鄉活動中心」）。
    本函式將兩段合併，新增 `category` 欄位（`特約醫療院所`／`醫療站`）忠實保留 PDF 原始分類，並
    依出現順序重新連續編號 1~66（不保留 PDF 內兩段各自從1開始的原始序號，避免前端誤以為是同一組
    序號體系）。「醫療院所」欄位偶有跨行斷字換行符號（如「國軍高雄總醫院屏東分院附設民眾\n診療
    服務處」），移除換行符號還原成完整名稱；「電話」欄位少數含分機（如「08-7557885#84457」），
    原文照登。

    county／district：地址欄位格式不一致——多數「屏東縣OO鄉/鎮」已含完整縣名字首，但「屏東市」
    本身（縣治所在，作為屏東縣的一個市轄區）在原始地址中**不會**再加「屏東縣」字首（如「屏東市
    自由路270號」），若沿用既有 parse_county_district(fallback_county="屏東縣") 會因地址不含
    字面「屏東縣」三字而解析失敗，故改用固定行政區清單 PINGTUNG_DISTRICTS（比照 build_tyc_elder()
    的 TYC_DISTRICTS 做法）：county 固定輸出「屏東縣」，district 由 _pingtung_denture_district()
    比對取得，實測 66 筆全數成功解析（無空值）。

    「機構類型」（type）由 _pingtung_denture_type() 依名稱關鍵字（醫院／衛生所／醫療站相關字樣）
    啟發式判斷，其餘歸類「牙醫診所」，非官方分類欄位；與 category 為兩個獨立維度（category 是
    PDF 原始段落分類，type 是名稱關鍵字啟發式推斷的機構性質，兩者不必然一致，例如「醫療站」段落
    內的「獅子鄉衛生所」category=醫療站 但 type=衛生所）。無經緯度座標，故本頁不含地圖。

    額外欄位 google_rating／google_review_count／google_place_id：使用者需求為呈現各院所的
    Google 地圖星等與評論數，且明確表示為一次性資料，之後不會重新抓取。資料來源：2026-08-08 用
    scripts/fetch_google_ratings.py --dataset pingtung-denture --name-field name
    --address-field address 一次性呼叫 Google Places API (Legacy) Text Search，整理成
    data/source/pingtung-denture-google-ratings.json（key 為「醫療院所」名稱）。查無對照資料或
    人工核對排除誤配對的院所，此三欄留空字串，前端顯示為「-」。
    """
    print("讀取 屏東縣115年長者假牙裝置補助合作醫療院所名冊 本地 PDF ...", file=sys.stderr)
    import pdfplumber  # 延遲載入：僅此資料集需要，避免其他資料集重跑時強制安裝

    try:
        with open(PINGTUNG_DENTURE_GOOGLE_RATINGS_FILE, "r", encoding="utf-8") as f:
            google_ratings = json.load(f)
    except FileNotFoundError:
        google_ratings = {}

    tables = []
    with pdfplumber.open(PINGTUNG_DENTURE_PDF) as pdf:
        for page in pdf.pages:
            tables.extend(page.extract_tables())

    records = []
    seq = 0
    for table_idx, table in enumerate(tables):
        # 3個 table 物件依序對應：第1、2個屬於「醫療院所」段落（PDF 跨頁被切成兩個 table），
        # 第3個是「醫療站」段落（各自從序號1開始，故用「序號重新從1出現」偵測段落邊界較不穩健，
        # 改直接用 table_idx 判斷，與實測結果一致）。
        category = "醫療站" if table_idx == len(tables) - 1 else "特約醫療院所"
        for row in table:
            row = row + [""] * (4 - len(row))
            rid, name, addr, phone = row[:4]
            rid = (rid or "").strip()
            if not rid.isdigit():
                continue  # 跳過表頭列（序號欄為「序號」文字）
            name = (name or "").replace("\n", "").strip()
            addr = (addr or "").replace("\n", "").strip()
            phone = (phone or "").replace("\n", "").strip()
            district = _pingtung_denture_district(addr)
            seq += 1
            g = google_ratings.get(name, {})
            records.append([
                seq,                             # 0 id（合併兩段後重新連續編號）
                category,                         # 1 category（特約醫療院所／醫療站）
                "屏東縣",                          # 2 county
                district,                           # 3 district
                name,                                # 4 name
                _pingtung_denture_type(name),         # 5 type（啟發式）
                addr,                                  # 6 address
                phone,                                  # 7 phone
                g.get("rating", ""),                     # 8 google_rating（一次性資料，查無留空字串）
                g.get("review_count", ""),                # 9 google_review_count（同上）
                g.get("place_id", ""),                     # 10 google_place_id（同上，用於評論連結）
            ])
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["id", "category", "county", "district", "name", "type", "address", "phone",
              "google_rating", "google_review_count", "google_place_id"]
    return {"fields": fields, "rows": records}


def _chiayi_denture_type(name: str) -> str:
    return "醫院" if "醫院" in name else "牙醫診所"


def build_chiayi_denture():
    """嘉義市假牙補助合約醫療院所，合併兩個各自獨立的補助方案（合約診所名單有重疊但不完全相同，
    刻意不做名稱比對合併，各自保留來源方案標記，如實呈現原始資料差異）：

    1.「中低收入老人免費裝置假牙合約醫院名單」（DCAT dataset https://data.gov.tw/dataset/8572，
       https://cms.data.gov.tw/dataset/130486，提供機關：嘉義市政府社會處）。
       來源 CHIAYI_DENTURE_LOW_INCOME_URL 為 CSV（逗號分隔＋引號包欄位，UTF-8），實測欄位為
       「序號,診所名稱,電話,地址,經度,緯度」，共 **27 筆，含經緯度座標**。地址已含「嘉義市東區/
       西區」字首，可直接用 parse_county_district() 解析，不需 fallback。無 CORS 標頭，改由本腳本
       於伺服器端下載。

    2.「115年度一般身分別老人補助裝置假牙合約院所」（嘉義市政府社會處長青及社會行政科公告 PDF，
       非 DCAT 開放資料，僅有 CHIAYI_DENTURE_GENERAL_PDF_URL 這個公告附件連結，未來若連結失效需
       重新至嘉義市政府社會處公告頁面尋找最新 PDF）。用 pdfplumber 解析單頁表格，欄位為
       「序號、診所名稱、地址、電話」，共 **29 筆，無經緯度座標**。PDF 文字每個中文字之間夾雜空白
       （如「誠 一 牙 醫 診 所」「嘉義市東區光彩街 400 號」），一律用 re.sub(r"\\s+", "", ...) 移除
       所有空白正規化。最後一筆「臺中榮民總醫院嘉義分院」的名稱／電話欄位跨兩行儲存格，換行以
       "".join(...) 方式合併（電話含「轉5786」分機文字，不強行拆解格式，比照其餘資料集分機表示法
       原樣保留）。地址同樣已含「嘉義市東區/西區」字首可直接解析。

    兩方案的「機構類型」皆由 _chiayi_denture_type() 依名稱是否含「醫院」二字啟發式判斷（僅
    臺中榮民總醫院嘉義分院歸類「醫院」，其餘歸類「牙醫診所」），非官方分類欄位。合併後統一重新
    編號 id（1..N，跨兩方案連續編號，不沿用個別來源的序號)，並用 program 欄位標記「中低收入」／
    「一般身分別」供前端篩選；一般身分別方案無座標，故該部分列不會出現在地圖上，僅在表格/統計/
    圖表呈現，詳見 chiayi-denture/app.js 的地圖繪製邏輯。

    人工補登（CHIAYI_DENTURE_LOW_INCOME_ADDED_20260601）：依「115年度「中低收入老人」補助裝置
    假牙計畫」公告文字，115年6月1日起新增杏林牙醫診所、劍橋牙醫診所、大明牙醫診所3家為「中低收入」
    方案合約診所，但 CHIAYI_DENTURE_LOW_INCOME_URL 的官方開放資料 CSV 截至本次建置時尚未反映此
    異動（仍僅27筆，不含此3家）。這3家診所本來就已存在於「一般身分別」方案名單中（地址/電話取自
    該來源），故不重新下載，改為在合併資料時，對這3個名稱各自「複製」一筆一般身分別的列並改標記
    program 為「中低收入」（無座標，因複製來源本身無座標欄位），原本的「一般身分別」列予以保留、
    不刪除，如實呈現該診所同時服務兩方案的狀態。未來若官方 CSV 已更新納入這3家，此人工補登邏輯
    應改為直接依 CSV 判斷是否重複，避免出現兩筆一模一樣的「中低收入」列（屆時需手動移除本段落）。
    """
    print("下載 嘉義市中低收入老人免費裝置假牙合約醫院名單 ...", file=sys.stderr)
    records = []
    idx = 0

    low_income_text = fetch(CHIAYI_DENTURE_LOW_INCOME_URL)
    reader = csv.DictReader(io.StringIO(low_income_text))
    for row in reader:
        addr = (row.get("地址", "") or "").strip()
        county, district = parse_county_district(addr)
        name = (row.get("診所名稱", "") or "").strip()
        lat_raw = (row.get("緯度", "") or "").strip()
        lng_raw = (row.get("經度", "") or "").strip()
        idx += 1
        records.append([
            idx,                                   # 0 id
            "中低收入",                             # 1 program
            district,                               # 2 district
            name,                                   # 3 name
            _chiayi_denture_type(name),             # 4 type
            addr,                                   # 5 address
            (row.get("電話", "") or "").strip(),  # 6 phone
            float(lat_raw) if lat_raw else "",       # 7 lat
            float(lng_raw) if lng_raw else "",       # 8 lng
        ])
    low_income_count = idx
    print(f"  共 {low_income_count} 筆", file=sys.stderr)

    print("下載 嘉義市115年度一般身分別老人補助裝置假牙合約院所 PDF ...", file=sys.stderr)
    import pdfplumber  # 延遲載入：僅此資料集需要，避免其他資料集重跑時強制安裝

    pdf_bytes = fetch_bytes(CHIAYI_DENTURE_GENERAL_PDF_URL)
    general_count = 0
    added_low_income_patch = []  # 115/6/1 起人工補登為「中低收入」方案的複製列，詳見函式 docstring
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                for row in table:
                    # 實測本表格共5欄：序號/診所名稱/地址/(空白，版面產生的多餘欄位)/電話，
                    # 第4欄（index 3）恆為 None，電話在 index 4，需以此為準，不可只補到4欄。
                    row = row + [""] * (5 - len(row))
                    rid_raw = re.sub(r"\s+", "", row[0] or "")
                    if not rid_raw.isdigit():
                        continue  # 跳過表頭列（序號欄位為「序號」文字）
                    name = re.sub(r"\s+", "", row[1] or "")
                    addr = re.sub(r"\s+", "", row[2] or "")
                    phone = re.sub(r"\s+", "", row[4] or "")
                    county, district = parse_county_district(addr)
                    idx += 1
                    general_count += 1
                    records.append([
                        idx,                          # 0 id
                        "一般身分別",                  # 1 program
                        district,                      # 2 district
                        name,                          # 3 name
                        _chiayi_denture_type(name),    # 4 type
                        addr,                           # 5 address
                        phone,                          # 6 phone
                        "",                             # 7 lat（此方案來源無座標）
                        "",                             # 8 lng
                    ])
                    if name in CHIAYI_DENTURE_LOW_INCOME_ADDED_20260601:
                        added_low_income_patch.append([district, name, addr, phone])
    print(f"  共 {general_count} 筆", file=sys.stderr)

    if added_low_income_patch:
        print(f"  人工補登 115/6/1 起新增為中低收入方案合約診所 {len(added_low_income_patch)} 筆", file=sys.stderr)
        for district, name, addr, phone in added_low_income_patch:
            idx += 1
            records.append([
                idx,                          # 0 id
                "中低收入",                    # 1 program（人工補登，官方 CSV 尚未更新，見 docstring）
                district,                      # 2 district
                name,                          # 3 name
                _chiayi_denture_type(name),    # 4 type
                addr,                           # 5 address
                phone,                          # 6 phone
                "",                             # 7 lat（來源複製自無座標的一般身分別列）
                "",                             # 8 lng
            ])

    print(f"  合計 {len(records)} 筆", file=sys.stderr)
    fields = ["id", "program", "district", "name", "type", "address", "phone", "lat", "lng"]
    return {"fields": fields, "rows": records}


def build_yl_ltc():
    """宜蘭縣立案老人長期照顧及安養機構名冊（宜蘭縣政府，來源網址無 CORS 標頭，改由本腳本下載）。

    來源為 JSON 陣列，欄位為編號、機構名稱、負責人、電話、傳真、地址。
    部分地址欄位缺少「宜蘭縣」前綴，先嘗試依已知鄉鎮市區名稱補上前綴後再解析。
    機構類型由機構名稱結尾括號內文字解析（如「(養護型)」），無標示者歸類為「未標示」。
    """
    print("下載 宜蘭縣立案老人長期照顧及安養機構名冊 ...", file=sys.stderr)
    text = fetch(YL_LTC_URL)
    rows_in = json.loads(text)
    type_re = re.compile(r"[（(]([^）)]+)[）)]\s*$")
    records = []
    for row in rows_in:
        addr = (row.get("地址", "") or "").strip()
        if not addr.startswith("宜蘭"):
            for d in YL_DISTRICTS:
                if addr.startswith(d):
                    addr = "宜蘭縣" + addr
                    break
        _county, district = parse_county_district(addr, fallback_county="宜蘭縣")
        name = row.get("機構名稱", "").strip()
        m = type_re.search(name)
        inst_type = m.group(1).strip() if m else "未標示"
        records.append([
            row.get("編號", "").strip(),   # 0 id
            name,                              # 1 name
            inst_type,                         # 2 type
            row.get("負責人", "").strip(),  # 3 owner
            district,                          # 4 district
            addr,                              # 5 address
            row.get("電話", "").strip(),    # 6 phone
            row.get("傳真", "").strip(),    # 7 fax
        ])
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["id", "name", "type", "owner", "district", "address", "phone", "fax"]
    return {"fields": fields, "rows": records}


def _yl_denture_type(name: str) -> str:
    """依「診所名稱」關鍵字啟發式推斷機構類型（醫院／衛生所／牙醫診所），非官方分類欄位，
    僅供前端篩選/圖表參考。比照 build_hsc_denture() / build_kcg_denture() 的 _xxx_denture_type()
    判斷邏輯。"""
    name = name or ""
    if "醫院" in name:
        return "醫院"
    if "衛生所" in name:
        return "衛生所"
    return "牙醫診所"


def build_yl_denture():
    """115年度宜蘭縣中低收入戶老人假牙裝置補助實施計畫－特約牙醫醫療院所名單（宜蘭縣政府社會處公告
    PDF，非 DCAT 開放資料 CSV/API）。

    來源網址 YL_DENTURE_PDF_URL 本身即為可直接下載的檔案（非公告網頁轉址），故與 build_specialty()
    不同，比照 build_tn_denture()，本函式直接於伺服器端自動下載並解析，不需人工存成 data/source/*.pdf；
    若未來此網址改版失效，需重新確認來源網址並視需要改回人工下載模式。

    用 pdfplumber 解析 PDF（共2頁：第1頁為表格，第2頁為申請流程圖，本函式僅解析第1頁表格），
    表頭為「編號、鄉鎮市、診所名稱、診所地址、聯絡電話」，共 29 筆，跳過表頭列（編號欄非數字）。

    實測 29 筆中有 3 筆（編號27~29）為跨縣市特約醫院，地址開頭為「花蓮縣花蓮市」/「花蓮縣玉里鎮」
    （分別為衛生福利部花蓮醫院、財團法人花蓮慈濟醫院、衛生福利部玉里醫院），並非宜蘭縣境內機構；
    故 county 欄位一律用 parse_county_district() 由地址解析而來（不寫死「宜蘭縣」），district 欄位
    則直接採用 PDF 本身的「鄉鎮市」欄位（與地址解析結果一致）。

    「機構名稱」欄位有2筆（編號16、17）因原始表格跨行斷字含換行符號（如「醫療財團法人羅許基金會羅東
    博愛\n醫院」），本函式會移除換行符號還原成完整名稱。

    「聯絡電話」欄位宜蘭縣境內26筆為不含區碼的7位數字（如「9771387」），花蓮縣3筆已含「03-」區碼；
    本函式為宜蘭縣境內號碼統一補上「03-」前碼，花蓮縣號碼保留原樣。

    「機構類型」由 _yl_denture_type() 依名稱是否含「醫院」「衛生所」關鍵字啟發式判斷，其餘歸類
    「牙醫診所」，非官方分類欄位。無經緯度座標，故本頁不含地圖。

    PDF 第2頁申請流程圖已另存為 yl-denture/flowchart.jpg（比照 chiayi-denture 的做法），供前端
    頁面內嵌顯示，本函式不處理該圖片。

    額外欄位 google_rating／google_review_count／google_place_id：使用者需求為呈現各院所的
    Google 地圖星等與評論數，且明確表示為一次性資料，之後不會重新抓取。資料來源：2026-08-07 用
    scripts/fetch_google_ratings.py --dataset yl-denture 一次性呼叫 Google Places API (Legacy)
    Text Search，29 筆全數比對成功（status=OK），整理成
    data/source/yl-denture-google-ratings.json（key 為「診所名稱」）。人工核對時特別確認以下
    容易誤判的案例，皆用 Place Details 核對地址後確認比對正確：
    - 「天主教靈醫會醫療財團法人羅東聖母醫院」Google 地點名稱僅顯示「天主教靈醫會」（非「羅東聖母
      醫院」），核對地址「宜蘭縣羅東鎮中正南路160號」與原始資料完全一致，確認為同一地點。
    - 「美佳牙醫診所」比對到「美佳牙醫」、「統一牙醫診所」比對到「統一牙科診所」，皆核對地址與原始
      資料一致，確認僅顯示名稱略有出入，非誤配對。
    - 跨縣市3筆花蓮縣特約醫院（衛生福利部花蓮醫院／財團法人花蓮慈濟醫院／衛生福利部玉里醫院）
      Google 地點名稱為英文（如「Hualien Hospital, Ministry of Health and Welfare」），核對地址
      確認為同一機構。
    查無對照資料的院所，此三欄留空字串，前端顯示為「-」（本次 29 筆全數有對照資料，故實務上不會
    出現空值，僅為程式穩健性保留）。
    """
    print("下載 115年度宜蘭縣中低收入戶老人假牙裝置補助特約牙醫醫療院所名單 PDF ...", file=sys.stderr)
    import pdfplumber  # 延遲載入：僅此資料集需要，避免其他資料集重跑時強制安裝

    data = fetch_bytes(YL_DENTURE_PDF_URL)

    try:
        with open(YL_DENTURE_GOOGLE_RATINGS_FILE, "r", encoding="utf-8") as f:
            google_ratings = json.load(f)
    except FileNotFoundError:
        google_ratings = {}

    records = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                for row in table:
                    row = row + [""] * (5 - len(row))
                    rid = (row[0] or "").replace("\n", "").strip()
                    if not rid.isdigit():
                        continue  # 跳過表頭列（編號欄為「編號」文字）與標題列
                    district_col = (row[1] or "").replace("\n", "").strip()
                    name = (row[2] or "").replace("\n", "").strip()
                    addr = (row[3] or "").replace("\n", "").strip()
                    phone = (row[4] or "").replace("\n", "").strip()
                    if phone and re.match(r"^\d{7}$", phone):
                        phone = "03-" + phone
                    county, district = parse_county_district(addr, fallback_county="宜蘭縣")
                    g = google_ratings.get(name, {})
                    records.append([
                        int(rid),                     # 0 id
                        county or "",                    # 1 county
                        district or district_col,          # 2 district
                        name,                                 # 3 name
                        _yl_denture_type(name),                 # 4 type
                        addr,                                     # 5 address
                        phone,                                      # 6 phone
                        g.get("rating", ""),                          # 7 google_rating（一次性資料，查無留空字串）
                        g.get("review_count", ""),                      # 8 google_review_count（同上）
                        g.get("place_id", ""),                            # 9 google_place_id（同上，用於評論連結）
                    ])
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["id", "county", "district", "name", "type", "address", "phone",
              "google_rating", "google_review_count", "google_place_id"]
    return {"fields": fields, "rows": records}


def build_hccg_elder():
    """新竹市老人福利機構一覽表（新竹市政府社會處，DCAT dataset id 67739）。

    來源：https://data.gov.tw/dataset/8572 提供 xlsx/csv/xml/json 四種同內容格式，
    本腳本選用 json（downloadURL 見 HCCG_ELDER_URL），內容為物件陣列，中文欄位鍵值。
    原始欄位：編號、屬性、機構名稱、負責人、郵遞區號、地址、經度、緯度、電話、收容對象、
    核定收容人數、立案日期。地址已含完整「新竹市OO區」字首，可直接用 parse_county_district()
    解析行政區；經緯度已內建於資料，不需另行地理編碼。
    已知資料品質問題：「編號」欄位有跳號（例如缺 7 號），為原始資料狀態非解析錯誤；
    「立案日期」欄位格式不一致（部分為民國年 yy.mm.dd，部分夾雜「設立/變更負責人」等敘述文字），
    前端僅原文顯示，不做日期排序/運算。
    """
    print("下載 新竹市老人福利機構一覽表 ...", file=sys.stderr)
    text = fetch(HCCG_ELDER_URL)
    rows_in = json.loads(text)
    records = []
    for row in rows_in:
        addr = (row.get("地址", "") or "").strip()
        _county, district = parse_county_district(addr, fallback_county="新竹市")
        try:
            lng = float(row.get("經度") or 0)
            lat = float(row.get("緯度") or 0)
        except ValueError:
            lng, lat = 0.0, 0.0
        records.append([
            row.get("編號", "").strip(),           # 0 id
            row.get("屬性", "").strip(),           # 1 attr
            row.get("機構名稱", "").strip(),       # 2 name
            row.get("負責人", "").strip(),         # 3 owner
            row.get("郵遞區號", "").strip(),       # 4 zipcode
            district,                                 # 5 district
            addr,                                     # 6 address
            round(lng, 6),                             # 7 lng
            round(lat, 6),                             # 8 lat
            row.get("電話", "").strip(),           # 9 phone
            row.get("收容對象", "").strip(),       # 10 target
            _to_int(row.get("核定收容人數")),      # 11 capacity
            row.get("立案日期", "").strip(),       # 12 approvedDate
        ])
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["id", "attr", "name", "owner", "zipcode", "district", "address",
              "lng", "lat", "phone", "target", "capacity", "approvedDate"]
    return {"fields": fields, "rows": records}


def build_tn_homecare_nursing():
    """臺南市居家護理機構（臺南市政府衛生局，DCAT dataset https://data.gov.tw/dataset/7626）。

    此 DCAT 罕見列出歷年 9 個版本的 distribution（104~114年度），欄位隨年度不同：
      104~106年度：機構名稱/機構代碼/地址/負責人/電話/經度/緯度（有座標但機構數少，缺官田/學甲/
        歸仁等多個行政區機構，資料已過時）
      107~109年度：機構名稱/機構代碼/地址/負責人/電話（無行政區、無座標）
      110年度：改用縣市代碼/行政區域代碼/村里/街路門牌等結構化欄位（格式與其他年度不相容）
      113~114年度：機構名稱/機構代碼/行政區/地址/負責人/電話/分機（無座標，資料最新最完整）
    本腳本選用 **114年度** CSV 下載網址（TN_HOMECARE_NURSING_URL），理由：資料最新且涵蓋臺南市
    全部行政區機構（36筆），雖無經緯度座標但地址已含完整「臺南市OO區」字首可直接解析行政區，
    不需要地理編碼；114年度原始「行政區」欄位為數字代碼（如 67000320），未提供對照表，因此不採用
    該欄位，改用 parse_county_district() 從地址欄位解析。
    「電話」與「分機」兩欄位常互斥出現（例如電話留空、分機欄位填入手機號碼），本腳本合併為單一
    聯絡電話欄位：若電話與分機皆有值則以「電話 轉 分機」呈現，否則兩者取其一。
    """
    print("下載 臺南市居家護理機構 ...", file=sys.stderr)
    text = fetch(TN_HOMECARE_NURSING_URL)
    reader = csv.DictReader(io.StringIO(text))
    records = []
    for row in reader:
        addr = (row.get("地址", "") or "").strip()
        _county, district = parse_county_district(addr, fallback_county="臺南市")
        phone = (row.get("電話", "") or "").strip()
        ext = (row.get("分機", "") or "").strip()
        if phone and ext:
            phone = f"{phone} 轉 {ext}"
        elif not phone and ext:
            phone = ext
        records.append([
            row.get("機構代碼", "").strip(),   # 0 code
            row.get("機構名稱", "").strip(),   # 1 name
            district,                             # 2 district
            addr,                                 # 3 address
            row.get("負責人", "").strip(),     # 4 owner
            phone,                                 # 5 phone
        ])
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["code", "name", "district", "address", "owner", "phone"]
    return {"fields": fields, "rows": records}


def build_tc_nursing():
    """臺中市一般護理之家清冊（DCAT dataset https://data.gov.tw/dataset/8572）。

    來源 CSV 欄位：編號/機構名稱/行政區/一般床許可床數/一般床開放床數/呼吸器依賴許可床數/
    呼吸器依賴開放床數/開業日期/評鑑結果/督考結果/負責人/電話/住址/附設日間照顧開放人數，
    與 DCAT description 完全一致。「行政區」欄位已是中文名稱（中區、西區…），不需從地址欄位
    解析。無經緯度座標。來源網址本身已允許 CORS（Access-Control-Allow-Origin: *），但仍依專案
    慣例由本腳本於伺服器端下載並輸出內嵌 JS 版本，避免依賴外部網址即時可用性。

    已知資料品質備註：「附設日間照顧開放人數」多數為「-」（無附設日照），本腳本以 _to_int()
    轉數字時視為 0；「評鑑結果」／「督考結果」欄位偶見同一格內夾帶兩個年度結果（例如
    「112不合格113不合格」），原文照登不重新拆分；「開業日期」為民國年格式字串（如
    「101/11/16」），原文呈現不轉換曆法；「負責人」欄位已由來源做隱私遮蔽（如「劉O媛」）。
    """
    print("下載 臺中市一般護理之家清冊 ...", file=sys.stderr)
    # 來源 CSV 檔頭含兩個連續 BOM（\ufeff\ufeff），fetch() 的 utf-8-sig 解碼只會去掉一個，
    # 剩餘一個會殘留在第一欄「編號」欄名前導致 DictReader 讀不到該欄，故額外 lstrip 處理。
    text = fetch(TC_NURSING_URL).lstrip("\ufeff")
    reader = csv.DictReader(io.StringIO(text))
    records = []
    for row in reader:
        records.append([
            row.get("編號", "").strip(),                       # 0 id
            row.get("機構名稱", "").strip(),                   # 1 name
            row.get("行政區", "").strip(),                     # 2 district
            _to_int(row.get("一般床許可床數")),                # 3 generalBedsLicensed
            _to_int(row.get("一般床開放床數")),                # 4 generalBedsOpen
            _to_int(row.get("呼吸器依賴許可床數")),            # 5 ventBedsLicensed
            _to_int(row.get("呼吸器依賴開放床數")),            # 6 ventBedsOpen
            row.get("開業日期", "").strip(),                   # 7 openDate
            row.get("評鑑結果", "").strip(),                   # 8 rating
            row.get("督考結果", "").strip(),                   # 9 superviseRating
            row.get("負責人", "").strip(),                     # 10 director
            row.get("電話", "").strip(),                       # 11 phone
            row.get("住址", "").strip(),                       # 12 address
            _to_int(row.get("附設日間照顧開放人數")),          # 13 dayCareOpen
        ])
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["id", "name", "district", "generalBedsLicensed", "generalBedsOpen",
              "ventBedsLicensed", "ventBedsOpen", "openDate", "rating", "superviseRating",
              "director", "phone", "address", "dayCareOpen"]
    return {"fields": fields, "rows": records}


def build_ntpc_nursing():
    """新北市一般護理之家清冊（新北市政府衛生局，新北市資料開放平臺
    dataset https://data.ntpc.gov.tw/datasets/467cb02f-1f94-4fa1-a440-4f08575cf181，
    授權：政府資料開放授權條款-第1版，更新頻率：每年）。

    來源為正式分頁 CSV API（NTPC_NURSING_URL_TEMPLATE，page 從 0 起算、size=100），本腳本迴圈
    遞增 page 直到某頁回傳空白列為止，避免未來筆數超過單頁上限時漏抓資料（實測目前共 75 筆，
    一頁即可取完）。

    來源欄位：seqno(序號)/hosp_name(機構名稱)/hospcnttype(特約類別)/hosp_addr(地址)/
    name(聯絡人姓名)/tel(電話)/extension(分機)/bed(開放床數)/number(機構應配置護理人員數)/
    date(資料日期，YYYYMMDD)。其中 hospcnttype 實測全數為常數 "6"，無篩選意義，本腳本不輸出
    此欄位。「聯絡人姓名」欄位來源**未做遮蔽處理**（不同於其他資料集常見的「劉O媛」式遮蔽），
    本腳本忠實照登，不額外遮蔽或移除。

    地址欄位固定為「新北市」＋行政區字首（如「新北市板橋區...」），用 parse_county_district()
    搭配 fallback_county="新北市" 可完整解析行政區；「電話」欄位部分尾端含多餘空白，做 strip()。
    無經緯度座標，前端不呈現地圖。
    """
    print("下載 新北市一般護理之家清冊 ...", file=sys.stderr)
    records = []
    page = 0
    while True:
        text = fetch(NTPC_NURSING_URL_TEMPLATE.format(page=page))
        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)
        if not rows:
            break
        for row in rows:
            addr = (row.get("hosp_addr", "") or "").strip()
            _county, district = parse_county_district(addr, fallback_county="新北市", strict=True)
            records.append([
                row.get("seqno", "").strip(),          # 0 id
                row.get("hosp_name", "").strip(),      # 1 name
                district,                                # 2 district
                addr,                                    # 3 address
                row.get("name", "").strip(),           # 4 contact
                (row.get("tel", "") or "").strip(),    # 5 phone
                (row.get("extension", "") or "").strip(),  # 6 extension
                _to_int(row.get("bed")),               # 7 bed
                _to_int(row.get("number")),            # 8 staffRequired
                row.get("date", "").strip(),           # 9 date
            ])
        page += 1
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["id", "name", "district", "address", "contact", "phone", "extension",
              "bed", "staffRequired", "date"]
    return {"fields": fields, "rows": records}


def build_ntpc_silver_hair_club():
    """新北市銀髮俱樂部（新北市政府社會局，DCAT dataset
    https://data.gov.tw/dataset/8572，dataset id 124643，授權：政府資料開放授權條款-第1版，
    更新頻率：每1年）。

    downloadURL：NTPC_SILVER_HAIR_CLUB_URL（單一 CSV 檔案，非分頁 API），共 1197 筆。來源網址
    CORS 標頭僅允許 data.ntpc.gov.tw 網域（與 build_ntpc_nursing() 相同情況），前端無法直接
    fetch，本腳本於伺服器端下載，另輸出內嵌 JS 版本供前端以 <script> 直接載入。

    來源欄位：seqno(序號)/title(名稱)/county(縣市，固定為「新北市」)/countycode/
    area(行政區，已是中文，如「板橋區」)/areacode/address(地址)/
    localcall service(市話)/mobile telephone(手機)。county、area 皆已是中文名稱，
    不需從地址解析行政區，直接採用 area 欄位。

    address 欄位**不含**「新北市」＋行政區字首（例如僅「中山路二段250巷1號(埔墘福德宮)」），
    前端顯示地址原文照登，但轉 Google Maps 連結時需自行補上「新北市」＋該筆 area 前綴才能正確
    查到地點，見 ntpc-silver-hair-club/app.js 的 addressLink()。

    電話分市話（localcall service）與手機（mobile telephone）兩欄，本腳本原樣輸出兩欄
    （不合併字串），交由前端合併顯示並各自轉 tel: 連結，避免字串裁切/分隔符號歧義。

    已知資料品質問題：極少數筆（實測 1 筆）市話與手機皆為空值，原文照登不處理。
    """
    print("下載 新北市銀髮俱樂部 ...", file=sys.stderr)
    text = fetch(NTPC_SILVER_HAIR_CLUB_URL)
    reader = csv.DictReader(io.StringIO(text))
    records = []
    for row in reader:
        records.append([
            (row.get("seqno", "") or "").strip(),                    # 0 id
            (row.get("title", "") or "").strip(),                    # 1 name
            (row.get("area", "") or "").strip(),                     # 2 district
            (row.get("address", "") or "").strip(),                  # 3 address
            (row.get("localcall service", "") or "").strip(),        # 4 localPhone
            (row.get("mobile telephone", "") or "").strip(),         # 5 mobilePhone
        ])
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["id", "name", "district", "address", "localPhone", "mobilePhone"]
    return {"fields": fields, "rows": records}


def _chiayi_township(address: str) -> str:
    """從嘉義縣地址欄位解析鄉鎮市：先移除可能存在的「嘉義縣」前綴，
    再比對 CHIAYI_TOWNSHIPS 清單找出地址開頭的鄉鎮市名稱。"""
    addr = (address or "").strip()
    if addr.startswith("嘉義縣"):
        addr = addr[len("嘉義縣"):]
    for township in CHIAYI_TOWNSHIPS:
        if addr.startswith(township):
            return township
    return ""


def build_chiayi_ltc():
    """嘉義縣立案長照及護理之家機構一覽（嘉義縣政府長期照護管理中心，
    https://ltccenter.cyhg.gov.tw/cp.aspx?n=F7AEF7883C88532B ，人工提供，非開放資料 CSV/API）。

    使用者提供兩份本機 CSV（已存放於 scripts/sources/chiayi-ltc/，供未來人工更新資料使用）：
      1. institutions.csv（原檔名「嘉義縣立案住宿長照機構名單.csv」，2筆）
         欄位：序號/機構名稱/許可床數/開業床數/地址/電話，地址已含「嘉義縣」字首。
      2. nursing-homes.csv（原檔名「嘉義縣護理之家名單.csv」，15筆）
         欄位：序號/機構名稱/負責人或聯絡人/許可床數/開業床數/核准開業日期/地址/電話，
         地址多數不含「嘉義縣」字首（僅鄉鎮市＋路名），僅1筆例外。

    兩份資料合併為單一資料集，以 category 欄位（住宿長照機構／護理之家）分類；因全部資料同屬
    嘉義縣，不需縣市篩選，僅解析鄉鎮市（見 _chiayi_township()）。住宿長照機構原始欄位無
    「負責人」「核准開業日期」，統一輸出時該兩欄位留空字串。「核准開業日期」為民國年字串
    （如「88.3.22」），原文照登不轉換為西元年，與 build_tc_nursing() 的處理方式一致。
    此資料集無公開下載網址、無法自動更新，未來如需更新資料須人工以最新 CSV 覆蓋
    scripts/sources/chiayi-ltc/ 下的兩個檔案後，重新執行本腳本。
    """
    print("讀取 嘉義縣立案長照及護理之家機構一覽 ...", file=sys.stderr)
    records = []

    with open(CHIAYI_LTC_INSTITUTIONS_CSV, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            addr = (row.get("地址", "") or "").strip()
            records.append([
                "住宿長照機構",                          # 0 category
                row.get("機構名稱", "").strip(),        # 1 name
                _chiayi_township(addr),                    # 2 township
                addr,                                       # 3 address
                row.get("電話", "").strip(),            # 4 phone
                "",                                         # 5 director（此類機構原始資料無此欄）
                _to_int(row.get("許可床數")),           # 6 approvedBeds
                _to_int(row.get("開業床數")),           # 7 operatingBeds
                "",                                         # 8 approvalDate（此類機構原始資料無此欄）
            ])

    with open(CHIAYI_LTC_NURSING_CSV, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            addr = (row.get("地址", "") or "").strip()
            records.append([
                "護理之家",                              # 0 category
                row.get("機構名稱", "").strip(),        # 1 name
                _chiayi_township(addr),                    # 2 township
                addr,                                       # 3 address
                row.get("電話", "").strip(),            # 4 phone
                row.get("負責人或聯絡人", "").strip(),  # 5 director
                _to_int(row.get("許可床數")),           # 6 approvedBeds
                _to_int(row.get("開業床數")),           # 7 operatingBeds
                row.get("核准開業日期", "").strip(),    # 8 approvalDate
            ])

    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["category", "name", "township", "address", "phone", "director",
              "approvedBeds", "operatingBeds", "approvalDate"]
    return {"fields": fields, "rows": records}


def _pingtung_township(address: str) -> str:
    """從屏東縣地址欄位解析鄉鎮市：先移除可能存在的「屏東縣」前綴，
    再比對 PINGTUNG_TOWNSHIPS 清單找出地址開頭的鄉鎮市名稱。"""
    addr = (address or "").strip()
    if addr.startswith("屏東縣"):
        addr = addr[len("屏東縣"):]
    for township in PINGTUNG_TOWNSHIPS:
        if addr.startswith(township):
            return township
    return ""


def build_pingtung_ltc():
    """屏東縣老人長期照顧機構（屏東縣政府社會處，DCAT dataset https://data.gov.tw/dataset/8572）。

    來源為 CSV（PINGTUNG_LTC_URL），欄位僅 name、address、phone 三欄，共57筆。地址多數不含
    「屏東縣」前綴（僅鄉鎮市名稱開頭，如「竹田鄉六巷村太平路70巷20號」），少數例外已含完整前綴
    （如「屏東縣竹田鄉六巷村太平路70巷20號」）。因全部資料同屬屏東縣，不需縣市篩選，僅用
    _pingtung_township() 比對屏東縣33個鄉鎮市清單解析鄉鎮市。機構類型由機構名稱結尾括號文字解析
    （如「(養護型)」「（養護型）」），無標示者歸類為「未標示」，與 build_yl_ltc() 處理方式一致。
    無經緯度座標；來源網址無 CORS 標頭，改由本腳本於伺服器端下載。
    """
    print("下載 屏東縣老人長期照顧機構 ...", file=sys.stderr)
    text = fetch(PINGTUNG_LTC_URL)
    reader = csv.DictReader(io.StringIO(text))
    type_re = re.compile(r"[（(]([^）)]+)[）)]\s*$")
    records = []
    for row in reader:
        name = (row.get("name", "") or "").strip()
        addr = (row.get("address", "") or "").strip()
        m = type_re.search(name)
        inst_type = m.group(1).strip() if m else "未標示"
        records.append([
            name,                              # 0 name
            inst_type,                          # 1 type
            _pingtung_township(addr),           # 2 township
            addr,                               # 3 address
            (row.get("phone", "") or "").strip(),  # 4 phone
        ])
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["name", "type", "township", "address", "phone"]
    return {"fields": fields, "rows": records}


def build_tc_transport():
    """臺中市失能者交通接送服務（臺中市政府衛生局，DCAT dataset https://data.gov.tw/dataset/8572，
    dataset id 91903）。

    來源為 CSV（TC_TRANSPORT_URL），欄位：辦理單位/連絡電話/地址/X坐標/Y坐標/服務區域，與 DCAT
    description 一致。地址已含完整「臺中市OO區」字首，用 parse_county_district() 搭配
    fallback_county="臺中市" 解析辦理單位所在行政區。

    X/Y 坐標為 TWD97 TM2 平面座標（EPSG:3826）而非經緯度，用 twd97_to_wgs84() 換算為 WGS84
    經緯度供地圖呈現。

    「服務區域」欄位是以全形逗號「、」分隔的行政區清單字串（例如「潭子、中區、東區」），少數為
    「全區」代表服務臺中市全部行政區；本腳本拆解為 serviceAreas 陣列，前端篩選時「全區」視為
    符合任一行政區選項。

    已知資料品質備註：「連絡電話」欄位格式不一，混雜市話「(04)xxxxxxxx」、手機「(09xx)xxxxxx」，
    偶夾帶「分機」文字（如「(04)23950256分機15」），原文照登不重新格式化；地址門牌偶含全形逗號
    列出多個樓層/單元（如「10樓之3、之4」），不影響地址解析；來源 CSV 檔案本身在最後一筆資料的
    「服務區域」欄位處疑似被伺服器端截斷（實測原始 bytes 在檔案結尾停在一個多位元組 UTF-8 字元
    的中間），導致該筆最後一個行政區名稱解碼成無法辨識的替換字元（U+FFFD），本腳本會過濾掉含有
    此替換字元的服務區域片段（保留該筆資料其他欄位與已完整解碼的服務區域），不嘗試猜測被截斷的
    原始行政區名稱；另有一筆服務區域含「棲棲」（應為「梧棲」的重複字錯字），原文照登不修正。
    """
    print("下載 臺中市失能者交通接送服務 ...", file=sys.stderr)
    # 來源 CSV 檔頭含兩個連續 BOM（\ufeff\ufeff），fetch() 的 utf-8-sig 解碼只會去掉一個，
    # 剩餘一個會殘留在第一欄「辦理單位」欄名前導致 DictReader 讀不到該欄，故額外 lstrip 處理
    # （與 build_tc_nursing() 相同問題，同網域來源共用此怪癖）。
    text = fetch(TC_TRANSPORT_URL).lstrip("\ufeff")
    reader = csv.DictReader(io.StringIO(text))
    records = []
    for row in reader:
        addr = (row.get("地址", "") or "").strip()
        _county, district = parse_county_district(addr, fallback_county="臺中市")
        try:
            x = float(row.get("X坐標") or 0)
            y = float(row.get("Y坐標") or 0)
            lat, lng = twd97_to_wgs84(x, y)
        except (TypeError, ValueError):
            lat, lng = 0.0, 0.0
        # 過濾含解碼替換字元（U+FFFD）的片段，見上方 docstring 說明（來源檔案結尾疑似被截斷）。
        service_areas = [
            s for s in (row.get("服務區域", "") or "").split("、") if s and "\ufffd" not in s
        ]
        records.append([
            row.get("辦理單位", "").strip(),   # 0 name
            (row.get("連絡電話", "") or "").strip(),  # 1 phone
            addr,                                        # 2 address
            district,                                     # 3 district
            round(lng, 6),                                 # 4 lng
            round(lat, 6),                                 # 5 lat
            service_areas,                                 # 6 serviceAreas
        ])
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["name", "phone", "address", "district", "lng", "lat", "serviceAreas"]
    return {"fields": fields, "rows": records}


# 「服務項目」欄位固定僅有這兩種文字值，對應臺中市失智照護服務計畫的兩類服務單位，
# 見 build_tc_dementia() docstring 說明。
TC_DEMENTIA_TYPE_MAP = {
    "個案管理服務、人才培訓課程": "失智共同照護中心",
    "提供認知促進、緩和失智，安全看視，家屬支持團體及家屬照顧課程": "失智社區服務據點",
}


def build_tc_dementia():
    """臺中市失智症服務及資源提供單位（臺中市政府衛生局，DCAT dataset https://data.gov.tw/dataset/8572，
    dataset id 108261）。

    來源為 CSV（TC_DEMENTIA_URL），與 build_tc_transport()／build_tc_nursing() 同網域，共49筆，
    原始欄位：序號、辦理單位、連絡電話、電子郵件、縣市別代碼、地址、X坐標、Y坐標、服務項目、行政區，
    與 DCAT description 一致。地址已含完整「臺中市OO區」字首，用 parse_county_district() 搭配
    fallback_county="臺中市" 解析行政區（「行政區」原始欄位可直接使用，本腳本仍以地址解析為準，
    與其他臺中市資料集處理方式一致）。「縣市別代碼」固定為66000（臺中市代碼），無篩選意義不輸出。

    X/Y 坐標欄位**混雜兩種格式**：實測41筆是 WGS84 經緯度（數值約在24/120上下），8筆是 TWD97 TM2
    平面座標（EPSG:3826，數值 > 1000，如209833.481, 2675490.683），研判為原始資料建置時部分筆數
    誤用地圖框選座標而非地理編碼結果所致。本腳本依數值是否大於1000判斷格式：屬 TWD97 者用既有
    twd97_to_wgs84() 換算為 WGS84 經緯度，其餘直接視為經緯度使用，統一轉換後不再區分來源格式。

    「服務項目」欄位固定只有兩種文字值（見 TC_DEMENTIA_TYPE_MAP），分別對應「失智共同照護中心」
    （提供個案管理服務、人才培訓課程）與「失智社區服務據點」（提供認知促進、緩和失智課程、安全看視
    及家屬照顧者支持團體），本腳本轉換為較短的 type 欄位供前端篩選/圖表分類使用，原始服務項目文字
    保留於 README／頁面文案中說明，不逐筆輸出完整長文字。
    """
    print("下載 臺中市失智症服務及資源提供單位 ...", file=sys.stderr)
    text = fetch(TC_DEMENTIA_URL)
    reader = csv.DictReader(io.StringIO(text))
    records = []
    for row in reader:
        addr = (row.get("地址", "") or "").strip()
        _county, district = parse_county_district(addr, fallback_county="臺中市")
        try:
            x = float(row.get("X坐標") or 0)
            y = float(row.get("Y坐標") or 0)
        except (TypeError, ValueError):
            x, y = 0.0, 0.0
        if x > 1000 or y > 1000:
            lat, lng = twd97_to_wgs84(x, y)
        else:
            lat, lng = x, y
        service_item = (row.get("服務項目", "") or "").strip()
        records.append([
            row.get("辦理單位", "").strip(),                  # 0 name
            (row.get("連絡電話", "") or "").strip(),          # 1 phone
            (row.get("電子郵件", "") or "").strip(),          # 2 email
            addr,                                              # 3 address
            district,                                          # 4 district
            round(lng, 6),                                     # 5 lng
            round(lat, 6),                                     # 6 lat
            TC_DEMENTIA_TYPE_MAP.get(service_item, "其他"),   # 7 type
        ])
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["name", "phone", "email", "address", "district", "lng", "lat", "type"]
    return {"fields": fields, "rows": records}


def _tyltc_service_type(name: str) -> str:
    """依「辦理單位」名稱關鍵字啟發式推斷服務類型，見 TYLTC_TYPE_RULES 說明。"""
    for keyword, label in TYLTC_TYPE_RULES:
        if keyword in (name or ""):
            return label
    return "其他"


def build_tyltc():
    """桃園市長期照護專業服務特約單位（桃園市政府衛生局，DCAT dataset id 94306）。

    來源為 CSV（TYLTC_URL），共約121筆，**編碼為 BIG5(cp950)**——與本專案其他資料集慣用的
    utf-8-sig 不同，需以 fetch(url, encoding="cp950") 下載解碼。原始欄位：性質、資源彙整機關、
    辦理單位、成立日期、立案文號、負責人、連絡電話、傳真、電子郵件、地址、服務區域、相關網址、
    X坐標、Y坐標、備註、最後更新時間，與 DCAT description 一致；實測「性質」「成立日期」
    「立案文號」「服務區域」「相關網址」「X坐標」「Y坐標」「備註」全數為空值，**無經緯度座標**，
    故本頁不含地圖。

    「地址」為特約單位（辦理單位）本身的地址，實測約12%機構位於新北市/臺北市等桃園市以外縣市
    （服務桃園市民但機構設址於外縣市），不可假設地址一律在桃園市：地址以「桃園市」開頭者，用既有
    TYC_DISTRICTS 固定清單解析行政區（沿用 build_tyc_elder() 的理由：ADDR_RE 對「平鎮區」等名稱
    中途含「鎮」字的行政區會誤判）；其餘縣市則改用 parse_county_district() 搭配 strict=True 解析。

    「服務類型」為本腳本依「辦理單位」名稱關鍵字啟發式推斷（TYLTC_TYPE_RULES，如含「居家式服務類
    機構」「職能治療所」「物理治療所」「護理之家」「日間照顧」等），**非官方分類欄位**，前端需標注
    為推斷值，僅供篩選/圖表參考，不代表衛生局正式分類。

    「連絡電話」欄位偶有跨行的多組號碼/分機備註（CSV 已用引號包住換行內容），本腳本統一以
    " / " 合併成單行，與 build_kcg_homecare() 的 informtel 處理方式一致。
    """
    print("下載 桃園市長期照護專業服務特約單位 ...", file=sys.stderr)
    text = fetch(TYLTC_URL, encoding="cp950")
    reader = csv.DictReader(io.StringIO(text))
    records = []
    for row in reader:
        name = (row.get("辦理單位", "") or "").strip()
        addr = (row.get("地址", "") or "").strip()
        if addr.startswith("桃園市"):
            county = "桃園市"
            rest = addr[len("桃園市"):]
            district = next((d for d in TYC_DISTRICTS if rest.startswith(d)), "")
        else:
            county, district = parse_county_district(addr, strict=True)
        phone_lines = [p.strip() for p in (row.get("連絡電話", "") or "").splitlines() if p.strip()]
        phone = " / ".join(phone_lines)
        records.append([
            name,                                              # 0 name
            _tyltc_service_type(name),                         # 1 type
            county,                                             # 2 county
            district,                                          # 3 district
            addr,                                              # 4 address
            (row.get("負責人", "") or "").strip(),          # 5 owner
            phone,                                              # 6 phone
            (row.get("傳真", "") or "").strip(),            # 7 fax
            (row.get("電子郵件", "") or "").strip(),        # 8 email
            (row.get("最後更新時間", "") or "").strip(),   # 9 updatedAt
        ])
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["name", "type", "county", "district", "address", "owner",
              "phone", "fax", "email", "updatedAt"]
    return {"fields": fields, "rows": records}


def _tyc_denture_type(name: str) -> str:
    """依「特約單位名稱」是否含「醫院」二字，啟發式推斷機構類型（醫院／診所），
    非官方分類欄位，僅供前端篩選/圖表參考。"""
    return "醫院" if "醫院" in (name or "") else "診所"


TYC_DENTURE_GOOGLE_RATINGS_FILE = "data/source/tyc-denture-google-ratings.json"


def build_tyc_denture():
    """桃園市長者裝置活動假牙合約醫療院所（桃園市政府衛生局，DCAT dataset id 26030）。

    來源為 CSV（TYC_DENTURE_URL），共約155筆，欄位：編號、特約單位名稱、區別、地址、電話，與 DCAT
    description 一致。「區別」欄位本身即為乾淨的桃園市鄉鎮市區中文名稱（如「八德區」），**不需**從
    地址欄位解析行政區，比 build_tyc_elder() 更單純；少數地址欄位（如編號140）本身多帶「桃園市」
    字首，屬原始資料不一致，原文照登不修正。無經緯度座標，故本頁不含地圖。

    「機構類型」為本腳本依「特約單位名稱」是否含「醫院」二字啟發式推斷（見 _tyc_denture_type()），
    **非官方分類欄位**，前端需標注為推斷值。

    來源網址與同平台的 tyc-elder／tyltc 資料集一致，CORS 僅允許 opendata.tycg.gov.tw 網域，改由
    本腳本於伺服器端下載，另輸出內嵌 JS 版本避免依賴外部網址即時可用性。

    額外欄位 google_rating／google_review_count／google_place_id：使用者需求為呈現各院所的
    Google 地圖星等與評論數，且明確表示為一次性資料，之後不會重新抓取。資料來源：2026-08-05 用
    scripts/fetch_google_ratings.py --dataset tyc-denture 一次性呼叫 Google Places API (Legacy)
    Text Search，155 筆中 154 筆比對成功並人工核對通過，整理成
    data/source/tyc-denture-google-ratings.json（key 為「特約單位名稱」）。人工核對重點：
    - 多筆機構（醫院類：天晟醫院、聖保祿醫院、桃園/新屋/樂生等衛福部醫院、長庚醫院、臺北榮總桃園
      分院；診所類：巧研美學、名家、何逢源、益皓、温、源美、杏美等）Google 地點名稱與原始名稱不同
      （英文譯名、簡稱、或用字略異如「温」/「溫」），皆已用 Place Details 核對 formatted_address
      與原始地址完全一致，確認為同一地點。
    - 「大園牙醫診所」比對到「大園牙科」但 Google 回傳 rating=None（無評分資料），予以排除，此筆
      三欄留空字串。
    查無對照資料的院所，此三欄留空字串，前端顯示為「-」。
    """
    print("下載 桃園市長者裝置活動假牙合約醫療院所 ...", file=sys.stderr)
    text = fetch(TYC_DENTURE_URL)
    reader = csv.DictReader(io.StringIO(text))

    try:
        with open(TYC_DENTURE_GOOGLE_RATINGS_FILE, "r", encoding="utf-8") as f:
            google_ratings = json.load(f)
    except FileNotFoundError:
        google_ratings = {}

    records = []
    for row in reader:
        name = (row.get("特約單位名稱", "") or "").strip()
        g = google_ratings.get(name, {})
        records.append([
            (row.get("編號", "") or "").strip(),   # 0 id
            name,                                     # 1 name
            _tyc_denture_type(name),                  # 2 type
            (row.get("區別", "") or "").strip(),    # 3 district
            (row.get("地址", "") or "").strip(),    # 4 address
            (row.get("電話", "") or "").strip(),    # 5 phone
            g.get("rating", ""),                    # 6 google_rating（一次性資料，查無留空字串）
            g.get("review_count", ""),              # 7 google_review_count（同上）
            g.get("place_id", ""),                   # 8 google_place_id（同上，用於評論連結）
        ])
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["id", "name", "type", "district", "address", "phone",
              "google_rating", "google_review_count", "google_place_id"]
    return {"fields": fields, "rows": records}


def _tyc_disability_note(cell: str) -> str:
    """解析單一儲存格內容，回傳 (是否可鑑定, 備註文字)。
    儲存格格式：空白＝不可鑑定；"V"＝可鑑定無條件；"V\\n(備註文字)"＝可鑑定但有條件限制，
    備註文字保留原始描述（去除外層括號）。"""
    cell = (cell or "").strip()
    if not cell:
        return None
    if not cell.startswith("V"):
        return ""  # 非預期格式，視為可鑑定且無備註，忠實照登
    note = cell[1:].strip()
    if note.startswith("(") and note.endswith(")"):
        note = note[1:-1]
    elif note.startswith("（") and note.endswith("）"):
        note = note[1:-1]
    return note


def build_tyc_disability_hospitals():
    """桃園市身心障礙類別、向度之鑑定醫院名冊（桃園市政府衛生局，DCAT dataset id 128335）。

    來源為 CSV（TYC_DISABILITY_HOSPITALS_URL），原始格式是一份「鑑定類別×向度×17家醫院」的勾選
    矩陣，而非機構名冊：欄位為 新制鑑定類別／新制鑑定向度／新制鑑定向度_名稱／相關疾病類別，接著
    17 個欄位對應 TYC_DISABILITY_HOSPITALS 清單的醫院，儲存格值為「V」（可鑑定）、空白（不可鑑定）
    或「V\\n(備註文字)」（有條件可鑑定，如「僅鑑定失智症」「限18歲以上民眾」「無鑑定智能障礙」）。

    原始 CSV 使用合併儲存格：「新制鑑定類別」（第一類～第八類）與「新制鑑定向度」（向度大分組）
    欄位只在該分組第一列填值，其餘列留空，本腳本以 forward-fill（沿用前一筆非空值）還原完整分組。
    有一筆特例「整體心理功能：發展遲緩」不屬於「第X類」編號格式，是獨立於分組之外的項目，本腳本
    偵測「新制鑑定類別」欄位非空但不以「第」開頭時，視為獨立項目（不做 dimension 的 forward-fill，
    以該欄位值本身作為 item 名稱）。檔案最後一列是「,,,,...,更新日期：112.1.19,...」的更新日期
    備註列，非資料列，本腳本偵測任一醫院欄位含「更新日期」字樣即略過整列。

    本腳本將矩陣展開為「長格式」：每筆 row 代表「一個類別＋向度＋相關疾病類別＋可鑑定醫院＋備註」
    的組合，只保留該醫院欄位有勾選（V 或 V+備註）的組合，欄位為 category／dimension／item／
    disease／hospital／note（note 為單純 V 時為空字串）。此格式可直接套用既有分頁表格元件與
    篩選/圖表模式；若需要原始矩陣視圖，可另外由 rows 依 item+hospital 重建。

    無地址、無電話、無經緯度座標欄位，故本頁不含地圖，也不套用地址/電話超連結慣例。

    來源網址與同平台的 tyc-elder／tyltc／tyc-denture 資料集一致，CORS 僅允許 opendata.tycg.gov.tw
    網域，改由本腳本於伺服器端下載，惟資料量小（預估400~500筆），前端以一般 fetch() 讀取本地靜態
    json 即可，不需另外輸出內嵌 JS 版本。
    """
    print("下載 桃園市身心障礙類別、向度之鑑定醫院名冊 ...", file=sys.stderr)
    text = fetch(TYC_DISABILITY_HOSPITALS_URL)
    reader = csv.reader(io.StringIO(text))
    rows_raw = list(reader)
    header, data_rows = rows_raw[0], rows_raw[1:]

    records = []
    prev_category = ""
    prev_dimension = ""
    for row in data_rows:
        row = row + [""] * (21 - len(row))  # 補齊欄位數避免索引錯誤
        # 原始 CSV 部分儲存格內容跨行斷開（如「神經系統構造\n及精神、心智功能」），屬版面換行，
        # 與資料語意無關，統一去除內部換行後再使用。
        cat, dim, item, disease = ((c or "").replace("\n", "").strip() for c in row[:4])
        hospital_cells = row[4:21]

        if any("更新日期" in (c or "") for c in hospital_cells):
            continue  # 結尾更新日期備註列，非資料列

        if cat and not cat.startswith("第"):
            # 特例：不屬於「第X類」編號格式的獨立項目（如「整體心理功能：發展遲緩」）
            category, dimension, item_name = cat, "", cat
        else:
            if cat:
                prev_category = cat
            if dim:
                prev_dimension = dim
            category, dimension, item_name = prev_category, prev_dimension, item

        if not disease:
            continue

        for hospital, cell in zip(TYC_DISABILITY_HOSPITALS, hospital_cells):
            note = _tyc_disability_note(cell)
            if note is None:
                continue
            records.append([category, dimension, item_name, disease, hospital, note])

    print(f"  共 {len(records)} 筆（展開為長格式後）", file=sys.stderr)
    fields = ["category", "dimension", "item", "disease", "hospital", "note"]
    return {"fields": fields, "hospitals": TYC_DISABILITY_HOSPITALS, "rows": records}


TYC_PLACEMENT_TYPE_RE = re.compile(r"[（(]([^）(]*型)[）)]")

# 第3筆「桃園市私立建元老人長期照顧中心（養護型）」地址欄位原始資料誤填為機構名稱本身（非真實
# 地址，原始資料品質問題）；經人工查證該機構實際地址為「330桃園市桃園區雲林里大豐路56號」，於此
# 手動補上正確地址（僅此一筆套用覆寫，其餘機構地址仍以原始 CSV 資料為準）。
TYC_PLACEMENT_ADDRESS_OVERRIDES = {
    "桃園市私立建元老人長期照顧中心（養護型）": "330桃園市桃園區雲林里大豐路56號",
}


def build_tyc_placement():
    """桃園市失能老人接受長期照顧機構服務暨老人保護安置機構名冊（桃園市政府社會局，
    DCAT dataset id 75570，distribution 備註「115-116年失能老人公費安置機構簽約名冊」）。

    來源為 CSV（TYC_PLACEMENT_URL），共123筆，**編碼為 BIG5(cp950)**，與 build_tyltc() 同一例外，
    需 fetch(url, encoding="cp950") 下載解碼。原始欄位：編號、機構名稱、電話、地址，與 DCAT
    description 一致，**無經緯度座標**，故本頁不含地圖。

    「機構名稱」結尾偶帶括號分類文字，本腳本只擷取以「型」結尾的括號內容作為「機構類型」（實測
    僅出現「養護型」「長期照護型」兩種），刻意排除名稱中其他非分類用途的括號備註（如「（更名前：
    海森）」「（玉里園區）」這類改名/分院說明，不以「型」結尾），避免誤判；無法擷取到「型」結尾
    括號者歸類「未標示」（實測占約46%，多為「OO護理之家」「OO精神護理之家」類機構，原始資料本身
    未在名稱標示分類），**非官方分類欄位**，僅供篩選/圖表參考。

    「地址」多數為「桃園市OO區」開頭，但因屬跨縣市公費安置合約名冊，實測約13筆位於新竹縣、花蓮縣、
    彰化縣、新北市、臺南市等桃園市以外縣市：比照 build_tyltc() 的作法，地址以「桃園市」開頭者用
    既有 TYC_DISTRICTS 固定清單解析行政區（避免「平鎮區」等名稱誤判），其餘縣市改用
    parse_county_district(strict=True) 一般規則解析。

    已知資料品質備註／人工修正：第92筆地址欄位以引號包住跨行兩段地址（機構行政聯絡地址＋實際
    所在地地址），csv.DictReader 已正確讀入為單一欄位值；第3筆「桃園市私立建元老人長期照顧中心
    （養護型）」原始地址欄位內容誤填為與機構名稱相同的文字（非本腳本解析錯誤），經人工查證該
    機構實際地址為「330桃園市桃園區雲林里大豐路56號」，以 TYC_PLACEMENT_ADDRESS_OVERRIDES
    手動覆寫該筆 address 後再解析 county/district（僅此一筆套用覆寫）；電話欄位格式不一，夾帶
    空格、「分機」文字、「#」分機、聯絡人姓名（如「03-8886141#1153葉小姐」），不重新格式化。

    來源網址與同平台其他 opendata.tycg.gov.tw 資料集一致，CORS 僅允許該平台網域，改由本腳本於
    伺服器端下載並輸出內嵌 JS 版本。
    """
    print("下載 桃園市失能老人接受長期照顧機構服務暨老人保護安置機構名冊 ...", file=sys.stderr)
    text = fetch(TYC_PLACEMENT_URL, encoding="cp950")
    reader = csv.DictReader(io.StringIO(text))
    records = []
    for row in reader:
        name = (row.get("機構名稱", "") or "").strip()
        addr = (row.get("地址", "") or "").strip()
        if name in TYC_PLACEMENT_ADDRESS_OVERRIDES:
            addr = TYC_PLACEMENT_ADDRESS_OVERRIDES[name]
        m = TYC_PLACEMENT_TYPE_RE.search(name)
        inst_type = m.group(1) if m else "未標示"
        addr_no_zip = re.sub(r"^\d{3,6}", "", addr)  # 部分地址帶郵遞區號字首，解析前先去除
        if addr_no_zip.startswith("桃園市"):
            county = "桃園市"
            rest = addr_no_zip[len("桃園市"):]
            district = next((d for d in TYC_DISTRICTS if rest.startswith(d)), "")
        else:
            county, district = parse_county_district(addr_no_zip, strict=True)
        records.append([
            name,                                  # 0 name
            inst_type,                              # 1 type
            county,                                  # 2 county
            district,                                # 3 district
            addr,                                    # 4 address
            (row.get("電話", "") or "").strip(),  # 5 phone
        ])
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["name", "type", "county", "district", "address", "phone"]
    return {"fields": fields, "rows": records}


# 一次性 Google 評分／評論數／place_id 靜態資料（2026-07-26 用 scripts/fetch_tpe_denture_ratings.py
# 呼叫 Google Places API (Legacy) Text Search 人工核對後謄寫），key 為「院所名稱」，value 為
# (rating, review_count, place_id)。place_id 用於前端評論連結直接導向 Google 地圖評論頁
# （https://search.google.com/local/reviews?placeid=）。此資料集僅6家院所且未來不會變動，故直接
# 寫死於此，不會隨 build_data.py 重跑而重新抓取或遺失；查無資料的院所（若有）不需列在字典中，
# 組裝 rows 時會自動補空字串。
TPE_DENTURE_GOOGLE_RATINGS = {
    "臺北市立聯合醫院中興院區": (3.7, 1322, "ChIJKfilEBKpQjQRiqgmYP6pC2g"),
    "臺北市立聯合醫院仁愛院區": (3.5, 1704, "ChIJmYpUC9GrQjQRT9YO_88LhP0"),
    "臺北市立聯合醫院和平院區": (3.5, 1234, "ChIJrZ0_kaapQjQRR4lFD2M6Lq0"),
    "臺北市立聯合醫院陽明院區": (3.7, 1114, "ChIJC5p2fJyuQjQRtS1OLXC18F4"),
    "臺北市立聯合醫院忠孝院區": (3.5, 1628, "ChIJZ4C2N3SrQjQRJnIHuKK6utU"),
    "臺北市立聯合醫院婦幼院區": (4.1, 818, "ChIJzf5reJmpQjQR-XZs3RiwfGI"),
}


def build_tpe_denture():
    """臺北市假牙補助醫療院所名單（臺北市政府社會局，DCAT dataset id 129840）。

    來源為 CSV（TPE_DENTURE_URL），**編碼為 BIG5(cp950)**，與 build_tyltc()/build_tyc_placement()
    同一例外，需 fetch(url, encoding="cp950") 下載解碼。原始欄位：補助類型、區域、院所名稱、地址、
    連絡電話，與 DCAT description 一致。

    實測**僅6筆資料**，「補助類型」全數為常數值「假牙補助」，無篩選/圖表意義；6家院所全部是
    「臺北市立聯合醫院」不同分院（中興、仁愛、和平、陽明、忠孝、婦幼），分布於5個行政區（中正區
    有2家）。「地址」已含完整「臺北市OO區」字首，用 parse_county_district(strict=True) 直接解析
    即可（臺北市12個行政區名稱互不含子字串歧義，不需像桃園市 TYC_DISTRICTS 那樣額外處理）；「區域」
    欄位本身也是乾淨的行政區中文名稱，與地址解析結果一致，僅保留供交叉核對，前端仍以地址解析出的
    district 為準。無經緯度座標，故本頁不含地圖。

    來源網址 data.taipei 平台無 CORS 標頭，改由本腳本於伺服器端下載；雖資料量極小，仍輸出內嵌 JS
    版本以維持與其他資料集一致的載入方式（避免 fetch 時序問題）。

    額外欄位 rating／review_count／place_id：使用者需求為呈現各院區 Google 評分與評論數，且明確
    表示「未來都不更新，只抓這一次」，故不透過即時 API 呼叫產生，而是查表套用上方
    TPE_DENTURE_GOOGLE_RATINGS 常數（見該常數註解）。place_id 用於前端把評論數連結直接導向該院所
    的 Google 地圖評論頁面。查無對照資料的院所此三欄留空字串，前端顯示為「-」。
    """
    print("下載 臺北市假牙補助醫療院所名單 ...", file=sys.stderr)
    text = fetch(TPE_DENTURE_URL, encoding="cp950")
    reader = csv.DictReader(io.StringIO(text))
    records = []
    for row in reader:
        addr = (row.get("地址", "") or "").strip()
        county, district = parse_county_district(addr, strict=True)
        name = (row.get("院所名稱", "") or "").strip()
        rating, review_count, place_id = TPE_DENTURE_GOOGLE_RATINGS.get(name, ("", "", ""))
        records.append([
            (row.get("補助類型", "") or "").strip(),  # 0 type
            (row.get("區域", "") or district).strip(),  # 1 district（優先用地址解析結果，缺值才退回原始欄位）
            name,                                        # 2 name
            addr,                                        # 3 address
            (row.get("連絡電話", "") or "").strip(),   # 4 phone
            rating,                                       # 5 rating（一次性 Google 評分，查無資料留空字串）
            review_count,                                 # 6 review_count（一次性 Google 評論數，查無資料留空字串）
            place_id,                                     # 7 place_id（一次性 Google Place ID，用於評論連結）
        ])
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["type", "district", "name", "address", "phone", "rating", "review_count", "place_id"]
    return {"fields": fields, "rows": records}


def _tyc_transport_county_district(addr: str) -> tuple[str, str]:
    """解析辦理單位地址所在縣市／行政區。地址分布多個縣市（桃園市/臺北市/新北市等，服務桃園市民但
    辦理單位本身設址於外縣市），若以「桃園市」開頭或直接以桃園市13個行政區名稱開頭（少數地址缺少
    「桃園市」字首，如「桃園區大興西路二段61號11樓」），改用既有 TYC_DISTRICTS 固定清單比對解析，
    與 build_tyc_elder()/build_tyltc() 理由一致：一般規則 ADDR_RE 對「平鎮區」等行政區名稱中途
    含「鎮」字會提前誤判（貪婪度不足，將「平鎮區」誤判為「平鎮」）；其餘縣市改用
    parse_county_district(strict=True) 解析。"""
    if addr.startswith("桃園市"):
        rest = addr[len("桃園市"):]
        district = next((d for d in TYC_DISTRICTS if rest.startswith(d)), "")
        return "桃園市", district
    matched = next((d for d in TYC_DISTRICTS if addr.startswith(d)), "")
    if matched:
        return "桃園市", matched
    return parse_county_district(addr, strict=True)


def build_tyc_transportation():
    """桃園市長照交通接送服務單位（桃園市政府社會局，DCAT dataset id 148536）。

    來源為 CSV（TYC_TRANSPORT_URL），**編碼為 BIG5**，需 fetch(url, encoding="big5") 下載解碼。
    共14筆，欄位：辦理單位、連絡電話、地址、服務區域，與 DCAT description（辦理單位、連絡電話、
    地址、服務區域）一致。

    「地址」為辦理單位本身的地址，實測分布桃園市/臺北市/新北市等多個縣市（服務桃園市民但辦理單位
    設址於外縣市），不可假設地址一律在桃園市，見 _tyc_transport_county_district() 解析規則。

    「連絡電話」欄位偶有跨行的多組號碼/分機（CSV 已用引號包住換行內容），本腳本統一以 " / " 合併
    成單行，與 build_tyltc() 處理方式一致。

    「服務區域」欄位實測僅兩種值：「桃園市全區」（11家）與「復興區(專車)」（3家，服務原住民區及
    偏遠地區之專車），資料量小不拆解為陣列，原文照登。

    無經緯度座標，故本頁不含地圖；因僅14筆資料量極小，比照 build_tyc_denture() 另輸出內嵌 JS 版本
    以維持與其他資料集一致的載入方式。
    """
    print("下載 桃園市長照交通接送服務單位 ...", file=sys.stderr)
    text = fetch(TYC_TRANSPORT_URL, encoding="big5")
    reader = csv.DictReader(io.StringIO(text))
    records = []
    for row in reader:
        addr = (row.get("地址", "") or "").strip()
        county, district = _tyc_transport_county_district(addr)
        phone_lines = [p.strip() for p in (row.get("連絡電話", "") or "").splitlines() if p.strip()]
        phone = " / ".join(phone_lines)
        records.append([
            (row.get("辦理單位", "") or "").strip(),      # 0 name
            phone,                                            # 1 phone
            addr,                                             # 2 address
            county,                                           # 3 county
            district,                                         # 4 district
            (row.get("服務區域", "") or "").strip(),      # 5 serviceArea
        ])
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["name", "phone", "address", "county", "district", "serviceArea"]
    return {"fields": fields, "rows": records}


TYC_HOSPICE_CATEGORY_HEADERS = {
    "安寧病房": "安寧病房",
    "安寧共照": "安寧共照",
    "安寧": "居家及社區安寧",  # 第三段標題列為「安寧,居家及社區安寧,」，取第二欄作為類別名稱
}


def _tyc_hospice_subtype(name: str, category: str) -> str:
    """依機構名稱關鍵字啟發式推斷「居家及社區安寧」類別內的機構型態，非官方分類欄位。
    僅對「居家及社區安寧」類別推斷，其餘類別（安寧病房／安寧共照）留空字串。"""
    if category != "居家及社區安寧":
        return ""
    if "居家護理所" in name:
        return "居家護理所"
    if "衛生所" in name:
        return "衛生所"
    return "診所"


def build_tyc_hospice():
    """桃園市社區安寧療護資源一覽表（桃園市政府衛生局，DCAT dataset https://data.gov.tw/dataset/8572 ，
    dataset id 45675）。

    來源為 CSV（TYC_HOSPICE_URL），**編碼為 BIG5(cp950)**，與 build_tyltc()/build_tyc_placement()/
    build_tpe_denture() 同一例外，需 fetch(url, encoding="cp950") 下載解碼。

    檔案僅62行、**無標準表頭列**，而是用三段「分類標題列」把資料切成三個服務類別區塊：
    「安寧病房,聯繫方式,地址」「安寧共照,聯繫方式,地址」「安寧,居家及社區安寧,」，本函式偵測這三種
    標題列（見 TYC_HOSPICE_CATEGORY_HEADERS）作為服務類別分段依據，欄位固定 3 欄：機構名稱／電話／
    地址。

    少數資料列機構名稱欄位為空、僅有電話（實測是前一筆機構的第二支聯絡電話），本函式會將這類列的
    電話合併進前一筆機構的電話欄位（以「、」分隔多支電話），不輸出空名稱的資料列。

    同一機構常出現在多個服務類別（例如「臺北榮民總醫院桃園分院」同時提供安寧病房／安寧共照／居家
    及社區安寧），屬資料集本身設計（一機構可對應多種服務），忠實照登為多筆（機構,服務類別）組合，
    不視為重複資料。

    地址已含完整「桃園市OO區」字首，但共用的 ADDR_RE 對「平鎮區」等名稱中途含「鎮」字的行政區會誤判
    （截斷成「平鎮」），比照 build_tyc_elder() 改用桃園市固定13區清單（TYC_DISTRICTS）比對取代
    parse_county_district()。無經緯度座標，故本頁不含地圖。

    「居家及社區安寧」類別內混雜性質不同的院所（居家護理所／診所／衛生所），原始欄位未區分，本函式
    另外依機構名稱關鍵字啟發式推斷「機構型態」（見 _tyc_hospice_subtype()），**非官方分類欄位**，
    僅對此類別推斷，其餘類別留空字串，前端會標注為推斷值。

    電話欄位格式不一（有無括號區碼、夾帶「分機」文字、以「/」分隔多組號碼），原文照登不重新格式化。

    來源網址與同平台其他 opendata.tycg.gov.tw 資料集一致，CORS 僅允許該平台網域，改由本函式於
    伺服器端下載並輸出內嵌 JS 版本，避免依賴外部網址即時可用性。
    """
    print("下載 桃園市社區安寧療護資源一覽表 ...", file=sys.stderr)
    text = fetch(TYC_HOSPICE_URL, encoding="cp950")
    reader = csv.reader(io.StringIO(text))
    rows_raw = [row for row in reader if any((c or "").strip() for c in row)]

    records = []
    category = ""
    for row in rows_raw:
        row = row + [""] * (3 - len(row))
        col0, col1, col2 = ((c or "").strip() for c in row[:3])
        header_category = TYC_HOSPICE_CATEGORY_HEADERS.get(col0)
        if header_category and col2 in ("地址", "", "聯繫方式"):
            # 分類標題列本身不是資料列（如「安寧病房,聯繫方式,地址」「安寧,居家及社區安寧,」）
            category = header_category
            continue
        name, phone, addr = col0, col1, col2
        if not name and phone:
            # 空名稱列＝前一筆機構的第二支電話，合併進前一筆的電話欄位
            if records and records[-1][0] == category:
                records[-1][2] = f"{records[-1][2]}、{phone}" if records[-1][2] else phone
            continue
        if not name and not phone and not addr:
            continue
        # 地址已含「桃園市OO區」字首，但共用的 ADDR_RE 對「平鎮區」等名稱中途含「鎮」字的行政區
        # 會誤判（截斷成「平鎮」），比照 build_tyc_elder() 改用桃園市固定13區清單比對。
        district = next((d for d in TYC_DISTRICTS if d in addr), "")
        subtype = _tyc_hospice_subtype(name, category)
        records.append([category, name, phone, district, addr, subtype])
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["category", "name", "phone", "district", "address", "subtype"]
    return {"fields": fields, "rows": records}


def _tyc_respite_parse_district(addr: str) -> tuple:
    """解析喘息服務提供單位地址的縣市／行政區。地址多數為「桃園市OO區」開頭，但共用的 ADDR_RE
    對「平鎮區」等名稱中途含「鎮」字的行政區會誤判（截斷成「平鎮」），比照 build_tyc_hospice()／
    build_tyc_placement() 改用桃園市固定13區清單（TYC_DISTRICTS）比對；少數（居家/機構各2筆）
    地址位於新北市、新竹縣等桃園市以外縣市，改用 parse_county_district(strict=True) 一般規則解析。"""
    if addr.startswith("桃園市"):
        district = next((d for d in TYC_DISTRICTS if d in addr), "")
        return "桃園市", district
    return parse_county_district(addr, strict=True)


def _tyc_respite_read_csv(url: str, category: str) -> list:
    """下載並解析單一喘息服務 CSV（居家或機構），回傳該類別的 records 陣列。"""
    text = fetch(url, encoding="cp950")
    reader = csv.DictReader(io.StringIO(text))
    records = []
    for row in reader:
        name = (row.get("辦理單位", "") or "").strip()
        if not name:
            # 機構喘息 CSV 尾端有大量僅含「資源彙整機關」欄位的空白列，以「辦理單位」非空過濾
            continue
        addr = (row.get("地址", "") or "").strip()
        county, district = _tyc_respite_parse_district(addr)
        # 服務區域欄位在居家喘息 CSV 中為多行文字（同一單位可涵蓋多個行政區），機構喘息固定「全區」
        service_area = (row.get("服務區域", "") or "").strip().replace("\n", "、").replace("\r", "")
        records.append([
            category,                                    # 0 category
            name,                                         # 1 name
            (row.get("負責人", "") or "").strip(),        # 2 contact
            (row.get("連絡電話", "") or "").strip(),      # 3 phone
            (row.get("傳真", "") or "").strip(),           # 4 fax
            (row.get("電子郵件", "") or "").strip(),      # 5 email
            county,                                        # 6 county
            district,                                       # 7 district
            service_area,                                    # 8 service_area
            addr,                                             # 9 address
        ])
    return records


def build_tyc_respite():
    """桃園市喘息服務提供單位（桃園市政府衛生局，DCAT dataset https://data.gov.tw/dataset/8572 ，
    dataset id 94332）。

    來源為兩份 CSV（TYC_RESPITE_HOME_URL 居家喘息、TYC_RESPITE_INST_URL 機構喘息），**編碼皆為
    BIG5(cp950)**，與 build_tyltc()/build_tyc_hospice() 同一例外，需 fetch(url, encoding="cp950")
    下載解碼。原始欄位（兩檔一致）：性質、資源彙整機關、辦理單位、成立日期、立案文號、負責人、
    連絡電話、傳真、電子郵件、地址、服務項目、服務區域、相關網址、X坐標、Y坐標、備註、最後更新時間。

    實測「性質」「成立日期」「立案文號」「相關網址」「備註」欄位全部為空白，本函式不採用；「負責人」
    「傳真」大多有值，予以保留。「服務項目」在居家喘息 CSV 固定為「居家喘息」、機構喘息 CSV 固定為
    「機構喘息」，作為 category 欄位。

    機構喘息 CSV 共153行，但尾端有大量僅含「資源彙整機關」欄位（值為「桃園市政府」）的空白列，本
    函式以「辦理單位」欄位非空過濾，實際有效資料為92筆；居家喘息 CSV 146筆皆為有效資料。

    **無經緯度座標**（X/Y坐標欄位全空），故本頁不含地圖。地址多數為「桃園市OO區」開頭，比照
    build_tyc_hospice() 用固定13區清單（TYC_DISTRICTS）解析（避免「平鎮區」等名稱誤判為「平鎮」），
    少數（居家/機構各2筆）位於新北市、新竹縣等桃園市以外縣市，改用 parse_county_district(strict=True)
    一般規則解析，詳見 _tyc_respite_parse_district()。

    「服務區域」欄位在居家喘息 CSV 為多行文字（同一居家喘息單位可同時涵蓋多個行政區，如「中壢區\\n
    楊梅區\\n大園區」），代表該單位實際服務範圍，比機構本身地址所在區更貼近使用者「我住OO區，哪些
    單位可服務我」的查詢情境；機構喘息 CSV 此欄位固定為「全區」。本函式將換行字元轉為頓號「、」
    後原文保留，前端「行政區」篩選會同時比對地址所在區與此欄位是否包含所選行政區。

    電話／傳真欄位格式不一（少數夾帶「分機」文字），原文照登不重新格式化。

    來源網址與同平台其他 opendata.tycg.gov.tw 資料集一致，CORS 僅允許該平台網域，改由本函式於
    伺服器端下載並輸出內嵌 JS 版本，避免依賴外部網址即時可用性。
    """
    print("下載 桃園市喘息服務提供單位（居家）...", file=sys.stderr)
    home_records = _tyc_respite_read_csv(TYC_RESPITE_HOME_URL, "居家喘息")
    print(f"  共 {len(home_records)} 筆", file=sys.stderr)
    print("下載 桃園市喘息服務提供單位（機構）...", file=sys.stderr)
    inst_records = _tyc_respite_read_csv(TYC_RESPITE_INST_URL, "機構喘息")
    print(f"  共 {len(inst_records)} 筆", file=sys.stderr)
    records = home_records + inst_records
    fields = [
        "category", "name", "contact", "phone", "fax", "email",
        "county", "district", "service_area", "address",
    ]
    return {"fields": fields, "rows": records}



# 2010（五都合併）／2014（桃園升格）前的舊縣名，看護機構名單偶爾沿用舊稱（如「台北縣」），
# 供 _caregiver_regions() 對應到現行縣市名稱。
CAREGIVER_OLD_NAME_ALIASES = {
    "臺北縣": "新北市", "桃園縣": "桃園市", "臺中縣": "臺中市",
    "臺南縣": "臺南市", "高雄縣": "高雄市",
}


def _caregiver_regions(text: str) -> list:
    """從看護機構「服務地區」自由文字欄位偵測涵蓋縣市：先將「台」正規化為「臺」，
    再依序比對：①舊縣名別名（如「臺北縣」對應「新北市」）②完整縣市名稱（如「新竹市」）
    ③去除「市／縣」字尾的簡稱（如「新竹」），對應到 CAREGIVER_REGIONS 中所有同名簡稱的縣市
    （新竹、嘉義因同時有市/縣兩個現行行政區，簡稱比對到時會同時列出兩者，屬已知限制，僅供參考）。
    找不到任何縣市（欄位空白或僅有模糊描述如「雙北」而未展開為個別縣市）時回傳空陣列。"""
    normalized = (text or "").strip().replace("台", "臺")
    found = []
    for old_name, region in CAREGIVER_OLD_NAME_ALIASES.items():
        if old_name in normalized and region not in found:
            found.append(region)
    for region in CAREGIVER_REGIONS:
        if region in normalized and region not in found:
            found.append(region)
    for region in CAREGIVER_REGIONS:
        stem = region.rstrip("市縣")
        if stem and stem in normalized and region not in found:
            found.append(region)
    return found


def build_caregivers():
    """看護／照服機構名錄（使用者人工蒐集網路公開資訊，非政府開放資料，無提供機關、無官方驗證）。

    原始 CSV 存放於 scripts/sources/caregiver/caregivers.csv（共27筆，欄位：名稱/網址/收費頁面/
    聯絡電話/服務地區/統一編號），此資料集無公開下載網址、非官方驗證資料，前端頁面會明確標示
    免責聲明。「服務地區」為自由文字且分隔符不一致（見 _caregiver_regions()），改用縣市清單子字串
    比對偵測，輸出 regions 陣列（可能為空陣列，代表原始欄位未填或無法辨識出具體縣市）；「聯絡電話」
    欄位偶有多餘換行/空白，逐一 strip 處理；僅3筆有填「統一編號」，其餘留空字串。
    未來如需更新資料，需人工以最新 CSV 覆蓋 scripts/sources/caregiver/caregivers.csv 後
    重新執行本腳本（`python3 scripts/build_data.py caregiver`）。

    額外欄位 google_rating／google_review_count／google_place_id：使用者需求為呈現各機構的
    Google 地圖星等與評論數，且明確表示「一次性資料，之後不會重新抓取」。本資料集與其他已套用
    此功能的資料集（如 tyc-elder）不同之處在於**沒有地址欄位**——這 27 筆是服務跨縣市的看護／
    照服仲介機構，並非單一實體地址的機構，故無法用「名稱＋地址」查詢，比對風險較高。

    資料來源：2026-08-08 用 scripts/fetch_google_ratings.py --dataset caregiver --name-field name
    --phone-field phone（僅用機構名稱查詢，並以 Place Details 的 international_phone_number
    交叉核對聯絡電話）一次性呼叫 Google Places API (Legacy) Text Search，取得比對結果後人工核對，
    整理成 data/source/caregiver-google-ratings.json（key 為「機構名稱」）。人工核對時除電話比對外，
    另外用 Place Details 的 website 欄位比對是否與 CSV「網址」欄位同網域，作為第二層交叉核對依據
    （電話與網域任一相符即視為可信），排除以下情況：
    - 多筆機構（照顧好居家照護／福家樂看護中心／仁安看護／善禾看護／全照護臨時看護／
      好照顧居家看護中心／瑞恩看護／亞力看護／照護家／安捷看護／平安家看護／安馨看護／優善看護）
      經電話與網域交叉核對後確認為誤配對（Google Text Search 因名稱過於通用，配對到完全不相關
      的地點，例如「照護家」「好照顧居家看護中心」皆被誤配對到「德宥居家長照」的 Google 地點）；
    - Home心、安康人力看護：Text Search 查無結果（ZERO_RESULTS）；
    - 仁安看護／惠順看護／兆福看護／天醫看護：雖電話或名稱部分相符，但 Google 回傳 rating 為
      None（無評分資料），比照「查無資料」處理予以排除；
    - 看護心：無電話/網域交叉核對證據支持，予以排除。
    保留的 15 筆機構（含長奕看護、德宥居家長照等）皆通過電話或官網網域至少一項交叉核對確認。
    查無對照資料的機構，此三欄留空字串，前端顯示為「-」。
    """
    print("讀取 看護／照服機構名錄 ...", file=sys.stderr)
    records = []
    try:
        with open(CAREGIVER_GOOGLE_RATINGS_FILE, "r", encoding="utf-8") as f:
            google_ratings = json.load(f)
    except FileNotFoundError:
        google_ratings = {}
    with open(CAREGIVER_CSV, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            name = (row.get("名稱") or "").strip()
            if not name:
                continue
            g = google_ratings.get(name, {})
            records.append([
                name,                                          # 0 name
                (row.get("網址") or "").strip(),              # 1 url
                (row.get("收費頁面") or "").strip(),          # 2 payUrl
                " / ".join(p.strip() for p in (row.get("聯絡電話") or "").split("\n") if p.strip()),  # 3 phone
                _caregiver_regions(row.get("服務地區")),        # 4 regions
                (row.get("統一編號") or "").strip(),          # 5 uid
                g.get("rating", ""),                            # 6 google_rating（一次性資料，查無留空字串）
                g.get("review_count", ""),                      # 7 google_review_count（同上）
                g.get("place_id", ""),                          # 8 google_place_id（同上，用於評論連結）
            ])
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["name", "url", "payUrl", "phone", "regions", "uid",
              "google_rating", "google_review_count", "google_place_id"]
    return {"fields": fields, "rows": records}


def build_dialysis_transport():
    """洗腎（透析）接送資源清單（使用者人工蒐集網路公開資訊，非政府開放資料，無提供機關、無官方驗證）。

    原始 CSV 存放於 scripts/sources/dialysis-transport/dialysis-transport.csv（共15筆，欄位：
    名稱/網址/聯絡電話/服務地區），性質與 build_caregivers() 相同，皆為使用者自行整理之民間資源
    清單，前端頁面會明確標示免責聲明。「服務地區」欄位極度稀疏（15筆僅5筆有填：新竹、基隆、屏東、
    彰化），資料量過小不足以做縣市正規化／篩選下拉，直接保留原始字串（空白則為空字串，前端顯示
    「—」），不比照 caregiver 的 regions 陣列偵測。「聯絡電話」欄位偶有多餘空白、tab 字元（來自
    原始試算表複製貼上），逐一 strip 後輸出；部分欄位含分機或以其他符號分隔多組電話，原文照登
    不重新拆分。

    頁面另有一段「長照交通接送服務制度說明」（BD03 社區式服務交通接送／DA01 交通接送給付碼別），
    文字來源為衛福部長期照顧司於 1966 長照專區之公告頁 https://1966.gov.tw/LTC/cp-6452-69937-207.html
    （建檔日期 111-06-10、更新時間 114-10-23），該頁僅為公告內容非可下載 CSV/JSON，故不進入本
    自動下載流程，僅作為頁面「制度說明」段落之引用來源連結。

    未來如需更新民間接送清單，需人工以最新 CSV 覆蓋
    scripts/sources/dialysis-transport/dialysis-transport.csv 後重新執行本腳本
    （`python3 scripts/build_data.py dialysis-transport`）。
    """
    print("讀取 洗腎（透析）接送資源清單 ...", file=sys.stderr)
    records = []
    with open(DIALYSIS_TRANSPORT_CSV, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            name = (row.get("名稱") or "").strip()
            if not name:
                continue
            phone_raw = (row.get("聯絡電話") or "").replace("\t", " ")
            phone = " / ".join(p.strip() for p in phone_raw.split("/") if p.strip())
            records.append([
                name,                                     # 0 name
                (row.get("網址") or "").strip(),          # 1 url
                phone,                                     # 2 phone
                (row.get("服務地區") or "").strip(),      # 3 serviceArea
            ])
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["name", "url", "phone", "serviceArea"]
    return {"fields": fields, "rows": records}


    """去除 PDF 儲存格內因欄寬過窄產生的換行，並還原被誤用的 CJK 部首符號為正常漢字。"""
    if not s:
        return ""
    chars = [SPECIALTY_RADICAL_MAP.get(ord(ch), ch) for ch in s]
    return "".join(chars).replace("\n", "").strip()


def _specialty_phone(s):
    """合併電話欄位跨行內容：緊接在數字/連字號後的『轉』分機直接接續，
    否則視為另一組聯絡電話，以『 / 』分隔。"""
    if not s:
        return ""
    segs = [seg for seg in s.split("\n") if seg]
    if not segs:
        return ""
    merged = [segs[0]]
    for seg in segs[1:]:
        prev = merged[-1]
        if seg.startswith("轉") or seg.startswith("#") or prev.endswith("-") or prev.endswith("轉"):
            merged[-1] = prev + seg
        else:
            merged.append(seg)
    return _specialty_norm(" / ".join(merged))


def build_specialty():
    """臺北市長照專業服務特約單位（臺北市政府衛生局公告 PDF 附件，非開放資料 API，
    需將最新 PDF 存於 data/source/tp-ltc-specialty-*.pdf 後才能解析，詳見 README）。"""
    matches = sorted(glob.glob(SPECIALTY_PDF_GLOB))
    if not matches:
        print(f"  找不到來源 PDF（{SPECIALTY_PDF_GLOB}），略過此資料集", file=sys.stderr)
        return None
    pdf_path = matches[-1]
    print(f"解析 臺北市長照專業服務特約單位 PDF：{pdf_path} ...", file=sys.stderr)
    import pdfplumber  # 延遲載入：僅此資料集需要，避免其他資料集重跑時強制安裝

    records = []
    cap_keys = list(CAPABILITY_LABELS.keys())
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            if not tables:
                continue
            for row in tables[0]:
                # 每個機構固定佔用最後 16 個欄位（序號 + 6 項基本資料 + 8 項服務能力 + 1 個尾端空欄），
                # 前面欄數會因跨頁合併儲存格數量不同而變動，故一律用負索引定位。
                if len(row) < 16:
                    continue
                raw_id = (row[-16] or "").replace("\n", "").strip()
                if not raw_id.isdigit():
                    continue
                caps = [1 if (row[i] or "").strip() == "V" else 0 for i in range(-9, -1)]
                records.append([
                    int(raw_id),                       # 0 id
                    _specialty_norm(row[-15]),          # 1 name
                    _specialty_norm(row[-14]),          # 2 district
                    _specialty_norm(row[-13]),          # 3 zipcode
                    _specialty_norm(row[-12]),          # 4 address
                    _specialty_phone(row[-11]),         # 5 phone
                    _specialty_norm(row[-10]),          # 6 contact
                ] + caps)
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["id", "name", "district", "zipcode", "address", "phone", "contact"] + cap_keys
    return {"fields": fields, "capabilityLabels": CAPABILITY_LABELS, "rows": records}


def build_tn_denture():
    """臺南市115年度長者免費裝置全口活動假牙計畫合約醫療院所名單（臺南市政府衛生局公告 PDF，
    非 DCAT 開放資料 CSV/API）。

    來源網址 TN_DENTURE_PDF_URL（health.tainan.gov.tw/warehouse/.../F_1780645430477e.pdf，PDF 標題
    內註記「1150305更新」）本身即為可直接下載的檔案（非公告網頁轉址），故與 build_specialty() 不同，
    本函式**直接於伺服器端自動下載並解析**，不需比照該函式將 PDF 存成 data/source/*.pdf 供人工更新；
    若未來此網址改版失效或格式變動，需重新確認來源網址並視需要改回人工下載模式。

    用 pdfplumber 解析 6 頁 PDF，每頁各含一張延續同一份表格的 table（僅第1頁表頭列含「編號」文字，
    其餘頁無重複表頭），欄位固定為：編號、地區、合約牙科醫療院所名稱、地址、電話，共161筆，與
    PDF 內文字內容一致，無需修正錯字或缺漏。

    「地區」欄位本身已是乾淨的「臺南市OO區」格式（涵蓋28個行政區），與地址欄位開頭一致，直接
    當作 district 使用；county 固定為「臺南市」，不需另外解析。無「機構類型」欄位（原始資料未提供
    分類資訊，不比照 build_tyc_denture() 做啟發式推斷），也無經緯度座標，故本頁不含地圖。
    """
    print("下載 臺南市長者免費裝置全口活動假牙計畫合約醫療院所 PDF ...", file=sys.stderr)
    import pdfplumber  # 延遲載入：僅此資料集需要，避免其他資料集重跑時強制安裝

    data = fetch_bytes(TN_DENTURE_PDF_URL)
    records = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                for row in table:
                    row = row + [""] * (5 - len(row))
                    rid = (row[0] or "").replace("\n", "").strip()
                    if not rid.isdigit():
                        continue  # 跳過表頭列（編號欄位為「編號」文字）與標題列
                    records.append([
                        rid,                                              # 0 id
                        (row[1] or "").replace("\n", "").strip(),          # 1 district
                        (row[2] or "").replace("\n", "").strip(),          # 2 name
                        (row[3] or "").replace("\n", "").strip(),          # 3 address
                        (row[4] or "").replace("\n", "").strip(),          # 4 phone
                    ])
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["id", "district", "name", "address", "phone"]
    return {"fields": fields, "rows": records}


def _kcg_denture_type(name: str) -> str:
    """依「機構名稱」關鍵字啟發式推斷機構類型（醫院／衛生所／醫療站／牙醫診所），
    非官方分類欄位，僅供前端篩選/圖表參考。"""
    name = name or ""
    if "醫院" in name:
        return "醫院"
    if "衛生所" in name:
        return "衛生所"
    if "醫療站" in name or "醫療服務站" in name:
        return "醫療站"
    return "牙醫診所"


def build_kcg_denture():
    """115年高雄市免費裝假牙特約牙醫醫療院所名冊（高雄市政府衛生局公告 PDF，
    非 DCAT 開放資料 CSV/API）。

    來源 PDF：KCG_DENTURE_PDF_URL
    （orgws.kcg.gov.tw/001/KcgOrgUploadFiles/463/RelFile/0/85588/23687658-8121-4268-8bf3-8def3a1e1bf8.pdf），
    2026-07-29 下載確認，共 8 頁：第1頁與第2~7頁為「行政區 × 機構名稱/電話/地址」表格（每頁2欄×2列，
    共4個行政區區塊，最後一頁僅2個區塊），第8頁為「注意事項」7條文字說明（申請資格、篩檢期間地點、
    保固/維修規定、諮詢電話等），該頁不含結構化資料，其文字內容改為人工節錄後寫入
    `kcg-denture/index.html` 的靜態說明區塊，不進入本函式的資料處理。

    **關鍵限制（務必先讀）**：此 PDF 的表格文字為「向量繪製曲線」而非可選取文字（常見政府文件防拷貝
    手法）——用 pdfplumber 檢測全頁 `chars` 數為 0，`extract_tables()`/`extract_text()` 皆無法取得任何
    內容；環境亦無 OCR（tesseract）可用。因此**無法比照 build_tn_denture()/build_specialty() 用程式自動
    解析文字**，改用「pdfplumber 將每頁渲染成圖片 + AI 視覺閱讀」的方式，人工逐頁確認全部 34 個行政區、
    189 筆機構資料（機構名稱／電話／地址），一次性轉寫為 KCG_DENTURE_MANUAL_JSON
    （data/source/kcg-denture-manual.json，格式為 `[{district, name, phone, address}, ...]`），本函式僅
    負責讀取該檔案並加上啟發式機構類型欄位、组装成標準 `{fields, rows}` 結構，**不會**重新下載/重新解析
    PDF 本身。

    後續影響：
    1. 若使用者要更新此名冊（如次年度 116 年版），需提供新版 PDF 連結，重新走一次「下載 → pdfplumber
       渲染成圖片 → AI 視覺閱讀轉寫 → 覆寫 KCG_DENTURE_MANUAL_JSON」的人工流程，無法單純重跑
       `python3 scripts/build_data.py kcg-denture` 自動取得最新資料。
    2. 轉寫結果建議人工抽樣核對（已抽查三民區32筆、苓雅區13筆等與原圖比對一致）。
    3. 原始 PDF 僅涵蓋 34 個行政區（未列出高雄市其餘行政區，如那瑪夏區以外部分偏遠區僅1~3筆），
       屬公告名冊原始範圍，非解析遺漏，如實呈現不另行標記。
    4. 地址欄位皆為「OO區＋路名門牌」，未含「高雄市」字首；電話欄位少數含分機（如「#7003補綴科」）
       或「及」「、」分隔多組分機，原文照登，前端 tel: 連結僅取第一組數字。

    「機構類型」由 `_kcg_denture_type()` 依名稱關鍵字（醫院／衛生所／醫療站）啟發式判斷，其餘歸類
    「牙醫診所」，非官方分類欄位。無經緯度座標，故本頁不含地圖。
    """
    print("讀取 115年高雄市免費裝假牙特約牙醫醫療院所 人工轉寫資料 ...", file=sys.stderr)
    try:
        with open(KCG_DENTURE_MANUAL_JSON, "r", encoding="utf-8") as f:
            manual_records = json.load(f)
    except FileNotFoundError:
        print(f"  找不到人工轉寫資料（{KCG_DENTURE_MANUAL_JSON}），略過此資料集", file=sys.stderr)
        return None

    records = []
    for i, r in enumerate(manual_records, start=1):
        name = (r.get("name", "") or "").strip()
        records.append([
            i,                              # 0 id
            (r.get("district", "") or "").strip(),  # 1 district
            name,                            # 2 name
            _kcg_denture_type(name),         # 3 type
            (r.get("address", "") or "").strip(),   # 4 address
            (r.get("phone", "") or "").strip(),     # 5 phone
        ])
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["id", "district", "name", "type", "address", "phone"]
    return {"fields": fields, "rows": records}


def build_tyc_dementia_hospitals():
    """桃園市提供失智症診療服務醫院一覽表（DCAT dataset id 147710，桃園市政府衛生局）。

    來源：TYC_DEMENTIA_HOSPITALS_URL，CSV，BIG5 編碼；原始欄位：序號、醫院名稱、電話、地址。
    2026-08-10 試抓確認共 18 筆（不含表頭），無跳號、無空值。

    地址欄位格式為「郵遞區號＋縣市＋鄉鎮市區＋路名門牌」（如「330桃園市桃園區中山路1492號」），
    與 build_tyc_elder() 相同，比照該作法用固定 TYC_DISTRICTS 清單比對地址開頭取得行政區
    （不用共用 ADDR_RE 正規式，避免「平鎮區」等名稱中途含「鎮」字被誤判)。

    無經緯度座標，資料量小（18 筆），故本頁不含地圖，且比照 tyc-elder 用內嵌 js 版本輸出
    （js_var=TYC_DEMENTIA_HOSPITALS_DATA），前端不透過 fetch() 讀取 json。
    """
    print("下載 桃園市提供失智症診療服務醫院一覽表 ...", file=sys.stderr)
    text = fetch(TYC_DEMENTIA_HOSPITALS_URL, encoding="cp950")
    reader = csv.DictReader(io.StringIO(text))
    records = []
    for row in reader:
        addr = (row.get("地址", "") or "").strip()
        district = next((d for d in TYC_DISTRICTS if d in addr[:10]), "")
        records.append([
            row.get("序號", "").strip(),   # 0 id
            row.get("醫院名稱", "").strip(),  # 1 name
            row.get("電話", "").strip(),   # 2 phone
            addr,                            # 3 address
            district,                        # 4 district
        ])
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["id", "name", "phone", "address", "district"]
    return {"fields": fields, "rows": records}


def build_tpe_dementia_hospitals():
    """臺北市失智症診療機構名冊（臺北市政府衛生局公告）。

    **資料來源特殊性（務必先讀）**：使用者最初提供的本機 CSV「失智症篩檢合約醫院 (1).csv」經試抓
    確認實為「12區健康服務中心篩檢轉介窗口」名冊（12區僅11區填有合約醫院、北投區該欄位空白，
    與「失智症診療機構」標題不符），故**未採用該 CSV**，僅記錄於此供留存追蹤。改用使用者提供的
    臺北市政府衛生局公告網頁 PDF 附件下載連結
    （`https://www-ws.gov.taipei/Download.ashx?u=...&n=5aSx5pm655eH6Ki655mC5qmf5qeLMDYxNS5wZGY%3d`，
    解碼檔名為「失智症診療機構0615.pdf」），內容為 34 家「失智症診療機構」，含醫院名稱、失智症看診
    科別、健保特約類別（醫學中心/區域醫院/地區醫院）、地址、電話，才是完整對應標題的名冊。此下載
    連結非開放資料平台（data.taipei）的標準 API/資源網址，而是衛生局公告網頁的動態下載連結，查無
    穩定的 DCAT dataset 頁面。PDF 已另存於 TPE_DEMENTIA_HOSPITALS_PDF
    （scripts/sources/tpe-dementia-hospitals/institution-list.pdf）。**日後如需更新此名冊**，需人工
    至臺北市政府衛生局公告頁面確認是否有新版 PDF，下載後覆蓋該檔案，再重新執行
    `python3 scripts/build_data.py tpe-dementia-hospitals`，無法自動重新下載。

    PDF 文字為可選取的一般文字（非向量繪製曲線圖形），`pdfplumber` 的 `extract_tables()` 可直接
    取得乾淨表格（單頁1個table，含表頭列「醫院名稱/失智症看診科別/健保特約類別/地址/電話」），不需
    比照 build_kcg_denture() 的「渲染成圖片+AI視覺閱讀」流程。

    2026-08-12 試抓確認共 34 筆（不含表頭），無跳號、無空值，各欄位皆完整。地址欄位皆為
    「臺北市＋行政區＋路名門牌」完整格式（如「臺北市士林區文昌路95號」），故沿用既有共用函式
    `parse_county_district(fallback_county="臺北市")` 即可解析出行政區，不需額外行政區清單或
    typo 修正。

    無經緯度座標，資料量小（34 筆），故本頁不含地圖，比照 tyc-dementia-hospitals／tyc-elder 慣例
    輸出內嵌 js 版本（js_var=TPE_DEMENTIA_HOSPITALS_DATA），前端不透過 fetch() 讀取 json。
    """
    print("讀取 臺北市失智症診療機構名冊 本地 PDF ...", file=sys.stderr)
    import pdfplumber  # 延遲載入：僅此資料集需要，避免其他資料集重跑時強制安裝

    records = []
    with pdfplumber.open(TPE_DEMENTIA_HOSPITALS_PDF) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                for row in table:
                    row = row + [""] * (5 - len(row))
                    name, department, level, addr, phone = row[:5]
                    name = (name or "").replace("\n", "").strip()
                    if not name or name in ("醫院名稱", "失智症診療機構"):
                        continue  # 跳過表頭列與頁首標題列
                    department = (department or "").replace("\n", "").strip()
                    level = (level or "").replace("\n", "").strip()
                    addr = (addr or "").replace("\n", "").strip()
                    phone = (phone or "").replace("\n", "").strip()
                    _, district = parse_county_district(addr, fallback_county="臺北市")
                    records.append([
                        len(records) + 1,  # 0 id
                        name,               # 1 name
                        department,         # 2 department
                        level,              # 3 level
                        addr,               # 4 address
                        phone,              # 5 phone
                        district,           # 6 district
                    ])
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["id", "name", "department", "level", "address", "phone", "district"]
    return {"fields": fields, "rows": records}


def _to_int(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0


DATASETS = [
    {
        "key": "abc",
        "builder": build_abc,
        "json": "data/abc.json",
        "js_var": None,
        "meta_key": "abc",
        "title": "長照ABC據點",
        "source": lambda: ABC_URL,
    },
    {
        "key": "lane",
        "builder": build_lane,
        "json": "data/lane.json",
        "js_var": None,
        "meta_key": "lane",
        "title": "巷弄長照站",
        "source": lambda: LANE_URL,
    },
    {
        "key": "tyc-elder",
        "builder": build_tyc_elder,
        "json": "data/tyc-elder.json",
        "js_var": "TYC_ELDER_DATA",
        "meta_key": "tycElder",
        "title": "桃園市老人福利機構一覽表",
        "source": lambda: TYC_ELDER_URL,
    },
    {
        "key": "specialty",
        "builder": build_specialty,
        "json": "data/specialty.json",
        "js_var": "SPECIALTY_DATA",
        "meta_key": "specialty",
        "title": "臺北市長照專業服務特約單位",
        "source": lambda: SPECIALTY_SOURCE_PAGE,
        "optional": True,
    },
    {
        "key": "kcg-homecare",
        "builder": build_kcg_homecare,
        "json": "data/kcg-homecare.json",
        "js_var": "KCG_HOMECARE_DATA",
        "meta_key": "kcgHomecare",
        "title": "銀髮族服務-居家長照機構",
        "source": lambda: KCG_HOMECARE_URL,
    },
    {
        "key": "hsc-ltc",
        "builder": build_hsc_ltc,
        "json": "data/hsc-ltc.json",
        "js_var": "HSC_LTC_DATA",
        "meta_key": "hscLtc",
        "title": "新竹縣長照機構名冊",
        "source": lambda: HSC_LTC_URL,
    },
    {
        "key": "yl-ltc",
        "builder": build_yl_ltc,
        "json": "data/yl-ltc.json",
        "js_var": "YL_LTC_DATA",
        "meta_key": "ylLtc",
        "title": "宜蘭縣立案老人長期照顧及安養機構名冊",
        "source": lambda: YL_LTC_URL,
    },
    {
        "key": "yl-denture",
        "builder": build_yl_denture,
        "json": "data/yl-denture.json",
        "js_var": "YL_DENTURE_DATA",
        "meta_key": "ylDenture",
        "title": "115年度宜蘭縣中低收入戶老人假牙裝置補助特約牙醫醫療院所",
        "source": lambda: YL_DENTURE_PDF_URL,
    },
    {
        "key": "hccg-elder",
        "builder": build_hccg_elder,
        "json": "data/hccg-elder.json",
        "js_var": "HCCG_ELDER_DATA",
        "meta_key": "hccgElder",
        "title": "新竹市老人福利機構一覽表",
        "source": lambda: HCCG_ELDER_URL,
    },
    {
        "key": "tn-homecare-nursing",
        "builder": build_tn_homecare_nursing,
        "json": "data/tn-homecare-nursing.json",
        "js_var": "TN_HOMECARE_NURSING_DATA",
        "meta_key": "tnHomecareNursing",
        "title": "臺南市居家護理機構",
        "source": lambda: TN_HOMECARE_NURSING_URL,
    },
    {
        "key": "tc-nursing",
        "builder": build_tc_nursing,
        "json": "data/tc-nursing.json",
        "js_var": "TC_NURSING_DATA",
        "meta_key": "tcNursing",
        "title": "臺中市一般護理之家清冊",
        "source": lambda: TC_NURSING_URL,
    },
    {
        "key": "ntpc-nursing",
        "builder": build_ntpc_nursing,
        "json": "data/ntpc-nursing.json",
        "js_var": "NTPC_NURSING_DATA",
        "meta_key": "ntpcNursing",
        "title": "新北市一般護理之家清冊",
        "source": lambda: NTPC_NURSING_URL_TEMPLATE.format(page=0),
    },
    {
        "key": "ntpc-silver-hair-club",
        "builder": build_ntpc_silver_hair_club,
        "json": "data/ntpc-silver-hair-club.json",
        "js_var": "NTPC_SILVER_HAIR_CLUB_DATA",
        "meta_key": "ntpcSilverHairClub",
        "title": "新北市銀髮俱樂部",
        "source": lambda: NTPC_SILVER_HAIR_CLUB_URL,
    },
    {
        "key": "chiayi-ltc",
        "builder": build_chiayi_ltc,
        "json": "data/chiayi-ltc.json",
        "js_var": "CHIAYI_LTC_DATA",
        "meta_key": "chiayiLtc",
        "title": "嘉義縣立案長照及護理之家機構一覽",
        "source": lambda: CHIAYI_LTC_SOURCE_PAGE,
    },
    {
        "key": "pingtung-ltc",
        "builder": build_pingtung_ltc,
        "json": "data/pingtung-ltc.json",
        "js_var": "PINGTUNG_LTC_DATA",
        "meta_key": "pingtungLtc",
        "title": "屏東縣老人長期照顧機構",
        "source": lambda: PINGTUNG_LTC_URL,
    },
    {
        "key": "tc-transport",
        "builder": build_tc_transport,
        "json": "data/tc-transport.json",
        "js_var": "TC_TRANSPORT_DATA",
        "meta_key": "tcTransport",
        "title": "臺中市失能者交通接送服務",
        "source": lambda: TC_TRANSPORT_URL,
    },
    {
        "key": "tc-dementia",
        "builder": build_tc_dementia,
        "json": "data/tc-dementia.json",
        "js_var": "TC_DEMENTIA_DATA",
        "meta_key": "tcDementia",
        "title": "臺中市失智症服務及資源提供單位",
        "source": lambda: TC_DEMENTIA_URL,
    },
    {
        "key": "tyltc",
        "builder": build_tyltc,
        "json": "data/tyltc.json",
        "js_var": "TYLTC_DATA",
        "meta_key": "tyltc",
        "title": "桃園市長期照護專業服務特約單位",
        "source": lambda: TYLTC_URL,
    },
    {
        "key": "tyc-denture",
        "builder": build_tyc_denture,
        "json": "data/tyc-denture.json",
        "js_var": "TYC_DENTURE_DATA",
        "meta_key": "tycDenture",
        "title": "桃園市長者裝置活動假牙合約醫療院所",
        "source": lambda: TYC_DENTURE_URL,
    },
    {
        "key": "tyc-disability-hospitals",
        "builder": build_tyc_disability_hospitals,
        "json": "data/tyc-disability-hospitals.json",
        "js_var": None,
        "meta_key": "tycDisabilityHospitals",
        "title": "桃園市身心障礙類別、向度之鑑定醫院名冊",
        "source": lambda: TYC_DISABILITY_HOSPITALS_URL,
    },
    {
        "key": "tyc-placement",
        "builder": build_tyc_placement,
        "json": "data/tyc-placement.json",
        "js_var": "TYC_PLACEMENT_DATA",
        "meta_key": "tycPlacement",
        "title": "桃園市失能老人接受長期照顧機構服務暨老人保護安置機構名冊",
        "source": lambda: TYC_PLACEMENT_URL,
    },
    {
        "key": "tpe-denture",
        "builder": build_tpe_denture,
        "json": "data/tpe-denture.json",
        "js_var": "TPE_DENTURE_DATA",
        "meta_key": "tpeDenture",
        "title": "臺北市假牙補助醫療院所名單",
        "source": lambda: TPE_DENTURE_URL,
    },
    {
        "key": "tyc-transport",
        "builder": build_tyc_transportation,
        "json": "data/tyc-transport.json",
        "js_var": "TYC_TRANSPORT_DATA",
        "meta_key": "tycTransport",
        "title": "桃園市長照交通接送服務單位",
        "source": lambda: TYC_TRANSPORT_URL,
    },
    {
        "key": "tyc-hospice",
        "builder": build_tyc_hospice,
        "json": "data/tyc-hospice.json",
        "js_var": "TYC_HOSPICE_DATA",
        "meta_key": "tycHospice",
        "title": "桃園市社區安寧療護資源一覽表",
        "source": lambda: TYC_HOSPICE_URL,
    },
    {
        "key": "tyc-respite",
        "builder": build_tyc_respite,
        "json": "data/tyc-respite.json",
        "js_var": "TYC_RESPITE_DATA",
        "meta_key": "tycRespite",
        "title": "桃園市喘息服務提供單位",
        "source": lambda: TYC_RESPITE_HOME_URL,
    },
    {
        "key": "caregiver",
        "builder": build_caregivers,
        "json": "data/caregiver.json",
        "js_var": "CAREGIVER_DATA",
        "meta_key": "caregiver",
        "title": "看護／照服機構名錄",
        "source": lambda: "使用者人工蒐集網路公開資訊（非政府開放資料，無官方驗證）",
    },
    {
        "key": "dialysis-transport",
        "builder": build_dialysis_transport,
        "json": "data/dialysis-transport.json",
        "js_var": "DIALYSIS_TRANSPORT_DATA",
        "meta_key": "dialysisTransport",
        "title": "洗腎（透析）接送資源清單",
        "source": lambda: "使用者人工蒐集網路公開資訊（非政府開放資料，無官方驗證）",
    },
    {
        "key": "tn-denture",
        "builder": build_tn_denture,
        "json": "data/tn-denture.json",
        "js_var": "TN_DENTURE_DATA",
        "meta_key": "tnDenture",
        "title": "臺南市長者免費裝置全口活動假牙計畫合約醫療院所",
        "source": lambda: TN_DENTURE_PDF_URL,
    },
    {
        "key": "kcg-denture",
        "builder": build_kcg_denture,
        "json": "data/kcg-denture.json",
        "js_var": "KCG_DENTURE_DATA",
        "meta_key": "kcgDenture",
        "title": "115年高雄市免費裝假牙特約牙醫醫療院所",
        "source": lambda: KCG_DENTURE_PDF_URL,
        "optional": True,
    },
    {
        "key": "hsc-denture",
        "builder": build_hsc_denture,
        "json": "data/hsc-denture.json",
        "js_var": "HSC_DENTURE_DATA",
        "meta_key": "hscDenture",
        "title": "新竹縣中低收入老人補助裝置假牙特約醫療院所",
        "source": lambda: HSC_DENTURE_URL,
    },
    {
        "key": "chc-denture",
        "builder": build_chc_denture,
        "json": "data/chc-denture.json",
        "js_var": "CHC_DENTURE_DATA",
        "meta_key": "chcDenture",
        "title": "彰化縣補助65歲以上老人裝置全口假牙契約診所名冊",
        "source": lambda: CHC_DENTURE_URL,
    },
    {
        "key": "hl-denture",
        "builder": build_hl_denture,
        "json": "data/hl-denture.json",
        "js_var": "HL_DENTURE_DATA",
        "meta_key": "hlDenture",
        "title": "花蓮縣115年度65歲以上長者假牙補助合約醫療院所",
        "source": lambda: HL_DENTURE_PDF,
    },
    {
        "key": "pingtung-denture",
        "builder": build_pingtung_denture,
        "json": "data/pingtung-denture.json",
        "js_var": "PINGTUNG_DENTURE_DATA",
        "meta_key": "pingtungDenture",
        "title": "屏東縣115年長者假牙裝置補助合作醫療院所",
        "source": lambda: PINGTUNG_DENTURE_PDF,
    },
    {
        "key": "tc-denture",
        "builder": build_tc_denture,
        "json": "data/tc-denture.json",
        "js_var": "TC_DENTURE_DATA",
        "meta_key": "tcDenture",
        "title": "臺中市65歲以上銀髮族假牙裝置補助計畫合約院所",
        "source": lambda: "使用者手動提供 Google 試算表匯出 CSV（原始資料，非官方開放資料 API）",
    },
    {
        "key": "chiayi-denture",
        "builder": build_chiayi_denture,
        "json": "data/chiayi-denture.json",
        "js_var": "CHIAYI_DENTURE_DATA",
        "meta_key": "chiayiDenture",
        "title": "嘉義市假牙補助合約醫療院所（中低收入／一般身分別）",
        "source": lambda: f"{CHIAYI_DENTURE_LOW_INCOME_URL} ; {CHIAYI_DENTURE_GENERAL_PDF_URL}",
    },
    {
        "key": "tyc-dementia-hospitals",
        "builder": build_tyc_dementia_hospitals,
        "json": "data/tyc-dementia-hospitals.json",
        "js_var": "TYC_DEMENTIA_HOSPITALS_DATA",
        "meta_key": "tycDementiaHospitals",
        "title": "桃園市提供失智症診療服務醫院一覽表",
        "source": lambda: TYC_DEMENTIA_HOSPITALS_URL,
    },
    {
        "key": "tpe-dementia-hospitals",
        "builder": build_tpe_dementia_hospitals,
        "json": "data/tpe-dementia-hospitals.json",
        "js_var": "TPE_DEMENTIA_HOSPITALS_DATA",
        "meta_key": "tpeDementiaHospitals",
        "title": "臺北市失智症診療機構名冊",
        "source": lambda: "臺北市政府衛生局公告（PDF附件，非開放資料平台標準API）",
    },
]

DATASET_KEYS = [d["key"] for d in DATASETS]


def _write_dataset(dataset, data):
    """寫出單一資料集的 json（一律）與內嵌 js（若有設定 js_var）。"""
    with open(dataset["json"], "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    if dataset["js_var"]:
        js_path = dataset["json"][:-len(".json")] + ".js"
        with open(js_path, "w", encoding="utf-8") as f:
            f.write(f"window.{dataset['js_var']} = ")
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
            f.write(";\n")


def main(argv=None):
    """執行資料建置。

    預設（不帶參數）會重新下載並轉換**全部**資料集，這是較耗時、且會對外發送多個網路請求的
    完整流程，僅在明確需要「全面更新」時才執行。

    若只是新增/調整單一資料集（例如剛新增一個 build_xxx()），可指定資料集 key 只重跑該資料集，
    不影響其他資料集的 json/js 輸出，也不會覆寫 meta.json 中其他資料集的既有紀錄：

        python3 scripts/build_data.py chiayi-ltc
        python3 scripts/build_data.py tc-nursing ntpc-nursing   # 可同時指定多個

    可用的 key 清單：見 DATASET_KEYS（等同各資料集 data/<key>.json 的檔名）。
    """
    parser = argparse.ArgumentParser(
        description=main.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "datasets",
        nargs="*",
        choices=DATASET_KEYS,
        metavar="dataset",
        help=(
            "只重新產生指定資料集（可指定多個，以空白分隔）。"
            f"可用值：{', '.join(DATASET_KEYS)}。不帶此參數則重新產生全部資料集。"
        ),
    )
    args = parser.parse_args(argv)

    selected_keys = args.datasets or DATASET_KEYS
    full_run = not args.datasets
    if full_run:
        print("未指定資料集，將重新產生全部資料集（完整流程，耗時較久）...", file=sys.stderr)
    else:
        print(f"僅重新產生指定資料集：{', '.join(selected_keys)}", file=sys.stderr)

    try:
        with open("data/meta.json", "r", encoding="utf-8") as f:
            meta = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        meta = {}

    for dataset in DATASETS:
        if dataset["key"] not in selected_keys:
            continue
        data = dataset["builder"]()
        if data is None:
            if dataset.get("optional"):
                continue
            print(f"警告：{dataset['key']} 未產生資料，略過寫入", file=sys.stderr)
            continue
        _write_dataset(dataset, data)
        meta[dataset["meta_key"]] = {
            "count": len(data["rows"]),
            "source": dataset["source"](),
            "title": dataset["title"],
        }

    meta["generatedAt"] = datetime.now(timezone.utc).isoformat()
    with open("data/meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print("完成！", file=sys.stderr)


if __name__ == "__main__":
    main()
