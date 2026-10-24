#!/usr/bin/env python3
"""產生縣市長照資源頁（county/<slug>/index.html）與縣市總覽頁（county/index.html）。

資料來源：
- data/counties.json：每個縣市的人工內容（導言、照管中心分站、依需求分類說明、FAQ、鄰近縣市）。
  只有含 "page" 欄位的縣市才會產生頁面。
- index.html 首頁的 .home-card：資料集標題、說明、所屬縣市（data-county），作為「哪個縣市有哪些資料集」
  的唯一來源，新增資料集卡片後重跑本腳本即可同步。
- data/meta.json：各資料集筆數（key 為資料夾名稱轉 camelCase，例如 tyc-respite → tycRespite）。
- data/abc.json：長照ABC據點，依機構代碼去重後統計各縣市／行政區 A、B、C 級據點數。

同時會更新（皆以 <!-- COUNTY_PAGES:... --> 標記區塊冪等替換，可重複執行）：
- index.html：首頁「縣市長照資源專頁」連結清單（靜態 HTML，讓爬蟲可直接抓到）
- 各縣市資料集頁面的「相關資料集」區塊：加上回到縣市總覽頁的連結
- sitemap.xml：縣市頁網址（indexable=false 的頁面不列入）

用法：python3 scripts/build_county_pages.py
不需網路連線，只讀取 repo 內既有檔案。
"""
import datetime as dt
import html
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://www.sunkuo.cc/gov-open-data-dashboard/"
TODAY = dt.date.today().isoformat()

CATEGORY_LABELS = {
    "ltc": "長照 / 老人福利",
    "denture": "老人假牙補助",
    "elder-checkup": "老人健康檢查",
    "disability": "身心障礙鑑定",
    "dementia": "失智症診療",
    "private": "私人機構名錄",
}


def esc(s):
    return html.escape(str(s), quote=True)


def camel(slug):
    head, *rest = slug.split("-")
    return head + "".join(p[:1].upper() + p[1:] for p in rest)


def tel_href(phone):
    """把「03-382-1265 分機503」轉成 tel:033821265，分機不放進撥號連結。"""
    main = re.split(r"分機|轉|#|,|、", phone)[0]
    return "tel:" + re.sub(r"[^0-9+]", "", main)


# ---------------------------------------------------------------------------
# 讀取資料
# ---------------------------------------------------------------------------

def load_cards():
    src = (ROOT / "index.html").read_text(encoding="utf-8")
    pattern = re.compile(
        r'<a class="home-card[^"]*" href="([^"]+)" data-county="([^"]+)" data-category="([^"]+)">\s*'
        r'<span class="tag">([^<]*)</span>\s*<h2>([^<]*)</h2>\s*<div class="desc">(.*?)</div>',
        re.S,
    )
    cards = []
    for href, county, category, tag, title, desc in pattern.findall(src):
        slug = href.split("/")[0]
        plain_desc = re.sub(r"<[^>]+>", "", desc).strip()
        cards.append({
            "slug": slug,
            "href": href,
            "county": county,
            "category": category,
            "tag": tag,
            "title": html.unescape(title),
            "desc": html.unescape(plain_desc),
        })
    if not cards:
        raise SystemExit("找不到首頁資料集卡片，請確認 index.html 的 .home-card 格式未變動")
    return cards


def load_abc_stats():
    data = json.loads((ROOT / "data" / "abc.json").read_text(encoding="utf-8"))
    fields = data["fields"]
    idx = {f: i for i, f in enumerate(fields)}
    # 原始資料一個據點常因登記多項服務而有多列，且同一機構代碼可能同時具 B、C 級身分，
    # 因此「各級數」以（縣市, 級別, 代碼）去重、「合計」以（縣市, 代碼）去重，各級加總會略大於合計。
    seen_cat, seen_total = set(), set()
    by_county = defaultdict(Counter)
    by_district = defaultdict(lambda: defaultdict(Counter))
    for row in data["rows"]:
        county = row[idx["county"]]
        if not county:
            continue
        code = row[idx["code"]] or row[idx["name"]]
        cat = row[idx["category"]]
        district = row[idx["district"]] or ""
        if county.endswith("市") and district and not district.endswith("區"):
            district += "區"  # 直轄市原始資料偶有「平鎮」缺「區」字
        if (county, code) not in seen_total:
            seen_total.add((county, code))
            by_county[county]["_total"] += 1
            by_district[county][district]["_total"] += 1
        if (county, cat, code) not in seen_cat:
            seen_cat.add((county, cat, code))
            by_county[county][cat] += 1
            by_district[county][district][cat] += 1
    return by_county, by_district


