#!/usr/bin/env python3
"""
通用一次性腳本：查詢任一資料集中各機構在 Google 地圖上的評分與評論數，供人工核對後手動整理成
data/source/<dataset>-google-ratings.json（詳見 scripts/build_data.py 各 build_xxx() 內對應資料集
的說明，例如 build_tpe_denture()、build_tyc_elder()）。

設計理由：多個資料集都有「加 Google 評分／評論數，且只抓一次不再更新」的需求，因此把查詢邏輯抽成
通用腳本，用 --dataset 指定要處理的 data/<key>.json，避免每個資料集都複製貼上幾乎相同的程式碼。

使用方式：
    GOOGLE_PLACES_API_KEY=xxxx python3 scripts/fetch_google_ratings.py --dataset tyc-elder
    GOOGLE_PLACES_API_KEY=xxxx python3 scripts/fetch_google_ratings.py --dataset tpe-denture \
        --name-field name --address-field address

輸出：僅列印比對結果（狀態／輸入名稱／Google配對名稱／rating／評論數／place_id）供人工核對，
不會自動寫檔——需人工確認配對正確性後，再手動整理成 data/source/<dataset>-google-ratings.json，
交由 scripts/build_data.py 對應的 build_xxx() 讀取合併。

注意：
- API key 一律透過環境變數傳入，不可寫入程式碼或任何要 commit 的檔案。
- 僅使用標準函式庫 urllib，不需安裝 googlemaps 套件，與專案 build_data.py 的零依賴風格一致。
"""
import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def text_search(query: str, api_key: str) -> dict:
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json?" + urllib.parse.urlencode(
        {"query": query, "key": api_key}
    )
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.load(resp)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dataset", required=True, help="資料集 key，對應 data/<dataset>.json")
    parser.add_argument("--name-field", default="name", help="機構名稱欄位名稱（預設 name）")
    parser.add_argument("--address-field", default="address", help="地址欄位名稱（預設 address）")
    args = parser.parse_args()

    api_key = os.environ.get("GOOGLE_PLACES_API_KEY")
    if not api_key:
        print("錯誤：請設定環境變數 GOOGLE_PLACES_API_KEY 後再執行本腳本。", file=sys.stderr)
        sys.exit(1)

    data_file = ROOT / "data" / f"{args.dataset}.json"
    if not data_file.exists():
        print(f"錯誤：找不到 {data_file}，請確認 --dataset 拼字或先執行 build_data.py。", file=sys.stderr)
        sys.exit(1)

    data = json.loads(data_file.read_text(encoding="utf-8"))
    fields = data["fields"]
    try:
        name_idx = fields.index(args.name_field)
        address_idx = fields.index(args.address_field)
    except ValueError as e:
        print(f"錯誤：欄位不存在（{e}）。可用欄位：{fields}", file=sys.stderr)
        sys.exit(1)

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
                    f"user_ratings_total={top.get('user_ratings_total', 0)}\tplace_id={top.get('place_id')}"
                )
        except Exception as e:  # noqa: BLE001
            print(f"ERROR\t{name}\t{e}", file=sys.stderr)
        time.sleep(0.2)


if __name__ == "__main__":
    main()
