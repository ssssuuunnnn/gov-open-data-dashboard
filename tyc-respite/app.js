/* 桃園市喘息服務提供單位 dashboard */
(function () {
  const state = { all: [], fields: [], filtered: [] };

  const els = {
    category: document.getElementById("f-category"),
    district: document.getElementById("f-district"),
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    statTotal: document.getElementById("stat-total"),
    statInstitutions: document.getElementById("stat-institutions"),
    statDistricts: document.getElementById("stat-districts"),
    statCategories: document.getElementById("stat-categories"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  let categoryChart, districtChart;

  const CATEGORY_BADGE = {
    "居家喘息": "a",
    "機構喘息": "b",
  };

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 25,
    columns: [
      {
        key: "category",
        label: "服務類別",
        render: (r) => `<span class="badge ${CATEGORY_BADGE[r.category] || ""}">${escapeHtml(r.category)}</span>`,
      },
      { key: "name", label: "單位名稱" },
      { key: "contact", label: "負責人", render: (r) => escapeHtml(r.contact) },
      { key: "phone", label: "電話", render: (r) => phoneLink(r.phone) },
      { key: "fax", label: "傳真", render: (r) => escapeHtml(r.fax) },
      { key: "email", label: "電子郵件", render: (r) => escapeHtml(r.email) },
      { key: "district", label: "行政區" },
      { key: "service_area", label: "服務區域", render: (r) => escapeHtml(r.service_area) },
      { key: "address", label: "地址", render: (r) => addressLink(r.address) },
    ],
  });

  function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  // 電話欄位少數夾帶「分機」文字，僅取主號碼轉為 tel: 連結，顯示文字保留原始格式。
  function phoneLink(phone) {
    if (!phone) return "";
    const main = phone.split(/[、/]/)[0].trim();
    const digits = main.replace(/[^\d+]/g, "");
    if (!digits) return escapeHtml(phone);
    return `<a href="tel:${digits}">${escapeHtml(phone)}</a>`;
  }

  // 地址已含完整「桃園市OO區」（或其他縣市）字首，可直接轉成 Google Maps 搜尋連結。
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
    const category = els.category.value;
    const district = els.district.value;
    const keyword = els.keyword.value.trim().toLowerCase();
    state.filtered = state.all.filter((r) => {
      if (category && r.category !== category) return false;
      // 行政區篩選同時比對單位地址所在區與「服務區域」欄位是否涵蓋所選行政區
      if (district && r.district !== district && !(r.service_area || "").includes(district)) return false;
      if (keyword) {
        const hay = `${r.name} ${r.address} ${r.phone} ${r.service_area}`.toLowerCase();
        if (!hay.includes(keyword)) return false;
      }
      return true;
    });
    renderAll();
  }

  function renderStats() {
    const rows = state.filtered;
    const institutions = new Set(rows.map((r) => r.name).filter(Boolean));
    const districts = new Set(rows.map((r) => r.district).filter(Boolean));
    const categories = new Set(rows.map((r) => r.category).filter(Boolean));
    els.statTotal.textContent = rows.length.toLocaleString();
    els.statInstitutions.textContent = institutions.size.toLocaleString();
    els.statDistricts.textContent = districts.size;
    els.statCategories.textContent = categories.size;
  }

  function renderCharts() {
    const categoryCounts = {};
    state.filtered.forEach((r) => (categoryCounts[r.category] = (categoryCounts[r.category] || 0) + 1));
    const categoryEntries = Object.entries(categoryCounts).sort((a, b) => b[1] - a[1]);

    if (categoryChart) categoryChart.destroy();
    categoryChart = new Chart(document.getElementById("chart-category"), {
      type: "doughnut",
      data: {
        labels: categoryEntries.map((e) => e[0]),
        datasets: [{ data: categoryEntries.map((e) => e[1]), backgroundColor: ["#1f6f5c", "#e07a2c"] }],
      },
      options: { responsive: true, maintainAspectRatio: false },
    });

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

  els.category.addEventListener("change", applyFilters);
  els.district.addEventListener("change", applyFilters);
  els.keyword.addEventListener("input", debounce(applyFilters, 250));
  els.reset.addEventListener("click", () => {
    els.category.value = "";
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
    const data = window.TYC_RESPITE_DATA;
    if (!data) {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：找不到內嵌資料 data/tyc-respite.js</div>`;
      return;
    }
    state.fields = data.fields;
    state.all = data.rows.map(rowToObj);

    const categories = Array.from(new Set(state.all.map((r) => r.category))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateSelect(els.category, categories);

    const districts = Array.from(new Set(state.all.map((r) => r.district))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateSelect(els.district, districts);

    els.metaUpdated.textContent = `資料筆數：${data.rows.length.toLocaleString()}`;
    applyFilters();

    // meta.json 僅用於補上資料整理時間，非核心資料，失敗也不影響上方篩選/圖表/表格運作。
    fetch("../data/meta.json")
      .then((r) => r.json())
      .then((meta) => {
        if (meta.tycRespite) {
          els.metaUpdated.textContent = `資料筆數：${meta.tycRespite.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;
        }
      })
      .catch(() => {});
  }

  init();
})();
