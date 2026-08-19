# 政府開放資料儀表板

以政府開放資料建置的靜態網站，整理四十二個長照/老人福利/身心障礙相關資料集為互動式儀表板，可直接部署於 GitHub Pages。

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
| `yl-denture/` | 115年度宜蘭縣中低收入戶老人假牙裝置補助特約牙醫醫療院所 | 宜蘭縣政府社會處 | 宜蘭縣中低收入戶老人假牙裝置補助實施計畫特約牙醫醫療院所名單，共29筆，收錄編號、縣市、鄉鎮市、機構名稱、地址、電話與 Google Map 星等、評論數，並整理申請資格、補助態樣與最高補助金額對照表（含流程圖）、申請流程、應備文件、洽詢單位等說明；「機構類型」（醫院／衛生所／牙醫診所）由名稱關鍵字啟發式推斷（非官方分類），其中3筆為跨縣市花蓮縣特約醫院，提供縣市／鄉鎮市／機構類型／關鍵字篩選與統計圖表，無經緯度座標。來源為社會處公告 PDF（非開放資料 CSV/API），由 `build_yl_denture()` 自動下載解析，Google 星等/評論數為一次性快照（2026-08-07） |
| `hccg-elder/` | 新竹市老人福利機構一覽表 | 新竹市政府社會處 | 新竹市立案老人福利機構清單，含經緯度座標，於地圖上呈現，並提供行政區／收容對象／關鍵字篩選與統計圖表 |
| `tn-homecare-nursing/` | 臺南市居家護理機構 | 臺南市政府衛生局 | 臺南市各行政區居家護理所清單（114年度），提供行政區／關鍵字篩選與統計圖表 |
| `tc-nursing/` | 臺中市一般護理之家清冊 | 臺中市政府衛生局 | 臺中市各行政區一般護理之家清單，含一般床／呼吸器依賴床許可與開放床數、評鑑結果、督考結果，提供行政區／關鍵字篩選與統計圖表 |
| `ntpc-nursing/` | 新北市一般護理之家清冊 | 新北市政府衛生局 | 新北市各行政區一般護理之家清單，含地址、聯絡人、電話、開放床數、機構應配置護理人員數，提供行政區／關鍵字篩選與統計圖表 |
| `ntpc-silver-hair-club/` | 新北市銀髮俱樂部 | 新北市政府社會局 | 新北市各行政區銀髮俱樂部據點清單，收錄名稱、地址、市話與手機聯絡電話，並提供官方網站與各據點活動查詢連結，提供行政區／關鍵字篩選與統計圖表，無經緯度座標 |
| `ntpc-dementia/` | 新北市失智症門診資訊 | 新北市政府衛生局 | 新北市各行政區提供失智症門診服務的醫院清單，共17筆，收錄醫院名稱、電話、地址，提供行政區／關鍵字篩選與統計圖表；原始經緯度座標欄位全數為0或空值，無地圖 |
| `chiayi-ltc/` | 嘉義縣立案長照及護理之家機構一覽 | 嘉義縣政府長期照護管理中心 | 合併嘉義縣立案住宿長照機構名單與護理之家名單，收錄機構類型、機構名稱、鄉鎮市、地址、電話、負責人、許可／開業床數，提供機構類型／鄉鎮市／關鍵字篩選與統計圖表。**資料來源為使用者提供之本機 CSV、無公開下載網址**，需人工更新，詳見下方「更新資料」說明 |
| `pingtung-ltc/` | 屏東縣老人長期照顧機構 | 屏東縣政府社會處 | 屏東縣老人長期照顧機構清單，收錄機構名稱、地址、電話，機構類型（養護型／失智型／未標示）由機構名稱解析而來，鄉鎮市由地址欄位解析，提供鄉鎮市／機構類型／關鍵字篩選與統計圖表，無經緯度座標 |
| `tc-transport/` | 臺中市失能者交通接送服務 | 臺中市政府衛生局 | 協助中重度失能者滿足以就醫及使用長期照顧服務為主要目的之交通服務需求，收錄辦理單位名稱、連絡電話、地址、服務區域，含經緯度座標（由原始 TWD97 TM2 平面座標換算），於地圖上呈現，並提供服務區域（多選）／辦理單位所在行政區／關鍵字篩選與統計圖表 |
| `tc-dementia/` | 臺中市失智症服務及資源提供單位 | 臺中市政府衛生局 | 臺中市失智照護服務計畫服務單位清單，共49筆，收錄失智共同照護中心、失智社區服務據點辦理單位名稱、連絡電話、電子郵件、地址，含經緯度座標（部分由原始 TWD97 TM2 平面座標換算，部分原始資料已為經緯度，本站依數值大小自動判斷格式），於地圖上呈現，並提供行政區／服務類型／關鍵字篩選與統計圖表 |
| `tyltc/` | 桃園市長期照護專業服務特約單位 | 桃園市政府衛生局 | 桃園市居家護理所、物理／職能治療所等長期照護專業服務特約單位清單，收錄機構名稱、負責人、電話、傳真、電子郵件、地址與最後更新時間；「服務類型」由機構名稱關鍵字啟發式推斷（非官方分類），部分機構地址位於新北市、臺北市等鄰近縣市，提供縣市／鄉鎮市區／服務類型／關鍵字篩選與統計圖表，無經緯度座標 |
| `tyc-denture/` | 桃園市長者裝置活動假牙合約醫療院所 | 桃園市政府衛生局 | 桃園市長者裝置活動假牙補助合約醫療院所（牙醫診所/醫院）清單，收錄特約單位名稱、區別、地址、電話，並整理補助對象、補助基準（部分/半口/全口活動假牙、假牙維修）與申請流程說明；「機構類型」由名稱關鍵字啟發式推斷（非官方分類），提供行政區／機構類型／關鍵字篩選與統計圖表，無經緯度座標 |
| `tyc-disability-hospitals/` | 桃園市身心障礙類別、向度之鑑定醫院名冊 | 桃園市政府衛生局 | 桃園市身心障礙「鑑定類別（第一類～第八類）×鑑定向度×17家醫院」勾選矩陣，本站展開為長格式（約623筆），收錄鑑定類別、向度、相關疾病類別、可鑑定醫院與備註條件（如年齡/疾病限制），提供鑑定類別／向度／醫院／關鍵字篩選與統計圖表，無地址、電話、經緯度座標 |
| `tyc-placement/` | 桃園市失能老人接受長期照顧機構服務暨老人保護安置機構名冊 | 桃園市政府社會局 | 115-116年失能老人公費安置機構簽約名冊，收錄約123筆機構名稱、電話、地址，機構多數位於桃園市但亦有少數位於新竹縣、花蓮縣、彰化縣、新北市、臺南市等縣市；「機構類型」由機構名稱結尾括號中以「型」結尾的文字解析（非官方分類），提供縣市／鄉鎮市區／機構類型／關鍵字篩選與統計圖表，無經緯度座標 |
| `tpe-denture/` | 臺北市假牙補助醫療院所名單 | 臺北市政府社會局 | 臺北市中低收入老人裝置假牙補助合約醫療院所名單，共6筆，全數為「臺北市立聯合醫院」不同分院，分布於5個行政區，並整理補助制度說明，提供行政區／關鍵字篩選與統計圖表，無經緯度座標 |
| `tyc-transport/` | 桃園市長照交通接送服務單位 | 桃園市政府社會局 | 桃園市長照交通接送服務單位清單，共14筆，收錄辦理單位名稱、連絡電話、地址、服務區域，辦理單位地址分布桃園市、臺北市、新北市等多個縣市，並整理洽辦單位、服務對象資格、一般服務地區與復興區偏遠地區補助金額說明，提供縣市／關鍵字篩選與統計圖表，無經緯度座標 |
| `tyc-hospice/` | 桃園市社區安寧療護資源一覽表 | 桃園市政府衛生局 | 桃園市社區安寧療護資源一覽表，收錄安寧病房、安寧共照、居家及社區安寧（居家護理所/診所/衛生所）共54筆機構名稱、電話、地址，並整理服務對象、服務內容、申請流程說明；「機構型態」由名稱關鍵字啟發式推斷（非官方分類，僅居家及社區安寧類別適用），提供行政區／服務類別／機構型態／關鍵字篩選與統計圖表，無經緯度座標 |
| `tyc-respite/` | 桃園市喘息服務提供單位 | 桃園市政府衛生局 | 桃園市居家喘息、機構住宿式喘息服務提供單位清單，共238筆（居家喘息146筆、機構喘息92筆），收錄單位名稱、負責人、電話、傳真、電子郵件、地址、服務區域，並整理服務對象與服務內容說明；「服務區域」欄位於居家喘息單位為涵蓋多個行政區的文字，行政區篩選會同時比對地址所在區與服務區域涵蓋區，提供服務類別／行政區／關鍵字篩選與統計圖表，無經緯度座標 |
| `tn-denture/` | 臺南市長者免費裝置全口活動假牙計畫合約醫療院所 | 臺南市政府衛生局 | 臺南市65歲以上長者及55歲以上原住民免費裝置全口活動假牙計畫的合約牙科醫療院所名單，共161筆，收錄編號、地區、機構名稱、地址、電話，並整理申請資格、補助金額（每人每顎上限2萬2,000元、全口雙顎上限4萬4,000元）、申請與核銷期程等說明，提供地區／關鍵字篩選與統計圖表，無經緯度座標。**資料來源為衛生局公告 PDF、非結構化 CSV/API**，由 build_data.py 自動下載並用 pdfplumber 解析 |
| `kcg-denture/` | 115年高雄市免費裝假牙特約牙醫醫療院所 | 高雄市政府衛生局 | 115年度免費裝假牙特約牙醫醫療院所名冊，共189筆，涵蓋34個行政區，收錄編號、行政區、機構名稱、地址、電話，並整理申請資格、篩檢期間地點、裝置期限、保固與維修規定、諮詢電話等說明；「機構類型」（醫院／衛生所／醫療站／牙醫診所）由名稱關鍵字啟發式推斷（非官方分類），提供行政區／機構類型／關鍵字篩選與統計圖表，無經緯度座標。**資料來源為衛生局公告 PDF，且 PDF 內文字為向量繪製圖形、無法程式化擷取文字**，改以人工視覺核對方式逐頁轉寫並寫死於 `data/source/kcg-denture-manual.json`，`build_kcg_denture()` 僅讀取該檔案組裝資料，**無法自動重新下載/解析更新**，需人工重新轉寫，詳見下方「更新資料」說明 |
| `hsc-denture/` | 新竹縣中低收入老人補助裝置假牙特約醫療院所 | 新竹縣政府社會處 | 中低收入老人補助裝置假牙特約醫療院所名冊，共7筆，收錄編號、鄉鎮市、機構名稱、負責人、地址、電話，並整理申請資格、補助內容/給付標準、申請方式/流程/期限、應備文件、承辦單位聯絡資訊等說明；「機構類型」（醫院／牙醫診所）由名稱是否含「醫院」關鍵字啟發式推斷（非官方分類），提供鄉鎮市／機構類型／關鍵字篩選與統計圖表，無經緯度座標。原始地址欄位不含「新竹縣」字首（僅郵遞區號＋鄉鎮市開頭），`build_hsc_denture()` 會移除郵遞區號並補上「新竹縣」前綴後解析鄉鎮市 |
| `chiayi-denture/` | 嘉義市假牙補助合約醫療院所（中低收入／一般身分別） | 嘉義市政府社會處長青及社會行政科 | 合併兩個各自獨立的嘉義市假牙補助方案合約診所名單，共59筆：「中低收入老人免費裝置假牙合約醫院名單」（DCAT機器可讀CSV，27筆，含經緯度座標，另依公告人工補登115年6月1日起新增之3家合約診所）與「115年度一般身分別老人補助裝置假牙合約院所」（社會處公告PDF，29筆，無座標），兩份名單有重疊但不完全相同，本站不做名稱比對合併，各筆保留原始來源方案標記（`program`欄位）；並整理兩方案的申請資格、應備文件、補助項目優先次序、通知單發放/補發流程與申請流程圖 Q&A。「機構類型」（醫院／牙醫診所）由名稱是否含「醫院」關鍵字啟發式推斷（非官方分類），提供方案／行政區／機構類型／關鍵字篩選、地圖（僅中低收入方案含座標）與統計圖表 |
| `chc-denture/` | 彰化縣補助65歲以上老人裝置全口假牙契約診所名冊 | 彰化縣政府社會處 | 彰化縣補助65歲以上老人裝置全口活動假牙契約診所名冊，共109筆，收錄編號、鄉鎮市、診所名稱、地址、電話，並整理申請資格、受理期間（每年3/1-9/30）、裝置態樣（全口/單上顎/單下顎活動假牙）、承辦單位聯絡資訊等說明；提供鄉鎮市／關鍵字篩選與統計圖表，無經緯度座標、無機構類型分類欄位。原始地址欄位不含「彰化縣」字首（僅鄉鎮市開頭），且來源 CSV 為 BIG5 編碼，`build_chc_denture()` 會補上「彰化縣」前綴解析鄉鎮市 |
| `tc-denture/` | 臺中市115年度65歲以上銀髮族假牙裝置補助計畫合約院所 | 臺中市政府衛生局 | 115年度65歲以上銀髮族假牙裝置補助計畫合約院所名單，共281筆，收錄編號、行政區、院所名稱、地址、電話，涵蓋27個行政區，並整理補助對象、申請期間、服務項目及給付金額、申請/初審/複審/製作假牙與核銷流程、其他身分別（低收入戶/原住民）轉介說明等說明；提供行政區／關鍵字篩選與統計圖表，另附 Google Map 星等／評論數（一次性抓取），無經緯度座標、無機構類型分類欄位。**資料來源為使用者手動提供之 Google 試算表匯出 CSV（非官方開放資料 API/CSV，無公開下載網址）**，`build_tc_denture()` 讀取本地已清理過的 `scripts/sources/tc-denture/tc-denture.csv`，無法自動重新抓取更新 |
| `hl-denture/` | 花蓮縣115年度65歲以上長者假牙補助合約醫療院所 | 花蓮縣政府社會處 | 花蓮縣115年度65歲以上長者假牙補助裝置醫療院所公開名單，共37筆，收錄編號、縣市、鄉鎮市、機構名稱、地址、電話與 Google Map 星等、評論數，並整理一般長者／中低收入戶等福利身分長者的申請資格、受理申請時間、應備文件、申請流程五步驟（含流程圖）、補助金額限制與常見問答 Q&A 等說明；「機構類型」（醫院／衛生所／牙醫診所）由名稱關鍵字啟發式推斷（非官方分類），其中1筆為跨縣市臺東縣特約診所，提供縣市／鄉鎮市／機構類型／關鍵字篩選與統計圖表，無經緯度座標。**資料來源為使用者手動提供之社會處公告 PDF（機構名單、申請流程圖、常見問答，皆非公開可下載之開放資料 CSV/API）**，`build_hl_denture()` 讀取本地已存放的 `scripts/sources/hl-denture/institution-list.pdf` 解析，無法自動重新下載更新，Google 星等/評論數為一次性快照（2026-08-08） |
| `pingtung-denture/` | 屏東縣115年長者假牙裝置補助合作醫療院所 | 屏東縣政府衛生局醫政科 | 屏東縣115年長者假牙裝置補助合作醫療院所名冊（115.3.18更新），共66筆（59筆「特約醫療院所」＋7筆「醫療站」，以 `category` 欄位保留原始分類並重新連續編號1~66），收錄編號、分類、縣市、鄉鎮市、機構名稱、地址、電話與 Google Map 星等、評論數，並整理服務對象資格、活動假牙／固定式假牙／假牙維修補助金額明細、申請流程五步驟、服務窗口等說明；「機構類型」（醫院／衛生所／醫療站／牙醫診所）由名稱關鍵字啟發式推斷（非官方分類），提供縣市／鄉鎮市／機構類型／分類／關鍵字篩選與統計圖表，無經緯度座標。**資料來源為使用者手動提供之衛生局公告 PDF 名冊（非公開可下載之開放資料 CSV/API），且屏東市地址不含「屏東縣」字首，改用固定行政區清單 `PINGTUNG_DISTRICTS` 解析鄉鎮市**，`build_pingtung_denture()` 讀取本地已存放的 `scripts/sources/pingtung-denture/institution-list.pdf` 解析，無法自動重新下載更新，Google 星等/評論數為一次性快照（2026-08-08，已人工核對地址/電話排除2筆誤配對） |
| `tyc-dementia-hospitals/` | 桃園市提供失智症診療服務醫院一覽表 | 桃園市政府衛生局 | 桃園市可提供失智症確診服務之醫院名冊，共18筆，收錄序號、醫院名稱、電話、地址，行政區由地址欄位解析（比照 `build_tyc_elder()` 用固定 `TYC_DISTRICTS` 清單比對），提供行政區／關鍵字篩選與統計圖表，無經緯度座標。頁面上方另收錄「認識失智症」十大警訊、常見症狀重點摘要與就醫建議（自撰摘要＋來源連結，整理自社團法人台灣失智症協會 https://www.cfad.org.tw/knowledge/37 ，非逐字轉貼），比照 tyc-elder 用內嵌 js 版本輸出 |
| `tpe-dementia-hospitals/` | 臺北市失智症診療機構名冊 | 臺北市政府衛生局 | 臺北市失智症診療機構名冊，共35筆，收錄醫院名稱、失智症看診科別、健保特約類別（醫學中心／區域醫院／地區醫院）、地址、電話，行政區由地址欄位解析（`parse_county_district(fallback_county="臺北市")`），提供行政區／健保特約類別／關鍵字篩選與統計圖表，無經緯度座標。頁面上方另收錄完整版「認識失智症」Q&A（定義、AD-8極早期篩檢量表、正常老化區別、預防方法【趨吉避凶】、三大類型【退化性—阿茲海默症/額顳葉型/路易氏體、血管性、其他原因引起之可逆性失智症】、年輕型失智症），內容整理自使用者提供之衛教資料。**資料來源為臺北市政府衛生局公告網頁 PDF 附件（非開放資料平台標準API），使用者原提供之 CSV 經試抓確認為不同性質的「篩檢轉介窗口」名冊而未採用**，比照 tyc-dementia-hospitals 用內嵌 js 版本輸出，無法自動重新下載，詳見下方「更新資料」說明 |
| `tpe-disability-hospitals/` | 115年臺北市身心障礙鑑定指定醫院及申請說明 | 臺北市政府衛生局 | 臺北市身心障礙鑑定指定醫院聯絡方式一覽表（DCAT dataset id 132448），共34筆，原始CSV共28個編號但編號7「臺北市立聯合醫院」本身僅為母機構分類標題（電話/地址空白，本腳本略過），其下7家分院（中興、仁愛、和平婦幼、陽明、忠孝、松德、林森(中醫)昆明院區）為正式資料列並依輸出順序重新編號，收錄醫院名稱、電話、地址，行政區由地址欄位解析（`parse_county_district(fallback_county="臺北市")`），提供行政區／關鍵字篩選與統計圖表，無經緯度座標。頁面上方收錄使用者提供之初次鑑定／重新鑑定／申請到宅鑑定應備文件清單與洽辦資訊（聯絡窗口、電話、傳真、洽辦單位：區公所社會課）Q&A，屬固定公告文字，比照 tpe-dementia-hospitals 用內嵌 js 版本輸出 |
| `tn-disability-hospitals/` | 115年臺南市身心障礙鑑定醫院及申請說明 | 臺南市政府衛生局 | 115年臺南市身心障礙鑑定醫院名冊（DCAT dataset id 147147），共16筆，來源CSV欄位為醫院名稱／鑑定類別／醫院電話／地址（另有一組CountyCode/AreaCode分欄格式等價distribution因需自行組回地址而捨棄），地址已含完整「(郵遞區號)台南市OO區OO路OO號」字串，county固定輸出正式全形「臺南市」（原文為簡體「台南市」），district由剝除郵遞區號後的地址解析；「鑑定類別」欄位額外近似解析出可辦理類別數字（1~8）清單供篩選/圖表使用（不解析括號除外備註細節，僅供粗略參考），提供行政區／鑑定類別／關鍵字篩選與統計圖表（各行政區醫院數、各鑑定類別可辦理醫院數），無經緯度座標。頁面上方收錄使用者提供之申請流程、到宅鑑定條件、應備文件與業務窗口/洽辦單位資訊Q&A，屬固定公告文字，來源網址無CORS標頭，比照 tpe-disability-hospitals 用內嵌 js 版本輸出 |
| `chiayi-disability-hospitals/` | 嘉義市身心障礙鑑定醫院及申請說明 | 嘉義市政府（醫政科） | 嘉義市身心障礙鑑定醫院（DCAT dataset id 95714），來源CSV欄位為醫院名稱／連絡電話／地址／新制鑑定類別及向度，實測共228列——逐「向度」子項一列（非逐醫院一列），涵蓋5家醫院；本腳本解析出類別數字(1~8)/類別全名/向度子項全名三段（另有「整體心理功能：發展遲緩」特例以"dev"標記），並依醫院彙整為5筆記錄（categories分號分隔類別清單、itemsByCategory為JSON字串記錄各類別向度子項清單、itemCount為向度總筆數），地址已含完整「嘉義市OO區」字首可直接解析行政區（僅東區/西區），無經緯度座標。提供鑑定類別／醫院／關鍵字篩選與統計圖表（各類別可辦理醫院數、各醫院可鑑定向度數量），表格以`<details>`展開完整向度明細。頁面上方收錄使用者提供之「身心障礙者鑑定流程報您知」完整公告文字（申請鑑定表/鑑定/到宅機構鑑定/審查製證/領證/異議複檢/鑑定費用/8大類別說明），來源網址無CORS標頭，比照 tn-disability-hospitals 用內嵌 js 版本輸出 |
| `tc-disability-hospitals/` | 臺中市身心障礙鑑定醫院及鑑定類別窗口 | 臺中市政府衛生局 | 臺中市33家新制身心障礙鑑定醫院清冊，來源為衛生局網站公告之兩份獨立PDF（**非DCAT開放資料CSV/API**）：一份為乾淨的窗口清冊（醫院層級／編號／名稱／一般鑑定窗口／居家鑑定窗口／電話），另一份為約46項「向度」子項（分屬第1~8類）的能力矩陣（每格v/無提供），本站僅將矩陣彙總至第1~8類層級（該類別下任一向度為v即視為可辦理，不保留46項向度細節）；兩份PDF醫院命名（全銜/簡稱、「臺」/「台」用字）與順序皆不同，改用人工核對之別名對照表配對，其中一份PDF「澄清復建醫院」對照另一份「澄清復健醫院」應為原始PDF錯字，忠實保留原文並於對照表修正供比對，提供醫院層級／鑑定類別／關鍵字篩選與統計圖表，無地址、無經緯度座標。頁面上方收錄使用者提供之申辦流程、應備物品、聯絡窗口資訊Q&A，屬固定公告文字，PDF需人工存放於`data/source/tc-disability-hospitals-*.pdf`後才能解析，無法自動重新下載更新，詳見下方「更新資料」說明 |
| `chc-disability-hospitals/` | 彰化縣身心障礙鑑定醫院及申請說明 | 彰化縣政府社會處 | 彰化縣身心障礙鑑定醫院名冊（DCAT dataset id 95224），共14筆，來源CSV欄位為項目／名稱／電話／地址縣市／地址鄉鎮市區／地址，DCAT標示編碼為**BIG5**（本腳本 fetch() 需另傳 `encoding="big5"`，預設 utf-8-sig 會整批解析失敗得到0筆）；「地址縣市」「地址鄉鎮市區」為行政區代碼非中文名稱，改用「地址」欄位以 `parse_county_district(fallback_county="彰化縣")` 解析，地址已含完整「彰化縣OO鄉鎮市」字首，無經緯度座標。提供鄉鎮市／關鍵字篩選與統計圖表（各鄉鎮市鑑定醫院數），頁面上方收錄使用者提供之「身心障礙證明申請（初次申請、屆期重鑑）」完整公告文字Q&A（申請對象／申請方式／郵寄申請／縣內跨鄉鎮市申請／進度查詢／效期延長／承辦單位聯絡資訊），屬固定公告文字，來源網址無CORS標頭，比照 tn-disability-hospitals 用內嵌 js 版本輸出 |
| `caregiver/` | 看護／照服機構名錄 | **無（使用者人工蒐集）** | 使用者手動整理目前網路上找得到的私人看護／居家照護機構名單（共35筆），收錄機構名稱、官網、收費頁面、聯絡電話、服務地區、統一編號，提供服務地區／是否有公開收費頁面／關鍵字篩選；**非政府開放資料，無提供機關、無官方驗證**，頁面明確標示免責聲明，資料來源為使用者提供之本機 CSV、無公開下載網址，需人工更新，詳見下方「更新資料」說明 |
| `dialysis-transport/` | 洗腎（透析）交通接送服務查詢 | 部分為衛生福利部長期照顧司（制度說明）／**無（民間清單為使用者人工蒐集）** | 頁面上方整理長照司「交通接送服務」BD03（社區式服務交通接送）／DA01（交通接送）給付碼別官方制度說明（資料來源：1966長照專區公告頁），下方為使用者手動整理之全台洗腎（透析）就醫民間接送/租賃服務名單（共16筆），收錄名稱、官網、聯絡電話、服務地區，因資料量小且服務地區欄位稀疏僅提供關鍵字篩選；**民間接送清單非政府開放資料，無官方驗證**，頁面明確標示免責聲明，資料來源為使用者提供之本機 CSV、無公開下載網址，需人工更新，詳見下方「更新資料」說明 |

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
- https://data.taipei/api/dataset/76b8b514-e793-4cca-8dcf-065d5af4b760/resource/d6522c9f-2026-4ab0-9642-65df9218a9bc/download　（BIG5(cp950) 編碼）
- https://opendata.tycg.gov.tw/api/dataset/7d03add1-aef5-4bbf-9b1b-7d601abd43a4/resource/5e7907b0-5418-4c36-9723-b6f786ad5871/download　（BIG5(cp950) 編碼）
- https://opendata.tycg.gov.tw/api/dataset/7ae18138-74f9-4ebb-8b7d-f03d9ddb1ef5/resource/0b949cb1-bfc3-4d02-8474-35e42a932643/download　（居家喘息，BIG5(cp950) 編碼）
- https://opendata.tycg.gov.tw/api/dataset/7ae18138-74f9-4ebb-8b7d-f03d9ddb1ef5/resource/b7c16660-f7ac-4bb6-b639-9c795581f160/download　（機構喘息，BIG5(cp950) 編碼）
- https://health.tainan.gov.tw/warehouse/F8BCB915-C08B-47F3-A731-1C30A3EE61EE/F_1780645430477e.pdf　（衛生局公告 PDF，由 build_data.py 自動下載並用 pdfplumber 解析）

