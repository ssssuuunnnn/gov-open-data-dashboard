/* 安寧療護機構資源查詢（臺北市衛生局提供）dashboard */
(function () {
  const state = { all: [], fields: [], filtered: [] };

  const els = {
    group: document.getElementById("f-group"),
    contractType: document.getElementById("f-contract-type"),
    county: document.getElementById("f-county"),
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    statTotal: document.getElementById("stat-total"),
    statCounties: document.getElementById("stat-counties"),
    statMedicalCenter: document.getElementById("stat-medical-center"),
    statGroups: document.getElementById("stat-groups"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  let contractTypeChart;
  let countyChart;

  const CONTRACT_TYPE_COLORS = {
    "醫學中心": "#b5533c",
    "區域醫院": "#c8963e",
    "地區醫院": "#1f6f5c",
  };

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 25,
    columns: [
      { key: "group", label: "業務組別" },
      { key: "contractType", label: "特約類別" },
      { key: "county", label: "縣市別" },
      { key: "name", label: "醫事機構名稱", render: (r) => escapeHtml(displayName(r.name)) },
      { key: "bedInfoLinks", label: "病床動態查詢", render: (r) => bedInfoLinksCell(r.bedInfoLinks) },
    ],
  });

  function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  // 少數機構名稱前誤植了與縣市代碼相同的數字前綴（如「63000000立聯合醫院」），為原始資料瑕疵。
  // 原始資料本身不修改（state.all 仍保留完整原文供搜尋比對），僅在表格顯示時移除此前綴以利閱讀與 SEO。
  function displayName(name) {
    return String(name ?? "").replace(/^\d{5,}立/, "");
  }

  // bedInfoLinks 為 build_data.py 產生的 JSON 字串（[{label, url}, ...]），拆解成多個獨立可點擊
  // 小連結；有分院標籤（如「中興」）時顯示標籤文字，無標籤時顯示「查詢」。
  function bedInfoLinksCell(raw) {
    let links = [];
    try {
      links = JSON.parse(raw || "[]");
    } catch (e) {
      links = [];
    }
    if (!links.length) return "-";
    return links
      .map((l) => {
        const label = escapeHtml(l.label || "查詢");
        const href = escapeHtml(l.url || "");
        if (!href) return "";
        return `<a href="${href}" target="_blank" rel="noopener">${label}</a>`;
      })
      .filter(Boolean)
      .join("　");
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
    const group = els.group.value;
    const contractType = els.contractType.value;
    const county = els.county.value;
    const keyword = els.keyword.value.trim().toLowerCase();
    state.filtered = state.all.filter((r) => {
      if (group && r.group !== group) return false;
      if (contractType && r.contractType !== contractType) return false;
      if (county && r.county !== county) return false;
      if (keyword) {
        const hay = `${r.name}`.toLowerCase();
        if (!hay.includes(keyword)) return false;
      }
      return true;
    });
    renderAll();
  }

  function renderStats() {
    const rows = state.filtered;
    els.statTotal.textContent = rows.length.toLocaleString();
    const counties = new Set(rows.map((r) => r.county).filter(Boolean));
    els.statCounties.textContent = counties.size;
    const medicalCenterCount = rows.filter((r) => r.contractType === "醫學中心").length;
    els.statMedicalCenter.textContent = medicalCenterCount.toLocaleString();
    const groups = new Set(rows.map((r) => r.group).filter(Boolean));
    els.statGroups.textContent = groups.size;
  }

  function renderCharts() {
    const contractTypeCounts = {};
    const countyCounts = {};
    state.filtered.forEach((r) => {
      if (r.contractType) contractTypeCounts[r.contractType] = (contractTypeCounts[r.contractType] || 0) + 1;
      if (r.county) countyCounts[r.county] = (countyCounts[r.county] || 0) + 1;
    });

    const contractTypeEntries = Object.entries(contractTypeCounts).sort((a, b) => b[1] - a[1]);
    if (contractTypeChart) contractTypeChart.destroy();
    contractTypeChart = new Chart(document.getElementById("chart-contract-type"), {
      type: "doughnut",
      data: {
        labels: contractTypeEntries.map((e) => e[0]),
        datasets: [{
          data: contractTypeEntries.map((e) => e[1]),
          backgroundColor: contractTypeEntries.map((e) => CONTRACT_TYPE_COLORS[e[0]] || "#888"),
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: "bottom" } },
      },
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
        scales: { x: { ticks: { precision: 0 } } },
      },
    });
  }

  function renderAll() {
    renderStats();
    renderCharts();
    table.setData(state.filtered);
  }

  els.group.addEventListener("change", applyFilters);
  els.contractType.addEventListener("change", applyFilters);
  els.county.addEventListener("change", applyFilters);
  els.keyword.addEventListener("input", debounce(applyFilters, 250));
  els.reset.addEventListener("click", () => {
    els.group.value = "";
    els.contractType.value = "";
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
    const data = window.TPE_HOSPICE_DATA;
    if (!data) {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：找不到內嵌資料 data/tpe-hospice.js</div>`;
      return;
    }
    state.fields = data.fields;
    state.all = data.rows.map(rowToObj);

    const groups = Array.from(new Set(state.all.map((r) => r.group))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateSelect(els.group, groups);
    const contractTypes = Array.from(new Set(state.all.map((r) => r.contractType))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateSelect(els.contractType, contractTypes);
    const counties = Array.from(new Set(state.all.map((r) => r.county))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateSelect(els.county, counties);

    els.metaUpdated.textContent = `資料筆數：${data.rows.length.toLocaleString()}`;
    applyFilters();

    // meta.json 僅用於補上資料整理時間，非核心資料，失敗也不影響上方篩選/圖表/表格運作。
    fetch("../data/meta.json")
      .then((r) => r.json())
      .then((meta) => {
        if (meta.tpeHospice) {
          els.metaUpdated.textContent = `資料筆數：${meta.tpeHospice.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;
        }
      })
      .catch(() => {});
  }

  init();
})();
