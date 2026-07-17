/* 嘉義縣立案長照及護理之家機構一覽 dashboard */
(function () {
  const state = { all: [], fields: [], filtered: [] };

  const catClass = { 住宿長照機構: "inst", 護理之家: "nurse" };
  const catColor = { 住宿長照機構: "#7c3aed", 護理之家: "#0891b2" };

  const els = {
    category: document.getElementById("f-category"),
    township: document.getElementById("f-township"),
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    statTotal: document.getElementById("stat-total"),
    statInst: document.getElementById("stat-inst"),
    statNurse: document.getElementById("stat-nurse"),
    statApprovedBeds: document.getElementById("stat-approved-beds"),
    statOperatingBeds: document.getElementById("stat-operating-beds"),
    statTownships: document.getElementById("stat-townships"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  let categoryChart, townshipChart;

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 25,
    columns: [
      {
        key: "category",
        label: "機構類型",
        render: (r) => `<span class="badge ${catClass[r.category] || ""}">${r.category}</span>`,
      },
      { key: "name", label: "機構名稱" },
      { key: "township", label: "鄉鎮市" },
      { key: "address", label: "地址" },
      { key: "phone", label: "電話" },
      { key: "director", label: "負責人", render: (r) => r.director || "—" },
      { key: "approvedBeds", label: "許可床數" },
      { key: "operatingBeds", label: "開業床數" },
      { key: "approvalDate", label: "核准開業日期", render: (r) => r.approvalDate || "—" },
    ],
  });

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
    const category = els.category.value;
    const township = els.township.value;
    const keyword = els.keyword.value.trim().toLowerCase();
    state.filtered = state.all.filter((r) => {
      if (category && r.category !== category) return false;
      if (township && r.township !== township) return false;
      if (keyword) {
        const hay = `${r.name} ${r.address} ${r.phone} ${r.director}`.toLowerCase();
        if (!hay.includes(keyword)) return false;
      }
      return true;
    });
    renderAll();
  }

  function renderStats() {
    const rows = state.filtered;
    const townships = new Set();
    let instCount = 0;
    let nurseCount = 0;
    let approvedBeds = 0;
    let operatingBeds = 0;
    rows.forEach((r) => {
      if (r.township) townships.add(r.township);
      if (r.category === "住宿長照機構") instCount++;
      if (r.category === "護理之家") nurseCount++;
      approvedBeds += r.approvedBeds || 0;
      operatingBeds += r.operatingBeds || 0;
    });
    els.statTotal.textContent = rows.length.toLocaleString();
    els.statInst.textContent = instCount.toLocaleString();
    els.statNurse.textContent = nurseCount.toLocaleString();
    els.statApprovedBeds.textContent = approvedBeds.toLocaleString();
    els.statOperatingBeds.textContent = operatingBeds.toLocaleString();
    els.statTownships.textContent = townships.size;
  }

  function renderCharts() {
    const catCounts = {};
    const townshipCounts = {};
    state.filtered.forEach((r) => {
      catCounts[r.category] = (catCounts[r.category] || 0) + 1;
      if (r.township) townshipCounts[r.township] = (townshipCounts[r.township] || 0) + 1;
    });
    const catEntries = Object.entries(catCounts);
    const townshipEntries = Object.entries(townshipCounts).sort((a, b) => b[1] - a[1]);

    if (categoryChart) categoryChart.destroy();
    categoryChart = new Chart(document.getElementById("chart-category"), {
      type: "doughnut",
      data: {
        labels: catEntries.map((e) => e[0]),
        datasets: [{ data: catEntries.map((e) => e[1]), backgroundColor: catEntries.map((e) => catColor[e[0]] || "#64748b") }],
      },
      options: { responsive: true, maintainAspectRatio: false },
    });

    if (townshipChart) townshipChart.destroy();
    townshipChart = new Chart(document.getElementById("chart-township"), {
      type: "bar",
      data: {
        labels: townshipEntries.map((e) => e[0]),
        datasets: [{ data: townshipEntries.map((e) => e[1]), backgroundColor: "#1f6f5c" }],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
      },
    });
  }

  function renderAll() {
    renderStats();
    renderCharts();
    table.setData(state.filtered);
  }

  els.category.addEventListener("change", applyFilters);
  els.township.addEventListener("change", applyFilters);
  els.keyword.addEventListener("input", debounce(applyFilters, 250));
  els.reset.addEventListener("click", () => {
    els.category.value = "";
    els.township.value = "";
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
    const data = window.CHIAYI_LTC_DATA;
    if (!data) {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：找不到內嵌資料 data/chiayi-ltc.js</div>`;
      return;
    }
    state.fields = data.fields;
    state.all = data.rows.map(rowToObj);

    const categories = Array.from(new Set(state.all.map((r) => r.category))).filter(Boolean);
    populateSelect(els.category, categories);
    const townships = Array.from(new Set(state.all.map((r) => r.township))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateSelect(els.township, townships);

    els.metaUpdated.textContent = `資料筆數：${data.rows.length.toLocaleString()}`;
    applyFilters();

    // meta.json 僅用於補上資料整理時間，非核心資料，失敗也不影響上方篩選/圖表/表格運作。
    fetch("../data/meta.json")
      .then((r) => r.json())
      .then((meta) => {
        if (meta.chiayiLtc) {
          els.metaUpdated.textContent = `資料筆數：${meta.chiayiLtc.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;
        }
      })
      .catch(() => {});
  }

  init();
})();