# ---------------------------------------------------------------------------
# 頁面片段
# ---------------------------------------------------------------------------

def head_html(*, title, description, keywords, canonical, indexable, jsonld, rel):
    robots = "index, follow" if indexable else "noindex, follow"
    blocks = "\n".join(
        f'<script type="application/ld+json">\n{json.dumps(obj, ensure_ascii=False, indent=2)}\n</script>'
        for obj in jsonld
    )
    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-DNHVGQP5W8"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());

  gtag('config', 'G-DNHVGQP5W8');
</script>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{esc(title)}｜郭愷</title>
<meta name="description" content="{esc(description)}" />
<meta name="keywords" content="{esc(','.join(keywords))}" />
<meta name="robots" content="{robots}" />
<link rel="canonical" href="{esc(canonical)}" />

<!-- Open Graph -->
<meta property="og:type" content="website" />
<meta property="og:site_name" content="台灣長照機構查詢儀表板" />
<meta property="og:locale" content="zh_TW" />
<meta property="og:title" content="{esc(title)}" />
<meta property="og:description" content="{esc(description)}" />
<meta property="og:url" content="{esc(canonical)}" />
<meta property="og:image" content="{SITE}assets/og-image.png" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{esc(title)}" />
<meta name="twitter:description" content="{esc(description)}" />
<meta name="twitter:image" content="{SITE}assets/og-image.png" />

<link rel="icon" type="image/png" href="{rel}assets/favicon.png" />
<link rel="stylesheet" href="{rel}assets/classical-style.css" />
{blocks}
<link rel="manifest" href="{rel}manifest.webmanifest" />
<meta name="theme-color" content="#1f6f5c" />
<link rel="apple-touch-icon" href="{rel}assets/icon-192.png" />
</head>
"""


def breadcrumb_jsonld(items):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": url}
            for i, (name, url) in enumerate(items)
        ],
    }


def breadcrumb_html(items):
    parts = []
    for i, (name, href) in enumerate(items):
        if i == len(items) - 1:
            parts.append(f'<span aria-current="page">{esc(name)}</span>')
        else:
            parts.append(f'<a href="{esc(href)}">{esc(name)}</a>')
    return '<nav class="breadcrumb" aria-label="麵包屑導覽">' + ' <span class="sep">›</span> '.join(parts) + "</nav>"


def footer_html(rel, extra=""):
    return f"""<footer class="site-footer">
  {extra}本頁資料集清單與據點數由本站依政府開放資料自動統計，說明文字整理自各縣市政府公告，僅供參考，實際規定請以主管機關最新公告為準。<br />
  依「政府資料開放授權條款-第1版」釋出，本站僅作資料視覺化整理，實際內容以原始資料集為準。<br />
  <a href="{rel}changelog/index.html">網站更新紀錄</a>　|　本頁面最後更新時間：{TODAY}
</footer>
<script src="{rel}assets/analytics.js"></script>
<script src="{rel}assets/pwa-install.js" defer></script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# 縣市頁
# ---------------------------------------------------------------------------

