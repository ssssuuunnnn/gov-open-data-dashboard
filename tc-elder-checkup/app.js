/* 臺中市老人健康檢查合約醫療院所名單 dashboard */
(function () {
  const state = { all: [], fields: [], filtered: [] };

  const CATEGORIES = ["醫學中心", "區域醫院", "地區醫院", "診所"];
  const catColor = {
    醫學中心: "#1f6f5c",
    區域醫院: "#2f855a",
    地區醫院: "#68a06f",
    診所: "#a3c9a8",
  };

  const els = {
    district: document.getElementById("f-district"),
    category: document.getElementById("f-category"),
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    statTotal: document.getElementById("stat-total"),
    statDistricts: document.getElementById("stat-districts"),
    statFree: document.getElementById("stat-free"),
    statMedicalCenter: document.getElementById("stat-medical-center"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  let districtChart, categoryChart;

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 25,
    columns: [
      { key: "category", label: "類別" },
      { key: "name", label: "院所名稱" },
      { key: "phone", label: "聯繫電話", render: (r) => phoneLink(r.phone) },
      { key: "address", label: "地址", render: (r) => addressLink(r.address) },
      { key: "district", label: "行政區" },
      { key: "feeNote", label: "是否收掛號費" },
      { key: "hours", label: "服務時段" },
      { key: "google_rating", label: "Google Map 星等", render: (r) => (r.google_rating ? `⭐ ${r.google_rating}` : "-") },
      { key: "google_review_count", label: "Google Map 評論數", render: (r) => googleReviewCell(r) },
    ],
  });

  function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  // 電話欄位格式如「(04)26862288」，轉成 tel: 連結：去除括號等裝飾字元，顯示文字仍保留原始格式。
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

  // Google Map 評論數欄位：有 google_place_id 時做成可點擊連結直接連到該院所的 Google 地圖評論頁，
  // 沒有 place_id（尚未執行一次性抓取或查無對照資料）則只顯示「-」，不猜測連結。
  function googleReviewCell(r) {
    if (!r.google_review_count) return "-";
    const label = `${Number(r.google_review_count).toLocaleString()} 則`;
    if (!r.google_place_id) return label;
    const href = `https://search.google.com/local/reviews?placeid=${encodeURIComponent(r.google_place_id)}`;
    return `<a href="${href}" target="_blank" rel="noopener">${escapeHtml(label)}</a>`;
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
    const district = els.district.value;
    const category = els.category.value;
    const keyword = els.keyword.value.trim().toLowerCase();
    state.filtered = state.all.filter((r) => {
      if (district && r.district !== district) return false;
      if (category && r.category !== category) return false;
      if (keyword) {
        const hay = `${r.name} ${r.phone} ${r.address}`.toLowerCase();
        if (!hay.includes(keyword)) return false;
      }
      return true;
    });
    renderAll();
  }

  function renderStats() {
    const rows = state.filtered;
    const districtCounts = {};
    let freeCount = 0;
    let medicalCenterCount = 0;
    rows.forEach((r) => {
      districtCounts[r.district] = (districtCounts[r.district] || 0) + 1;
      if (r.feeNote === "否") freeCount += 1;
      if (r.category === "醫學中心") medicalCenterCount += 1;
    });
    els.statTotal.textContent = rows.length.toLocaleString();
    els.statDistricts.textContent = Object.keys(districtCounts).filter(Boolean).length;
    els.statFree.textContent = freeCount.toLocaleString();
    els.statMedicalCenter.textContent = medicalCenterCount.toLocaleString();
  }

  function renderCharts() {
    const districtCounts = {};
    const categoryCounts = {};
    state.filtered.forEach((r) => {
      districtCounts[r.district] = (districtCounts[r.district] || 0) + 1;
      categoryCounts[r.category] = (categoryCounts[r.category] || 0) + 1;
    });
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

    const categoryEntries = CATEGORIES.map((c) => [c, categoryCounts[c] || 0]).filter(([, v]) => v > 0);
    if (categoryChart) categoryChart.destroy();
    categoryChart = new Chart(document.getElementById("chart-category"), {
      type: "doughnut",
      data: {
        labels: categoryEntries.map((e) => e[0]),
        datasets: [{ data: categoryEntries.map((e) => e[1]), backgroundColor: categoryEntries.map((e) => catColor[e[0]]) }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: "bottom" } },
      },
    });
  }

  function renderAll() {
    renderStats();
    renderCharts();
    table.setData(state.filtered);
  }

  els.district.addEventListener("change", applyFilters);
  els.category.addEventListener("change", applyFilters);
  els.keyword.addEventListener("input", debounce(applyFilters, 250));
  els.reset.addEventListener("click", () => {
    els.district.value = "";
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
    const data = window.TC_ELDER_CHECKUP_DATA;
    if (!data) {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：找不到內嵌資料 data/tc-elder-checkup.js</div>`;
      return;
    }
    state.fields = data.fields;
    state.all = data.rows.map(rowToObj);

    const districts = Array.from(new Set(state.all.map((r) => r.district))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateSelect(els.district, districts);
    populateSelect(els.category, CATEGORIES);

    els.metaUpdated.textContent = `資料筆數：${data.rows.length.toLocaleString()}`;
    applyFilters();

    // meta.json 僅用於補上資料整理時間，非核心資料，失敗也不影響上方篩選/圖表/表格運作。
    fetch("../data/meta.json")
      .then((r) => r.json())
      .then((meta) => {
        if (meta.tcElderCheckup) {
          els.metaUpdated.textContent = `資料筆數：${meta.tcElderCheckup.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;
        }
      })
      .catch(() => {});
  }

  init();
})();