授權方式：政府資料開放授權條款-第1版

## 網站架構

```
index.html          首頁，連結至二十個儀表板與更新紀錄頁
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
yl-denture/index.html 115年度宜蘭縣中低收入戶老人假牙裝置補助特約牙醫醫療院所儀表板（Chart.js 圖表 +
                       篩選表格，無地圖）
yl-denture/app.js
yl-denture/flowchart.jpg 申請流程圖（取自來源 PDF 第2頁）
hccg-elder/index.html 新竹市老人福利機構一覽表地圖儀表板（Leaflet 地圖 + Chart.js 圖表 + 篩選表格）
hccg-elder/app.js
tn-homecare-nursing/index.html 臺南市居家護理機構儀表板（Chart.js 圖表 + 篩選表格，無地圖）
tn-homecare-nursing/app.js
tc-nursing/index.html 臺中市一般護理之家清冊儀表板（Chart.js 圖表 + 篩選表格，無地圖）
tc-nursing/app.js
ntpc-nursing/index.html 新北市一般護理之家清冊儀表板（Chart.js 圖表 + 篩選表格，無地圖）
ntpc-nursing/app.js
ntpc-silver-hair-club/index.html 新北市銀髮俱樂部儀表板（Chart.js 圖表 + 篩選表格，無地圖）
ntpc-silver-hair-club/app.js
ntpc-dementia/index.html 新北市失智症門診資訊儀表板（Chart.js 圖表 + 篩選表格，無地圖）
ntpc-dementia/app.js
chiayi-ltc/index.html 嘉義縣立案長照及護理之家機構一覽儀表板（Chart.js 圖表 + 篩選表格，無地圖）
chiayi-ltc/app.js
pingtung-ltc/index.html 屏東縣老人長期照顧機構儀表板（Chart.js 圖表 + 篩選表格，無地圖）
pingtung-ltc/app.js
tc-transport/index.html 臺中市失能者交通接送服務地圖儀表板（Leaflet 地圖 + Chart.js 圖表 + 篩選表格）
tc-transport/app.js
tc-dementia/index.html 臺中市失智症服務及資源提供單位地圖儀表板（Leaflet 地圖 + Chart.js 圖表 + 篩選表格）
tc-dementia/app.js
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
tpe-denture/index.html 臺北市假牙補助醫療院所名單儀表板（Chart.js 圖表 + 篩選表格，無地圖；
                       頁面上方另有補助制度說明靜態卡片）
tpe-denture/app.js
tyc-transport/index.html 桃園市長照交通接送服務單位儀表板（Chart.js 圖表 + 篩選表格，無地圖；
                       頁面上方另有洽辦單位/服務對象/補助金額說明靜態卡片）
tyc-transport/app.js
tyc-hospice/index.html 桃園市社區安寧療護資源一覽表儀表板（Chart.js 圖表 + 篩選表格，無地圖；
                       頁面上方另有服務對象/服務內容/申請流程/諮詢窗口說明靜態卡片）
tyc-hospice/app.js
tyc-respite/index.html 桃園市喘息服務提供單位儀表板（Chart.js 圖表 + 篩選表格，無地圖；
                       頁面上方另有服務對象/服務內容說明靜態卡片）
tyc-respite/app.js
tn-denture/index.html 臺南市長者免費裝置全口活動假牙計畫合約醫療院所儀表板（Chart.js 圖表 + 篩選表格，
                       無地圖；頁面上方另有申請資格/補助金額/申請與核銷期程/聯絡窗口 Q&A 說明）
tn-denture/app.js
kcg-denture/index.html 115年高雄市免費裝假牙特約牙醫醫療院所儀表板（Chart.js 圖表 + 篩選表格，無地圖；
                       頁面上方另有申請資格/篩檢期間地點/裝置期限/保固維修/諮詢窗口 Q&A 說明）
kcg-denture/app.js
hsc-denture/index.html 新竹縣中低收入老人補助裝置假牙特約醫療院所儀表板（Chart.js 圖表 + 篩選表格，
                       無地圖；頁面上方另有申請資格/補助內容/申請流程/應備文件/聯絡窗口 Q&A 說明）
hsc-denture/app.js
chiayi-denture/index.html 嘉義市假牙補助合約醫療院所（中低收入／一般身分別）儀表板（Leaflet 地圖 +
                       Chart.js 圖表 + 篩選表格；頁面上方另有一般身分別方案申請資格/通知單發放與
                       補發流程 Q&A 說明）
chiayi-denture/app.js
chc-denture/index.html 彰化縣補助65歲以上老人裝置全口假牙契約診所名冊儀表板（Chart.js 圖表 + 篩選
                       表格，無地圖；頁面上方另有申請資格/受理期間/裝置態樣/承辦單位 Q&A 說明）
chc-denture/app.js
tc-denture/index.html 臺中市115年度65歲以上銀髮族假牙裝置補助計畫合約院所儀表板（Chart.js 圖表 +
                       篩選表格，無地圖；頁面上方另有補助對象/申請期間/給付金額/申請審查流程/其他
                       身分別轉介 Q&A 說明）
tc-denture/app.js
hl-denture/index.html 花蓮縣115年度65歲以上長者假牙補助合約醫療院所儀表板（Chart.js 圖表 + 篩選
                       表格，無地圖；頁面上方另有補助對象/受理時間/應備文件/申請流程五步驟（含流程圖）
                       /補助金額限制/常見問答 Q&A 說明）
hl-denture/app.js
hl-denture/flowchart.jpg 申請流程圖（取自來源 PDF 附件四）
pingtung-denture/index.html 屏東縣長者假牙裝置補助合作醫療院所儀表板（Chart.js 圖表 + 篩選表格，
                       無地圖；頁面上方另有補助對象/補助金額與項目/申請流程/服務窗口 Q&A 說明）
pingtung-denture/app.js
caregiver/index.html  看護／照服機構名錄儀表板（無圖表無地圖，僅篩選表格 + 統計卡；頁面上方另有
                       非官方資料免責聲明卡片）
caregiver/app.js
dialysis-transport/index.html  洗腎（透析）交通接送服務查詢儀表板（無圖表無地圖，僅關鍵字篩選表格 +
                       統計卡；頁面上方另有 BD03/DA01 官方制度說明卡片與民間接送清單免責聲明卡片）
dialysis-transport/app.js
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
data/yl-denture.json  115年度宜蘭縣中低收入戶老人假牙裝置補助特約牙醫醫療院所資料（由
                       scripts/build_data.py 產生）
data/yl-denture.js    同上資料的內嵌 JS 版本（window.YL_DENTURE_DATA），供 yl-denture 頁面以
                       <script> 標籤直接載入，因來源為 PDF 附件、不透過 fetch()
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
data/ntpc-silver-hair-club.json 新北市銀髮俱樂部資料（由 scripts/build_data.py 產生）
data/ntpc-silver-hair-club.js   同上資料的內嵌 JS 版本（window.NTPC_SILVER_HAIR_CLUB_DATA），供
                       ntpc-silver-hair-club 頁面以 <script> 標籤直接載入，因來源網址 CORS 僅允許
                       data.ntpc.gov.tw 網域，不透過 fetch()
data/ntpc-dementia.json 新北市失智症門診資訊資料（由 scripts/build_data.py 產生）
data/ntpc-dementia.js   同上資料的內嵌 JS 版本（window.NTPC_DEMENTIA_DATA），供 ntpc-dementia 頁面以
                       <script> 標籤直接載入，因來源網址無 CORS 標頭，不透過 fetch()
data/chiayi-ltc.json  嘉義縣立案長照及護理之家機構一覽資料（由 scripts/build_data.py 讀取本機 CSV 產生）
data/chiayi-ltc.js    同上資料的內嵌 JS 版本（window.CHIAYI_LTC_DATA），供 chiayi-ltc 頁面以
                       <script> 標籤直接載入，因無公開下載網址，不透過 fetch()
data/pingtung-ltc.json 屏東縣老人長期照顧機構資料（由 scripts/build_data.py 產生）
data/pingtung-ltc.js   同上資料的內嵌 JS 版本（window.PINGTUNG_LTC_DATA），供 pingtung-ltc 頁面以
                       <script> 標籤直接載入，因來源網址無 CORS 標頭，不透過 fetch()
data/tc-transport.json 臺中市失能者交通接送服務資料（由 scripts/build_data.py 產生，含座標換算）
data/tc-transport.js   同上資料的內嵌 JS 版本（window.TC_TRANSPORT_DATA），供 tc-transport 頁面以
                       <script> 標籤直接載入，避免依賴外部網址即時可用性
data/tc-dementia.json 臺中市失智症服務及資源提供單位資料（由 scripts/build_data.py 產生，含座標換算）
data/tc-dementia.js   同上資料的內嵌 JS 版本（window.TC_DEMENTIA_DATA），供 tc-dementia 頁面以
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
data/tpe-denture.json 臺北市假牙補助醫療院所名單資料（由 scripts/build_data.py 產生，BIG5(cp950) 解碼）
data/tpe-denture.js   同上資料的內嵌 JS 版本（window.TPE_DENTURE_DATA），供 tpe-denture
                       頁面以 <script> 標籤直接載入，因來源網址無 CORS 標頭，不透過 fetch()
data/tyc-transport.json 桃園市長照交通接送服務單位資料（由 scripts/build_data.py 產生，BIG5 解碼）
data/tyc-transport.js  同上資料的內嵌 JS 版本（window.TYC_TRANSPORT_DATA），供 tyc-transport
                       頁面以 <script> 標籤直接載入，因來源網址無 CORS 標頭，不透過 fetch()
data/tyc-hospice.json 桃園市社區安寧療護資源一覽表資料（由 scripts/build_data.py 產生，BIG5(cp950)
                       解碼；原始 CSV 無標準表頭，靠三段分類標題列切分服務類別）
data/tyc-hospice.js   同上資料的內嵌 JS 版本（window.TYC_HOSPICE_DATA），供 tyc-hospice
                       頁面以 <script> 標籤直接載入，因來源網址無 CORS 標頭，不透過 fetch()
data/tyc-respite.json 桃園市喘息服務提供單位資料（由 scripts/build_data.py 產生，合併居家喘息與
                       機構喘息兩份 BIG5(cp950) 編碼 CSV，機構喘息尾端空白列已過濾）
data/tyc-respite.js  同上資料的內嵌 JS 版本（window.TYC_RESPITE_DATA），供 tyc-respite
                       頁面以 <script> 標籤直接載入，因來源網址無 CORS 標頭，不透過 fetch()
data/tn-denture.json  臺南市長者免費裝置全口活動假牙計畫合約醫療院所資料（由 scripts/build_data.py
                       自動下載衛生局公告 PDF 並用 pdfplumber 解析產生）
data/tn-denture.js    同上資料的內嵌 JS 版本（window.TN_DENTURE_DATA），供 tn-denture 頁面以
                       <script> 標籤直接載入，因來源為 PDF 檔案，不透過 fetch()
data/kcg-denture.json 115年高雄市免費裝假牙特約牙醫醫療院所資料（由 scripts/build_data.py 讀取人工
                       轉寫的 data/source/kcg-denture-manual.json 產生；原始 PDF 文字為向量繪製圖形，
                       無法程式化解析，故非自動下載/解析，詳見下方「更新資料」說明）
data/kcg-denture.js   同上資料的內嵌 JS 版本（window.KCG_DENTURE_DATA），供 kcg-denture 頁面以
                       <script> 標籤直接載入，因來源為 PDF 檔案，不透過 fetch()
data/hsc-denture.json 新竹縣中低收入老人補助裝置假牙特約醫療院所資料（由 scripts/build_data.py 自動
                       下載新竹縣政府開放資料 JSON 產生）
data/hsc-denture.js   同上資料的內嵌 JS 版本（window.HSC_DENTURE_DATA），供 hsc-denture 頁面以
                       <script> 標籤直接載入，因來源網址無 CORS 標頭，不透過 fetch()
data/chiayi-denture.json 嘉義市假牙補助合約醫療院所資料（由 scripts/build_data.py 自動下載嘉義市
                       政府中低收入方案CSV並用 pdfplumber 解析一般身分別方案公告PDF後合併產生）
data/chiayi-denture.js 同上資料的內嵌 JS 版本（window.CHIAYI_DENTURE_DATA），供 chiayi-denture 頁面
                       以 <script> 標籤直接載入，因兩來源皆無 CORS 標頭，不透過 fetch()
data/chc-denture.json 彰化縣補助65歲以上老人裝置全口假牙契約診所名冊資料（由 scripts/build_data.py
                       自動下載彰化縣政府社會處公告 BIG5 編碼 CSV 並解析產生）
data/chc-denture.js   同上資料的內嵌 JS 版本（window.CHC_DENTURE_DATA），供 chc-denture 頁面以
                       <script> 標籤直接載入，因來源網址無 CORS 標頭，不透過 fetch()
data/tc-denture.json  臺中市115年度65歲以上銀髮族假牙裝置補助計畫合約院所資料（由 scripts/build_data.py
                       讀取本地已清理過的 scripts/sources/tc-denture/tc-denture.csv 產生，非向遠端
                       網址下載，因原始資料無公開下載網址）
data/tc-denture.js    同上資料的內嵌 JS 版本（window.TC_DENTURE_DATA），供 tc-denture 頁面以
                       <script> 標籤直接載入
data/hl-denture.json  花蓮縣115年度65歲以上長者假牙補助合約醫療院所資料（由 scripts/build_data.py
                       讀取本地存放的 scripts/sources/hl-denture/institution-list.pdf 解析產生，
                       非向遠端網址下載，因原始資料無公開下載網址）
data/hl-denture.js    同上資料的內嵌 JS 版本（window.HL_DENTURE_DATA），供 hl-denture 頁面以
                       <script> 標籤直接載入
data/pingtung-denture.json  屏東縣115年長者假牙裝置補助合作醫療院所資料（由 scripts/build_data.py
                       讀取本地存放的 scripts/sources/pingtung-denture/institution-list.pdf
                       解析產生，非向遠端網址下載，因原始資料無公開下載網址）
data/pingtung-denture.js  同上資料的內嵌 JS 版本（window.PINGTUNG_DENTURE_DATA），供
                       pingtung-denture 頁面以 <script> 標籤直接載入
data/tpe-dementia-hospitals.json  臺北市失智症診療機構名冊（由 scripts/build_data.py 讀取本地存放的
                       scripts/sources/tpe-dementia-hospitals/institution-list.pdf 解析產生，
                       非向遠端網址下載，因原始資料無公開開放資料 API/CSV，僅有衛生局公告頁面 PDF）
data/tpe-dementia-hospitals.js  同上資料的內嵌 JS 版本（window.TPE_DEMENTIA_HOSPITALS_DATA），供
                       tpe-dementia-hospitals 頁面以 <script> 標籤直接載入
data/tpe-disability-hospitals.json  臺北市身心障礙鑑定指定醫院聯絡方式一覽表（由 scripts/build_data.py
                       下載 data.taipei CSV 產生，資料量小且來源網址無 CORS 標頭）
data/tpe-disability-hospitals.js  同上資料的內嵌 JS 版本（window.TPE_DISABILITY_HOSPITALS_DATA），供
                       tpe-disability-hospitals 頁面以 <script> 標籤直接載入
data/tn-disability-hospitals.json  115年臺南市身心障礙鑑定醫院（由 scripts/build_data.py 下載
                       data.tainan.gov.tw CSV 產生，資料量小且來源網址無 CORS 標頭）
data/tn-disability-hospitals.js  同上資料的內嵌 JS 版本（window.TN_DISABILITY_HOSPITALS_DATA），供
                       tn-disability-hospitals 頁面以 <script> 標籤直接載入
data/chiayi-disability-hospitals.json  嘉義市身心障礙鑑定醫院（由 scripts/build_data.py 下載
                       data.chiayi.gov.tw CSV 產生，資料量小且來源網址無 CORS 標頭）
data/chiayi-disability-hospitals.js  同上資料的內嵌 JS 版本（window.CHIAYI_DISABILITY_HOSPITALS_DATA），
                       供 chiayi-disability-hospitals 頁面以 <script> 標籤直接載入
data/source/tc-disability-hospitals-categories-11412.pdf  臺中市33家新制身心障礙鑑定醫院及鑑定
                       類別及向度一覽表（衛生局公告 PDF，需人工存放，無法自動下載）
data/source/tc-disability-hospitals-contacts-11412.pdf  臺中市請領身心障礙證明之鑑定醫院及窗口
                       （衛生局公告 PDF，需人工存放，無法自動下載）
data/tc-disability-hospitals.json  臺中市身心障礙鑑定醫院及鑑定類別窗口（由 scripts/build_data.py
                       用 pdfplumber 解析上述兩份本機 PDF 產生，共33筆）
data/chc-disability-hospitals.json  彰化縣身心障礙鑑定醫院（由 scripts/build_data.py 下載
                       email.chcg.gov.tw BIG5 編碼 CSV 產生，資料量小且來源網址無 CORS 標頭）
data/chc-disability-hospitals.js  同上資料的內嵌 JS 版本（window.CHC_DISABILITY_HOSPITALS_DATA），供
                       chc-disability-hospitals 頁面以 <script> 標籤直接載入
data/tc-disability-hospitals.js  同上資料的內嵌 JS 版本（window.TC_DISABILITY_HOSPITALS_DATA），供
                       tc-disability-hospitals 頁面以 <script> 標籤直接載入
data/caregiver.json   看護／照服機構名錄資料（由 scripts/build_data.py 讀取本機 CSV 產生）
data/caregiver.js     同上資料的內嵌 JS 版本（window.CAREGIVER_DATA），供 caregiver 頁面以
                       <script> 標籤直接載入，因無公開下載網址，不透過 fetch()
data/dialysis-transport.json  洗腎（透析）接送資源清單資料（由 scripts/build_data.py 讀取本機
                       CSV 產生；頁面上方 BD03/DA01 制度說明文字為靜態內容，未存於此檔案）
data/dialysis-transport.js  同上資料的內嵌 JS 版本（window.DIALYSIS_TRANSPORT_DATA），供
                       dialysis-transport 頁面以 <script> 標籤直接載入，因無公開下載網址，不透過 fetch()
data/source/          長照專業服務特約單位來源 PDF（人工下載存放於此，供 build_data.py 解析）；
                       另含 kcg-denture-manual.json（115年高雄市免費裝假牙名冊人工轉寫結果）與
                       kcg-denture-115.pdf（原始公告 PDF 存檔，供未來人工核對/重新轉寫參考）
data/meta.json        資料筆數與更新時間
scripts/build_data.py 資料下載與轉換腳本
scripts/sources/chiayi-ltc/  嘉義縣立案長照及護理之家機構一覽的原始 CSV（institutions.csv／
                       nursing-homes.csv，人工提供，無公開下載網址，需人工更新後重跑 build_data.py）
scripts/sources/caregiver/   看護／照服機構名錄的原始 CSV（caregivers.csv，使用者人工蒐集，
                       無公開下載網址，需人工更新後重跑 build_data.py）
scripts/sources/dialysis-transport/  洗腎（透析）接送資源清單的原始 CSV（dialysis-transport.csv，
                       使用者人工蒐集，無公開下載網址，需人工更新後重跑 build_data.py）
scripts/sources/tpe-dementia-hospitals/  臺北市失智症診療機構名冊的原始 PDF（institution-list.pdf，
                       臺北市政府衛生局公告網頁附件，無公開開放資料 API/CSV，需人工至公告頁面下載
                       新版 PDF 覆蓋後重跑 build_data.py）
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

不帶參數執行會重新下載二十份 CSV/JSON（長照ABC據點、巷弄長照站、桃園市老人福利機構一覽表、
銀髮族服務-居家長照機構、新竹縣長照機構名冊、宜蘭縣立案老人長期照顧及安養機構名冊、
新竹市老人福利機構一覽表、臺南市居家護理機構、臺中市一般護理之家清冊、新北市一般護理之家清冊、
新北市銀髮俱樂部、屏東縣老人長期照顧機構、臺中市失能者交通接送服務、桃園市長期照護專業服務特約單位、
桃園市長者裝置活動假牙合約醫療院所、桃園市身心障礙類別、向度之鑑定醫院名冊、
桃園市失能老人接受長期照顧機構服務暨老人保護安置機構名冊、臺北市假牙補助醫療院所名單、
桃園市長照交通接送服務單位、桃園市社區安寧療護資源一覽表、臺南市長者免費裝置全口活動假牙計畫合約
醫療院所、新竹縣中低收入老人補助裝置假牙特約醫療院所、嘉義市假牙補助合約醫療院所（中低收入／
一般身分別，其中一般身分別方案來源為公告PDF，用pdfplumber自動解析，另一中低收入方案來源為CSV）、
彰化縣補助65歲以上老人裝置全口假牙契約診所名冊（來源為BIG5編碼CSV）
並覆寫對應
`data/*.json`；同時嘗試解析
`data/source/tp-ltc-specialty-*.pdf`
（若存在）產生 `data/specialty.json`／`data/specialty.js`，並讀取 `scripts/sources/chiayi-ltc/`、
`scripts/sources/caregiver/` 下的本機 CSV 分別產生 `data/chiayi-ltc.json`／`data/chiayi-ltc.js`
與 `data/caregiver.json`／`data/caregiver.js`（後者為使用者人工蒐集之非政府開放資料，見下方
「更新資料集列表」與「更新「看護／照服機構名錄」」說明），以及讀取 `scripts/sources/dialysis-transport/`
下的本機 CSV 產生 `data/dialysis-transport.json`／`data/dialysis-transport.js`（同樣為使用者人工
蒐集之非政府開放資料，見下方「更新「洗腎（透析）接送資源清單」」說明），還有讀取人工轉寫的
`data/source/kcg-denture-manual.json` 產生 `data/kcg-denture.json`／`data/kcg-denture.js`
（見下方「更新「115年高雄市免費裝假牙特約牙醫醫療院所」」說明）。這是**完整流程**，會對外發送多個網路請求且較耗時，
**僅在明確需要全面更新所有資料集時才執行**；建議依資料集「更新頻率」（每1月 / 每1年 / 不定期）
定期執行後再部署，平常開發（例如新增單一資料集頁面）不需要、也不應該每次都跑全部。

### 只更新單一資料集

新增或調整單一資料集時（例如剛寫好一個新的 `build_xxx()`），可指定資料集 key 只重跑該資料集，
不會影響其他資料集既有的 `data/*.json`／`.js`，也不會覆寫 `data/meta.json` 中其他資料集的紀錄：

```bash
python3 scripts/build_data.py chiayi-ltc          # 只重新產生嘉義縣立案長照及護理之家機構一覽
python3 scripts/build_data.py pingtung-ltc        # 只重新產生屏東縣老人長期照顧機構
python3 scripts/build_data.py tc-transport        # 只重新產生臺中市失能者交通接送服務
python3 scripts/build_data.py tc-dementia         # 只重新產生臺中市失智症服務及資源提供單位
python3 scripts/build_data.py tyc-placement       # 只重新產生桃園市失能老人長照暨老人保護安置機構名冊
python3 scripts/build_data.py tpe-denture         # 只重新產生臺北市假牙補助醫療院所名單
python3 scripts/build_data.py tyc-transport       # 只重新產生桃園市長照交通接送服務單位
python3 scripts/build_data.py tyc-hospice         # 只重新產生桃園市社區安寧療護資源一覽表
python3 scripts/build_data.py tyc-respite         # 只重新產生桃園市喘息服務提供單位
python3 scripts/build_data.py tn-denture          # 只重新產生臺南市長者免費裝置全口活動假牙計畫合約醫療院所
python3 scripts/build_data.py kcg-denture         # 只重新產生115年高雄市免費裝假牙特約牙醫醫療院所
python3 scripts/build_data.py hsc-denture         # 只重新產生新竹縣中低收入老人補助裝置假牙特約醫療院所
python3 scripts/build_data.py yl-denture          # 只重新產生115年度宜蘭縣中低收入戶老人假牙裝置補助特約牙醫醫療院所
python3 scripts/build_data.py chiayi-denture      # 只重新產生嘉義市假牙補助合約醫療院所（中低收入／一般身分別）
python3 scripts/build_data.py chc-denture         # 只重新產生彰化縣補助65歲以上老人裝置全口假牙契約診所名冊
python3 scripts/build_data.py tc-denture          # 只重新產生臺中市115年度65歲以上銀髮族假牙裝置補助計畫合約院所
python3 scripts/build_data.py hl-denture          # 只重新產生花蓮縣115年度65歲以上長者假牙補助合約醫療院所
python3 scripts/build_data.py pingtung-denture    # 只重新產生屏東縣115年長者假牙裝置補助合作醫療院所
python3 scripts/build_data.py tpe-dementia-hospitals  # 只重新產生臺北市失智症診療機構名冊
python3 scripts/build_data.py tpe-disability-hospitals  # 只重新產生臺北市身心障礙鑑定指定醫院聯絡方式一覽表
python3 scripts/build_data.py tn-disability-hospitals  # 只重新產生115年臺南市身心障礙鑑定醫院
python3 scripts/build_data.py chiayi-disability-hospitals  # 只重新產生嘉義市身心障礙鑑定醫院
python3 scripts/build_data.py tc-disability-hospitals  # 只重新產生臺中市身心障礙鑑定醫院及鑑定類別窗口
                                                        # （需先將兩份來源PDF存至 data/source/，見下方說明）
python3 scripts/build_data.py chc-disability-hospitals  # 只重新產生彰化縣身心障礙鑑定醫院
python3 scripts/build_data.py caregiver           # 只重新產生看護／照服機構名錄
python3 scripts/build_data.py dialysis-transport  # 只重新產生洗腎（透析）接送資源清單
python3 scripts/build_data.py ntpc-dementia       # 只重新產生新北市失智症門診資訊
python3 scripts/build_data.py tc-nursing ntpc-nursing   # 可同時指定多個，以空白分隔
python3 scripts/build_data.py ntpc-silver-hair-club     # 只重新產生新北市銀髮俱樂部
python3 scripts/build_data.py --help              # 列出所有可用的資料集 key
```

執行前請先安裝 PDF 解析用的額外相依套件（僅 `specialty` 資料集需要，其他資料集僅用標準庫）：

```bash
python3 -m pip install pdfplumber
```


### 更新「115年高雄市免費裝假牙特約牙醫醫療院所」

此資料集**沒有開放資料 CSV/API**，來源為高雄市政府衛生局公告的固定名冊 PDF，且該 PDF 內文字為
**向量繪製圖形**（無法用 pdfplumber 等工具程式化擷取文字/表格），因此**無法由腳本自動下載並解析**，
需人工重新轉寫：

1. 到高雄市政府衛生局官網或搜尋「115年高雄市免費裝假牙特約牙醫醫療院所」取得最新年度公告 PDF。
2. 用 `pdfplumber` 將 PDF 每頁渲染成圖片（`page.to_image(resolution=150).save(...)`），逐頁以視覺方式
   核對每個行政區的機構名稱、電話、地址，轉寫更新 `data/source/kcg-denture-manual.json`
   （格式為 `[{district, name, phone, address}, ...]`），並將新版 PDF 存成
   `data/source/kcg-denture-<年度>.pdf` 供日後核對。
3. 若「注意事項」頁內容（申請資格、篩檢期間地點、保固維修規定等）有變動，需同步更新
   `kcg-denture/index.html` 內對應的 Q&A 文字與 FAQPage JSON-LD。
4. 執行 `python3 scripts/build_data.py kcg-denture` 只重新產生 `data/kcg-denture.json`／
   `data/kcg-denture.js`（`build_kcg_denture()` 僅讀取上述人工轉寫 JSON，不會重新下載/解析 PDF）。
5. 建議抽樣核對幾個行政區（如三民區、鳳山區）的筆數與內容是否與 PDF 原圖一致。

### 更新「臺北市長照專業服務特約單位」

此資料集**沒有開放資料 CSV/API**，臺北市政府衛生局僅於公告頁面提供 PDF 附件，因此無法由腳本自動下載，
需手動維護：

1. 到[長照服務特約專區公告頁面](https://health.gov.taipei/News_Content.aspx?n=F0D7A5A451D2493C&sms=549F98C9E5942A2B&s=9138F86B8A3CBF69)下載最新版 PDF。
2. 將檔案存成 `data/source/tp-ltc-specialty-<公告日期，例如20260430>.pdf`（腳本會自動抓取
   `data/source/` 目錄下符合此檔名規則、依檔名排序最新的一份 PDF）。
3. 執行 `python3 scripts/build_data.py specialty` 只重新產生 `data/specialty.json`／`data/specialty.js`。
4. 建議抽樣核對幾筆機構名稱、地址與服務能力是否正確解析（PDF 表格跨頁與換行清理邏輯詳見
   `scripts/build_data.py` 的 `build_specialty()`）。

### 更新「臺中市身心障礙鑑定醫院及鑑定類別窗口」

此資料集**沒有開放資料 CSV/API**，臺中市政府衛生局僅於網站公告兩份獨立 PDF（醫院及窗口清冊、
鑑定類別及向度一覽表），因此無法由腳本自動下載，需手動維護：

1. 到臺中市政府衛生局網站下載最新版兩份 PDF：
   - [臺中市請領身心障礙證明之鑑定醫院及窗口](https://www.health.taichung.gov.tw/media/1364235/)
   - [臺中市33家新制身心障礙鑑定醫院及鑑定類別及向度一覽表](https://www.health.taichung.gov.tw/media/1364236/)
2. 分別覆蓋 `data/source/tc-disability-hospitals-contacts-11412.pdf`（窗口清冊）與
   `data/source/tc-disability-hospitals-categories-11412.pdf`（類別矩陣）。
3. 執行 `python3 scripts/build_data.py tc-disability-hospitals` 只重新產生
   `data/tc-disability-hospitals.json`／`data/tc-disability-hospitals.js`。
4. **重要**：兩份 PDF 的醫院命名方式（全銜/簡稱）、「臺」/「台」用字與清單順序皆不同，
   `scripts/build_data.py` 用人工核對的 `TC_DISABILITY_HOSPITAL_ALIASES` 對照表配對兩邊資料，
   若醫院清冊改版（增減院所、更名），須重新核對並更新此對照表；腳本執行時若有醫院名稱配對失敗
   會印出警告（不會中斷），請務必留意並修正對照表後再重新產生資料。
5. 建議抽樣核對幾筆醫院層級、窗口姓名、電話與可辦理鑑定類別（第1~8類）是否正確解析（矩陣彙總
   邏輯詳見 `scripts/build_data.py` 的 `build_tc_disability_hospitals()`）。

### 更新「嘉義縣立案長照及護理之家機構一覽」

此資料集**沒有開放資料 CSV/API**，來源為[嘉義縣政府長期照護管理中心](https://ltccenter.cyhg.gov.tw/cp.aspx?n=F7AEF7883C88532B)網站，
資料由使用者以本機 CSV 提供，因此無法由腳本自動下載，需手動維護：

1. 取得最新版「嘉義縣立案住宿長照機構名單」與「嘉義縣護理之家名單」CSV（UTF-8 編碼）。
2. 分別覆蓋 `scripts/sources/chiayi-ltc/institutions.csv`（住宿長照機構）與
   `scripts/sources/chiayi-ltc/nursing-homes.csv`（護理之家），維持原有欄位名稱與順序。
3. 執行 `python3 scripts/build_data.py chiayi-ltc` 只重新產生 `data/chiayi-ltc.json`／`data/chiayi-ltc.js`。
4. 建議抽樣核對幾筆機構名稱、鄉鎮市解析與床數是否正確（地址解析邏輯詳見
   `scripts/build_data.py` 的 `build_chiayi_ltc()` 與 `_chiayi_township()`）。

### 更新「看護／照服機構名錄」

此資料集**非政府開放資料**，為使用者手動蒐集目前網路上找得到的私人看護／居家照護機構名單，
無公開下載網址、無官方驗證，因此無法由腳本自動下載，需手動維護：

1. 取得最新版機構名單 CSV（UTF-8 編碼，欄位依序為：名稱／網址／收費頁面／聯絡電話／服務地區／
   統一編號）。
2. 覆蓋 `scripts/sources/caregiver/caregivers.csv`，維持原有欄位名稱與順序。
3. 執行 `python3 scripts/build_data.py caregiver` 只重新產生 `data/caregiver.json`／`data/caregiver.js`。
4. 「服務地區」欄位為自由文字，本站以子字串比對縣市清單方式解析（詳見
   `scripts/build_data.py` 的 `build_caregivers()` 與 `_caregiver_regions()`），無法辨識出具體
   縣市時 `regions` 會是空陣列，屬已知限制；建議抽樣核對幾筆機構名稱、服務地區解析是否合理。
5. 因本資料集無官方驗證，頁面已於顯著位置加入免責聲明，新增/更新機構時請避免加入主觀評語或推薦排序。

### 更新「洗腎（透析）交通接送服務查詢」

此頁面分兩部分，更新方式不同：

- **上方 BD03/DA01 制度說明**：內容為衛生福利部長期照顧司於
  [1966長照專區公告頁](https://1966.gov.tw/LTC/cp-6452-69937-207.html) 公告之官方文字，屬靜態
  內容直接寫在 `dialysis-transport/index.html`，非開放資料 CSV/JSON，若該公告頁內容有異動
  （給付額度、給付價格等），需人工比對後更新頁面對應段落與「資料來源」附註的建檔/更新日期。
- **下方民間洗腎接送資源清單**：**非政府開放資料**，為使用者手動蒐集目前網路上找得到的洗腎/透析
  就醫民間接送業者，無公開下載網址、無官方驗證，需手動維護：
  1. 取得最新版資源清單 CSV（UTF-8 編碼，欄位依序為：名稱／網址／聯絡電話／服務地區）。
  2. 覆蓋 `scripts/sources/dialysis-transport/dialysis-transport.csv`，維持原有欄位名稱與順序。
  3. 執行 `python3 scripts/build_data.py dialysis-transport` 只重新產生
     `data/dialysis-transport.json`／`data/dialysis-transport.js`。
  4. 「服務地區」欄位極度稀疏，本站不做縣市正規化，原文照登；建議抽樣核對幾筆名稱、電話、
     網址連結是否有效。
  5. 因本資料集無官方驗證，頁面已於顯著位置加入免責聲明，新增/更新業者時請避免加入主觀評語或
     推薦排序。

## 本機預覽

```bash
python3 -m http.server 8000
# 開啟 http://localhost:8000
```

## 部署到 GitHub Pages

1. 將本專案推送到 GitHub repository。
2. 到 repository 的 Settings → Pages，Source 選擇 `main` 分支、根目錄 `/`。
3. 儲存後幾分鐘即可透過 `https://<你的帳號>.github.io/<repo名稱>/` 瀏覽。

## Push 前自動檢查 API key

專案內建 `.githooks/pre-push` hook，會在每次 `git push` 前掃描即將推送的 commit 內容，若偵測到常見
API key／密鑰格式（Google API key、AWS Access Key、GitHub token、OpenAI key 等），會直接中止 push
並列出可疑內容所在行，避免密鑰意外上傳到遠端。

**每個 clone 都要先啟用一次**（hook 檔案本身會隨 repo 一起 clone，但 Git 預設不會自動套用
`.githooks/` 目錄，需手動指定）：

```bash
git config core.hooksPath .githooks
```

若真的需要略過檢查（例如確認是誤判），可用 `git push --no-verify`，但務必先確認內容真的安全。

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

## 技術說明. 

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

  


