# PWA 安裝提示 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 讓除了 `changelog/index.html` 以外的全站 54 個頁面（首頁＋53 個資料集頁面）都具備各自獨立的
PWA manifest、共用 Service Worker、以及「可以將此頁面加入應用程式，方便未來持續查詢或找不到頁面」的
安裝提示橫幅。

**Architecture:** 兩支一次性 Python 產生腳本（manifest 產生器＋批次標籤插入器）+ 兩支共用前端資源
（`assets/sw.js`、`assets/pwa-install.js`）+ 兩個新增圖示檔（`assets/icon-192.png`、
`assets/icon-512.png`）。零建置：所有輸出皆為靜態檔案，瀏覽器直接讀取，不需 bundler。

**Tech Stack:** Python 3 標準函式庫＋Pillow（圖示縮放，專案已用於既有 og-image 產生）、原生 ES5+
瀏覽器 JS（Service Worker API、Web App Manifest、`beforeinstallprompt`）。

本專案沒有自動化測試框架（純靜態網站），因此本計畫中的「測試」步驟一律替換為專案既有慣例的驗證方式：
`node -c` 語法檢查、Python 直接執行驗證輸出、`grep` 抽查標籤是否插入、瀏覽器 DevTools／curl 檢查本機
伺服器回應。這與本 repo 現有的驗證慣例一致（見 `README.md`「已知限制」章節）。

## Global Constraints

- 排除頁面：`changelog/index.html` 完全不得被本計畫任何腳本修改。
- 提示橫幅文字必須逐字使用：「可以將此頁面加入應用程式，方便未來持續查詢或找不到頁面」。
- 不引入任何 npm 套件／bundler／Workbox 等第三方 PWA 框架。
- 不修改 `robots.txt`／`sitemap.xml`（manifest／sw.js 不需要列入）。
- `<title>` 結尾「|郭愷」等既有 SEO 慣例維持不變，manifest 的 `name` 需去除該後綴。
- theme_color 固定 `#1f6f5c`（沿用 `assets/classical-style.css` 的 `--color-primary`），
  background_color 固定 `#ffffff`。
- Service Worker 對 `data/*.json`／`data/*.js`／HTML 頁面採 network-first；對共用靜態資源
  （css/js/圖示）採 cache-first；不快取跨網域資源（CDN／GA）。

---

### Task 1：產生 PWA 圖示（192×192、512×512）

**Files:**
- Create: `assets/icon-192.png`
- Create: `assets/icon-512.png`

**Interfaces:**
- Consumes: 既有 `assets/favicon.png`（256×256 PNG）
- Produces: 供 Task 2（manifest JSON 的 `icons` 欄位）與 Task 4（`<link rel="apple-touch-icon">`）
  使用的兩個固定檔名圖示檔。

- [ ] **Step 1：用 Pillow 從既有 favicon 產生兩種尺寸圖示**

```bash
cd /Users/sun/Projects/gov_open_data && python3 -c "
from PIL import Image
src = Image.open('assets/favicon.png').convert('RGBA')
for size in (192, 512):
    img = src.resize((size, size), Image.LANCZOS)
    img.save(f'assets/icon-{size}.png')
    print(f'assets/icon-{size}.png ->', img.size)
"
```

- [ ] **Step 2：驗證輸出檔案存在且尺寸正確**

```bash
file assets/icon-192.png assets/icon-512.png
```
Expected: 兩行輸出皆為 `PNG image data, <size> x <size>`，尺寸分別為 192x192 與 512x512。

- [ ] **Step 3：Commit**

```bash
git add assets/icon-192.png assets/icon-512.png
git commit -m "feat(pwa): add 192/512 icons generated from favicon

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 2：`scripts/generate_pwa_manifests.py` — 逐頁產生 manifest.webmanifest

**Files:**
- Create: `scripts/generate_pwa_manifests.py`
- Create（由腳本執行產生，非手寫）: `manifest.webmanifest`（根目錄，供首頁使用）以及每個資料集
  目錄下的 `<dir>/manifest.webmanifest`（53 份）

**Interfaces:**
- Consumes: 各頁面既有 `<title>...</title>` 與 `<meta name="description" content="...">`（正規表達式解析，
  不需額外相依套件）。
- Produces: 每個目錄下的 `manifest.webmanifest` 檔案，固定 schema（`name`／`short_name`／
  `description`／`start_url`／`scope`／`id`／`display`／`lang`／`theme_color`／`background_color`／
  `icons`），供 Task 4 的 `<link rel="manifest">` 參照。

- [ ] **Step 1：建立腳本骨架與頁面清單掃描邏輯**

建立 `scripts/generate_pwa_manifests.py`：

```python
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
    # 移除全站慣例的 SEO 後綴「|郭愷」（manifest 的 name 不需要這個作者標記）
    title = re.sub(r"\s*\|\s*郭愷\s*$", "", title)
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


