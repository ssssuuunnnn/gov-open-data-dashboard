/* 新北市失智症門診資訊 dashboard */
(function () {
  const state = { all: [], fields: [], filtered: [] };

  const els = {
    district: document.getElementById("f-district"),
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    statTotal: document.getElementById("stat-total"),
    statDistricts: document.getElementById("stat-districts"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  let districtChart;

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 25,
    columns: [
      { key: "name", label: "醫院名稱" },
      { key: "phone", label: "電話", render: (r) => phoneLink(r.phone) },
      { key: "district", label: "行政區" },
      { key: "address", label: "地址", render: (r) => addressLink(r.address) },
    ],
  });

  function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  // 電話欄位轉成 tel: 連結，顯示文字保留原始格式，去除裝飾字元作為連結號碼。
  function phoneLink(phone) {
    if (!phone) return "";
    const digits = phone.replace(/[^\d+]/g, "");
    if (!digits) return escapeHtml(phone);
    return `<a href="tel:${digits}">${escapeHtml(phone)}</a>`;
  }

  // 地址欄位轉成 Google Maps 搜尋連結（無經緯度座標，故用地址文字查詢）。
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
    const keyword = els.keyword.value.trim().toLowerCase();
    state.filtered = state.all.filter((r) => {
      if (district && r.district !== district) return false;
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
  }

  function renderCharts() {
    const districtCounts = {};
    state.filtered.forEach((r) => {
      districtCounts[r.district] = (districtCounts[r.district] || 0) + 1;
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
    const data = window.NTPC_DEMENTIA_DATA;
    if (!data) {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：找不到內嵌資料 data/ntpc-dementia.js</div>`;
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
        if (meta.ntpcDementia) {
          els.metaUpdated.textContent = `資料筆數：${meta.ntpcDementia.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;
        }
      })
      .catch(() => {});
  }

  init();
})();
