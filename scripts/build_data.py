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
    data/meta.json  (資料更新時間等資訊)

額外相依套件：
    僅 build_specialty() 需要 pdfplumber（`python3 -m pip install pdfplumber`）解析 PDF 表格，
    其餘資料集仍只用標準庫 urllib/csv 下載/解析 CSV。
"""
import csv
import glob
import io
import json
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

# 宜蘭縣行政區清單，用於補上原始地址欄位缺漏的「宜蘭縣」前綴（部分機構地址僅寫鄉鎮市區名，
# 未包含縣名，例如「羅東鎮站前南路11號」）。
YL_DISTRICTS = [
    "宜蘭市", "羅東鎮", "蘇澳鎮", "頭城鎮", "礁溪鄉", "壯圍鄉", "員山鄉",
    "五結鄉", "冬山鄉", "三星鄉", "大同鄉", "南澳鄉",
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


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read()
    return raw.decode("utf-8-sig", errors="replace")


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


def main():
    abc = build_abc()
    lane = build_lane()
    tyc_elder = build_tyc_elder()
    specialty = build_specialty()
    kcg_homecare = build_kcg_homecare()
    hsc_ltc = build_hsc_ltc()
    yl_ltc = build_yl_ltc()

    with open("data/abc.json", "w", encoding="utf-8") as f:
        json.dump(abc, f, ensure_ascii=False, separators=(",", ":"))
    with open("data/lane.json", "w", encoding="utf-8") as f:
        json.dump(lane, f, ensure_ascii=False, separators=(",", ":"))
    with open("data/tyc-elder.json", "w", encoding="utf-8") as f:
        json.dump(tyc_elder, f, ensure_ascii=False, separators=(",", ":"))
    # 額外輸出內嵌式 JS 版本（window.TYC_ELDER_DATA），前端以 <script> 標籤直接載入，
    # 不透過 fetch()，避免任何網路請求/快取/部署時序問題導致資料顯示空白。
    with open("data/tyc-elder.js", "w", encoding="utf-8") as f:
        f.write("window.TYC_ELDER_DATA = ")
        json.dump(tyc_elder, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    with open("data/kcg-homecare.json", "w", encoding="utf-8") as f:
        json.dump(kcg_homecare, f, ensure_ascii=False, separators=(",", ":"))
    # 同 tyc-elder，來源網址無 CORS 標頭，改用內嵌式 JS 版本（window.KCG_HOMECARE_DATA）。
    with open("data/kcg-homecare.js", "w", encoding="utf-8") as f:
        f.write("window.KCG_HOMECARE_DATA = ")
        json.dump(kcg_homecare, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    with open("data/hsc-ltc.json", "w", encoding="utf-8") as f:
        json.dump(hsc_ltc, f, ensure_ascii=False, separators=(",", ":"))
    # 同 tyc-elder，來源網址無 CORS 標頭，改用內嵌式 JS 版本（window.HSC_LTC_DATA）。
    with open("data/hsc-ltc.js", "w", encoding="utf-8") as f:
        f.write("window.HSC_LTC_DATA = ")
        json.dump(hsc_ltc, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    with open("data/yl-ltc.json", "w", encoding="utf-8") as f:
        json.dump(yl_ltc, f, ensure_ascii=False, separators=(",", ":"))
    # 同 tyc-elder，來源網址無 CORS 標頭，改用內嵌式 JS 版本（window.YL_LTC_DATA）。
    with open("data/yl-ltc.js", "w", encoding="utf-8") as f:
        f.write("window.YL_LTC_DATA = ")
        json.dump(yl_ltc, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")

    meta = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "abc": {"count": len(abc["rows"]), "source": ABC_URL, "title": "長照ABC據點"},
        "lane": {"count": len(lane["rows"]), "source": LANE_URL, "title": "巷弄長照站"},
        "tycElder": {
            "count": len(tyc_elder["rows"]),
            "source": TYC_ELDER_URL,
            "title": "桃園市老人福利機構一覽表",
        },
        "kcgHomecare": {
            "count": len(kcg_homecare["rows"]),
            "source": KCG_HOMECARE_URL,
            "title": "銀髮族服務-居家長照機構",
        },
        "hscLtc": {
            "count": len(hsc_ltc["rows"]),
            "source": HSC_LTC_URL,
            "title": "新竹縣長照機構名冊",
        },
        "ylLtc": {
            "count": len(yl_ltc["rows"]),
            "source": YL_LTC_URL,
            "title": "宜蘭縣立案老人長期照顧及安養機構名冊",
        },
    }

    if specialty is not None:
        with open("data/specialty.json", "w", encoding="utf-8") as f:
            json.dump(specialty, f, ensure_ascii=False, separators=(",", ":"))
        # 同 tyc-elder，另外輸出內嵌式 JS 版本（window.SPECIALTY_DATA），供前端以 <script> 直接載入。
        with open("data/specialty.js", "w", encoding="utf-8") as f:
            f.write("window.SPECIALTY_DATA = ")
            json.dump(specialty, f, ensure_ascii=False, separators=(",", ":"))
            f.write(";\n")
        meta["specialty"] = {
            "count": len(specialty["rows"]),
            "source": SPECIALTY_SOURCE_PAGE,
            "title": "臺北市長照專業服務特約單位",
        }

    with open("data/meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print("完成！", file=sys.stderr)


if __name__ == "__main__":
    main()
