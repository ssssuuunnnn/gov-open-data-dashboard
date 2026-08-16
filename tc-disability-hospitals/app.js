/* 臺中市身心障礙鑑定醫院及鑑定類別窗口 dashboard */
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
    level: document.getElementById("f-level"),
    category: document.getElementById("f-category"),
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    statTotal: document.getElementById("stat-total"),
    statLevels: document.getElementById("stat-levels"),
    statTop: document.getElementById("stat-top"),
    statFull: document.getElementById("stat-full"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  let levelChart, categoryChart;

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 25,
    columns: [
      { key: "level", label: "醫院層級" },
      { key: "name", label: "醫院名稱", render: (r) => escapeHtml(r.name) },
      { key: "generalContact", label: "一般鑑定窗口", render: (r) => escapeHtml(r.generalContact) },
      { key: "homeContact", label: "居家鑑定窗口", render: (r) => escapeHtml(r.homeContact) },
      { key: "phone", label: "聯絡電話", render: (r) => phoneLink(r.phone) },
      { key: "categoryList", label: "可辦理類別", render: (r) => categoryBadges(r.categoryList) },
    ],
  });

  function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  function phoneLink(phone) {
    if (!phone) return "";
    // 電話欄位可能含多組號碼（以「、」分隔），僅取第一組號碼供 tel: 連結使用，顯示文字保留原文。
    const first = String(phone).split("、")[0];
    const digits = first.replace(/[^\d+]/g, "");
    if (!digits) return escapeHtml(phone);
    return `<a href="tel:${digits}">${escapeHtml(phone)}</a>`;
  }

  function categoryBadges(list) {
    if (!list || !list.length) return `<span style="color:var(--color-muted);">無提供</span>`;
    return list.map((c) => `<span class="badge cap">第${escapeHtml(c)}類</span>`).join(" ");
  }

  function rowToObj(row) {
    const o = {};
    state.fields.forEach((f, i) => (o[f] = row[i]));
    o.categoryList = Object.keys(CATEGORY_LABELS).filter((c) => o[`cat${c}`] === 1);
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
    return String(phone).split("、")[0].replace(/[^\d+]/g, "");
  }

  // 動態插入 ItemList 結構化資料（列出全部醫院），供搜尋引擎理解本頁機構名單內容；因資料以 JS
  // 內嵌方式載入，改於資料載入完成後插入 <head>，主流搜尋引擎爬蟲會執行 JS 後再擷取結構化資料。
  function injectItemListJsonLd(rows) {
    const itemListElement = rows.map((r, i) => {
      const item = { "@type": "Hospital", name: r.name };
      const telephone = firstPhoneDigits(r.phone);
      if (telephone) item.telephone = telephone;
      return { "@type": "ListItem", position: i + 1, item };
    });
    const jsonLd = {
      "@context": "https://schema.org",
      "@type": "ItemList",
      name: "臺中市身心障礙鑑定醫院",
      numberOfItems: rows.length,
      itemListElement,
    };
    const script = document.createElement("script");
    script.type = "application/ld+json";
    script.textContent = JSON.stringify(jsonLd);
    document.head.appendChild(script);
  }

  function applyFilters() {
    const level = els.level.value;
    const category = els.category.value;
    const keyword = els.keyword.value.trim().toLowerCase();
    state.filtered = state.all.filter((r) => {
      if (level && r.level !== level) return false;
      if (category && !r.categoryList.includes(category)) return false;
      if (keyword) {
        const hay = `${r.name} ${r.generalContact} ${r.homeContact}`.toLowerCase();
        if (!hay.includes(keyword)) return false;
      }
      return true;
    });
    renderAll();
  }

  function renderStats() {
    const rows = state.filtered;
    const levelCounts = {};
    let fullCount = 0;
    rows.forEach((r) => {
      if (r.level) levelCounts[r.level] = (levelCounts[r.level] || 0) + 1;
      if (r.categoryList.length >= 8) fullCount += 1;
    });
    els.statTotal.textContent = rows.length.toLocaleString();
    els.statLevels.textContent = Object.keys(levelCounts).length;
    const top = Object.entries(levelCounts).sort((a, b) => b[1] - a[1])[0];
    els.statTop.textContent = top ? `${top[0]}（${top[1]}）` : "-";
    els.statFull.textContent = fullCount.toLocaleString();
  }

  function renderCharts() {
    const levelCounts = {};
    const categoryCounts = {};
    state.filtered.forEach((r) => {
      if (r.level) levelCounts[r.level] = (levelCounts[r.level] || 0) + 1;
      r.categoryList.forEach((c) => {
        categoryCounts[c] = (categoryCounts[c] || 0) + 1;
      });
    });
    // 依醫院層級固定順序顯示（醫學中心 > 區域醫院 > 地區醫院），而非依數量排序。
    const levelOrder = ["醫學中心", "區域醫院", "地區醫院"];
    const levelEntries = levelOrder
      .filter((l) => levelCounts[l])
      .map((l) => [l, levelCounts[l]])
      .concat(Object.entries(levelCounts).filter(([l]) => !levelOrder.includes(l)));
    const categoryEntries = Object.keys(CATEGORY_LABELS).map((c) => [c, categoryCounts[c] || 0]);

    if (levelChart) levelChart.destroy();
    levelChart = new Chart(document.getElementById("chart-level"), {
      type: "doughnut",
      data: {
        labels: levelEntries.map((e) => e[0]),
        datasets: [{ data: levelEntries.map((e) => e[1]), backgroundColor: ["#9d174d", "#0f766e", "#b45309"] }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: "bottom" } },
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

  els.level.addEventListener("change", applyFilters);
  els.category.addEventListener("change", applyFilters);
  els.keyword.addEventListener("input", debounce(applyFilters, 250));
  els.reset.addEventListener("click", () => {
    els.level.value = "";
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
    const data = window.TC_DISABILITY_HOSPITALS_DATA;
    if (!data) {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：找不到內嵌資料 data/tc-disability-hospitals.js</div>`;
      return;
    }
    state.fields = data.fields;
    state.all = data.rows.map(rowToObj);

    const levelOrder = ["醫學中心", "區域醫院", "地區醫院"];
    const levels = Array.from(new Set(state.all.map((r) => r.level))).filter(Boolean);
    levels.sort((a, b) => levelOrder.indexOf(a) - levelOrder.indexOf(b));
    populateSelect(els.level, levels);
    populateSelect(els.category, Object.keys(CATEGORY_LABELS), (v) => CATEGORY_LABELS[v]);

    els.metaUpdated.textContent = `資料筆數：${data.rows.length.toLocaleString()}`;
    applyFilters();
    injectItemListJsonLd(state.all);

    // meta.json 僅用於補上資料整理時間，非核心資料，失敗也不影響上方篩選/圖表/表格運作。
    fetch("../data/meta.json")
      .then((r) => r.json())
      .then((meta) => {
        if (meta.tcDisabilityHospitals) {
          els.metaUpdated.textContent = `資料筆數：${meta.tcDisabilityHospitals.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;
        }
      })
      .catch(() => {});
  }

  init();
})();