def build_county_page(county, slug_by_name, county_by_slug, cards, meta, abc_county, abc_district):
    page = county["page"]
    name = county["name"]
    slug = county["slug"]
    rel = "../../"
    url = f"{SITE}county/{slug}/"
    cards_by_slug = {c["slug"]: c for c in cards}

    crumbs = [("首頁", f"{rel}index.html"), ("縣市長照資源", "../"), (name, "")]
    crumbs_ld = [("首頁", SITE), ("縣市長照資源", f"{SITE}county/"), (name, url)]

    faq_ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
            for f in page.get("faq", [])
        ],
    }
    webpage_ld = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": page["h1"],
        "description": page["description"],
        "url": url,
        "inLanguage": "zh-Hant-TW",
        "dateModified": TODAY,
        "about": {"@type": "Place", "name": name},
        "isPartOf": {"@type": "WebSite", "name": "台灣長照機構查詢儀表板", "url": SITE},
    }

    out = [head_html(
        title=page["title"],
        description=page["description"],
        keywords=page.get("keywords", []),
        canonical=url,
        indexable=page.get("indexable", False),
        jsonld=[webpage_ld, breadcrumb_jsonld(crumbs_ld)] + ([faq_ld] if page.get("faq") else []),
        rel=rel,
    )]

    out.append(f"""<body>
<header class="site-header">
  <div class="header-inner">
    <h1>{esc(page['h1'])}</h1>
    <div class="meta"><a href="{rel}index.html" style="color:#201f1d;font-weight:bold">← 回首頁</a></div>
  </div>
  <div class="header-inner">
    {breadcrumb_html(crumbs)}
    <div class="meta">內容檢視日期：{esc(page.get('reviewedAt', TODAY))}</div>
  </div>
</header>
<main class="county-page">
""")

    # 導言
    out.append('  <div class="card county-intro">\n')
    for p in page.get("intro", []):
        out.append(f"    <p>{esc(p)}</p>\n")
    out.append("  </div>\n")

    # 快速資訊
    center = page.get("center")
    out.append('  <div class="card">\n    <h2 class="section-title" style="margin-top:0;">申請長照的第一步</h2>\n')
    out.append('    <div class="county-quick">\n')
    out.append('      <div class="quick-item"><div class="label">長照專線（全國）</div>'
               '<div class="value"><a href="tel:1966">1966</a></div>'
               '<div class="hint">手機、市話皆可撥打，前 5 分鐘免費</div></div>\n')
    if center:
        out.append(f'      <div class="quick-item"><div class="label">{esc(center["name"])}</div>'
                   f'<div class="value"><a href="{tel_href(center["phone"])}">{esc(center["phone"])}</a></div>'
                   f'<div class="hint">{esc(center["address"])}</div></div>\n')
    out.append('      <div class="quick-item"><div class="label">住院中的長輩</div>'
               '<div class="value small">醫院出院準備服務</div>'
               '<div class="hint">出院前即可完成評估，出院後銜接長照服務</div></div>\n')
    out.append("    </div>\n")
    out.append(f'    <p class="county-note">申請流程、四包錢、費用與部分負擔等通用說明，請見<a href="{rel}index.html#faq">首頁長照常見問答</a>。</p>\n')
    out.append("  </div>\n")

    # 據點數總覽
    total = abc_county.get("_total", 0)
    if total:
        out.append('  <div class="card">\n')
        out.append(f'    <h2 class="section-title" style="margin-top:0;">{esc(name)}長照據點數總覽</h2>\n')
        out.append('    <div class="stat-grid">\n')
        for label, num in [
            ("ABC 據點合計", total),
            ("A 級 社區整合型服務中心", abc_county.get("A", 0)),
            ("B 級 複合型服務中心", abc_county.get("B", 0)),
            ("C 級 巷弄長照站", abc_county.get("C", 0)),
        ]:
            out.append(f'      <div class="stat-card"><div class="num">{num:,}</div><div class="label">{esc(label)}</div></div>\n')
        out.append("    </div>\n")
        out.append('    <p class="county-note">依衛生福利部「長照ABC據點」開放資料，以機構代碼去除重複後統計'
                   '（同一據點登記多項服務時只計一次，因此會少於 ABC 地圖頁的服務筆數；少數據點同時具 B、C 級身分，'
                   '各級加總會略大於合計）。</p>\n')
        out.append("  </div>\n")

    # 各區分站 × 據點數
    if center and center.get("branches"):
        district_rows = []
        for b in center["branches"]:
            for d in b["districts"]:
                district_rows.append((d, b))
        out.append('  <div class="card">\n')
        out.append(f'    <h2 class="section-title" style="margin-top:0;">{esc(name)}各區長照管理中心分站與據點數</h2>\n')
        out.append('    <p class="county-note" style="margin-top:-6px;">找長輩居住行政區對應的分站即可，'
                   '照管專員會到府評估。據點數為該區 A／B／C 級據點數。</p>\n')
        out.append('    <div class="table-container-full"><div class="table-wrap"><table class="data-table">\n')
        out.append("      <thead><tr><th>行政區</th><th>負責分站</th><th>電話</th><th>地址</th>"
                   "<th>A</th><th>B</th><th>C</th></tr></thead>\n      <tbody>\n")
        for d, b in district_rows:
            c = abc_district.get(d, Counter())
            note = f'<br /><span class="county-note">{esc(b["note"])}</span>' if b.get("note") else ""
            out.append(
                f'        <tr><th scope="row">{esc(d)}</th><td>{esc(b["name"])}{note}</td>'
                f'<td><a href="{tel_href(b["phone"])}">{esc(b["phone"])}</a></td>'
                f'<td>{esc(b["address"])}</td>'
                f'<td>{c.get("A", 0)}</td><td>{c.get("B", 0)}</td><td>{c.get("C", 0)}</td></tr>\n'
            )
        out.append("      </tbody>\n    </table></div></div>\n")
        src_note = f'分站資料來源：<a href="{esc(center["source"])}" target="_blank" rel="noopener">{esc(name)}長期照顧管理中心</a>'
        if center.get("note"):
            src_note += f"；{esc(center['note'])}"
        out.append(f'    <p class="county-note">{src_note}</p>\n')
        out.append("  </div>\n")

    # 依需求找資源
    out.append('  <div class="card">\n')
    out.append('    <h2 class="section-title" style="margin-top:0;">依需求找資源</h2>\n')
    out.append('    <div class="need-list">\n')
    used = set()
    for need in page.get("needs", []):
        ds = need["dataset"]
        card = cards_by_slug.get(ds)
        if not card:
            print(f"  ⚠️ {name}：needs 指定的資料集 {ds} 不在首頁卡片中，略過")
            continue
        used.add(ds)
        m = meta.get(camel(ds)) or {}
        if ds == "abc" and total:
            count_text = f"{total:,} 個據點"
        elif need.get("countText"):
            count_text = need["countText"]
        elif m.get("count"):
            count_text = f"{m['count']:,} 筆"
        else:
            count_text = ""
        href = f"{rel}{ds}/index.html{need.get('query', '')}"
        out.append('      <section class="need-item">\n')
        out.append(f'        <h3><a href="{esc(href)}">{esc(need["heading"])}</a></h3>\n')
        out.append(f'        <p>{esc(need["text"])}</p>\n')
        meta_line = f'<a href="{esc(href)}">查看資料集：{esc(card["title"])} →</a>'
        if count_text:
            meta_line += f' <span class="count">{esc(count_text)}</span>'
        out.append(f'        <div class="need-meta">{meta_line}</div>\n')
        out.append("      </section>\n")
    out.append("    </div>\n")

    # 未在 needs 中說明、但屬於此縣市的資料集，自動補列，避免新增資料集後漏掉
    others = [c for c in cards if c["county"] == name and c["slug"] not in used]
    if others:
        out.append(f'    <h3 class="county-subhead">其他{esc(name)}資料集</h3>\n    <ul class="county-links">\n')
        for c in others:
            out.append(f'      <li><a href="{rel}{esc(c["href"])}">{esc(c["title"])}</a></li>\n')
        out.append("    </ul>\n")
    out.append("  </div>\n")

    # 全國性資料集
    national = [c for c in cards if c["county"] == "all" and c["slug"] not in used]
    if national:
        out.append('  <div class="card">\n')
        out.append(f'    <h2 class="section-title" style="margin-top:0;">{esc(name)}也適用的全國性資源</h2>\n')
        out.append('    <ul class="county-links">\n')
        for c in national:
            out.append(f'      <li><a href="{rel}{esc(c["href"])}">{esc(c["title"])}</a>'
                       f'<span class="county-note">　{esc(c["tag"])}</span></li>\n')
        out.append("    </ul>\n  </div>\n")

    # FAQ
    if page.get("faq"):
        out.append('  <section class="faq-section card" id="faq">\n')
        out.append(f'    <h2>{esc(name)}長照常見問題</h2>\n')
        out.append('    <p class="faq-intro">整理自本站各資料集頁面的公告說明，實際規定以主管機關最新公告為準。</p>\n')
        for f in page["faq"]:
            out.append('    <details class="faq-item">\n')
            out.append(f'      <summary><h3>{esc(f["q"])}</h3></summary>\n')
            out.append(f'      <div class="faq-answer"><p>{esc(f["a"])}</p></div>\n')
            out.append("    </details>\n")
        out.append("  </section>\n")

    # 鄰近縣市
    if page.get("neighbors"):
        out.append('  <div class="card">\n    <h2 class="section-title" style="margin-top:0;">鄰近縣市長照資源</h2>\n')
        out.append('    <ul class="county-links inline">\n')
        for nslug in page["neighbors"]:
            n = county_by_slug.get(nslug)
            if not n:
                continue
            if n.get("page"):
                href = f"../{nslug}/"
            else:
                href = f"{rel}index.html?counties={n['name']}"
            out.append(f'      <li><a href="{esc(href)}">{esc(n["name"])}</a></li>\n')
        out.append("    </ul>\n  </div>\n")

    out.append("</main>\n")
    out.append(f"""<div class="back-home-cta">
  <a href="../" class="home-cta-btn"><span class="arrow" aria-hidden="true">←</span>其他縣市長照資源</a>
  <a href="{rel}index.html" class="home-cta-btn"><span class="arrow" aria-hidden="true">←</span>回首頁</a>
</div>
""")
    out.append(footer_html(rel))
    return "".join(out)


