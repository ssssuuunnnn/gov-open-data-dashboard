/* 嘉義市假牙補助合約醫療院所（中低收入／一般身分別）dashboard */
(function () {
  const state = { all: [], fields: [], filtered: [] };

  const els = {
    program: document.getElementById("f-program"),
    district: document.getElementById("f-district"),
    type: document.getElementById("f-type"),
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    statTotal: document.getElementById("stat-total"),
    statDistricts: document.getElementById("stat-districts"),
    statLowIncome: document.getElementById("stat-low-income"),
    statGeneral: document.getElementById("stat-general"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  const map = L.map("map", { preferCanvas: true }).setView([23.478, 120.449], 14);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);
  const clusterGroup = L.markerClusterGroup({ chunkedLoading: true, disableClusteringAtZoom: 17 });
  map.addLayer(clusterGroup);

  let districtChart, programChart;

  const TYPE_BADGE = { 醫院: "inst", 牙醫診所: "" };
  const PROGRAM_BADGE = { 中低收入: "nurse", 一般身分別: "" };

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 25,
    columns: [
      { key: "id", label: "編號" },
      {
        key: "program",
        label: "方案",
        render: (r) => `<span class="badge ${PROGRAM_BADGE[r.program] || ""}">${escapeHtml(r.program)}</span>`,
      },
      { key: "district", label: "行政區" },
      { key: "name", label: "機構名稱" },
      {
        key: "type",
        label: "機構類型",
        render: (r) => `<span class="badge ${TYPE_BADGE[r.type] || ""}">${escapeHtml(r.type)}</span>`,
      },
      { key: "address", label: "地址", render: (r) => addressLink(r.address) },
      { key: "phone", label: "電話", render: (r) => phoneLink(r.phone) },
      { key: "google_rating", label: "Google Map 星等", render: (r) => (r.google_rating ? `⭐ ${r.google_rating}` : "-") },
      { key: "google_review_count", label: "Google Map 評論數", render: (r) => googleReviewCell(r) },
    ],
    onRowClick: (row) => {
      if (row.lat && row.lng) {
        map.setView([row.lat, row.lng], 17);
      }
    },
  });

  // Google Map 評論數欄位：有 google_place_id 時做成可點擊連結直接連到該診所的 Google 地圖評論頁，
  // 沒有 place_id（一次性抓取時查無對照資料）則只顯示數字或「-」，不猜測連結。
  function googleReviewCell(r) {
    if (!r.google_review_count) return "-";
    const label = `${Number(r.google_review_count).toLocaleString()} 則`;
    if (!r.google_place_id) return label;
    const href = `https://search.google.com/local/reviews?placeid=${encodeURIComponent(r.google_place_id)}`;
    return `<a href="${href}" target="_blank" rel="noopener">${label}</a>`;
  }

  function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  // 電話欄位混雜「XXXX-XXXX」與「XXXXXXX#5786」分機兩種格式（分別來自中低收入 CSV 與一般身分別
  // PDF 兩個不同來源），轉成 tel: 連結時統一去除裝飾字元、分機以 ;ext= 表示，顯示文字保留原始格式。
  function phoneLink(phone) {
    if (!phone) return "";
    const m = phone.match(/^(.*?)(?:轉|#)(\d+)\s*$/);
    const main = m ? m[1] : phone;
    const ext = m ? m[2] : "";
    const digits = main.replace(/[^\d+]/g, "");
    if (!digits) return escapeHtml(phone);
    const href = ext ? `tel:${digits};ext=${ext}` : `tel:${digits}`;
    return `<a href="${href}">${escapeHtml(phone)}</a>`;
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
    const program = els.program.value;
    const district = els.district.value;
    const type = els.type.value;
    const keyword = els.keyword.value.trim().toLowerCase();
    state.filtered = state.all.filter((r) => {
      if (program && r.program !== program) return false;
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
    let lowIncomeCount = 0;
    let generalCount = 0;
    rows.forEach((r) => {
      districtCounts[r.district] = (districtCounts[r.district] || 0) + 1;
      if (r.program === "中低收入") lowIncomeCount += 1;
      if (r.program === "一般身分別") generalCount += 1;
    });
    els.statTotal.textContent = rows.length.toLocaleString();
    els.statDistricts.textContent = Object.keys(districtCounts).filter(Boolean).length;
    els.statLowIncome.textContent = lowIncomeCount.toLocaleString();
    els.statGeneral.textContent = generalCount.toLocaleString();
  }

  function renderMap() {
    clusterGroup.clearLayers();
    const markers = [];
    state.filtered.forEach((r) => {
      if (!r.lat || !r.lng) return; // 一般身分別方案來源 PDF 無座標，不會出現在地圖上
      const marker = L.circleMarker([r.lat, r.lng], {
        radius: 6,
        color: "#fff",
        weight: 1,
        fillColor: r.program === "中低收入" ? "#1f6f5c" : "#e07a2c",
        fillOpacity: 0.9,
      });
      marker.bindPopup(
        `<strong>${escapeHtml(r.name)}</strong>（${escapeHtml(r.program)}）<br/>${escapeHtml(r.address)}<br/>電話：${escapeHtml(r.phone || "-")}`
      );
      markers.push(marker);
    });
    clusterGroup.addLayers(markers);
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
        scales: { x: { ticks: { precision: 0 } } },
      },
    });

    const programCounts = {};
    state.filtered.forEach((r) => (programCounts[r.program] = (programCounts[r.program] || 0) + 1));
    const programEntries = Object.entries(programCounts).sort((a, b) => b[1] - a[1]);

    if (programChart) programChart.destroy();
    programChart = new Chart(document.getElementById("chart-program"), {
      type: "doughnut",
      data: {
        labels: programEntries.map((e) => e[0]),
        datasets: [{ data: programEntries.map((e) => e[1]), backgroundColor: ["#1f6f5c", "#e07a2c"] }],
      },
      options: { responsive: true, maintainAspectRatio: false },
    });
  }

  function renderAll() {
    renderStats();
    renderMap();
    renderCharts();
    table.setData(state.filtered);
  }

  els.program.addEventListener("change", applyFilters);
  els.district.addEventListener("change", applyFilters);
  els.type.addEventListener("change", applyFilters);
  els.keyword.addEventListener("input", debounce(applyFilters, 250));
  els.reset.addEventListener("click", () => {
    els.program.value = "";
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
    const data = window.CHIAYI_DENTURE_DATA;
    if (!data) {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：找不到內嵌資料 data/chiayi-denture.js</div>`;
      return;
    }
    state.fields = data.fields;
    state.all = data.rows.map(rowToObj);

    const programs = Array.from(new Set(state.all.map((r) => r.program))).filter(Boolean);
    populateSelect(els.program, programs);

    const districts = Array.from(new Set(state.all.map((r) => r.district))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateSelect(els.district, districts);

    const types = Array.from(new Set(state.all.map((r) => r.type))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateSelect(els.type, types);

    els.metaUpdated.textContent = `資料筆數：${data.rows.length.toLocaleString()}`;
    applyFilters();

    // meta.json 僅用於補上資料整理時間，非核心資料，失敗也不影響上方篩選/地圖/圖表/表格運作。
    fetch("../data/meta.json")
      .then((r) => r.json())
      .then((meta) => {
        if (meta.chiayiDenture) {
          els.metaUpdated.textContent = `資料筆數：${meta.chiayiDenture.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;
        }
      })
      .catch(() => {});
  }

  init();
})();
