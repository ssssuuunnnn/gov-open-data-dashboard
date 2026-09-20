/* 全台22縣市身心障礙者輔具費用補助懶人包：縣市切換元件 */
(function () {
  const tabs = Array.from(document.querySelectorAll(".county-tab"));
  const panels = Array.from(document.querySelectorAll(".county-panel"));

  const els = {
    statTotal: document.getElementById("stat-total"),
    statLinks: document.getElementById("stat-links"),
    statUpdated: document.getElementById("stat-updated"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  function showCounty(key) {
    let matched = false;
    tabs.forEach((tab) => {
      const isActive = tab.dataset.county === key;
      tab.classList.toggle("active", isActive);
      tab.setAttribute("aria-pressed", isActive ? "true" : "false");
      if (isActive) matched = true;
    });
    if (!matched) return;
    panels.forEach((panel) => {
      panel.hidden = panel.dataset.county !== key;
    });
  }

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const key = tab.dataset.county;
      showCounty(key);
      const url = new URL(window.location.href);
      url.searchParams.set("county", key);
      window.history.replaceState({}, "", url);
      document.querySelector(".county-tabs").scrollIntoView({ behavior: "smooth", block: "nearest" });
    });
  });

  function renderStats() {
    const data = window.ASSISTIVE_DEVICES_DATA;
    if (!data) return;
    const fields = data.fields;
    const rows = data.rows.map((row) => {
      const o = {};
      fields.forEach((f, i) => (o[f] = row[i]));
      return o;
    });
    els.statTotal.textContent = rows.length.toLocaleString();
    const totalLinks = rows.reduce((sum, r) => {
      try {
        return sum + JSON.parse(r.links || "[]").length;
      } catch (e) {
        return sum;
      }
    }, 0);
    els.statLinks.textContent = totalLinks.toLocaleString();
  }

  function init() {
    if (!window.ASSISTIVE_DEVICES_DATA) {
      panels.forEach((panel, i) => {
        panel.hidden = i !== 0;
      });
    }

    // 深連結：頁面載入時讀取網址列 ?county= 參數預選縣市（例如 ?county=hualien），
    // 方便分享／收藏特定縣市的補助資訊，若參數值不在既有縣市清單中則忽略，維持預設顯示第一筆。
    const params = new URLSearchParams(window.location.search);
    const countyParam = params.get("county");
    if (countyParam && tabs.some((t) => t.dataset.county === countyParam)) {
      showCounty(countyParam);
    }

    renderStats();
    els.statUpdated.textContent = "載入中…";

    fetch("../data/meta.json")
      .then((r) => r.json())
      .then((meta) => {
        if (meta.assistiveDevices) {
          const updatedText = new Date(meta.generatedAt).toLocaleDateString("zh-Hant-TW");
          els.statUpdated.textContent = updatedText;
          els.metaUpdated.textContent = `資料整理時間：${updatedText}`;
        }
      })
      .catch(() => {
        els.statUpdated.textContent = "—";
      });
  }

  init();
})();
