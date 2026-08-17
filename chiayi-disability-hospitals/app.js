/* 嘉義市身心障礙鑑定醫院 dashboard */
(function () {
  const state = { all: [], fields: [], filtered: [] };

  const CATEGORY_ORDER = ["1", "2", "3", "4", "5", "6", "7", "8", "dev"];
  let categoryLabels = {};

  const els = {
    category: document.getElementById("f-category"),
    hospital: document.getElementById("f-hospital"),
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    statTotal: document.getElementById("stat-total"),
    statFull: document.getElementById("stat-full"),
    statCategories: document.getElementById("stat-categories"),
    statDev: document.getElementById("stat-dev"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  let categoryChart, hospitalChart;

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 25,
    columns: [
      { key: "name", label: "醫院名稱" },
      { key: "district", label: "行政區" },
      { key: "address", label: "地址", render: (r) => addressLink(r.address) },
      { key: "phone", label: "電話", render: (r) => phoneLink(r.phone) },
      { key: "categories", label: "可辦理鑑定類別", render: (r) => renderCategoryBadges(r) },
      { key: "itemCount", label: "鑑定向度明細", render: (r) => renderItemDetails(r) },
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

  function categoryShortLabel(key) {
    if (key === "dev") return "發展遲緩";
    return `第${key}類`;
  }

  function renderCategoryBadges(r) {
    return r.categoryList
      .map((k) => `<span class="badge ${k === "dev" ? "c" : "b"}">${escapeHtml(categoryShortLabel(k))}</span>`)
      .join(" ");
  }

  function renderItemDetails(r) {
    const blocks = r.categoryList
      .map((k) => {
        const entry = r.itemsByCategory[k];
        if (!entry) return "";
        const items = (entry.items || []).map((it) => `<li>${escapeHtml(it)}</li>`).join("");
        return `<p style="margin:6px 0 2px;font-weight:bold;">${escapeHtml(entry.label || categoryShortLabel(k))}</p><ul style="margin:0 0 4px;padding-left:1.2em;">${items}</ul>`;
      })
      .join("");
    return `<details><summary>共 ${r.itemCount} 項向度，點此展開明細</summary>${blocks}</details>`;
  }

  function rowToObj(row) {
    const o = {};
    state.fields.forEach((f, i) => (o[f] = row[i]));
    o.categoryList = o.categories ? o.categories.split(";").filter(Boolean) : [];
    o.itemsByCategory = o.itemsByCategory ? JSON.parse(o.itemsByCategory) : {};
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
      name: "嘉義市身心障礙鑑定醫院",
      numberOfItems: rows.length,
      itemListElement,
    };
    const script = document.createElement("script");
    script.type = "application/ld+json";
    script.textContent = JSON.stringify(jsonLd);
    document.head.appendChild(script);
  }

  function applyFilters() {
    const category = els.category.value;
    const hospital = els.hospital.value;
    const keyword = els.keyword.value.trim().toLowerCase();
    state.filtered = state.all.filter((r) => {
      if (category && !r.categoryList.includes(category)) return false;
      if (hospital && r.name !== hospital) return false;
      if (keyword) {
        const detailText = Object.values(r.itemsByCategory)
          .map((c) => (c.items || []).join(" "))
          .join(" ");
        const hay = `${r.name} ${r.address} ${detailText}`.toLowerCase();
        if (!hay.includes(keyword)) return false;
      }
      return true;
    });
    renderAll();
  }

  function renderStats() {
    const rows = state.filtered;
    let fullCount = 0;
    let devCount = 0;
    const categorySet = new Set();
    rows.forEach((r) => {
      const numericCats = r.categoryList.filter((c) => c !== "dev");
      if (numericCats.length >= 8) fullCount += 1;
      if (r.categoryList.includes("dev")) devCount += 1;
      numericCats.forEach((c) => categorySet.add(c));
    });
    els.statTotal.textContent = rows.length.toLocaleString();
    els.statFull.textContent = fullCount.toLocaleString();
    els.statCategories.textContent = categorySet.size;
    els.statDev.textContent = devCount.toLocaleString();
  }

  function renderCharts() {
    const categoryCounts = {};
    CATEGORY_ORDER.forEach((k) => (categoryCounts[k] = 0));
    state.filtered.forEach((r) => {
      r.categoryList.forEach((k) => {
        categoryCounts[k] = (categoryCounts[k] || 0) + 1;
      });
    });

    if (categoryChart) categoryChart.destroy();
    categoryChart = new Chart(document.getElementById("chart-category"), {
      type: "bar",
      data: {
        labels: CATEGORY_ORDER.map((k) => categoryShortLabel(k)),
        datasets: [{ data: CATEGORY_ORDER.map((k) => categoryCounts[k] || 0), backgroundColor: "#9d174d" }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { y: { ticks: { stepSize: 1 } } },
      },
    });

    const hospitalEntries = state.filtered
      .map((r) => [r.name, r.itemCount])
      .sort((a, b) => b[1] - a[1]);

    if (hospitalChart) hospitalChart.destroy();
    hospitalChart = new Chart(document.getElementById("chart-hospital"), {
      type: "bar",
      data: {
        labels: hospitalEntries.map((e) => e[0]),
        datasets: [{ data: hospitalEntries.map((e) => e[1]), backgroundColor: "#0f766e" }],
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

  els.category.addEventListener("change", applyFilters);
  els.hospital.addEventListener("change", applyFilters);
  els.keyword.addEventListener("input", debounce(applyFilters, 250));
  els.reset.addEventListener("click", () => {
    els.category.value = "";
    els.hospital.value = "";
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
    const data = window.CHIAYI_DISABILITY_HOSPITALS_DATA;
    if (!data) {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：找不到內嵌資料 data/chiayi-disability-hospitals.js</div>`;
      return;
    }
    state.fields = data.fields;
    categoryLabels = data.categoryLabels || {};
    state.all = data.rows.map(rowToObj);

    populateSelect(els.category, CATEGORY_ORDER, (v) => categoryLabels[v] || categoryShortLabel(v));
    populateSelect(
      els.hospital,
      state.all.map((r) => r.name),
    );

    els.metaUpdated.textContent = `資料筆數：${data.rows.length.toLocaleString()} 家醫院`;
    applyFilters();
    injectItemListJsonLd(state.all);

    // meta.json 僅用於補上資料整理時間，非核心資料，失敗也不影響上方篩選/圖表/表格運作。
    fetch("../data/meta.json")
      .then((r) => r.json())
      .then((meta) => {
        if (meta.chiayiDisabilityHospitals) {
          els.metaUpdated.textContent = `資料筆數：${meta.chiayiDisabilityHospitals.count.toLocaleString()} 家醫院　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;
        }
      })
      .catch(() => {});
  }

  init();
})();
