/* 臺中市一般護理之家清冊 dashboard */
(function () {
  const state = { all: [], fields: [], filtered: [] };

  const els = {
    district: document.getElementById("f-district"),
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    statTotal: document.getElementById("stat-total"),
    statDistricts: document.getElementById("stat-districts"),
    statGeneralBeds: document.getElementById("stat-general-beds"),
    statVentBeds: document.getElementById("stat-vent-beds"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  let districtChart;

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 25,
    columns: [
      { key: "name", label: "機構名稱" },
      { key: "district", label: "行政區" },
      { key: "generalBedsOpen", label: "一般床開放床數" },
      { key: "ventBedsOpen", label: "呼吸器依賴開放床數" },
      { key: "openDate", label: "開業日期" },
      { key: "rating", label: "評鑑結果" },
      { key: "superviseRating", label: "督考結果" },
      { key: "director", label: "負責人" },
      { key: "phone", label: "電話", render: (r) => phoneLink(r.phone) },
      { key: "address", label: "住址" },
      { key: "dayCareOpen", label: "附設日照開放人數" },
    ],
  });

  function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  // 電話欄位常見格式如「(04)22200902#18」，轉成 tel: 連結：去除括號/連字號等裝飾字元，
  // 「#」分機以 ;ext= 表示，供手機點擊直接撥號，顯示文字仍保留原始格式。
  function phoneLink(phone) {
    if (!phone) return "";
    const [main, ext] = phone.split("#");
    const digits = main.replace(/[^\d+]/g, "");
    if (!digits) return escapeHtml(phone);
    const href = ext ? `tel:${digits};ext=${ext.replace(/[^\d]/g, "")}` : `tel:${digits}`;
    return `<a href="${href}">${escapeHtml(phone)}</a>`;
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
    const keyword = els.keyword.value.trim().toLowerCase();
    state.filtered = state.all.filter((r) => {
      if (district && r.district !== district) return false;
      if (keyword) {
        const hay = `${r.name} ${r.director} ${r.phone} ${r.address}`.toLowerCase();
        if (!hay.includes(keyword)) return false;
      }
      return true;
    });
    renderAll();
  }

  function renderStats() {
    const rows = state.filtered;
    const districtCounts = {};
    let generalBeds = 0;
    let ventBeds = 0;
    rows.forEach((r) => {
      districtCounts[r.district] = (districtCounts[r.district] || 0) + 1;
      generalBeds += r.generalBedsOpen || 0;
      ventBeds += r.ventBedsOpen || 0;
    });
    els.statTotal.textContent = rows.length.toLocaleString();
    els.statDistricts.textContent = Object.keys(districtCounts).filter(Boolean).length;
    els.statGeneralBeds.textContent = generalBeds.toLocaleString();
    els.statVentBeds.textContent = ventBeds.toLocaleString();
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
  }

  function renderAll() {
    renderStats();
    renderCharts();
    table.setData(state.filtered);
  }

  els.district.addEventListener("change", applyFilters);
  els.keyword.addEventListener("input", debounce(applyFilters, 250));
  els.reset.addEventListener("click", () => {
    els.district.value = "";
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
    const data = window.TC_NURSING_DATA;
    if (!data) {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：找不到內嵌資料 data/tc-nursing.js</div>`;
      return;
    }
    state.fields = data.fields;
    state.all = data.rows.map(rowToObj);

    const districts = Array.from(new Set(state.all.map((r) => r.district))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateSelect(els.district, districts);

    els.metaUpdated.textContent = `資料筆數：${data.rows.length.toLocaleString()}`;
    applyFilters();

    // meta.json 僅用於補上資料整理時間，非核心資料，失敗也不影響上方篩選/圖表/表格運作。
    fetch("../data/meta.json")
      .then((r) => r.json())
      .then((meta) => {
        if (meta.tcNursing) {
          els.metaUpdated.textContent = `資料筆數：${meta.tcNursing.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;
        }
      })
      .catch(() => {});
  }

  init();
})();
