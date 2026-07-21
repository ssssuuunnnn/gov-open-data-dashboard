/* 桃園市長期照護專業服務特約單位 dashboard */
(function () {
  const state = { all: [], fields: [], filtered: [] };

  const els = {
    county: document.getElementById("f-county"),
    district: document.getElementById("f-district"),
    type: document.getElementById("f-type"),
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    statTotal: document.getElementById("stat-total"),
    statCounties: document.getElementById("stat-counties"),
    statDistricts: document.getElementById("stat-districts"),
    statTop: document.getElementById("stat-top"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  let countyChart, typeChart;

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 25,
    columns: [
      { key: "name", label: "機構名稱" },
      { key: "type", label: "服務類型（推斷）" },
      { key: "county", label: "縣市" },
      { key: "district", label: "鄉鎮市區" },
      { key: "address", label: "地址" },
      { key: "owner", label: "負責人" },
      { key: "phone", label: "電話" },
      { key: "email", label: "電子郵件" },
      { key: "updatedAt", label: "最後更新時間" },
    ],
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
    const type = els.type.value;
    const keyword = els.keyword.value.trim().toLowerCase();
    state.filtered = state.all.filter((r) => {
      if (county && r.county !== county) return false;
      if (district && r.district !== district) return false;
      if (type && r.type !== type) return false;
      if (keyword) {
        const hay = `${r.name} ${r.owner} ${r.address}`.toLowerCase();
        if (!hay.includes(keyword)) return false;
      }
      return true;
    });
    renderAll();
  }

  function renderStats() {
    const rows = state.filtered;
    const countyCounts = {};
    const districts = new Set();
    rows.forEach((r) => {
      if (r.county) countyCounts[r.county] = (countyCounts[r.county] || 0) + 1;
      if (r.district) districts.add(`${r.county}${r.district}`);
    });
    els.statTotal.textContent = rows.length.toLocaleString();
    els.statCounties.textContent = Object.keys(countyCounts).length;
    els.statDistricts.textContent = districts.size;
    const top = Object.entries(countyCounts).sort((a, b) => b[1] - a[1])[0];
    els.statTop.textContent = top ? `${top[0]}（${top[1]}）` : "-";
  }

  function renderCharts() {
    const countyCounts = {};
    state.filtered.forEach((r) => {
      if (r.county) countyCounts[r.county] = (countyCounts[r.county] || 0) + 1;
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
      },
    });

    const typeCounts = {};
    state.filtered.forEach((r) => {
      const label = r.type || "其他";
      typeCounts[label] = (typeCounts[label] || 0) + 1;
    });
    const typeEntries = Object.entries(typeCounts).sort((a, b) => b[1] - a[1]);

    if (typeChart) typeChart.destroy();
    typeChart = new Chart(document.getElementById("chart-type"), {
      type: "doughnut",
      data: {
        labels: typeEntries.map((e) => e[0]),
        datasets: [{ data: typeEntries.map((e) => e[1]), backgroundColor: ["#e07a2c", "#1f6f5c", "#3b6fd6", "#a83279", "#c9a227", "#64748b"] }],
      },
      options: { responsive: true, maintainAspectRatio: false },
    });
  }

  function renderAll() {
    renderStats();
    renderCharts();
    table.setData(state.filtered);
  }

  els.county.addEventListener("change", () => {
    refreshDistrictOptions();
    applyFilters();
  });
  els.district.addEventListener("change", applyFilters);
  els.type.addEventListener("change", applyFilters);
  els.keyword.addEventListener("input", debounce(applyFilters, 250));
  els.reset.addEventListener("click", () => {
    els.county.value = "";
    els.type.value = "";
    els.keyword.value = "";
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

  function init() {
    const data = window.TYLTC_DATA;
    if (!data) {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：找不到內嵌資料 data/tyltc.js</div>`;
      return;
    }
    state.fields = data.fields;
    state.all = data.rows.map(rowToObj);

    const counties = Array.from(new Set(state.all.map((r) => r.county))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateSelect(els.county, counties, "全部");
    refreshDistrictOptions();

    const types = Array.from(new Set(state.all.map((r) => r.type))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateSelect(els.type, types, "全部");

    els.metaUpdated.textContent = `資料筆數：${data.rows.length.toLocaleString()}`;
    applyFilters();

    // meta.json 僅用於補上資料整理時間，非核心資料，失敗也不影響上方篩選/圖表/表格運作。
    fetch("../data/meta.json")
      .then((r) => r.json())
      .then((meta) => {
        if (meta.tyltc) {
          els.metaUpdated.textContent = `資料筆數：${meta.tyltc.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;
        }
      })
      .catch(() => {});
  }

  init();
})();
