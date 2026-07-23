/* 桃園市失能老人接受長期照顧機構服務暨老人保護安置機構名冊 dashboard */
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
    statOutside: document.getElementById("stat-outside"),
    statTop: document.getElementById("stat-top"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  let countyChart, typeChart;

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 25,
    columns: [
      { key: "name", label: "機構名稱" },
      { key: "type", label: "機構類型（解析）" },
      { key: "county", label: "縣市" },
      { key: "district", label: "鄉鎮市區" },
      { key: "address", label: "地址", render: (r) => addressLink(r.address) },
      { key: "phone", label: "電話", render: (r) => phoneLink(r.phone) },
    ],
  });

  function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  // 電話欄位可能含「分機」「#」裝飾字元與聯絡人姓名（如「03-8886141#1153葉小姐」），
  // 逐段轉成 tel: 連結，無法辨識數字的片段維持原文顯示。
  function phoneLink(phone) {
    if (!phone) return "";
    return String(phone)
      .split(" / ")
      .map((seg) => singlePhoneLink(seg.trim()))
      .join(" / ");
  }

  function singlePhoneLink(seg) {
    if (!seg) return "";
    const m = seg.match(/^([\d\-() ]+)(?:分機|#)(\d+)/);
    const main = m ? m[1] : seg;
    const ext = m ? m[2] : "";
    const digits = main.replace(/[^\d+]/g, "");
    if (!digits) return escapeHtml(seg);
    const href = ext ? `tel:${digits};ext=${ext}` : `tel:${digits}`;
    return `<a href="${href}">${escapeHtml(seg)}</a>`;
  }

  // 地址轉成 Google Maps 搜尋連結；因部分機構地址位於桃園市以外縣市，一律用完整地址文字
  // 搜尋，不假設座標範圍。第92筆地址含跨行兩段地址，換行以空白取代後仍可正確搜尋。
  function addressLink(address) {
    if (!address) return "";
    const query = String(address).replace(/\n/g, " ");
    const href = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(query)}`;
    return `<a href="${href}" target="_blank" rel="noopener">${escapeHtml(address)}</a>`;
  }

  function rowToObj(row) {
    const o = {};
    state.fields.forEach((f, i) => (o[f] = row[i]));
    return o;
  }

  // 取電話欄位第一段的純數字（去除分機/#/聯絡人姓名），供結構化資料 telephone 屬性使用。
  function firstPhoneDigits(phone) {
    if (!phone) return "";
    const seg = String(phone).split(" / ")[0].trim();
    const m = seg.match(/^([\d\-() ]+)(?:分機|#)(\d+)/);
    const main = m ? m[1] : seg;
    return main.replace(/[^\d+]/g, "");
  }

  // 動態插入 ItemList 結構化資料（列出全部機構的 LocalBusiness 項目），供搜尋引擎理解本頁
  // 大量機構名冊內容、有機會呈現 Rich Results；因資料以 JS 內嵌方式載入，無法於靜態 HTML
  // 產生，改於資料載入完成後插入 <head>，主流搜尋引擎爬蟲會執行 JS 後再擷取結構化資料。
  function injectItemListJsonLd(rows) {
    const itemListElement = rows.map((r, i) => {
      const item = { "@type": "LocalBusiness", name: r.name };
      if (r.address) item.address = String(r.address).replace(/\n/g, " ");
      const telephone = firstPhoneDigits(r.phone);
      if (telephone) item.telephone = telephone;
      if (r.type) item.additionalType = r.type;
      return { "@type": "ListItem", position: i + 1, item };
    });
    const jsonLd = {
      "@context": "https://schema.org",
      "@type": "ItemList",
      name: "桃園市失能老人接受長期照顧機構服務暨老人保護安置機構名冊",
      numberOfItems: rows.length,
      itemListElement,
    };
    const script = document.createElement("script");
    script.type = "application/ld+json";
    script.textContent = JSON.stringify(jsonLd);
    document.head.appendChild(script);
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
        const hay = `${r.name} ${r.address}`.toLowerCase();
        if (!hay.includes(keyword)) return false;
      }
      return true;
    });
    renderAll();
  }

  function renderStats() {
    const rows = state.filtered;
    const countyCounts = {};
    let outside = 0;
    rows.forEach((r) => {
      if (r.county) countyCounts[r.county] = (countyCounts[r.county] || 0) + 1;
      if (r.county && r.county !== "桃園市") outside += 1;
    });
    els.statTotal.textContent = rows.length.toLocaleString();
    els.statCounties.textContent = Object.keys(countyCounts).length;
    els.statOutside.textContent = outside.toLocaleString();
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
      const label = r.type || "未標示";
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
    const data = window.TYC_PLACEMENT_DATA;
    if (!data) {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：找不到內嵌資料 data/tyc-placement.js</div>`;
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
    injectItemListJsonLd(state.all);

    // meta.json 僅用於補上資料整理時間，非核心資料，失敗也不影響上方篩選/圖表/表格運作。
    fetch("../data/meta.json")
      .then((r) => r.json())
      .then((meta) => {
        if (meta.tycPlacement) {
          els.metaUpdated.textContent = `資料筆數：${meta.tycPlacement.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;
        }
      })
      .catch(() => {});
  }

  init();
})();
