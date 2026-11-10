/**
 * 全站共用推廣版位：在每個頁面 footer.site-footer 之前插入 Bookdex 系列系統的推廣卡片。
 * 新增／修改推廣內容只需調整下方 PROMOS 陣列，所有頁面同步生效。
 *
 * Google Analytics 事件（gtag 未載入時略過）：
 *   promo_click  使用者點擊推廣卡片，promo_name 為系統名稱
 */
(function () {
  var PROMOS = [
    {
      name: "Bookdex 預約簿",
      title: "開工作室，常常有客人預約的需求？",
      desc: "預約、方案、會員，一個後台全搞定",
      cta: "免費試用 30 天 →",
      url: "https://bookdex.cc/",
    },
    {
      name: "Bookdex 大團報名",
      title: "旅行社辦員工旅遊，還在用 Excel 收名單？",
      desc: "員工登入就能報名，名額保留 15 分鐘不超賣，公司補助自動計算，名單一鍵匯出。不用信用卡。",
      cta: "免費試用 30 天 →",
      url: "https://bigtour.bookdex.cc/",
    },
  ];

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function render() {
    if (document.querySelector(".promo-section")) return;
    var section = document.createElement("aside");
    section.className = "promo-section";
    section.setAttribute("aria-label", "推薦服務");
    section.innerHTML = PROMOS.map(function (p) {
      var href = p.url + "?utm_source=gov-open-data&utm_medium=banner&utm_campaign=site-promo";
      return (
        '<a class="promo-card" href="' + esc(href) + '" target="_blank" rel="noopener" data-promo-name="' + esc(p.name) + '">' +
        '<span class="promo-name">' + esc(p.name) + "</span>" +
        '<span class="promo-title">' + esc(p.title) + "</span>" +
        '<span class="promo-desc">' + esc(p.desc) + "</span>" +
        '<span class="promo-cta">' + esc(p.cta) + "</span>" +
        "</a>"
      );
    }).join("");

    var footer = document.querySelector("footer.site-footer");
    if (footer) footer.parentNode.insertBefore(section, footer);
    else document.body.appendChild(section);

    section.addEventListener("click", function (e) {
      var card = e.target.closest(".promo-card");
      if (!card || typeof gtag !== "function") return;
      var name = card.getAttribute("data-promo-name");
      gtag("event", "promo_click", {
        event_category: "promo",
        event_label: name,
        promo_name: name,
        page_path: location.pathname,
      });
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", render);
  else render();
})();
