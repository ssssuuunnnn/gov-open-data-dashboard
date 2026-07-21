#!/usr/bin/env python3
"""
下載並轉換政府開放資料集為前端可用的 JSON。

資料來源：
1. 長照ABC據點  https://ltcpap.mohw.gov.tw/publish/abc.csv
2. 巷弄長照站    https://email.chcg.gov.tw/df/pufnpn5i5741iy9efkn2rrz5ga6uhb
3. 桃園市老人福利機構一覽表  https://opendata.tycg.gov.tw/api/dataset/536bb44b-b9f1-4336-ad26-34b9e25b3a68/resource/3d7e3b4c-8bc5-47c4-85a9-eec70415b189/download
   （來源網址的 CORS 標頭僅允許 opendata.tycg.gov.tw 網域，前端無法直接 fetch，
   需由本腳本於伺服器端下載）
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
KCG_HOMECARE_URL = "https://data.kcg.gov.tw/File/DirectDownload/59ac925f-10dd-42f7-a540-ab6c4218b93d"
HSC_LTC_URL = "https://ws.hsinchu.gov.tw/001/Upload/1/opendata/8774/283/b14a70a1-784c-4586-babf-ade99a7e8277.json"
YL_LTC_URL = "https://opendataap2.e-land.gov.tw/./resource/files/2019-12-03/a91e966d8b5b07d1e9bb8c3a767e9d1f.json"
HCCG_ELDER_URL = "https://odws.hccg.gov.tw/001/Upload/25/opendataback/9059/33/b253c75b-9e30-42d5-81bd-eb1f37e74af2.json"
TN_HOMECARE_NURSING_URL = "https://data.tainan.gov.tw/File/ResourceCsvDownload/4de27549-893c-4e8e-8644-538a35076607"
TC_NURSING_URL = "https://newdatacenter.taichung.gov.tw/api/v1/no-auth/resource.download?rid=af086949-239b-41ef-8316-5c12dd26a672"
# {page} 佔位符，page 從 0 起算，size=100；資料集目前僅 75 筆一頁即可取完，
# 但保留分頁迴圈以防未來筆數超過 100（見 build_ntpc_nursing()）。
NTPC_NURSING_URL_TEMPLATE = (
    "https://data.ntpc.gov.tw/api/datasets/467cb02f-1f94-4fa1-a440-4f08575cf181/csv"
    "?page={page}&size=100"
)
CHIAYI_LTC_SOURCE_PAGE = "https://ltccenter.cyhg.gov.tw/cp.aspx?n=F7AEF7883C88532B"
CHIAYI_LTC_INSTITUTIONS_CSV = "scripts/sources/chiayi-ltc/institutions.csv"
CHIAYI_LTC_NURSING_CSV = "scripts/sources/chiayi-ltc/nursing-homes.csv"
PINGTUNG_LTC_URL = (
    "https://www-ws.pthg.gov.tw/Upload/2015pthg/0/relfile/0/0/"
    "886f59e6-23b6-4de3-a04a-4de087bdf9b8.csv"
)
TC_TRANSPORT_URL = "https://newdatacenter.taichung.gov.tw/api/v1/no-auth/resource.download?rid=96251524-861c-4b92-9401-590444adcb8f"
TYLTC_URL = (
    "https://opendata.tycg.gov.tw/api/dataset/2e087011-3a3d-4ae1-9038-19b2f3f43a9a/"
    "resource/cc33a2eb-c1cf-47f1-b6f7-d4b37ba4c797/download"
)

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


def build_tyc_elder():
    """桃園市老人福利機構一覽表（桃園市政府開放資料平台，CORS 僅允許該平台網域，改由本腳本下載）。"""
    print("下載 桃園市老人福利機構一覽表 ...", file=sys.stderr)
    text = fetch(TYC_ELDER_URL)
    reader = csv.DictReader(io.StringIO(text))
    rows_in = list(reader)
    records = []
    for row in rows_in:
        addr = (row.get("地址", "") or "").strip()
        # 地址開頭即為鄉鎮市區（無縣市字首），且共用的 ADDR_RE 對「平鎮區」等
        # 名稱中途含「鎮」字的行政區會誤判，故改用桃園市固定 13 區清單比對。
        district = next((d for d in TYC_DISTRICTS if addr.startswith(d)), "")
        occupants = [s for s in re.split(r"\s+", (row.get("收容對象", "") or "").strip()) if s]
        records.append([
            row.get("編號", "").strip(),          # 0 id
            row.get("機構名稱", "").strip(),      # 1 name
            row.get("負責人", "").strip(),        # 2 director
            district,                               # 3 district
            addr,                                   # 4 address
            row.get("電話", "").strip(),          # 5 phone
            ";".join(occupants),                    # 6 occupants (';' joined)
            _to_int(row.get("立案床數")),          # 7 beds
            row.get("最近1次評鑑成績", "").strip(), # 8 rating
        ])
    print(f"  共 {len(records)} 筆", file=sys.stderr)
    fields = ["id", "name", "director", "district", "address", "phone",
              "occupants", "beds", "rating"]
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


def _specialty_norm(s):
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
        "key": "tyltc",
        "builder": build_tyltc,
        "json": "data/tyltc.json",
        "js_var": "TYLTC_DATA",
        "meta_key": "tyltc",
        "title": "桃園市長期照護專業服務特約單位",
        "source": lambda: TYLTC_URL,
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
