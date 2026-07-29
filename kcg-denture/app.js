/* 115年高雄市免費裝假牙特約牙醫醫療院所 dashboard */
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

  let districtChart, typeChart;

  const TYPE_BADGE = {
    醫院: "inst",
    衛生所: "b",
    醫療站: "c",
    牙醫診所: "",
  };

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 25,
    columns: [
      { key: "id", label: "編號" },
      { key: "district", label: "行政區" },
      { key: "name", label: "機構名稱" },
      {
        key: "type",
        label: "機構類型",
        render: (r) => `<span class="badge ${TYPE_BADGE[r.type] || ""}">${escapeHtml(r.type)}</span>`,
      },
      { key: "address", label: "地址", render: (r) => addressLink(r.address, r.district) },
      { key: "phone", label: "電話", render: (r) => phoneLink(r.phone) },
    ],
  });

  function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  // 電話欄位少數含分機（如「#7003補綴科」）或以「及」「、」分隔多組分機，僅取最前面的數字部分轉為
  // tel: 連結，顯示文字保留原始格式。
  function phoneLink(phone) {
    if (!phone) return "";
    const main = phone.split(/[#及、]/)[0].trim();
    const digits = main.replace(/[^\d+]/g, "");
    if (!digits) return escapeHtml(phone);
    return `<a href="tel:${digits}">${escapeHtml(phone)}</a>`;
  }

  // 地址欄位缺少「高雄市」字首（僅「OO區＋路名門牌」），轉成 Google Maps 搜尋連結時需補上「高雄市」
  // 才能準確定位；顯示文字仍保留原始地址。
  function addressLink(address, district) {
    if (!address) return "";
    const full = address.startsWith("高雄市") ? address : `高雄市${address}`;
    const href = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(full)}`;
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
        const hay = `${r.name} ${r.address} ${r.phone}`.toLowerCase();
        if (!hay.includes(keyword)) return false;
      }
      return true;
    });
    renderAll();
  }

  function renderStats() {
    const rows = state.filtered;
    const districtCounts = {};
    let hospitalCount = 0;
    rows.forEach((r) => {
      districtCounts[r.district] = (districtCounts[r.district] || 0) + 1;
      if (r.type === "醫院") hospitalCount += 1;
    });
    els.statTotal.textContent = rows.length.toLocaleString();
    els.statDistricts.textContent = Object.keys(districtCounts).filter(Boolean).length;
    const top = Object.entries(districtCounts).filter(([k]) => k).sort((a, b) => b[1] - a[1])[0];
    els.statTop.textContent = top ? `${top[0]}（${top[1]}）` : "-";
    els.statHospital.textContent = hospitalCount.toLocaleString();
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

    const typeCounts = {};
    state.filtered.forEach((r) => (typeCounts[r.type] = (typeCounts[r.type] || 0) + 1));
    const typeEntries = Object.entries(typeCounts).sort((a, b) => b[1] - a[1]);

    if (typeChart) typeChart.destroy();
    typeChart = new Chart(document.getElementById("chart-type"), {
      type: "doughnut",
      data: {
        labels: typeEntries.map((e) => e[0]),
        datasets: [{ data: typeEntries.map((e) => e[1]), backgroundColor: ["#1f6f5c", "#e07a2c", "#3b6fd6", "#a855c9"] }],
      },
      options: { responsive: true, maintainAspectRatio: false },
    });
  }

  function renderAll() {
    renderStats();
    renderCharts();
    table.setData(state.filtered);
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

  function debounce(fn, ms) {
    let t;
    return (...args) => {
      clearTimeout(t);
      t = setTimeout(() => fn(...args), ms);
    };
  }

  function init() {
    const data = window.KCG_DENTURE_DATA;
    if (!data) {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：找不到內嵌資料 data/kcg-denture.js</div>`;
      return;
    }
    state.fields = data.fields;
    state.all = data.rows.map(rowToObj);

    const districts = Array.from(new Set(state.all.map((r) => r.district))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateSelect(els.district, districts);

    const types = Array.from(new Set(state.all.map((r) => r.type))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateSelect(els.type, types);

    els.metaUpdated.textContent = `資料筆數：${data.rows.length.toLocaleString()}`;
    applyFilters();

    // meta.json 僅用於補上資料整理時間，非核心資料，失敗也不影響上方篩選/圖表/表格運作。
    fetch("../data/meta.json")
      .then((r) => r.json())
      .then((meta) => {
        if (meta.kcgDenture) {
          els.metaUpdated.textContent = `資料筆數：${meta.kcgDenture.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;
        }
      })
      .catch(() => {});
  }

  init();
})();
