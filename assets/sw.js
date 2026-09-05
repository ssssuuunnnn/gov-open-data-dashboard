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
