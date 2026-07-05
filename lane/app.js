/* 巷弄長照站 dashboard */
(function () {
  const state = { all: [], fields: [], filtered: [] };

  const els = {
    district: document.getElementById("f-district"),
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    statTotal: document.getElementById("stat-total"),
    statDistricts: document.getElementById("stat-districts"),
    statTop: document.getElementById("stat-top"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  let districtChart, unitChart;

  const UNIT_KEYWORDS = ["社區發展協會", "衛生所", "教會", "護理之家", "基金會", "農會", "照顧服務", "醫院", "協進會"];

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 25,
    columns: [
      { key: "item", label: "項目" },
      { key: "unit", label: "單位" },
      { key: "county", label: "縣市" },
      { key: "district", label: "鄉鎮市區" },
      { key: "address", label: "地址" },
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
    const district = els.district.value;
    const keyword = els.keyword.value.trim().toLowerCase();
    state.filtered = state.all.filter((r) => {
      if (district && r.district !== district) return false;
      if (keyword) {
        const hay = `${r.unit} ${r.address}`.toLowerCase();
        if (!hay.includes(keyword)) return false;
      }
      return true;
    });
    renderAll();
  }

  function renderStats() {
    const rows = state.filtered;
    const districtCounts = {};
    rows.forEach((r) => (districtCounts[r.district] = (districtCounts[r.district] || 0) + 1));
    els.statTotal.textContent = rows.length.toLocaleString();
    els.statDistricts.textContent = Object.keys(districtCounts).filter(Boolean).length;
    const top = Object.entries(districtCounts).sort((a, b) => b[1] - a[1])[0];
    els.statTop.textContent = top ? `${top[0]}（${top[1]}）` : "-";
  }

  function renderCharts() {
    const districtCounts = {};
    state.filtered.forEach((r) => (districtCounts[r.district] = (districtCounts[r.district] || 0) + 1));
    const entries = Object.entries(districtCounts)
      .filter(([k]) => k)
      .sort((a, b) => b[1] - a[1]);

    if (districtChart) districtChart.destroy();
    districtChart = new Chart(document.getElementById("chart-district"), {
      type: "bar",
      data: {
        labels: entries.map((e) => e[0]),
        datasets: [{ data: entries.map((e) => e[1]), backgroundColor: "#1f6f5c" }],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
      },
    });

    const unitCounts = {};
    UNIT_KEYWORDS.forEach((k) => (unitCounts[k] = 0));
    let other = 0;
    state.filtered.forEach((r) => {
      const matched = UNIT_KEYWORDS.find((k) => (r.unit || "").includes(k));
      if (matched) unitCounts[matched] += 1;
      else other += 1;
    });
    const unitEntries = Object.entries(unitCounts).sort((a, b) => b[1] - a[1]).slice(0, 10);
    if (other > 0) unitEntries.push(["其他", other]);

    if (unitChart) unitChart.destroy();
    unitChart = new Chart(document.getElementById("chart-unit"), {
      type: "bar",
      data: {
        labels: unitEntries.map((e) => e[0]),
        datasets: [{ data: unitEntries.map((e) => e[1]), backgroundColor: "#e07a2c" }],
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } },
    });
  }

  function renderAll() {
    renderStats();
    renderCharts();
    table.setData(state.filtered);
  }

  els.district.addEventListener("change", applyFilters);
  els.keyword.addEventListener("input", debounce(applyFilters, 250));
  els.reset.addEventListener("click", () => {
    els.district.value = "";
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

  Promise.all([fetch("../data/lane.json").then((r) => r.json()), fetch("../data/meta.json").then((r) => r.json())])
    .then(([data, meta]) => {
      state.fields = data.fields;
      state.all = data.rows.map(rowToObj);

      const districts = Array.from(new Set(state.all.map((r) => r.district))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
      populateSelect(els.district, districts);

      els.metaUpdated.textContent = `資料筆數：${meta.lane.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;

      applyFilters();
    })
    .catch((err) => {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：${err}</div>`;
    });
})();
