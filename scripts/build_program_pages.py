#!/usr/bin/env python3
"""依 data/programs/*.json 的結構化重點，產生跨縣市比較頁，並提供縣市頁使用的重點區塊。

目前支援：
- data/programs/denture.json → denture-subsidy/index.html（全台老人假牙補助比較）

由 scripts/build_county_pages.py 的 main() 呼叫，不需單獨執行；也可以單獨執行只重產比較頁：
    python3 scripts/build_program_pages.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DENTURE_PATH = "denture-subsidy"
TYPE_LABELS = {"general": "一般長者", "welfare": "低收入／中低收入等福利身分"}
STATUS_LABELS = {"verified": "已對照官方公告", "partial": "部分確認", "pending": "待確認"}


def load_denture():
    path = ROOT / "data" / "programs" / "denture.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _money(n):
    return f"{n:,} 元" if n else None


def _src_href(url, rel):
    return url if url.startswith("http") else f"{rel}{url}"


def _program_dl(p, esc):
    rows = []
    for label, key in [("資格", "eligibility"), ("補助金額", "amounts"), ("受理期間", "period"),
                       ("申請方式", "apply"), ("洽詢", "contact")]:
        if p.get(key):
            rows.append(f"<dt>{label}</dt><dd>{esc(p[key])}</dd>")
    if not p.get("amounts"):
        rows.append('<dt>補助金額</dt><dd class="county-note">本站尚未確認，請見官方公告</dd>')
    return '<dl class="program-dl">' + "".join(rows) + "</dl>"


def _best(c, ptype):
    ps = [p for p in c.get("programs", []) if p["type"] == ptype]
    if not ps:
        return None
    return ps[0]


def denture_anchor(slug):
    return f"county-{slug}"


def county_denture_html(county_name, data, rel, esc):
    """縣市頁使用：該縣市假牙補助重點區塊（找不到資料時回傳空字串）。"""
    if not data:
        return ""
    c = next((x for x in data["counties"] if x["county"] == county_name), None)
    if not c:
        return ""
    compare = f"{rel}{DENTURE_PATH}/#{denture_anchor(c['slug'])}"
    out = ['  <div class="card">\n',
           f'    <h2 class="section-title" style="margin-top:0;">{esc(county_name)}老人假牙補助重點</h2>\n']
    if c["status"] == "pending" or not c.get("programs"):
        src = c["sources"][0] if c.get("sources") else None
        link = f'<a href="{esc(src["url"])}" target="_blank" rel="noopener">{esc(src["title"])}</a>' if src else "縣市政府公告"
        out.append(f'    <p>本站還在確認{esc(county_name)}的假牙補助內容，申請前請先看{link}，或撥打照管中心、公所詢問。</p>\n')
    else:
        for p in c["programs"]:
            out.append(f'    <h3 class="county-subhead">{esc(p["name"])}<span class="county-note">　{esc(TYPE_LABELS[p["type"]])}</span></h3>\n')
            out.append("    " + _program_dl(p, esc) + "\n")
        if c.get("notes"):
            out.append(f'    <p class="county-note">{esc(c["notes"])}</p>\n')
        year = f"{c['year']} 年度" if c.get("year") else ""
        out.append(f'    <p class="county-note">整理依據{esc(year)}公告，僅供參考，實際規定以主管機關最新公告為準。</p>\n')
    out.append(f'    <p><a href="{compare}">比較全台 22 縣市老人假牙補助 →</a></p>\n')
    out.append("  </div>\n")
    return "".join(out)


def build_denture_page(data, h):
    """h：build_county_pages 模組，借用 head_html / footer_html / breadcrumb 與 esc。"""
    esc = h.esc
    rel = "../"
    url = f"{h.SITE}{DENTURE_PATH}/"
    counties = data["counties"]
    n_known = sum(1 for c in counties if c["status"] != "pending")
    n_general = sum(1 for c in counties if _best(c, "general"))
    title = "2026 全台老人假牙補助比較｜22 縣市一般長者與中低收入資格、金額、申請方式"
    description = (f"一頁比較全台 22 縣市老人假牙補助：一般長者與低收入、中低收入長者的申請資格、全口假牙最高補助、"
                   f"受理期間與申請窗口。115 年起中低收入老人假牙補助改由地方政府辦理，各縣市規定不同。")
    faq = [
        {"q": "2026 年（115 年）老人假牙補助還有嗎？",
         "a": "有。衛福部原本補助縣市辦理的中低收入老人假牙補助，自 115 年度起因財政收支劃分法修正改由各地方政府辦理，多數縣市持續辦理，部分縣市另有不限福利身分的一般長者假牙補助。各縣市資格與金額不同，請以戶籍所在縣市公告為準。"},
        {"q": "一般長者假牙補助和中低收入老人假牙補助有什麼不同？",
         "a": "中低收入老人假牙補助的對象是低收入戶、中低收入戶，或領中低收入老人生活津貼、身心障礙者生活補助費等福利身分的長者；一般長者假牙補助則由部分縣市自辦，不限福利身分，但通常有設籍年限、年齡、缺牙程度或所得等條件，而且多為終身一次。"},
        {"q": "假牙補助要先申請還是先做假牙？",
         "a": "幾乎所有縣市都是「先申請、核定後才製作」：先到合約或特約牙醫院所口腔篩檢，由院所或公所送件，核定後才開始做假牙。自行做完再申請，多數縣市不予補助或只補助部分金額。"},
    ]
    webpage_ld = {"@context": "https://schema.org", "@type": "WebPage", "name": "全台老人假牙補助比較",
                  "description": description, "url": url, "inLanguage": "zh-Hant-TW", "dateModified": h.TODAY}
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in faq]}
    crumbs = [("首頁", f"{rel}index.html"), ("全台老人假牙補助比較", "")]
    crumbs_ld = [("首頁", h.SITE), ("全台老人假牙補助比較", url)]

    out = [h.head_html(title=title, description=description,
                       keywords=["老人假牙補助", "假牙補助2026", "115年假牙補助", "中低收入老人假牙", "各縣市假牙補助", "全口假牙補助"],
                       canonical=url, indexable=True,
                       jsonld=[webpage_ld, h.breadcrumb_jsonld(crumbs_ld), faq_ld], rel=rel)]
    out.append(f"""<body>