# ---------------------------------------------------------------------------
# 縣市總覽頁
# ---------------------------------------------------------------------------

def build_hub(counties, cards, abc_by_county):
    rel = "../"
    url = f"{SITE}county/"
    title = "全台22縣市長照資源查詢｜各縣市長照據點、喘息、交通接送與補助資料集總覽"
    description = "依縣市整理長照資源：各縣市長照ABC據點數、專屬政府開放資料集（喘息服務、交通接送、失智症診療、假牙補助、身心障礙鑑定等），點選縣市即可查看當地長照資源。"
    crumbs = [("首頁", f"{rel}index.html"), ("縣市長照資源", "")]
    crumbs_ld = [("首頁", SITE), ("縣市長照資源", url)]
    built = [c for c in counties if c.get("page")]
    itemlist = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "縣市長照資源頁",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": f"{c['name']}長照資源", "url": f"{url}{c['slug']}/"}
            for i, c in enumerate(built)
        ],
    }
    out = [head_html(
        title=title, description=description,
        keywords=["縣市長照資源", "長照據點", "長照查詢", "長照2.0", "長照3.0", "喘息服務", "長照交通接送"],
        canonical=url, indexable=True, jsonld=[breadcrumb_jsonld(crumbs_ld), itemlist], rel=rel,
    )]
    out.append(f"""<body>
<header class="site-header">
  <div class="header-inner">
    <h1>全台縣市長照資源查詢</h1>
    <div class="meta"><a href="{rel}index.html" style="color:#201f1d;font-weight:bold">← 回首頁</a></div>
  </div>
  <div class="header-inner">
    {breadcrumb_html(crumbs)}
  </div>
</header>
<main class="county-page">
  <div class="card county-intro">
    <p>長照服務由各縣市政府的長期照顧管理中心受理，補助細節與服務單位也因縣市而異。下表列出每個縣市的長照 ABC 據點數與本站收錄的專屬資料集數；已建立專頁的縣市可直接點進查看分站電話、各類資源與常見問題，其他縣市則會帶你到首頁的縣市篩選結果。</p>
  </div>
  <div class="card">
    <h2 class="section-title" style="margin-top:0;">選擇縣市</h2>
    <div class="county-grid">
""")
    dataset_counts = Counter(c["county"] for c in cards if c["county"] != "all")
    for c in counties:
        abc_total = abc_by_county.get(c["name"], Counter()).get("_total", 0)
        n = dataset_counts.get(c["name"], 0)
        if c.get("page"):
            href, badge = f"{c['slug']}/", '<span class="tag">完整專頁</span>'
        else:
            href, badge = f"{rel}index.html?counties={c['name']}", ""
        out.append(
            f'      <a class="county-tile{" built" if c.get("page") else ""}" href="{esc(href)}">'
            f'{badge}<strong>{esc(c["name"])}</strong>'
            f'<span class="county-note">ABC 據點 {abc_total:,} 處 · 專屬資料集 {n} 個</span></a>\n'
        )
    out.append("""    </div>
    <p class="county-note">ABC 據點數依衛生福利部「長照ABC據點」開放資料以機構代碼去重統計；專屬資料集數不含全國性資料集。</p>
  </div>
</main>
""")
    out.append(f"""<div class="back-home-cta">
  <a href="{rel}index.html" class="home-cta-btn"><span class="arrow" aria-hidden="true">←</span>回首頁</a>
</div>
""")
    out.append(footer_html(rel))
    return "".join(out)


