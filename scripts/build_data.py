#!/usr/bin/env python3
"""
下載並轉換政府開放資料集為前端可用的 JSON。

資料來源：
1. 長照ABC據點  https://ltcpap.mohw.gov.tw/publish/abc.csv
2. 巷弄長照站    https://email.chcg.gov.tw/df/pufnpn5i5741iy9efkn2rrz5ga6uhb
3. 桃園市老人福利機構一覽表  https://opendata.tycg.gov.tw/api/dataset/536bb44b-b9f1-4336-ad26-34b9e25b3a68/resource/3d7e3b4c-8bc5-47c4-85a9-eec70415b189/download
   （來源網址的 CORS 標頭僅允許 opendata.tycg.gov.tw 網域，前端無法直接 fetch，
   需由本腳本於伺服器端下載）

用法：
    python3 scripts/build_data.py
輸出：
    data/abc.json
    data/lane.json
    data/tyc-elder.json
    data/meta.json  (資料更新時間等資訊)
"""
import csv
import io
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone

ABC_URL = "https://ltcpap.mohw.gov.tw/publish/abc.csv"
LANE_URL = "https://email.chcg.gov.tw/df/pufnpn5i5741iy9efkn2rrz5ga6uhb"
TYC_ELDER_URL = "https://opendata.tycg.gov.tw/api/dataset/536bb44b-b9f1-4336-ad26-34b9e25b3a68/resource/3d7e3b4c-8bc5-47c4-85a9-eec70415b189/download"

# O_ABC 類別中文說明
CATEGORY_LABELS = {
    "A": "A級 社區整合型服務中心（旗艦店）",
    "B": "B級 複合型服務中心（據點）",
    "C": "C級 巷弄長照站",
}

ADDR_RE = re.compile(r"^(..[市縣])(.*?[市區鄉鎮])")


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read()
    return raw.decode("utf-8-sig", errors="replace")


def parse_county_district(address: str, fallback_county: str = "") -> tuple[str, str]:
    m = ADDR_RE.match(address or "")
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


def _to_int(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0


def main():
    abc = build_abc()
    lane = build_lane()
    tyc_elder = build_tyc_elder()

    with open("data/abc.json", "w", encoding="utf-8") as f:
        json.dump(abc, f, ensure_ascii=False, separators=(",", ":"))
    with open("data/lane.json", "w", encoding="utf-8") as f:
        json.dump(lane, f, ensure_ascii=False, separators=(",", ":"))
    with open("data/tyc-elder.json", "w", encoding="utf-8") as f:
        json.dump(tyc_elder, f, ensure_ascii=False, separators=(",", ":"))

    meta = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "abc": {"count": len(abc["rows"]), "source": ABC_URL, "title": "長照ABC據點"},
        "lane": {"count": len(lane["rows"]), "source": LANE_URL, "title": "巷弄長照站"},
        "tycElder": {
            "count": len(tyc_elder["rows"]),
            "source": TYC_ELDER_URL,
            "title": "桃園市老人福利機構一覽表",
        },
    }
    with open("data/meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print("完成！", file=sys.stderr)


if __name__ == "__main__":
    main()