<header class="site-header">
  <div class="header-inner">
    <h1>全台老人假牙補助比較</h1>
    <div class="meta"><a href="{rel}index.html" style="color:#201f1d;font-weight:bold">← 回首頁</a></div>
  </div>
  <div class="header-inner">
    {h.breadcrumb_html(crumbs)}
    <div class="meta">內容檢視日期：{esc(data.get('reviewedAt', h.TODAY))}</div>
  </div>
</header>
<main class="county-page">
  <div class="card county-intro">
    <p>老人假牙補助由各縣市自己辦理，資格、金額、受理期間和申請窗口差很多：有的縣市只補助低收入、中低收入長者，有的另外開放一般長者申請，但會限制設籍年限、缺牙程度或所得。這一頁把 22 縣市的重點放在同一張表，方便你先確認長輩適用哪一種、可以補助多少。</p>
    <p>{esc(data['background']['text'])}（<a href="{esc(data['background']['source']['url'])}" target="_blank" rel="noopener">{esc(data['background']['source']['title'])}</a>）</p>
  </div>
  <div class="card">
    <div class="stat-grid">
      <div class="stat-card"><div class="num">{n_known}</div><div class="label">已整理的縣市</div></div>
      <div class="stat-card"><div class="num">{n_general}</div><div class="label">有一般長者方案的縣市（已整理範圍內）</div></div>
      <div class="stat-card"><div class="num">{22 - n_known}</div><div class="label">尚待確認的縣市</div></div>
    </div>
  </div>
  <div class="card">
    <h2 class="section-title" style="margin-top:0;">22 縣市假牙補助一覽</h2>
    <p class="county-note" style="margin-top:-6px;">「全口上限」為上下顎全口活動假牙最高補助；「—」表示本站尚未確認，不代表該縣市沒有補助。點縣市名稱看詳細資格與申請方式。</p>
    <div class="table-container-full"><div class="table-wrap"><table class="data-table compare-table">
      <thead><tr><th>縣市</th><th>一般長者方案</th><th>全口上限</th><th>福利身分方案</th><th>全口上限</th><th>資料年度</th><th>本站名冊</th></tr></thead>
      <tbody>
