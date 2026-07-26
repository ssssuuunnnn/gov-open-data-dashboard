#!/usr/bin/env python3
"""
一次性腳本：查詢臺北市假牙補助合約醫療院所（tpe-denture）在 Google 地圖上的評分與評論數。

用途：
- 讀取 data/tpe-denture.json 取得院區名稱與地址，組合查詢字串呼叫 Google Places API (Legacy)
  Text Search 端點，印出比對結果（matched_name / rating / user_ratings_total）供人工核對。
- 此資料集院區僅 6 筆、且未來不會再更新，因此本腳本只需人工執行一次；核對後的結果應手動謄寫進
  scripts/build_data.py 的 TPE_DENTURE_GOOGLE_RATINGS 靜態字典，不會由本腳本自動寫檔。

使用方式：
    GOOGLE_PLACES_API_KEY=xxxx python3 scripts/fetch_tpe_denture_ratings.py

注意：
- API key 一律透過環境變數傳入，不可寫入程式碼或任何要 commit 的檔案。
- 僅使用標準函式庫 urllib，不需安裝 googlemaps 套件，與專案 build_data.py 的零依賴風格一致。
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "tpe-denture.json"


def text_search(query: str, api_key: str) -> dict:
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json?" + urllib.parse.urlencode(
        {"query": query, "key": api_key}
    )
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.load(resp)


def main() -> None:
    api_key = os.environ.get("GOOGLE_PLACES_API_KEY")
    if not api_key:
        print("錯誤：請設定環境變數 GOOGLE_PLACES_API_KEY 後再執行本腳本。", file=sys.stderr)
        sys.exit(1)

    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    fields = data["fields"]
    name_idx = fields.index("name")
    address_idx = fields.index("address")

    for row in data["rows"]:
        name = row[name_idx]
        address = row[address_idx]
        query = f"{name} {address}"
        try:
            result = text_search(query, api_key)
            if result.get("status") != "OK" or not result.get("results"):
                print(f"NOT_FOUND\t{name}\tstatus={result.get('status')}")
            else:
                top = result["results"][0]
                print(
                    f"OK\t{name}\tmatched={top.get('name')}\trating={top.get('rating')}\t"
                    f"user_ratings_total={top.get('user_ratings_total', 0)}"
                )
        except Exception as e:  # noqa: BLE001
            print(f"ERROR\t{name}\t{e}", file=sys.stderr)
        time.sleep(0.2)


if __name__ == "__main__":
    main()
