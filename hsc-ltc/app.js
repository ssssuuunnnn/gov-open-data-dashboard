/* 新竹縣長照機構名冊 dashboard */
(function () {
  const state = { all: [], fields: [], filtered: [] };

  const els = {
    district: document.getElementById("f-district"),
    servType: document.getElementById("f-servtype"),
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    statTotal: document.getElementById("stat-total"),
    statDistricts: document.getElementById("stat-districts"),
    statServTypes: document.getElementById("stat-servtypes"),
    statTop: document.getElementById("stat-top"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  let districtChart, servTypeChart;

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 25,
    columns: [
      { key: "id", label: "編號" },
      { key: "name", label: "機構名稱" },
      { key: "servType", label: "服務類型" },
      { key: "district", label: "鄉鎮市區" },
      { key: "address", label: "地址" },
      { key: "zipcode", label: "郵遞區號" },
      { key: "phone", label: "電話" },
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
    const servType = els.servType.value;
    const keyword = els.keyword.value.trim().toLowerCase();
    state.filtered = state.all.filter((r) => {
      if (district && r.district !== district) return false;
      if (servType && r.servType !== servType) return false;
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
    const servTypes = new Set();
    rows.forEach((r) => {
      districtCounts[r.district] = (districtCounts[r.district] || 0) + 1;
      if (r.servType) servTypes.add(r.servType);
    });
    els.statTotal.textContent = rows.length.toLocaleString();
    els.statDistricts.textContent = Object.keys(districtCounts).filter(Boolean).length;
    els.statServTypes.textContent = servTypes.size;
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

    const servTypeCounts = {};
    state.filtered.forEach((r) => {
      const label = r.servType || "未標示";
      servTypeCounts[label] = (servTypeCounts[label] || 0) + 1;
    });
    const servTypeEntries = Object.entries(servTypeCounts).sort((a, b) => b[1] - a[1]);

    if (servTypeChart) servTypeChart.destroy();
    servTypeChart = new Chart(document.getElementById("chart-servtype"), {
      type: "bar",
      data: {
        labels: servTypeEntries.map((e) => e[0]),
        datasets: [{ data: servTypeEntries.map((e) => e[1]), backgroundColor: "#e07a2c" }],
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
  els.servType.addEventListener("change", applyFilters);
  els.keyword.addEventListener("input", debounce(applyFilters, 250));
  els.reset.addEventListener("click", () => {
    els.district.value = "";
    els.servType.value = "";
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
    const data = window.HSC_LTC_DATA;
    if (!data) {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：找不到內嵌資料 data/hsc-ltc.js</div>`;
      return;
    }
    state.fields = data.fields;
    state.all = data.rows.map(rowToObj);

    const districts = Array.from(new Set(state.all.map((r) => r.district))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateSelect(els.district, districts);

    const servTypes = Array.from(new Set(state.all.map((r) => r.servType))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateSelect(els.servType, servTypes);

    els.metaUpdated.textContent = `資料筆數：${data.rows.length.toLocaleString()}`;
    applyFilters();

    // meta.json 僅用於補上資料整理時間，非核心資料，失敗也不影響上方篩選/圖表/表格運作。
    fetch("../data/meta.json")
      .then((r) => r.json())
      .then((meta) => {
        if (meta.hscLtc) {
          els.metaUpdated.textContent = `資料筆數：${meta.hscLtc.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;
        }
      })
      .catch(() => {});
  }

  init();
})();