""")
    for c in counties:
        g, w = _best(c, "general"), _best(c, "welfare")
        def cell(p):
            if not p:
                return "—"
            return "有" + (f'<br /><span class="county-note">{esc(p["period"])}</span>' if p.get("period") else "")
        ds = f'<a href="{rel}{esc(c["dataset"])}/index.html">合約院所</a>' if c.get("dataset") else "—"
        year = f"{c['year']}" if c.get("year") else "—"
        if c["status"] == "pending":
            year = "待確認"
        out.append(
            f'        <tr><th scope="row"><a href="#{denture_anchor(c["slug"])}">{esc(c["county"])}</a></th>'
            f'<td>{cell(g)}</td><td>{_money(g.get("maxFull")) if g and g.get("maxFull") else "—"}</td>'
            f'<td>{cell(w)}</td><td>{_money(w.get("maxFull")) if w and w.get("maxFull") else "—"}</td>'
            f'<td>{year}</td><td>{ds}</td></tr>\n'
        )
    out.append("""      </tbody>
    </table></div></div>
  </div>
""")

    out.append('  <div class="card">\n    <h2 class="section-title" style="margin-top:0;">各縣市詳細資格與申請方式</h2>\n')
    for c in counties:
        out.append(f'    <section class="program-county" id="{denture_anchor(c["slug"])}">\n')
        out.append(f'      <h3>{esc(c["county"])}老人假牙補助'
                   f'<span class="county-note">　{esc(STATUS_LABELS[c["status"]])}'
                   f'{"・" + str(c["year"]) + " 年度" if c.get("year") else ""}</span></h3>\n')
        if not c.get("programs"):
            out.append(f'      <p>本站尚未取得{esc(c["county"])}的官方公告內容，申請前請先查看官方頁面或洽詢公所、衛生局。</p>\n')
        for p in c.get("programs", []):
            out.append(f'      <h4>{esc(p["name"])}<span class="county-note">　{esc(TYPE_LABELS[p["type"]])}</span></h4>\n')
            out.append("      " + _program_dl(p, esc) + "\n")
        if c.get("notes"):
            out.append(f'      <p class="county-note">{esc(c["notes"])}</p>\n')
        links = []
        if c.get("dataset"):
            links.append(f'<a href="{rel}{esc(c["dataset"])}/index.html">本站合約院所名冊</a>')
        if c.get("clinics"):
            links.append(f'<a href="{esc(c["clinics"]["url"])}" target="_blank" rel="noopener">{esc(c["clinics"]["note"])}</a>')
        links.append(f'<a href="{rel}county/{esc(c["slug"])}/">{esc(c["county"])}長照資源總整理</a>')
        out.append(f'      <p class="program-links">{"　｜　".join(links)}</p>\n')
        ext = ' target="_blank" rel="noopener"'
        srcs = "；".join(
            f'<a href="{esc(_src_href(s["url"], rel))}"{ext if s["url"].startswith("http") else ""}>{esc(s["title"])}</a>'
            for s in c.get("sources", []))
        if srcs:
            out.append(f'      <p class="county-note">資料來源：{srcs}</p>\n')
        out.append("    </section>\n")
    out.append("  </div>\n")

    out.append('  <section class="faq-section card" id="faq">\n    <h2>老人假牙補助常見問題</h2>\n')
    for f in faq:
        out.append(f'    <details class="faq-item">\n      <summary><h3>{esc(f["q"])}</h3></summary>\n'
                   f'      <div class="faq-answer"><p>{esc(f["a"])}</p></div>\n    </details>\n')
    out.append("  </section>\n</main>\n")
    out.append(f"""<div class="back-home-cta">
  <a href="{rel}county/" class="home-cta-btn"><span class="arrow" aria-hidden="true">←</span>縣市長照資源</a>
  <a href="{rel}index.html" class="home-cta-btn"><span class="arrow" aria-hidden="true">←</span>回首頁</a>
</div>
""")
    out.append(h.footer_html(rel))
    return "".join(out)


def build_all(h):
    """產生所有比較頁，回傳已產生頁面的網址路徑清單（供 sitemap 使用）。"""
    built = []
    data = load_denture()
    if data:
        out = ROOT / DENTURE_PATH / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(build_denture_page(data, h), encoding="utf-8")
        print(f"✓ {DENTURE_PATH}/index.html")
        built.append(f"{DENTURE_PATH}/")
    return built


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import build_county_pages as h  # noqa: E402
    build_all(h)
