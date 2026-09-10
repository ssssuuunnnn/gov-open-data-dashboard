/* 全國糖尿病醫療給付改善方案試辦院所 dashboard */
(function () {
  const state = { all: [], fields: [], filtered: [] };

  const els = {
    county: document.getElementById("f-county"),
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    statTotal: document.getElementById("stat-total"),
    statCounties: document.getElementById("stat-counties"),
    statTopCounty: document.getElementById("stat-top-county"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  let countyChart, yearChart;

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 25,
    columns: [
      { key: "name", label: "醫事機構名稱" },
      { key: "county", label: "縣市" },
      { key: "district", label: "鄉鎮市區" },
      { key: "address", label: "地址", render: (r) => addressLink(r.address) },
      { key: "phone", label: "電話", render: (r) => phoneLink(r.phone) },
      { key: "effectiveStart", label: "生效起日", render: (r) => escapeHtml(formatDate(r.effectiveStart)) },
      { key: "effectiveEnd", label: "生效迄日", render: (r) => effectiveEndDisplay(r.effectiveEnd) },
    ],
  });

  function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  // 電話欄位轉成 tel: 連結，去除裝飾字元僅保留數字（保留開頭「+」），顯示文字保留原始格式。
  function phoneLink(phone) {
    if (!phone) return "";
    const digits = phone.replace(/[^\d+]/g, "");
    if (!digits) return escapeHtml(phone);
    return `<a href="tel:${digits}">${escapeHtml(phone)}</a>`;
  }

  // 地址欄位轉成 Google Maps 搜尋連結，點選開新分頁瀏覽該地址位置。
  function addressLink(address) {
    if (!address) return "";
    const href = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(address)}`;
    return `<a href="${href}" target="_blank" rel="noopener">${escapeHtml(address)}</a>`;
  }

  // 原始日期為西元 YYYYMMDD 字串，僅顯示時轉換為 YYYY-MM-DD，原始值不變更。
  function formatDate(s) {
    if (!s || s.length !== 8) return s || "-";
    return `${s.slice(0, 4)}-${s.slice(4, 6)}-${s.slice(6, 8)}`;
  }

  // 迄日絕大多數為常數 29101231（代表無期限／持續有效）；其餘極少數為已知/預定終止日，需特別標示。
  function effectiveEndDisplay(effectiveEnd) {
    if (effectiveEnd === "29101231") {
      return `<span style="color:#1f6f5c;">持續有效</span>`;
    }
    return `${escapeHtml(formatDate(effectiveEnd))}<br/><span style="color:#dc2626;font-size:.75rem;">已知／預定終止日</span>`;
  }

  function rowToObj(row) {
    const o = {};
    state.fields.forEach((f, i) => (o[f] = row[i]));
    return o;
  }

  function populateSelect(select, values) {
    select.innerHTML = `<option value="">全部</option>`;
    values.forEach((v) => {
      const opt = document.createElement("option");
      opt.value = v;
      opt.textContent = v;
      select.appendChild(opt);
    });
  }

  function applyFilters() {
    const county = els.county.value;
    const keyword = els.keyword.value.trim().toLowerCase();
    state.filtered = state.all.filter((r) => {
      if (county && r.county !== county) return false;
      if (keyword) {
        const hay = `${r.name} ${r.address}`.toLowerCase();
        if (!hay.includes(keyword)) return false;
      }
      return true;
    });
    renderAll();
  }

  function renderStats() {
    const rows = state.filtered;
    const countyCounts = {};
    rows.forEach((r) => {
      const label = r.county || "未標示";
      countyCounts[label] = (countyCounts[label] || 0) + 1;
    });
    els.statTotal.textContent = rows.length.toLocaleString();
    els.statCounties.textContent = Object.keys(countyCounts).filter((k) => k !== "未標示").length;
    const top = Object.entries(countyCounts).sort((a, b) => b[1] - a[1])[0];
    els.statTopCounty.textContent = top ? `${top[0]}（${top[1]}）` : "-";
  }

  function renderCharts() {
    const countyCounts = {};
    state.filtered.forEach((r) => {
      const label = r.county || "未標示";
      countyCounts[label] = (countyCounts[label] || 0) + 1;
    });
    const countyEntries = Object.entries(countyCounts).sort((a, b) => b[1] - a[1]);

    if (countyChart) countyChart.destroy();
    countyChart = new Chart(document.getElementById("chart-county"), {
      type: "bar",
      data: {
        labels: countyEntries.map((e) => e[0]),
        datasets: [{ data: countyEntries.map((e) => e[1]), backgroundColor: "#1f6f5c" }],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
      },
    });

    const yearCounts = {};
    state.filtered.forEach((r) => {
      const year = (r.effectiveStart || "").slice(0, 4);
      if (year) yearCounts[year] = (yearCounts[year] || 0) + 1;
    });
    const years = Object.keys(yearCounts).sort();
    let cumulative = 0;
    const cumulativeData = years.map((y) => {
      cumulative += yearCounts[y];
      return cumulative;
    });

    if (yearChart) yearChart.destroy();
    yearChart = new Chart(document.getElementById("chart-year"), {
      type: "line",
      data: {
        labels: years,
        datasets: [{
          data: cumulativeData,
          borderColor: "#e07a2c",
          backgroundColor: "#e07a2c33",
          fill: true,
          tension: 0.2,
        }],
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } },
    });
  }

  function renderAll() {
    renderStats();
    renderCharts();
    table.setData(state.filtered);
  }

  els.county.addEventListener("change", applyFilters);
  els.keyword.addEventListener("input", debounce(applyFilters, 250));
  els.reset.addEventListener("click", () => {
    els.county.value = "";
    els.keyword.value = "";
    applyFilters();
  });

  function debounce(fn, ms) {
    let t;
    return (...args) => {
      clearTimeout(t);
      t = setTimeout(() => fn(...args), ms);
    };
  }

  function init() {
    const data = window.DIABETES_CARE_DATA;
    if (!data) {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：找不到內嵌資料 data/diabetes-care.js</div>`;
      return;
    }
    state.fields = data.fields;
    state.all = data.rows.map(rowToObj);

    const counties = Array.from(new Set(state.all.map((r) => r.county))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateSelect(els.county, counties);

    els.metaUpdated.textContent = `資料筆數：${data.rows.length.toLocaleString()}`;
    applyFilters();

    // meta.json 僅用於補上資料整理時間，非核心資料，失敗也不影響上方篩選/圖表/表格運作。
    fetch("../data/meta.json")
      .then((r) => r.json())
      .then((meta) => {
        if (meta.diabetesCare) {
          els.metaUpdated.textContent = `資料筆數：${meta.diabetesCare.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;
        }
      })
      .catch(() => {});
  }

  init();
})();
