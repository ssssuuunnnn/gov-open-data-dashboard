/* 桃園市身心障礙類別、向度之鑑定醫院名冊 dashboard */
(function () {
  const state = { all: [], fields: [], filtered: [], combos: [], filteredCombos: [], hospitals: [], categories: [], itemsByCategory: {} };

  const els = {
    category: document.getElementById("f-category"),
    item: document.getElementById("f-item"),
    hospital: document.getElementById("f-hospital"),
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    statTotal: document.getElementById("stat-total"),
    statCategories: document.getElementById("stat-categories"),
    statHospitals: document.getElementById("stat-hospitals"),
    statNote: document.getElementById("stat-note"),
    metaUpdated: document.getElementById("meta-updated"),
    tableContainer: document.getElementById("table-container"),
  };

  let hospitalChart, categoryChart;

  function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  function rowToObj(row) {
    const o = {};
    state.fields.forEach((f, i) => (o[f] = row[i]));
    return o;
  }

  function populateSelect(select, values, keepFirst = true) {
    select.innerHTML = keepFirst ? `<option value="">全部</option>` : "";
    values.forEach((v) => {
      const opt = document.createElement("option");
      opt.value = v;
      opt.textContent = v;
      select.appendChild(opt);
    });
  }

  function refreshItemOptions() {
    const category = els.category.value;
    const items = category
      ? state.itemsByCategory[category] || []
      : Array.from(new Set(state.all.map((r) => r.item))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    const current = els.item.value;
    populateSelect(els.item, items);
    if (items.includes(current)) els.item.value = current;
  }

  function buildCombos() {
    // 依原始檔案列順序，將長格式資料還原成「類別×向度×醫院」矩陣，每個組合保留所有醫院的鑑定結果
    // （含未勾選/blank），供表格以原始勾選矩陣樣式呈現。
    const comboMap = new Map();
    state.all.forEach((r) => {
      const key = `${r.category}\u0001${r.dimension}\u0001${r.item}\u0001${r.disease}`;
      if (!comboMap.has(key)) {
        comboMap.set(key, { category: r.category, dimension: r.dimension, item: r.item, disease: r.disease, cells: {} });
      }
      comboMap.get(key).cells[r.hospital] = r.note;
    });
    state.combos = Array.from(comboMap.values());
  }

  function applyFilters() {
    const category = els.category.value;
    const item = els.item.value;
    const hospital = els.hospital.value;
    const keyword = els.keyword.value.trim().toLowerCase();

    state.filteredCombos = state.combos.filter((c) => {
      if (category && c.category !== category) return false;
      if (item && c.item !== item) return false;
      if (hospital && !Object.prototype.hasOwnProperty.call(c.cells, hospital)) return false;
      if (keyword) {
        const noteTexts = Object.values(c.cells).filter(Boolean).join(" ");
        const hay = `${c.item} ${c.disease} ${noteTexts}`.toLowerCase();
        if (!hay.includes(keyword)) return false;
      }
      return true;
    });

    // 展平為「類別+向度+醫院」一列一筆，供統計卡與圖表計算使用（若已選定醫院，僅計入該醫院）
    state.filtered = [];
    state.filteredCombos.forEach((c) => {
      Object.entries(c.cells).forEach(([h, note]) => {
        if (hospital && h !== hospital) return;
        state.filtered.push({ category: c.category, dimension: c.dimension, item: c.item, disease: c.disease, hospital: h, note });
      });
    });

    renderAll();
  }

  function renderStats() {
    const rows = state.filtered;
    els.statTotal.textContent = rows.length.toLocaleString();
    els.statCategories.textContent = new Set(rows.map((r) => r.category)).size;
    els.statHospitals.textContent = new Set(rows.map((r) => r.hospital)).size;
    els.statNote.textContent = rows.filter((r) => r.note).length.toLocaleString();
  }

  function renderCharts() {
    const hospitalCounts = {};
    state.filtered.forEach((r) => (hospitalCounts[r.hospital] = (hospitalCounts[r.hospital] || 0) + 1));
    const hospitalEntries = Object.entries(hospitalCounts).sort((a, b) => b[1] - a[1]);

    if (hospitalChart) hospitalChart.destroy();
    hospitalChart = new Chart(document.getElementById("chart-hospital"), {
      type: "bar",
      data: {
        labels: hospitalEntries.map((e) => e[0]),
        datasets: [{ data: hospitalEntries.map((e) => e[1]), backgroundColor: "#1f6f5c" }],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
      },
    });

    const categoryCounts = {};
    state.filtered.forEach((r) => (categoryCounts[r.category] = (categoryCounts[r.category] || 0) + 1));
    const categoryEntries = Object.entries(categoryCounts).sort((a, b) => b[1] - a[1]);
    const palette = ["#1f6f5c", "#e07a2c", "#2563eb", "#b45309", "#7c3aed", "#dc2626", "#0891b2", "#65a30d", "#64748b"];

    if (categoryChart) categoryChart.destroy();
    categoryChart = new Chart(document.getElementById("chart-category"), {
      type: "doughnut",
      data: {
        labels: categoryEntries.map((e) => e[0]),
        datasets: [{ data: categoryEntries.map((e) => e[1]), backgroundColor: categoryEntries.map((_, i) => palette[i % palette.length]) }],
      },
      options: { responsive: true, maintainAspectRatio: false },
    });
  }

  function renderMatrixTable() {
    const combos = state.filteredCombos;
    const hospitals = state.hospitals;
    const selectedHospital = els.hospital.value;

    if (!combos.length) {
      els.tableContainer.innerHTML = `<div class="loading">沒有符合篩選條件的資料</div>`;
      return;
    }

    let html = '<div class="table-wrap"><table class="data-table disability-matrix"><thead><tr>';
    html += "<th>新制鑑定類別</th><th>新制鑑定向度</th><th>新制鑑定向度_名稱</th><th>相關疾病類別</th>";
    hospitals.forEach((h) => {
      html += `<th class="${h === selectedHospital ? "hl-col" : ""}">${escapeHtml(h)}</th>`;
    });
    html += "</tr></thead><tbody>";

    combos.forEach((c, i) => {
      html += "<tr>";
      const prev = combos[i - 1];
      if (!prev || prev.category !== c.category) {
        let span = 1;
        while (combos[i + span] && combos[i + span].category === c.category) span++;
        html += `<td rowspan="${span}">${escapeHtml(c.category)}</td>`;
      }
      if (!prev || prev.category !== c.category || prev.dimension !== c.dimension) {
        let span = 1;
        while (combos[i + span] && combos[i + span].category === c.category && combos[i + span].dimension === c.dimension) span++;
        html += `<td rowspan="${span}">${escapeHtml(c.dimension)}</td>`;
      }
      html += `<td>${escapeHtml(c.item)}</td><td>${escapeHtml(c.disease)}</td>`;
      hospitals.forEach((h) => {
        const cls = h === selectedHospital ? ' class="hl-col"' : "";
        if (!Object.prototype.hasOwnProperty.call(c.cells, h)) {
          html += `<td${cls}></td>`;
          return;
        }
        const note = c.cells[h];
        html += `<td${cls}>${note ? `V<br><span class="note">(${escapeHtml(note)})</span>` : "V"}</td>`;
      });
      html += "</tr>";
    });

    html += "</tbody></table></div>";
    els.tableContainer.innerHTML = html;
  }

  function renderAll() {
    renderStats();
    renderCharts();
    renderMatrixTable();
  }

  els.category.addEventListener("change", () => {
    els.item.value = "";
    refreshItemOptions();
    applyFilters();
  });
  els.item.addEventListener("change", applyFilters);
  els.hospital.addEventListener("change", applyFilters);
  els.keyword.addEventListener("input", debounce(applyFilters, 250));
  els.reset.addEventListener("click", () => {
    els.category.value = "";
    els.item.value = "";
    els.hospital.value = "";
    els.keyword.value = "";
    refreshItemOptions();
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
    fetch("../data/tyc-disability-hospitals.json").then((r) => r.json()),
    fetch("../data/meta.json").then((r) => r.json()),
  ])
    .then(([data, meta]) => {
      state.fields = data.fields;
      state.all = data.rows.map(rowToObj);

      state.hospitals = data.hospitals || Array.from(new Set(state.all.map((r) => r.hospital))).filter(Boolean);
      buildCombos();

      state.categories = Array.from(new Set(state.all.map((r) => r.category))).filter(Boolean);
      state.itemsByCategory = {};
      state.categories.forEach((c) => {
        state.itemsByCategory[c] = Array.from(new Set(state.all.filter((r) => r.category === c).map((r) => r.item)))
          .filter(Boolean)
          .sort((a, b) => a.localeCompare(b, "zh-Hant"));
      });

      populateSelect(els.category, state.categories);
      refreshItemOptions();
      populateSelect(els.hospital, state.hospitals);

      const m = meta.tycDisabilityHospitals;
      els.metaUpdated.textContent = m
        ? `資料筆數：${m.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`
        : "";

      applyFilters();
    })
    .catch((err) => {
      els.tableContainer.innerHTML = `<div class="loading">資料載入失敗：${err}</div>`;
    });
})();
