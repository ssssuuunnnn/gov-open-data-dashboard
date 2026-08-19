/* 彰化縣身心障礙鑑定醫院 dashboard */
(function () {
  const state = { all: [], fields: [], filtered: [] };

  const els = {
    district: document.getElementById("f-district"),
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    statTotal: document.getElementById("stat-total"),
    statDistricts: document.getElementById("stat-districts"),
    statTop: document.getElementById("stat-top"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  let districtChart;

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 25,
    columns: [
      { key: "name", label: "醫院名稱" },
      { key: "district", label: "鄉鎮市" },
      { key: "address", label: "地址", render: (r) => addressLink(r.address) },
      { key: "phone", label: "電話", render: (r) => phoneLink(r.phone) },
    ],
  });

  function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  function phoneLink(phone) {
    if (!phone) return "";
    const digits = String(phone).replace(/[^\d+]/g, "");
    if (!digits) return escapeHtml(phone);
    return `<a href="tel:${digits}">${escapeHtml(phone)}</a>`;
  }

  function addressLink(address) {
    if (!address) return "";
    const href = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(address)}`;
    return `<a href="${href}" target="_blank" rel="noopener">${escapeHtml(address)}</a>`;
  }

  function firstPhoneDigits(phone) {
    if (!phone) return "";
    return String(phone).replace(/[^\d+]/g, "");
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

  // 動態插入 ItemList 結構化資料（列出全部醫院），供搜尋引擎理解本頁機構名單內容；因資料以 JS
  // 內嵌方式載入，改於資料載入完成後插入 <head>，主流搜尋引擎爬蟲會執行 JS 後再擷取結構化資料。
  function injectItemListJsonLd(rows) {
    const itemListElement = rows.map((r, i) => {
      const item = { "@type": "Hospital", name: r.name };
      if (r.address) item.address = r.address;
      const telephone = firstPhoneDigits(r.phone);
      if (telephone) item.telephone = telephone;
      return { "@type": "ListItem", position: i + 1, item };
    });
    const jsonLd = {
      "@context": "https://schema.org",
      "@type": "ItemList",
      name: "彰化縣身心障礙鑑定醫院",
      numberOfItems: rows.length,
      itemListElement,
    };
    const script = document.createElement("script");
    script.type = "application/ld+json";
    script.textContent = JSON.stringify(jsonLd);
    document.head.appendChild(script);
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
      if (!r.district) return;
      districtCounts[r.district] = (districtCounts[r.district] || 0) + 1;
    });
    const entries = Object.entries(districtCounts).sort((a, b) => b[1] - a[1]);
    els.statTotal.textContent = rows.length.toLocaleString();
    els.statDistricts.textContent = entries.length;
    els.statTop.textContent = entries.length ? `${entries[0][0]}（${entries[0][1]}）` : "-";
  }

  function renderCharts() {
    const districtCounts = {};
    state.filtered.forEach((r) => {
      if (!r.district) return;
      districtCounts[r.district] = (districtCounts[r.district] || 0) + 1;
    });
    const entries = Object.entries(districtCounts).sort((a, b) => b[1] - a[1]);

    if (districtChart) districtChart.destroy();
    districtChart = new Chart(document.getElementById("chart-district"), {
      type: "bar",
      data: {
        labels: entries.map((e) => e[0]),
        datasets: [{ data: entries.map((e) => e[1]), backgroundColor: "#0f766e" }],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { ticks: { stepSize: 1 } } },
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
    const data = window.CHC_DISABILITY_HOSPITALS_DATA;
    if (!data) {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：找不到內嵌資料 data/chc-disability-hospitals.js</div>`;
      return;
    }
    state.fields = data.fields;
    state.all = data.rows.map(rowToObj);

    const districts = [...new Set(state.all.map((r) => r.district).filter(Boolean))].sort((a, b) =>
      a.localeCompare(b, "zh-Hant-TW"),
    );
    populateSelect(els.district, districts);

    els.metaUpdated.textContent = `資料筆數：${data.rows.length.toLocaleString()} 家醫院`;
    applyFilters();
    injectItemListJsonLd(state.all);

    // meta.json 僅用於補上資料整理時間，非核心資料，失敗也不影響上方篩選/圖表/表格運作。
    fetch("../data/meta.json")
      .then((r) => r.json())
      .then((meta) => {
        if (meta.chcDisabilityHospitals) {
          els.metaUpdated.textContent = `資料筆數：${meta.chcDisabilityHospitals.count.toLocaleString()} 家醫院　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;
        }
      })
      .catch(() => {});
  }

  init();
})();