if __name__ == "__main__":
    main()
```

- [ ] **Step 2：實作 `main()` 寫出各頁 manifest**

在同一檔案補上 `main()`（放在 `if __name__` 判斷之前）：

```python
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
```

- [ ] **Step 3：執行腳本並驗證輸出**

```bash
cd /Users/sun/Projects/gov_open_data && python3 scripts/generate_pwa_manifests.py
```
Expected: 印出 54 行（首頁 + 53 個資料集頁面）`寫入 .../manifest.webmanifest ...` 訊息，
最後一行 `完成，共產生 54 份 manifest.webmanifest`。

```bash
ls manifest.webmanifest tc-elder-checkup/manifest.webmanifest
ls changelog/manifest.webmanifest 2>&1
```
Expected: 前兩個檔案存在；`changelog/manifest.webmanifest` 回報 `No such file or directory`。

```bash
python3 -c "
import json
m = json.load(open('tc-elder-checkup/manifest.webmanifest', encoding='utf-8'))
assert m['start_url'] == './index.html'
assert m['icons'][0]['src'] == '../assets/icon-192.png'
assert '|' not in m['name']
print('OK', m['name'], m['short_name'])
"
```
Expected: 印出 `OK <頁面名稱> <短名稱>`，不拋出 AssertionError。

- [ ] **Step 4：Commit**

```bash
git add scripts/generate_pwa_manifests.py manifest.webmanifest '*/manifest.webmanifest'
git commit -m "feat(pwa): generate per-page web app manifests

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 3：`assets/sw.js` — 共用 Service Worker

**Files:**
- Create: `assets/sw.js`

**Interfaces:**
- Consumes: 無（獨立檔案，瀏覽器直接以 `navigator.serviceWorker.register(url)` 註冊，`url` 由
  Task 5 的 `assets/pwa-install.js` 動態計算後傳入）。
- Produces: 全域 Service Worker，攔截 `fetch` 事件；不匯出任何 JS 符號供其他檔案 import（Service
  Worker 執行在獨立的 worker context，本來就無法被其他頁面 script 直接呼叫）。

- [ ] **Step 1：建立 `assets/sw.js`**

```javascript
/**
 * 全站共用 Service Worker。
 *
 * 快取策略：
 * - 共用靜態資源（CSS/共用 JS/圖示，見 SHELL_ASSETS）：cache-first，減少重複下載。
 * - HTML 頁面與資料檔（data/*.json、data/*.js）：network-first，失敗（離線）才退回快取，
 *   確保平常都拿最新版本的政府開放資料，只有離線時才顯示上次瀏覽的內容。
 * - 其餘（跨網域 CDN、Google Analytics 等第三方資源、非 GET 請求）：一律略過，交還瀏覽器預設處理，
 *   不快取任何第三方資源。
 *
 * 版本管理：修改 SHELL_ASSETS 或快取邏輯時，遞增 CACHE_VERSION，install/activate 會自動清除舊版快取。
 */
const CACHE_VERSION = "shell-v1";

// 這份清單需與 assets/ 目錄實際檔案同步；新增/更名共用資源時記得一併更新。
const SHELL_ASSETS = [
  "/gov-open-data-dashboard/assets/classical-style.css",
  "/gov-open-data-dashboard/assets/table.js",
  "/gov-open-data-dashboard/assets/analytics.js",
  "/gov-open-data-dashboard/assets/favicon.png",
  "/gov-open-data-dashboard/assets/icon-192.png",
  "/gov-open-data-dashboard/assets/icon-512.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION).then((cache) => cache.addAll(SHELL_ASSETS)).catch(() => {
      // 本機開發伺服器路徑可能與正式站不同（無 /gov-open-data-dashboard/ 前綴），
      // 預快取失敗不應阻擋 Service Worker 安裝，僅記錄略過。
    })
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE_VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

function isDataOrHtml(url) {
  return url.pathname.endsWith(".html") || url.pathname.endsWith("/") ||
    (url.pathname.includes("/data/") && (url.pathname.endsWith(".json") || url.pathname.endsWith(".js")));
}

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return; // 不快取跨網域（CDN/GA）資源

  if (isDataOrHtml(url)) {
    // network-first：平常都拿最新資料，離線時才退回快取
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE_VERSION).then((cache) => cache.put(req, copy));
          return res;
        })
        .catch(() => caches.match(req))
    );
    return;
  }

  // cache-first：共用靜態資源（css/共用 js/圖示）
  event.respondWith(
    caches.match(req).then((cached) => {
      if (cached) return cached;
      return fetch(req).then((res) => {
        const copy = res.clone();
        caches.open(CACHE_VERSION).then((cache) => cache.put(req, copy));
        return res;
      });
    })
  );
});
```

