#!/usr/bin/env python3
"""一次性腳本：對全站頁面（changelog 除外）的 index.html 插入 PWA 相關標籤：
- <head> 內：<link rel="manifest">、<meta name="theme-color">、<link rel="apple-touch-icon">
- </body> 前：<script src=".../assets/pwa-install.js" defer></script>

冪等設計：執行前會檢查是否已插入過（搜尋 'rel="manifest"' 字串），已插入的頁面會跳過，
避免重複執行造成標籤重複。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXCLUDE_DIRS = {"changelog"}


def find_pages():
    pages = [(ROOT, ROOT / "index.html")]
    for child in sorted(ROOT.iterdir()):
        if not child.is_dir() or child.name in EXCLUDE_DIRS:
            continue
        index_html = child / "index.html"
        if index_html.exists():
            pages.append((child, index_html))
    return pages


def apply_tags(html_text, rel_prefix):
    if 'rel="manifest"' in html_text:
        return html_text, False  # 已插入過，跳過

    head_tags = (
        f'<link rel="manifest" href="manifest.webmanifest" />\n'
        f'<meta name="theme-color" content="#1f6f5c" />\n'
        f'<link rel="apple-touch-icon" href="{rel_prefix}assets/icon-192.png" />\n'
    )
    new_html, n_head = re.subn(r"</head>", head_tags + "</head>", html_text, count=1)
    if n_head != 1:
        raise ValueError("找不到 </head>，無法插入 PWA head 標籤")

    body_tag = f'<script src="{rel_prefix}assets/pwa-install.js" defer></script>\n'
    new_html, n_body = re.subn(r"</body>", body_tag + "</body>", new_html, count=1)
    if n_body != 1:
        raise ValueError("找不到 </body>，無法插入 pwa-install.js")

    return new_html, True


def main():
    pages = find_pages()
    updated = 0
    for page_dir, index_html in pages:
        rel_prefix = "" if page_dir == ROOT else "../"
        html_text = index_html.read_text(encoding="utf-8")
        new_html, changed = apply_tags(html_text, rel_prefix)
        if changed:
            index_html.write_text(new_html, encoding="utf-8")
            print(f"已插入 PWA 標籤：{index_html.relative_to(ROOT)}")
            updated += 1
        else:
            print(f"跳過（已插入過）：{index_html.relative_to(ROOT)}")
    print(f"完成，共更新 {updated} 個頁面", file=sys.stderr)


if __name__ == "__main__":
    main()
