/* 屏東縣115年長者假牙裝置補助合作醫療院所 dashboard */
(function () {
  const state = { all: [], fields: [], filtered: [] };

  const els = {
    county: document.getElementById("f-county"),
    district: document.getElementById("f-district"),
    type: document.getElementById("f-type"),
    category: document.getElementById("f-category"),
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    statTotal: document.getElementById("stat-total"),
    statDistricts: document.getElementById("stat-districts"),
    statHospital: document.getElementById("stat-hospital"),
    statStation: document.getElementById("stat-station"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  let districtChart, typeChart;

  const TYPE_BADGE = {
    醫院: "inst",
    衛生所: "b",
    醫療站: "c",
    牙醫診所: "",
  };

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 25,
    columns: [
      { key: "id", label: "編號" },
      {
        key: "category",
        label: "分類",
        render: (r) => `<span class="badge ${r.category === "醫療站" ? "c" : ""}">${escapeHtml(r.category)}</span>`,
      },
      { key: "district", label: "鄉鎮市" },
      { key: "name", label: "機構名稱" },
      {
        key: "type",
        label: "機構類型（推斷）",
        render: (r) => `<span class="badge ${TYPE_BADGE[r.type] || ""}">${escapeHtml(r.type)}</span>`,
      },
      { key: "address", label: "地址", render: (r) => addressLink(r.address) },
      { key: "phone", label: "電話", render: (r) => phoneLink(r.phone) },
      { key: "google_rating", label: "Google Map 星等", render: (r) => (r.google_rating ? `⭐ ${r.google_rating}` : "-") },
      { key: "google_review_count", label: "Google Map 評論數", render: (r) => googleReviewCell(r) },
    ],
  });

  // Google Map 評論數欄位：有 google_place_id 時做成可點擊連結直接連到該院所的 Google 地圖評論頁，
  // 沒有 place_id（一次性抓取時查無對照資料，或人工核對後排除的誤配對）則只顯示數字或「-」，不猜測連結。
  function googleReviewCell(r) {
    if (!r.google_review_count) return "-";
    const label = `${Number(r.google_review_count).toLocaleString()} 則`;
    if (!r.google_place_id) return label;
    const href = `https://search.google.com/local/reviews?placeid=${encodeURIComponent(r.google_place_id)}`;
    return `<a href="${href}" target="_blank" rel="noopener">${label}</a>`;
  }

  function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  function phoneLink(phone) {
    if (!phone) return "";
    const digits = phone.replace(/[^\d+]/g, "");
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
    const district = els.district.value;
    const type = els.type.value;
    const category = els.category.value;
    const keyword = els.keyword.value.trim().toLowerCase();
    state.filtered = state.all.filter((r) => {
      if (county && r.county !== county) return false;
      if (district && r.district !== district) return false;
      if (type && r.type !== type) return false;
      if (category && r.category !== category) return false;
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
    const districtCounts = {};
    let hospitalCount = 0;
    let stationCount = 0;
    rows.forEach((r) => {
      districtCounts[r.district] = (districtCounts[r.district] || 0) + 1;
      if (r.type === "醫院") hospitalCount += 1;
      if (r.category === "醫療站") stationCount += 1;
    });
    els.statTotal.textContent = rows.length.toLocaleString();
    els.statDistricts.textContent = Object.keys(districtCounts).filter(Boolean).length;
    els.statHospital.textContent = hospitalCount.toLocaleString();
    els.statStation.textContent = stationCount.toLocaleString();
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
        scales: { x: { ticks: { precision: 0 } } },
      },
    });

    const typeCounts = {};
    state.filtered.forEach((r) => (typeCounts[r.type] = (typeCounts[r.type] || 0) + 1));
    const typeEntries = Object.entries(typeCounts).sort((a, b) => b[1] - a[1]);

    if (typeChart) typeChart.destroy();
    typeChart = new Chart(document.getElementById("chart-type"), {
      type: "doughnut",
      data: {
        labels: typeEntries.map((e) => e[0]),
        datasets: [{ data: typeEntries.map((e) => e[1]), backgroundColor: ["#1f6f5c", "#e07a2c", "#3b6fd6", "#a855c9"] }],
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
  els.district.addEventListener("change", applyFilters);
  els.type.addEventListener("change", applyFilters);
  els.category.addEventListener("change", applyFilters);
  els.keyword.addEventListener("input", debounce(applyFilters, 250));
  els.reset.addEventListener("click", () => {
    els.county.value = "";
    els.district.value = "";
    els.type.value = "";
    els.category.value = "";
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
    const data = window.PINGTUNG_DENTURE_DATA;
    if (!data) {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：找不到內嵌資料 data/pingtung-denture.js</div>`;
      return;
    }
    state.fields = data.fields;
    state.all = data.rows.map(rowToObj);

    const counties = Array.from(new Set(state.all.map((r) => r.county))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateSelect(els.county, counties);

    const districts = Array.from(new Set(state.all.map((r) => r.district))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateSelect(els.district, districts);

    const types = Array.from(new Set(state.all.map((r) => r.type))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateSelect(els.type, types);

    const categories = Array.from(new Set(state.all.map((r) => r.category))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateSelect(els.category, categories);

    els.metaUpdated.textContent = `資料筆數：${data.rows.length.toLocaleString()}`;
    applyFilters();

    // meta.json 僅用於補上資料整理時間，非核心資料，失敗也不影響上方篩選/圖表/表格運作。
    fetch("../data/meta.json")
      .then((r) => r.json())
      .then((meta) => {
        if (meta.pingtungDenture) {
          els.metaUpdated.textContent = `資料筆數：${meta.pingtungDenture.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;
        }
      })
      .catch(() => {});
  }

  init();
})();