- [ ] **Step 2：語法檢查**

```bash
cd /Users/sun/Projects/gov_open_data && node -c assets/sw.js
```
Expected: 無輸出（exit code 0）。

- [ ] **Step 3：Commit**

```bash
git add assets/sw.js
git commit -m "feat(pwa): add shared service worker with network-first data caching

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 4：`assets/pwa-install.js` — 安裝提示橫幅

**Files:**
- Create: `assets/pwa-install.js`
- Modify: `assets/classical-style.css`（新增 `.pwa-install-banner` 相關樣式，加在檔案最末）

**Interfaces:**
- Consumes: 無外部依賴；使用瀏覽器原生 `beforeinstallprompt`／`appinstalled` 事件、
  `navigator.serviceWorker`、`localStorage`。
- Produces: 全域自動執行（IIFE），頁面載入後自動判斷是否需要顯示橫幅；不匯出符號供其他腳本呼叫。

- [ ] **Step 1：在 `assets/classical-style.css` 末尾新增橫幅樣式**

```css
/* PWA 安裝提示橫幅（assets/pwa-install.js 動態注入 DOM，樣式集中於此，供全站共用） */
.pwa-install-banner {
  position: fixed;
  left: 50%;
  bottom: 16px;
  transform: translateX(-50%);
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 12px;
  max-width: min(520px, calc(100vw - 32px));
  background: #1f6f5c;
  color: #fff;
  border-radius: 10px;
  padding: 12px 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
  font-size: 0.9rem;
  line-height: 1.4;
}
.pwa-install-banner .pwa-install-text { flex: 1; }
.pwa-install-banner button {
  flex-shrink: 0;
  border: none;
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 0.85rem;
  cursor: pointer;
}
.pwa-install-banner .pwa-install-accept { background: #fff; color: #1f6f5c; font-weight: 600; }
.pwa-install-banner .pwa-install-dismiss { background: transparent; color: #fff; text-decoration: underline; }
@media (max-width: 480px) {
  .pwa-install-banner { flex-direction: column; align-items: stretch; }
  .pwa-install-banner button { width: 100%; }
}
```

- [ ] **Step 2：建立 `assets/pwa-install.js`**

```javascript
/**
 * 全站共用 PWA 安裝提示橫幅（changelog/index.html 不引入本檔案，維持原樣不受影響）。
 *
 * 行為：
 * - 用 document.currentScript.src 動態算出 assets/ 目錄網址，據此推導同目錄的 sw.js 網址並註冊，
 *   不論本腳本被哪個深度的頁面引入（首頁 "assets/pwa-install.js" 或子頁面
 *   "../assets/pwa-install.js"）都能正確運作，不需頁面額外傳入路徑參數。
 * - 監聽 beforeinstallprompt：保留事件，顯示橫幅提示「可以將此頁面加入應用程式，方便未來持續查詢
 *   或找不到頁面」，使用者按「加入」才呼叫 deferredPrompt.prompt()。
 * - 若使用者在這一頁按過「不用了」（localStorage 記錄，key 含 pathname，僅影響單一頁面，不影響
 *   其他資料集頁面的提示），或已經是安裝後以 standalone 模式開啟，則不顯示橫幅。
 * - iOS Safari 不支援 beforeinstallprompt，該裝置使用者不會看到本橫幅（已知限制，見設計文件）。
 */
(function () {
  if (!("serviceWorker" in navigator)) return;

  var scriptURL = document.currentScript.src;
  var swURL = new URL("sw.js", scriptURL).href;
  navigator.serviceWorker.register(swURL).catch(function () {
    // 本機開發伺服器或非標準部署路徑可能註冊失敗，不影響頁面其餘功能，靜默略過。
  });

  var isStandalone =
    (window.matchMedia && window.matchMedia("(display-mode: standalone)").matches) ||
    window.navigator.standalone === true;
  if (isStandalone) return;

  var dismissKey = "pwaInstallDismissed:" + location.pathname;
  if (localStorage.getItem(dismissKey)) return;

  var deferredPrompt = null;
  var banner = null;

  function showBanner() {
    if (banner) return;
    banner = document.createElement("div");
    banner.className = "pwa-install-banner";
    banner.innerHTML =
      '<span class="pwa-install-text">可以將此頁面加入應用程式，方便未來持續查詢或找不到頁面</span>' +
      '<button type="button" class="pwa-install-accept">加入</button>' +
      '<button type="button" class="pwa-install-dismiss">不用了</button>';
    document.body.appendChild(banner);

    banner.querySelector(".pwa-install-accept").addEventListener("click", function () {
      if (!deferredPrompt) {
        hideBanner();
        return;
      }
      deferredPrompt.prompt();
      deferredPrompt.userChoice.finally(function () {
        deferredPrompt = null;
        hideBanner();
      });
    });

    banner.querySelector(".pwa-install-dismiss").addEventListener("click", function () {
      localStorage.setItem(dismissKey, "1");
      hideBanner();
    });
  }

  function hideBanner() {
    if (banner && banner.parentNode) banner.parentNode.removeChild(banner);
    banner = null;
  }

  window.addEventListener("beforeinstallprompt", function (event) {
    event.preventDefault();
    deferredPrompt = event;
    showBanner();
  });

  window.addEventListener("appinstalled", function () {
    hideBanner();
  });
})();
```

- [ ] **Step 3：語法檢查**

```bash
cd /Users/sun/Projects/gov_open_data && node -c assets/pwa-install.js
```
Expected: 無輸出（exit code 0）。

- [ ] **Step 4：Commit**

```bash
git add assets/pwa-install.js assets/classical-style.css
git commit -m "feat(pwa): add install-prompt banner script and styles

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 5：`scripts/apply_pwa_tags.py` — 批次插入 54 個頁面的 `<head>`／`<body>` 標籤

**Files:**
- Create: `scripts/apply_pwa_tags.py`
- Modify（由腳本執行）: 54 個 `*/index.html`（不含 `changelog/index.html`）

**Interfaces:**
- Consumes: Task 2 產生的 `manifest.webmanifest`（僅用來確認同目錄檔案存在，不解析內容）、
  Task 1 產生的圖示檔、Task 3/4 的 `sw.js`／`pwa-install.js`（僅路徑引用，不解析內容）。
- Produces: 修改後的 54 個 `index.html`，`</head>` 前多 3 行、`</body>` 前多 1 行；
  `changelog/index.html` 保持位元組不變。

- [ ] **Step 1：建立 `scripts/apply_pwa_tags.py`**

```python
#!/usr/bin/env python3
"""一次性腳本：對全站 54 個頁面（changelog 除外）的 index.html 插入 PWA 相關標籤：
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
```

- [ ] **Step 2：執行腳本**

```bash
cd /Users/sun/Projects/gov_open_data && python3 scripts/apply_pwa_tags.py
```
Expected: 印出 54 行 `已插入 PWA 標籤：...`，最後 `完成，共更新 54 個頁面`。

- [ ] **Step 3：驗證 changelog 未被修改、其餘頁面皆已插入**

```bash
git diff --stat changelog/index.html
grep -L 'rel="manifest"' */index.html index.html 2>/dev/null
```
Expected: 第一行指令**沒有輸出**（`changelog/index.html` 完全未變動）；第二行指令僅列出
`changelog/index.html`（唯一沒有 manifest 標籤的頁面）。

```bash
grep -c 'pwa-install.js' */index.html index.html | grep -v ':1$' | grep -v 'changelog'
```
Expected: 無輸出（代表除了 changelog 以外，每個頁面都恰好插入 1 次 `pwa-install.js`）。

- [ ] **Step 4：抽查首頁與一個子頁面的相對路徑是否正確**

```bash
grep -A2 'rel="manifest"' index.html
grep -A2 'rel="manifest"' tc-elder-checkup/index.html
```
Expected: 首頁顯示 `href="assets/icon-192.png"`（無 `../` 前綴）；`tc-elder-checkup/index.html`
顯示 `href="../assets/icon-192.png"`。

- [ ] **Step 5：Commit**

```bash
git add scripts/apply_pwa_tags.py '*/index.html' index.html
git commit -m "feat(pwa): apply manifest/theme-color/install-script tags to all pages except changelog

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 6：本機驗證與收尾

**Files:**
- 無新增/修改檔案（純驗證步驟）；若驗證發現問題則回到對應 Task 修正。

**Interfaces:**
- Consumes: Task 1-5 的全部產出。
- Produces: 驗證通過的最終狀態，可安全視為完成。

- [ ] **Step 1：確認本機伺服器仍在執行，重新整理後檢查關鍵檔案回應**

```bash
curl -s -o /dev/null -w "manifest: %{http_code}\n" http://localhost:8899/tc-elder-checkup/manifest.webmanifest
curl -s -o /dev/null -w "sw.js: %{http_code}\n" http://localhost:8899/assets/sw.js
curl -s -o /dev/null -w "pwa-install.js: %{http_code}\n" http://localhost:8899/assets/pwa-install.js
curl -s -o /dev/null -w "icon-192: %{http_code}\n" http://localhost:8899/assets/icon-192.png
curl -s -o /dev/null -w "changelog manifest (應為404): %{http_code}\n" http://localhost:8899/changelog/manifest.webmanifest
```
Expected: 前四項皆為 `200`；最後一項為 `404`（確認 changelog 沒有被誤產生 manifest）。

- [ ] **Step 2：驗證所有 manifest.webmanifest 皆為合法 JSON**

```bash
cd /Users/sun/Projects/gov_open_data && python3 -c "
import json, glob
files = glob.glob('manifest.webmanifest') + glob.glob('*/manifest.webmanifest')
assert 'changelog/manifest.webmanifest' not in files
for f in files:
    json.load(open(f, encoding='utf-8'))
print('全部合法 JSON，共', len(files), '份')
"
```
Expected: 印出 `全部合法 JSON，共 54 份`，不拋出例外。

- [ ] **Step 3：驗證既有頁面 JSON-LD 未被破壞（插入的標籤不影響既有 script 區塊）**

```bash
cd /Users/sun/Projects/gov_open_data && python3 -c "
import re, json, glob
pages = ['index.html'] + [p for p in glob.glob('*/index.html') if not p.startswith('changelog/')]
for p in pages:
    html = open(p, encoding='utf-8').read()
    for m in re.findall(r'<script type=\"application/ld\+json\">(.*?)</script>', html, re.S):
        json.loads(m)
print('全部頁面 JSON-LD 驗證通過，共', len(pages), '頁')
"
```
Expected: 印出 `全部頁面 JSON-LD 驗證通過，共 54 頁`，不拋出例外。

- [ ] **Step 4：更新 `README.md`，記錄本次新增的 PWA 能力與新腳本用途**

在 `README.md` 找到既有「資料更新方式」或工具腳本說明段落，新增一小節說明：
- `scripts/generate_pwa_manifests.py`／`scripts/apply_pwa_tags.py` 的用途與何時需要重新執行
  （新增資料集頁面後）。
- 全站（changelog 除外）皆為可安裝 PWA，安裝後開啟仍停留在原頁面。

具體插入位置與文字需視當下 `README.md` 內容而定，插入後執行：
```bash
grep -n "generate_pwa_manifests\|apply_pwa_tags" README.md
```
Expected: 至少各出現 1 次，確認已寫入說明。

- [ ] **Step 5：最終 commit（若 Step 4 有變更 README）**

```bash
cd /Users/sun/Projects/gov_open_data && git add README.md
git commit -m "docs: document PWA generator scripts in README

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Self-Review 紀錄（規劃階段自查，執行時不需重做）

- **spec 覆蓋度**：設計文件的 5 個元件（圖示／manifest 產生腳本／Service Worker／安裝橫幅腳本／
  批次標籤插入）皆對應 Task 1-5；驗證方式章節對應 Task 6。
- **排除 changelog**：Task 2、Task 5 的 `find_pages()` 皆以 `EXCLUDE_DIRS = {"changelog"}` 過濾，
  且 Task 5 Step 3、Task 6 Step 1 都有專門驗證 changelog 未被觸及的步驟。
- **型別/介面一致性**：`rel_prefix`（`""`／`"../"`）在 Task 2 與 Task 5 兩支腳本中各自獨立計算但
  邏輯完全一致（`page_dir == ROOT` 判斷）；`dismissKey`／`showBanner`／`hideBanner` 等命名在
  Task 4 內部一致，未跨檔案重複定義。
