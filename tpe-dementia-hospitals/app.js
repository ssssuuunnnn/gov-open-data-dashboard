/* 臺北市失智症診療機構名冊 dashboard */
(function () {
  const state = { all: [], fields: [], filtered: [] };

  const els = {
    district: document.getElementById("f-district"),
    level: document.getElementById("f-level"),
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    statTotal: document.getElementById("stat-total"),
    statDistricts: document.getElementById("stat-districts"),
    statTop: document.getElementById("stat-top"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  let districtChart;
  let levelChart;

  function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  // 電話欄位一律轉成 tel: 連結，僅取號碼數字（去除括號/連字號等裝飾字元），顯示文字保留原始格式。
  function phoneLink(phone) {
    if (!phone) return "-";
    const digits = phone.replace(/[^\d]/g, "");
    return `<a href="tel:${digits}">${escapeHtml(phone)}</a>`;
  }

  // 地址欄位一律轉成 Google Maps 搜尋連結，顯示文字維持原始地址。
  function addressLink(address) {
    if (!address) return "-";
    const href = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(address)}`;
    return `<a href="${href}" target="_blank" rel="noopener">${escapeHtml(address)}</a>`;
  }

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 25,
    columns: [
      { key: "id", label: "序號" },
      { key: "name", label: "醫院名稱" },
      { key: "department", label: "失智症看診科別" },
      { key: "level", label: "健保特約類別" },
      { key: "phone", label: "電話", render: (r) => phoneLink(r.phone) },
      { key: "address", label: "地址", render: (r) => addressLink(r.address) },
      { key: "district", label: "行政區" },
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
    const level = els.level.value;
    const keyword = els.keyword.value.trim().toLowerCase();
    state.filtered = state.all.filter((r) => {
      if (district && r.district !== district) return false;
      if (level && r.level !== level) return false;
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
    const districtCounts = {};
    rows.forEach((r) => {
      districtCounts[r.district] = (districtCounts[r.district] || 0) + 1;
    });
    els.statTotal.textContent = rows.length.toLocaleString();
    els.statDistricts.textContent = Object.keys(districtCounts).filter(Boolean).length;
    const top = Object.entries(districtCounts).filter(([k]) => k).sort((a, b) => b[1] - a[1])[0];
    els.statTop.textContent = top ? `${top[0]}（${top[1]}）` : "-";
  }

  function renderCharts() {
    const districtCounts = {};
    const levelCounts = {};
    state.filtered.forEach((r) => {
      districtCounts[r.district] = (districtCounts[r.district] || 0) + 1;
      levelCounts[r.level] = (levelCounts[r.level] || 0) + 1;
    });
    const districtEntries = Object.entries(districtCounts)
      .filter(([k]) => k)
      .sort((a, b) => b[1] - a[1]);
    const levelEntries = Object.entries(levelCounts).filter(([k]) => k);

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

    if (levelChart) levelChart.destroy();
    levelChart = new Chart(document.getElementById("chart-level"), {
      type: "doughnut",
      data: {
        labels: levelEntries.map((e) => e[0]),
        datasets: [{ data: levelEntries.map((e) => e[1]), backgroundColor: ["#1f6f5c", "#d97706", "#2563eb", "#9333ea"] }],
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
  els.level.addEventListener("change", applyFilters);
  els.keyword.addEventListener("input", debounce(applyFilters, 250));
  els.reset.addEventListener("click", () => {
    els.district.value = "";
    els.level.value = "";
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
    const data = window.TPE_DEMENTIA_HOSPITALS_DATA;
    if (!data) {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：找不到內嵌資料 data/tpe-dementia-hospitals.js</div>`;
      return;
    }
    state.fields = data.fields;
    state.all = data.rows.map(rowToObj);

    const districts = Array.from(new Set(state.all.map((r) => r.district))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateSelect(els.district, districts);

    const levels = Array.from(new Set(state.all.map((r) => r.level))).filter(Boolean);
    populateSelect(els.level, levels);

    els.metaUpdated.textContent = `資料筆數：${data.rows.length.toLocaleString()}`;
    applyFilters();

    // meta.json 僅用於補上資料整理時間，非核心資料，失敗也不影響上方篩選/圖表/表格運作。
    fetch("../data/meta.json")
      .then((r) => r.json())
      .then((meta) => {
        if (meta.tpeDementiaHospitals) {
          els.metaUpdated.textContent = `資料筆數：${meta.tpeDementiaHospitals.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;
        }
      })
      .catch(() => {});
  }

  init();
})();
