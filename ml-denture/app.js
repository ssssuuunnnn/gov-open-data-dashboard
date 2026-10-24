/* 苗栗縣中低收入老人補助裝置假牙合約牙科醫療診所 dashboard */
(function () {
  const state = { all: [], fields: [], filtered: [] };

  const els = {
    district: document.getElementById("f-district"),
    type: document.getElementById("f-type"),
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    statTotal: document.getElementById("stat-total"),
    statDistricts: document.getElementById("stat-districts"),
    statTop: document.getElementById("stat-top"),
    statHospital: document.getElementById("stat-hospital"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  let districtChart;

  const columns = [
    { key: "id", label: "編號" },
    { key: "district", label: "鄉鎮市" },
    { key: "name", label: "機構名稱" },
    { key: "doctor", label: "負責醫師" },
    {
      key: "type",
      label: "機構類型（推斷）",
      render: (r) => `<span class="badge ${r.type === "醫院" ? "inst" : ""}">${escapeHtml(r.type)}</span>`,
    },
    { key: "address", label: "地址", render: (r) => addressLink(r.address) },
    { key: "phone", label: "電話", render: (r) => phoneLink(r.phone) },
  ];

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 25,
    columns,
  });

  function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  function phoneLink(phone) {
    if (!phone) return "";
    const digits = phone.split("#")[0].replace(/[^\d+]/g, "");
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
    const district = els.district.value;
    const type = els.type.value;
    const keyword = els.keyword.value.trim().toLowerCase();
    state.filtered = state.all.filter((r) => {
      if (district && r.district !== district) return false;
      if (type && r.type !== type) return false;
      if (keyword) {
        const hay = `${r.name} ${r.address} ${r.phone} ${r.doctor || ""}`.toLowerCase();
        if (!hay.includes(keyword)) return false;
      }
      return true;
    });
    renderAll();
  }

  function districtEntries() {
    const counts = {};
    state.filtered.forEach((r) => (counts[r.district] = (counts[r.district] || 0) + 1));
    return Object.entries(counts).filter(([k]) => k).sort((a, b) => b[1] - a[1]);
  }

  function renderStats() {
    const entries = districtEntries();
    els.statTotal.textContent = state.filtered.length.toLocaleString();
    els.statDistricts.textContent = entries.length;
    els.statTop.textContent = entries.length ? entries[0][0] : "-";
    els.statHospital.textContent = state.filtered.filter((r) => r.type === "醫院").length;
  }

  function renderCharts() {
    const entries = districtEntries();
    if (districtChart) districtChart.destroy();
    districtChart = new Chart(document.getElementById("chart-district"), {
      type: "bar",
      data: {
        labels: entries.map((e) => e[0]),
        datasets: [{ data: entries.map((e) => e[1]), backgroundColor: "#7d5411" }],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { ticks: { precision: 0 } } },
      },
    });
  }

  function renderAll() {
    renderStats();
    if (typeof Chart !== "undefined") renderCharts();
    table.setData(state.filtered);
  }

  function debounce(fn, ms) {
    let t;
    return (...args) => {
      clearTimeout(t);
      t = setTimeout(() => fn(...args), ms);
    };
  }

  els.district.addEventListener("change", applyFilters);
  els.type.addEventListener("change", applyFilters);
  els.keyword.addEventListener("input", debounce(applyFilters, 250));
  els.reset.addEventListener("click", () => {
    els.district.value = "";
    els.type.value = "";
    els.keyword.value = "";
    applyFilters();
  });

  function init() {
    const data = window.ML_DENTURE_DATA;
    if (!data) {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：找不到內嵌資料 data/ml-denture.js</div>`;
      return;
    }
    state.fields = data.fields;
    state.all = data.rows.map(rowToObj);
    const sortZh = (a, b) => a.localeCompare(b, "zh-Hant");
    populateSelect(els.district, Array.from(new Set(state.all.map((r) => r.district))).filter(Boolean).sort(sortZh));
    populateSelect(els.type, Array.from(new Set(state.all.map((r) => r.type))).filter(Boolean).sort(sortZh));
    els.metaUpdated.textContent = `資料筆數：${data.rows.length.toLocaleString()}`;
    applyFilters();

    // meta.json 僅用於補上資料整理時間，失敗不影響篩選與表格。
    fetch("../data/meta.json")
      .then((r) => r.json())
      .then((meta) => {
        if (meta.mlDenture) {
          els.metaUpdated.textContent = `資料筆數：${meta.mlDenture.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;
        }
      })
      .catch(() => {});
  }

  init();
})();
