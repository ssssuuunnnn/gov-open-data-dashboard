#!/usr/bin/env python3
"""一次性/可重複執行腳本：為全站每個頁面（changelog 除外）各自產生一份
manifest.webmanifest，start_url 指向頁面自己，讓「加入應用程式」後開啟的仍是原本瀏覽的那一頁，
而不是全站共用同一個 start_url（Web App Manifest 的 start_url 是相對於 manifest 自身網址解析，
而非相對於當下頁面網址，因此無法用單一共用 manifest 達成「各頁各自安裝」的需求）。

用法：python3 scripts/generate_pwa_manifests.py
每次執行皆完整覆寫所有 manifest.webmanifest（幂等），新增資料集頁面後重新執行本腳本即可自動涵蓋。
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXCLUDE_DIRS = {"changelog"}
THEME_COLOR = "#1f6f5c"
BACKGROUND_COLOR = "#ffffff"


def find_pages():
    """回傳 (page_dir, index_html_path) tuples：根目錄首頁 + 各資料集子目錄，排除 EXCLUDE_DIRS。"""
    pages = [(ROOT, ROOT / "index.html")]
    for child in sorted(ROOT.iterdir()):
        if not child.is_dir() or child.name in EXCLUDE_DIRS:
            continue
        index_html = child / "index.html"
        if index_html.exists():
            pages.append((child, index_html))
    return pages


def extract_title_description(html_text):
    title_m = re.search(r"<title>(.*?)</title>", html_text, re.S)
    title = title_m.group(1).strip() if title_m else ""
    # 移除全站慣例的 SEO 後綴「|郭愷」（manifest 的 name 不需要這個作者標記）。
    # 部分頁面標題使用全形「｜」(U+FF5C) 而非半形「|」，兩種分隔符皆需比對。
    title = re.sub(r"\s*[|｜]\s*郭愷\s*$", "", title)
    desc_m = re.search(
        r'<meta\s+name="description"\s+content="(.*?)"\s*/?>', html_text, re.S
    )
    description = desc_m.group(1).strip() if desc_m else ""
    return title, description


def make_short_name(name):
    """從 name 截斷產生 short_name，優先在頓號/空白處截斷，上限 12 個字元。"""
    if len(name) <= 12:
        return name
    for sep in ("、", " ", "－", "-"):
        idx = name.find(sep)
        if 0 < idx <= 12:
            return name[:idx]
    return name[:12]


def build_manifest(name, description, rel_prefix):
    """rel_prefix：相對於該頁面目錄回到 repo 根目錄 assets/ 的相對路徑前綴，
    首頁為 ""，子頁面為 "../"（比照既有 <link rel="icon"> 相對路徑慣例）。"""
    short_name = make_short_name(name)
    return {
        "name": name,
        "short_name": short_name,
        "description": description,
        "start_url": "./index.html",
        "scope": "./",
        "id": "./index.html",
        "display": "standalone",
        "lang": "zh-Hant-TW",
        "theme_color": THEME_COLOR,
        "background_color": BACKGROUND_COLOR,
        "icons": [
            {
                "src": f"{rel_prefix}assets/icon-192.png",
                "sizes": "192x192",
                "type": "image/png",
            },
            {
                "src": f"{rel_prefix}assets/icon-512.png",
                "sizes": "512x512",
                "type": "image/png",
            },
        ],
    }


def main():
    pages = find_pages()
    count = 0
    for page_dir, index_html in pages:
        html_text = index_html.read_text(encoding="utf-8")
        name, description = extract_title_description(html_text)
        if not name:
            print(f"跳過（找不到 <title>）：{index_html}", file=sys.stderr)
            continue
        rel_prefix = "" if page_dir == ROOT else "../"
        manifest = build_manifest(name, description, rel_prefix)
        out_path = page_dir / "manifest.webmanifest"
        out_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"寫入 {out_path.relative_to(ROOT)}　name={name!r} short_name={manifest['short_name']!r}")
        count += 1
    print(f"完成，共產生 {count} 份 manifest.webmanifest", file=sys.stderr)


if __name__ == "__main__":
    main()
