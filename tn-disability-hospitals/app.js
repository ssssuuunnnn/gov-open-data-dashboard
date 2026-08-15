/* 115年臺南市身心障礙鑑定醫院 dashboard */
(function () {
  const state = { all: [], fields: [], filtered: [] };

  const CATEGORY_LABELS = {
    "1": "第1類（神經系統構造及精神、心智功能）",
    "2": "第2類（眼、耳及相關構造與感官功能、疼痛）",
    "3": "第3類（涉及聲音與言語構造及其功能）",
    "4": "第4類（循環、造血、免疫與呼吸系統構造及功能）",
    "5": "第5類（消化、新陳代謝與內分泌系統相關構造及功能）",
    "6": "第6類（泌尿與生殖系統相關構造及功能）",
    "7": "第7類（神經、肌肉、骨骼之移動相關構造及功能）",
    "8": "第8類（皮膚與相關構造及功能）",
  };

  const els = {
    district: document.getElementById("f-district"),
    category: document.getElementById("f-category"),
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    statTotal: document.getElementById("stat-total"),
    statDistricts: document.getElementById("stat-districts"),
    statTop: document.getElementById("stat-top"),
    statFull: document.getElementById("stat-full"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  let districtChart, categoryChart;

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 25,
    columns: [
      { key: "name", label: "醫院名稱" },
      { key: "district", label: "行政區" },
      { key: "address", label: "地址", render: (r) => addressLink(r.address) },
      { key: "phone", label: "電話", render: (r) => phoneLink(r.phone) },
      { key: "categoryText", label: "鑑定類別", render: (r) => escapeHtml(r.categoryText) },
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

  function rowToObj(row) {
    const o = {};
    state.fields.forEach((f, i) => (o[f] = row[i]));
    o.categoryList = o.categories ? o.categories.split(";").filter(Boolean) : [];
    return o;
  }

  function populateSelect(select, values, labelFn) {
    select.innerHTML = `<option value="">全部</option>`;
    values.forEach((v) => {
      const opt = document.createElement("option");
      opt.value = v;
      opt.textContent = labelFn ? labelFn(v) : v;
      select.appendChild(opt);
    });
  }

  function firstPhoneDigits(phone) {
    if (!phone) return "";
    return String(phone).replace(/[^\d+]/g, "");
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
      name: "115年臺南市身心障礙鑑定醫院",
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
    const category = els.category.value;
    const keyword = els.keyword.value.trim().toLowerCase();
    state.filtered = state.all.filter((r) => {
      if (district && r.district !== district) return false;
      if (category && !r.categoryList.includes(category)) return false;
      if (keyword) {
        const hay = `${r.name} ${r.address} ${r.categoryText}`.toLowerCase();
        if (!hay.includes(keyword)) return false;
      }
      return true;
    });
    renderAll();
  }

  function renderStats() {
    const rows = state.filtered;
    const districtCounts = {};
    let fullCount = 0;
    rows.forEach((r) => {
      if (r.district) districtCounts[r.district] = (districtCounts[r.district] || 0) + 1;
      if (r.categoryList.length >= 8) fullCount += 1;
    });
    els.statTotal.textContent = rows.length.toLocaleString();
    els.statDistricts.textContent = Object.keys(districtCounts).length;
    const top = Object.entries(districtCounts).sort((a, b) => b[1] - a[1])[0];
    els.statTop.textContent = top ? `${top[0]}（${top[1]}）` : "-";
    els.statFull.textContent = fullCount.toLocaleString();
  }

  function renderCharts() {
    const districtCounts = {};
    const categoryCounts = {};
    state.filtered.forEach((r) => {
      if (r.district) districtCounts[r.district] = (districtCounts[r.district] || 0) + 1;
      r.categoryList.forEach((c) => {
        categoryCounts[c] = (categoryCounts[c] || 0) + 1;
      });
    });
    const districtEntries = Object.entries(districtCounts).sort((a, b) => b[1] - a[1]);
    const categoryEntries = Object.keys(CATEGORY_LABELS).map((c) => [c, categoryCounts[c] || 0]);

    if (districtChart) districtChart.destroy();
    districtChart = new Chart(document.getElementById("chart-district"), {
      type: "bar",
      data: {
        labels: districtEntries.map((e) => e[0]),
        datasets: [{ data: districtEntries.map((e) => e[1]), backgroundColor: "#9d174d" }],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { ticks: { stepSize: 1 } } },
      },
    });

    if (categoryChart) categoryChart.destroy();
    categoryChart = new Chart(document.getElementById("chart-category"), {
      type: "bar",
      data: {
        labels: categoryEntries.map((e) => `第${e[0]}類`),
        datasets: [{ data: categoryEntries.map((e) => e[1]), backgroundColor: "#0f766e" }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { y: { ticks: { stepSize: 1 } } },
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
    const data = window.TN_DISABILITY_HOSPITALS_DATA;
    if (!data) {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：找不到內嵌資料 data/tn-disability-hospitals.js</div>`;
      return;
    }
    state.fields = data.fields;
    state.all = data.rows.map(rowToObj);

    const districts = Array.from(new Set(state.all.map((r) => r.district))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateSelect(els.district, districts);
    populateSelect(els.category, Object.keys(CATEGORY_LABELS), (v) => CATEGORY_LABELS[v]);

    els.metaUpdated.textContent = `資料筆數：${data.rows.length.toLocaleString()}`;
    applyFilters();
    injectItemListJsonLd(state.all);

    // meta.json 僅用於補上資料整理時間，非核心資料，失敗也不影響上方篩選/圖表/表格運作。
    fetch("../data/meta.json")
      .then((r) => r.json())
      .then((meta) => {
        if (meta.tnDisabilityHospitals) {
          els.metaUpdated.textContent = `資料筆數：${meta.tnDisabilityHospitals.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;
        }
      })
      .catch(() => {});
  }

  init();
})();