# ---------------------------------------------------------------------------
# 更新既有檔案（標記區塊冪等替換）
# ---------------------------------------------------------------------------

def replace_block(text, name, new_inner, indent=""):
    start, end = f"<!-- COUNTY_PAGES:{name}:START -->", f"<!-- COUNTY_PAGES:{name}:END -->"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    block = f"{start}\n{new_inner}{indent}{end}"
    if not pattern.search(text):
        return None
    return pattern.sub(lambda _: block, text, count=1)


def update_homepage(built):
    path = ROOT / "index.html"
    text = path.read_text(encoding="utf-8")
    links = "".join(
        f'      <a class="county-page-link" href="county/{c["slug"]}/" data-county-page="{esc(c["name"])}">{esc(c["name"])}長照資源總整理</a>\n'
        for c in built
    )
    inner = f'      <a class="county-page-link all" href="county/">全台縣市總覽</a>\n{links}'
    new = replace_block(text, "HOME", inner, indent="      ")
    if new is None:
        print("  ⚠️ index.html 找不到 COUNTY_PAGES:HOME 標記，略過首頁更新")
        return
    path.write_text(new, encoding="utf-8")


def update_dataset_pages(cards, built):
    slug_of = {c["name"]: c["slug"] for c in built}
    for card in cards:
        cslug = slug_of.get(card["county"])
        path = ROOT / card["slug"] / "index.html"
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        marker_start = "<!-- COUNTY_PAGES:RELATED:START -->"
        if cslug:
            inner = f'    <a href="../county/{cslug}/" class="county-hub-link">{esc(card["county"])}長照資源總整理</a>\n'
        else:
            inner = ""
        if marker_start in text:
            new = replace_block(text, "RELATED", inner, indent="    ")
        elif cslug and "<strong>相關資料集：</strong>" in text:
            new = text.replace(
                "<strong>相關資料集：</strong>",
                f"<strong>相關資料集：</strong>\n    {marker_start}\n{inner}    <!-- COUNTY_PAGES:RELATED:END -->",
                1,
            )
        else:
            continue
        if new and new != text:
            path.write_text(new, encoding="utf-8")
            print(f"  ↺ {card['slug']}/index.html 加上縣市頁連結")


