/* 桃園市長照交通接送服務單位 dashboard */
(function () {
  const state = { all: [], fields: [], filtered: [] };

  const els = {
    county: document.getElementById("f-county"),
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    statTotal: document.getElementById("stat-total"),
    statCounties: document.getElementById("stat-counties"),
    statFull: document.getElementById("stat-full"),
    statFuxing: document.getElementById("stat-fuxing"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  let countyChart, areaChart;

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 25,
    columns: [
      { key: "name", label: "辦理單位" },
      { key: "phone", label: "電話", render: (r) => phoneLink(r.phone) },
      { key: "address", label: "地址", render: (r) => addressLink(r.address) },
      { key: "county", label: "縣市" },
      { key: "serviceArea", label: "服務區域" },
    ],
  });

  function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  // 電話欄位偶含多組號碼（以「 / 」分隔），僅第一組轉為 tel: 連結，顯示文字保留原始格式。
  function phoneLink(phone) {
    if (!phone) return "";
    const main = phone.split("/")[0].trim();
    const digits = main.replace(/[^\d+]/g, "");
    if (!digits) return escapeHtml(phone);
    return `<a href="tel:${digits}">${escapeHtml(phone)}</a>`;
  }

  function addressLink(address) {
    if (!address) return "";
    const href = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(address)}`;
    return `<a href="${href}" target="_blank" rel="noopener">${escapeHtml(address)}</a>`;
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
        const hay = `${r.name} ${r.address} ${r.phone}`.toLowerCase();
        if (!hay.includes(keyword)) return false;
      }
      return true;
    });
    renderAll();
  }

  function renderStats() {
    const rows = state.filtered;
    const counties = new Set();
    let fullCount = 0;
    let fuxingCount = 0;
    rows.forEach((r) => {
      if (r.county) counties.add(r.county);
      if (r.serviceArea === "桃園市全區") fullCount += 1;
      if (r.serviceArea && r.serviceArea.includes("復興區")) fuxingCount += 1;
    });
    els.statTotal.textContent = rows.length.toLocaleString();
    els.statCounties.textContent = counties.size;
    els.statFull.textContent = fullCount.toLocaleString();
    els.statFuxing.textContent = fuxingCount.toLocaleString();
  }

  function renderCharts() {
    const countyCounts = {};
    state.filtered.forEach((r) => (countyCounts[r.county] = (countyCounts[r.county] || 0) + 1));
    const countyEntries = Object.entries(countyCounts)
      .filter(([k]) => k)
      .sort((a, b) => b[1] - a[1]);

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

    const areaCounts = {};
    state.filtered.forEach((r) => (areaCounts[r.serviceArea] = (areaCounts[r.serviceArea] || 0) + 1));
    const areaEntries = Object.entries(areaCounts)
      .filter(([k]) => k)
      .sort((a, b) => b[1] - a[1]);

    if (areaChart) areaChart.destroy();
    areaChart = new Chart(document.getElementById("chart-area"), {
      type: "doughnut",
      data: {
        labels: areaEntries.map((e) => e[0]),
        datasets: [{ data: areaEntries.map((e) => e[1]), backgroundColor: ["#1f6f5c", "#e07a2c", "#3b6fa0"] }],
      },
      options: { responsive: true, maintainAspectRatio: false },
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
    const data = window.TYC_TRANSPORT_DATA;
    if (!data) {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：找不到內嵌資料 data/tyc-transport.js</div>`;
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
        if (meta.tycTransport) {
          els.metaUpdated.textContent = `資料筆數：${meta.tycTransport.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;
        }
      })
      .catch(() => {});
  }

  init();
})();
