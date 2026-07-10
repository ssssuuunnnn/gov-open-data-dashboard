/* 桃園市老人福利機構一覽表 dashboard */
(function () {
  const state = { all: [], fields: [], filtered: [] };

  const els = {
    district: document.getElementById("f-district"),
    occupant: document.getElementById("f-occupant"),
    rating: document.getElementById("f-rating"),
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    statTotal: document.getElementById("stat-total"),
    statDistricts: document.getElementById("stat-districts"),
    statBeds: document.getElementById("stat-beds"),
    statTop: document.getElementById("stat-top"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  let districtChart, ratingChart, occupantChart, bedsChart;

  const BED_BUCKETS = [
    { label: "< 30", min: 0, max: 29 },
    { label: "30-49", min: 30, max: 49 },
    { label: "50-99", min: 50, max: 99 },
    { label: "100+", min: 100, max: Infinity },
  ];

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 25,
    columns: [
      { key: "id", label: "編號" },
      { key: "name", label: "機構名稱" },
      { key: "director", label: "負責人" },
      { key: "district", label: "鄉鎮市區" },
      { key: "address", label: "地址" },
      { key: "phone", label: "電話" },
      { key: "occupants", label: "收容對象", render: (r) => r.occupants.join("、") },
      { key: "beds", label: "立案床數" },
      { key: "rating", label: "最近1次評鑑成績" },
    ],
  });

  function rowToObj(row) {
    const o = {};
    state.fields.forEach((f, i) => (o[f] = row[i]));
    o.occupants = o.occupants ? o.occupants.split(";").filter(Boolean) : [];
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
    const occupant = els.occupant.value;
    const rating = els.rating.value;
    const keyword = els.keyword.value.trim().toLowerCase();
    state.filtered = state.all.filter((r) => {
      if (district && r.district !== district) return false;
      if (occupant && !r.occupants.includes(occupant)) return false;
      if (rating && r.rating !== rating) return false;
      if (keyword) {
        const hay = `${r.name} ${r.director} ${r.address}`.toLowerCase();
        if (!hay.includes(keyword)) return false;
      }
      return true;
    });
    renderAll();
  }

  function renderStats() {
    const rows = state.filtered;
    const districtCounts = {};
    let totalBeds = 0;
    rows.forEach((r) => {
      districtCounts[r.district] = (districtCounts[r.district] || 0) + 1;
      totalBeds += r.beds || 0;
    });
    els.statTotal.textContent = rows.length.toLocaleString();
    els.statDistricts.textContent = Object.keys(districtCounts).filter(Boolean).length;
    els.statBeds.textContent = totalBeds.toLocaleString();
    const top = Object.entries(districtCounts).filter(([k]) => k).sort((a, b) => b[1] - a[1])[0];
    els.statTop.textContent = top ? `${top[0]}（${top[1]}）` : "-";
  }

  function renderCharts() {
    const districtCounts = {};
    state.filtered.forEach((r) => (districtCounts[r.district] = (districtCounts[r.district] || 0) + 1));
    const districtEntries = Object.entries(districtCounts)
      .filter(([k]) => k)
      .sort((a, b) => b[1] - a[1]);

    if (districtChart) districtChart.destroy();
    districtChart = new Chart(document.getElementById("chart-district"), {
      type: "bar",
      data: {
        labels: districtEntries.map((e) => e[0]),
        datasets: [{ data: districtEntries.map((e) => e[1]), backgroundColor: "#1f6f5c" }],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
      },
    });

    const ratingCounts = {};
    state.filtered.forEach((r) => (ratingCounts[r.rating] = (ratingCounts[r.rating] || 0) + 1));
    const ratingEntries = Object.entries(ratingCounts).filter(([k]) => k).sort((a, b) => b[1] - a[1]);

    if (ratingChart) ratingChart.destroy();
    ratingChart = new Chart(document.getElementById("chart-rating"), {
      type: "doughnut",
      data: {
        labels: ratingEntries.map((e) => e[0]),
        datasets: [{ data: ratingEntries.map((e) => e[1]), backgroundColor: ["#1f6f5c", "#e07a2c", "#2563eb", "#a855f7", "#dc2626", "#64748b"] }],
      },
      options: { responsive: true, maintainAspectRatio: false },
    });

    const occupantCounts = {};
    state.filtered.forEach((r) => r.occupants.forEach((o) => (occupantCounts[o] = (occupantCounts[o] || 0) + 1)));
    const occupantEntries = Object.entries(occupantCounts).sort((a, b) => b[1] - a[1]);

    if (occupantChart) occupantChart.destroy();
    occupantChart = new Chart(document.getElementById("chart-occupant"), {
      type: "bar",
      data: {
        labels: occupantEntries.map((e) => e[0]),
        datasets: [{ data: occupantEntries.map((e) => e[1]), backgroundColor: "#e07a2c" }],
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } },
    });

    const bedCounts = BED_BUCKETS.map((b) => 0);
    state.filtered.forEach((r) => {
      const idx = BED_BUCKETS.findIndex((b) => r.beds >= b.min && r.beds <= b.max);
      if (idx >= 0) bedCounts[idx] += 1;
    });

    if (bedsChart) bedsChart.destroy();
    bedsChart = new Chart(document.getElementById("chart-beds"), {
      type: "bar",
      data: {
        labels: BED_BUCKETS.map((b) => b.label),
        datasets: [{ data: bedCounts, backgroundColor: "#2563eb" }],
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
  els.occupant.addEventListener("change", applyFilters);
  els.rating.addEventListener("change", applyFilters);
  els.keyword.addEventListener("input", debounce(applyFilters, 250));
  els.reset.addEventListener("click", () => {
    els.district.value = "";
    els.occupant.value = "";
    els.rating.value = "";
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

  Promise.all([
    fetch("../data/tyc-elder.json").then((r) => r.json()),
    fetch("../data/meta.json").then((r) => r.json()),
  ])
    .then(([data, meta]) => {
      state.fields = data.fields;
      state.all = data.rows.map(rowToObj);

      const districts = Array.from(new Set(state.all.map((r) => r.district))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
      populateSelect(els.district, districts);

      const occupants = Array.from(new Set(state.all.flatMap((r) => r.occupants))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
      populateSelect(els.occupant, occupants);

      const ratings = Array.from(new Set(state.all.map((r) => r.rating))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
      populateSelect(els.rating, ratings);

      els.metaUpdated.textContent = `資料筆數：${meta.tycElder.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;

      applyFilters();
    })
    .catch((err) => {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：${err}</div>`;
    });
})();
