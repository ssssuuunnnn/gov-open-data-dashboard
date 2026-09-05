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
