/* 屏東縣老人長期照顧機構 dashboard */
(function () {
  const state = { all: [], fields: [], filtered: [] };

  const els = {
    township: document.getElementById("f-township"),
    type: document.getElementById("f-type"),
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    statTotal: document.getElementById("stat-total"),
    statTownships: document.getElementById("stat-townships"),
    statTypes: document.getElementById("stat-types"),
    statTop: document.getElementById("stat-top"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  let townshipChart, typeChart;

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 25,
    columns: [
      { key: "name", label: "機構名稱" },
      { key: "type", label: "機構類型" },
      { key: "township", label: "鄉鎮市" },
      { key: "address", label: "地址" },
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
    const township = els.township.value;
    const type = els.type.value;
    const keyword = els.keyword.value.trim().toLowerCase();
    state.filtered = state.all.filter((r) => {
      if (township && r.township !== township) return false;
      if (type && r.type !== type) return false;
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
    const townshipCounts = {};
    const types = new Set();
    rows.forEach((r) => {
      if (r.township) townshipCounts[r.township] = (townshipCounts[r.township] || 0) + 1;
      if (r.type) types.add(r.type);
    });
    els.statTotal.textContent = rows.length.toLocaleString();
    els.statTownships.textContent = Object.keys(townshipCounts).length;
    els.statTypes.textContent = types.size;
    const top = Object.entries(townshipCounts).sort((a, b) => b[1] - a[1])[0];
    els.statTop.textContent = top ? `${top[0]}（${top[1]}）` : "-";
  }

  function renderCharts() {
    const townshipCounts = {};
    state.filtered.forEach((r) => {
      if (r.township) townshipCounts[r.township] = (townshipCounts[r.township] || 0) + 1;
    });
    const townshipEntries = Object.entries(townshipCounts).sort((a, b) => b[1] - a[1]);

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

    const typeCounts = {};
    state.filtered.forEach((r) => {
      const label = r.type || "未標示";
      typeCounts[label] = (typeCounts[label] || 0) + 1;
    });
    const typeEntries = Object.entries(typeCounts).sort((a, b) => b[1] - a[1]);

    if (typeChart) typeChart.destroy();
    typeChart = new Chart(document.getElementById("chart-type"), {
      type: "doughnut",
      data: {
        labels: typeEntries.map((e) => e[0]),
        datasets: [{ data: typeEntries.map((e) => e[1]), backgroundColor: ["#e07a2c", "#1f6f5c", "#3b6fd6", "#a83279", "#c9a227"] }],
      },
      options: { responsive: true, maintainAspectRatio: false },
    });
  }

  function renderAll() {
    renderStats();
    renderCharts();
    table.setData(state.filtered);
  }

  els.township.addEventListener("change", applyFilters);
  els.type.addEventListener("change", applyFilters);
  els.keyword.addEventListener("input", debounce(applyFilters, 250));
  els.reset.addEventListener("click", () => {
    els.township.value = "";
    els.type.value = "";
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
    const data = window.PINGTUNG_LTC_DATA;
    if (!data) {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：找不到內嵌資料 data/pingtung-ltc.js</div>`;
      return;
    }
    state.fields = data.fields;
    state.all = data.rows.map(rowToObj);

    const townships = Array.from(new Set(state.all.map((r) => r.township))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateSelect(els.township, townships);

    const types = Array.from(new Set(state.all.map((r) => r.type))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateSelect(els.type, types);

    els.metaUpdated.textContent = `資料筆數：${data.rows.length.toLocaleString()}`;
    applyFilters();

    // meta.json 僅用於補上資料整理時間，非核心資料，失敗也不影響上方篩選/圖表/表格運作。
    fetch("../data/meta.json")
      .then((r) => r.json())
      .then((meta) => {
        if (meta.pingtungLtc) {
          els.metaUpdated.textContent = `資料筆數：${meta.pingtungLtc.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;
        }
      })
      .catch(() => {});
  }

  init();
})();
