/* 長照ABC據點 dashboard */
(function () {
  const state = {
    all: [],
    fields: [],
    categoryLabels: {},
    filtered: [],
  };

  const els = {
    county: document.getElementById("f-county"),
    district: document.getElementById("f-district"),
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    categoryBoxes: Array.from(document.querySelectorAll("#f-category input")),
    statTotal: document.getElementById("stat-total"),
    statA: document.getElementById("stat-a"),
    statB: document.getElementById("stat-b"),
    statC: document.getElementById("stat-c"),
    statBeds: document.getElementById("stat-beds"),
    statResidents: document.getElementById("stat-residents"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  const map = L.map("map", { preferCanvas: true }).setView([23.6, 120.9], 8);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);
  const clusterGroup = L.markerClusterGroup({ chunkedLoading: true, disableClusteringAtZoom: 16 });
  map.addLayer(clusterGroup);

  const catColor = { A: "#2563eb", B: "#16a34a", C: "#d97706" };

  let countyChart, categoryChart;

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 25,
    columns: [
      { key: "name", label: "機構名稱" },
      {
        key: "category",
        label: "類別",
        render: (r) => `<span class="badge ${r.category.toLowerCase()}">${r.category}</span>`,
      },
      { key: "county", label: "縣市" },
      { key: "district", label: "鄉鎮市區" },
      { key: "address", label: "地址" },
      { key: "services", label: "特約服務項目", render: (r) => (r.services || "").split(";").join("、") },
      { key: "phone", label: "電話" },
      { key: "bedsOpen", label: "開放床數" },
      { key: "bedsCurrent", label: "現有住民" },
    ],
    onRowClick: (row) => {
      if (row.lat && row.lng) {
        map.setView([row.lat, row.lng], 16);
      }
    },
  });

  function rowToObj(row) {
    const o = {};
    state.fields.forEach((f, i) => (o[f] = row[i]));
    return o;
  }

  function populateSelect(select, values, placeholder) {
    select.innerHTML = `<option value="">${placeholder}</option>`;
    values.forEach((v) => {
      const opt = document.createElement("option");
      opt.value = v;
      opt.textContent = v;
      select.appendChild(opt);
    });
  }

  function refreshDistrictOptions() {
    const county = els.county.value;
    const districts = new Set();
    state.all.forEach((r) => {
      if (!county || r.county === county) districts.add(r.district);
    });
    populateSelect(els.district, Array.from(districts).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant")), "全部");
  }

  function applyFilters() {
    const county = els.county.value;
    const district = els.district.value;
    const keyword = els.keyword.value.trim().toLowerCase();
    const activeCats = new Set(els.categoryBoxes.filter((c) => c.checked).map((c) => c.value));

    state.filtered = state.all.filter((r) => {
      if (county && r.county !== county) return false;
      if (district && r.district !== district) return false;
      if (!activeCats.has(r.category)) return false;
      if (keyword) {
        const hay = `${r.name} ${r.address} ${r.services}`.toLowerCase();
        if (!hay.includes(keyword)) return false;
      }
      return true;
    });

    renderAll();
  }

  function renderStats() {
    const rows = state.filtered;
    const counts = { A: 0, B: 0, C: 0 };
    let beds = 0;
    let residents = 0;
    rows.forEach((r) => {
      if (counts[r.category] !== undefined) counts[r.category] += 1;
      beds += r.bedsOpen || 0;
      residents += r.bedsCurrent || 0;
    });
    els.statTotal.textContent = rows.length.toLocaleString();
    els.statA.textContent = counts.A.toLocaleString();
    els.statB.textContent = counts.B.toLocaleString();
    els.statC.textContent = counts.C.toLocaleString();
    els.statBeds.textContent = beds.toLocaleString();
    els.statResidents.textContent = residents.toLocaleString();
  }

  function renderMap() {
    clusterGroup.clearLayers();
    const markers = [];
    // 為避免過度耗費效能，地圖最多渲染前 8000 筆（統計數字仍以完整篩選結果為準）
    const cap = 8000;
    const rows = state.filtered;
    const sampled = rows.length > cap ? rows.filter((_, i) => i % Math.ceil(rows.length / cap) === 0) : rows;
    sampled.forEach((r) => {
      if (!r.lat || !r.lng) return;
      const marker = L.circleMarker([r.lat, r.lng], {
        radius: 6,
        color: "#fff",
        weight: 1,
        fillColor: catColor[r.category] || "#64748b",
        fillOpacity: 0.9,
      });
      marker.bindPopup(
        `<strong>${escapeHtml(r.name)}</strong><br/>${escapeHtml(r.county)}${escapeHtml(r.district)}<br/>${escapeHtml(r.address)}<br/>類別：${r.category}｜電話：${escapeHtml(r.phone || "-")}`
      );
      markers.push(marker);
    });
    clusterGroup.addLayers(markers);
  }

  function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  function renderCharts() {
    const countyCounts = {};
    const catCounts = { A: 0, B: 0, C: 0 };
    state.filtered.forEach((r) => {
      countyCounts[r.county] = (countyCounts[r.county] || 0) + 1;
      if (catCounts[r.category] !== undefined) catCounts[r.category] += 1;
    });
    const topCounties = Object.entries(countyCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10);

    if (countyChart) countyChart.destroy();
    countyChart = new Chart(document.getElementById("chart-county"), {
      type: "bar",
      data: {
        labels: topCounties.map((e) => e[0]),
        datasets: [{ data: topCounties.map((e) => e[1]), backgroundColor: "#1f6f5c" }],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
      },
    });

    if (categoryChart) categoryChart.destroy();
    categoryChart = new Chart(document.getElementById("chart-category"), {
      type: "doughnut",
      data: {
        labels: ["A級", "B級", "C級"],
        datasets: [{ data: [catCounts.A, catCounts.B, catCounts.C], backgroundColor: [catColor.A, catColor.B, catColor.C] }],
      },
      options: { responsive: true, maintainAspectRatio: false },
    });
  }

  function renderAll() {
    renderStats();
    renderMap();
    renderCharts();
    table.setData(state.filtered);
  }

  els.county.addEventListener("change", () => {
    refreshDistrictOptions();
    applyFilters();
  });
  els.district.addEventListener("change", applyFilters);
  els.keyword.addEventListener("input", debounce(applyFilters, 250));
  els.categoryBoxes.forEach((c) => c.addEventListener("change", applyFilters));
  els.reset.addEventListener("click", () => {
    els.county.value = "";
    els.keyword.value = "";
    els.categoryBoxes.forEach((c) => (c.checked = true));
    refreshDistrictOptions();
    els.district.value = "";
    applyFilters();
  });

  function debounce(fn, ms) {
    let t;
    return (...args) => {
      clearTimeout(t);
      t = setTimeout(() => fn(...args), ms);
    };
  }

  Promise.all([fetch("../data/abc.json").then((r) => r.json()), fetch("../data/meta.json").then((r) => r.json())])
    .then(([data, meta]) => {
      state.fields = data.fields;
      state.categoryLabels = data.categoryLabels || {};
      state.all = data.rows.map(rowToObj);

      const counties = Array.from(new Set(state.all.map((r) => r.county))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
      populateSelect(els.county, counties, "全部");
      refreshDistrictOptions();

      els.metaUpdated.textContent = `資料筆數：${meta.abc.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;

      applyFilters();
    })
    .catch((err) => {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：${err}</div>`;
    });
})();