def update_sitemap(built):
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    entries = [f"{SITE}county/"] + [f"{SITE}county/{c['slug']}/" for c in built if c["page"].get("indexable")]
    inner = "".join(
        f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.9</priority>\n  </url>\n"
        for u in entries
    )
    new = replace_block(text, "SITEMAP", inner, indent="  ")
    if new is None:
        new = text.replace(
            "</urlset>",
            f"  <!-- COUNTY_PAGES:SITEMAP:START -->\n{inner}  <!-- COUNTY_PAGES:SITEMAP:END -->\n</urlset>",
        )
    path.write_text(new, encoding="utf-8")


def main():
    cfg = json.loads((ROOT / "data" / "counties.json").read_text(encoding="utf-8"))
    counties = cfg["counties"]
    county_by_slug = {c["slug"]: c for c in counties}
    slug_by_name = {c["name"]: c["slug"] for c in counties}
    cards = load_cards()
    meta = json.loads((ROOT / "data" / "meta.json").read_text(encoding="utf-8"))
    abc_by_county, abc_by_district = load_abc_stats()

    built = [c for c in counties if c.get("page")]
    for c in built:
        html_text = build_county_page(
            c, slug_by_name, county_by_slug, cards, meta,
            abc_by_county.get(c["name"], Counter()), abc_by_district.get(c["name"], {}),
        )
        out = ROOT / "county" / c["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html_text, encoding="utf-8")
        print(f"✓ county/{c['slug']}/index.html（{'索引' if c['page'].get('indexable') else 'noindex'}）")

    hub = ROOT / "county" / "index.html"
    hub.parent.mkdir(parents=True, exist_ok=True)
    hub.write_text(build_hub(counties, cards, abc_by_county), encoding="utf-8")
    print("✓ county/index.html")

    update_homepage(built)
    update_dataset_pages(cards, built)
    update_sitemap(built)
    print("✓ index.html / sitemap.xml 已同步")


if __name__ == "__main__":
    main()
