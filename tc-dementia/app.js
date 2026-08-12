/* 臺中市失智症服務及資源提供單位 dashboard */
(function () {
  const state = { all: [], fields: [], filtered: [] };

  const els = {
    district: document.getElementById("f-district"),
    type: document.getElementById("f-type"),
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    statTotal: document.getElementById("stat-total"),
    statDistricts: document.getElementById("stat-districts"),
    statCoop: document.getElementById("stat-coop"),
    statCommunity: document.getElementById("stat-community"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  const TYPE_BADGE = {
    "失智共同照護中心": "coop",
    "失智社區服務據點": "community",
  };
  const TYPE_COLOR = {
    "失智共同照護中心": "#2563eb",
    "失智社區服務據點": "#16a34a",
  };

  const map = L.map("map", { preferCanvas: true }).setView([24.17, 120.72], 10);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);
  const clusterGroup = L.markerClusterGroup({ chunkedLoading: true, disableClusteringAtZoom: 16 });
  map.addLayer(clusterGroup);

  let districtChart, typeChart;

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 25,
    columns: [
      { key: "name", label: "辦理單位" },
      { key: "type", label: "服務類型", render: (r) => typeBadge(r.type) },
      { key: "district", label: "行政區" },
      { key: "address", label: "地址", render: (r) => addressLink(r.address) },
      { key: "phone", label: "連絡電話", render: (r) => phoneLink(r.phone) },
      { key: "email", label: "電子郵件", render: (r) => emailLink(r.email) },
    ],
    onRowClick: (row) => {
      if (row.lat && row.lng) {
        map.setView([row.lat, row.lng], 16);
      }
    },
  });

  function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  function typeBadge(type) {
    const cls = TYPE_BADGE[type] || "";
    return `<span class="badge ${cls}">${escapeHtml(type || "-")}</span>`;
  }

  // 電話欄位格式不一，混雜市話/手機，轉成 tel: 連結時去除裝飾字元，顯示文字保留原始格式。
  function phoneLink(phone) {
    if (!phone) return "";
    const digits = phone.replace(/[^\d+]/g, "");
    if (!digits) return escapeHtml(phone);
    return `<a href="tel:${digits}">${escapeHtml(phone)}</a>`;
  }

  function emailLink(email) {
    if (!email) return "";
    return `<a href="mailto:${escapeHtml(email)}">${escapeHtml(email)}</a>`;
  }

  // 地址欄位轉成 Google Maps 搜尋連結，點選開新分頁瀏覽該地址位置。
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
    const type = els.type.value;
    const keyword = els.keyword.value.trim().toLowerCase();
    state.filtered = state.all.filter((r) => {
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
    const districtSet = new Set();
    let coopCount = 0;
    let communityCount = 0;
    rows.forEach((r) => {
      if (r.district) districtSet.add(r.district);
      if (r.type === "失智共同照護中心") coopCount++;
      else if (r.type === "失智社區服務據點") communityCount++;
    });
    els.statTotal.textContent = rows.length.toLocaleString();
    els.statDistricts.textContent = districtSet.size;
    els.statCoop.textContent = coopCount.toLocaleString();
    els.statCommunity.textContent = communityCount.toLocaleString();
  }

  function renderMap() {
    clusterGroup.clearLayers();
    const markers = [];
    state.filtered.forEach((r) => {
      if (!r.lat || !r.lng) return;
      const marker = L.circleMarker([r.lat, r.lng], {
        radius: 6,
        color: "#fff",
        weight: 1,
        fillColor: TYPE_COLOR[r.type] || "#1f6f5c",
        fillOpacity: 0.9,
      });
      marker.bindPopup(
        `<strong>${escapeHtml(r.name)}</strong><br/>${escapeHtml(r.type || "-")}<br/>${escapeHtml(r.address)}<br/>電話：${escapeHtml(r.phone || "-")}`
      );
      markers.push(marker);
    });
    clusterGroup.addLayers(markers);
  }

  function renderCharts() {
    const districtCounts = {};
    state.filtered.forEach((r) => {
      const label = r.district || "未標示";
      districtCounts[label] = (districtCounts[label] || 0) + 1;
    });
    const districtEntries = Object.entries(districtCounts).sort((a, b) => b[1] - a[1]);

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
        datasets: [{
          data: typeEntries.map((e) => e[1]),
          backgroundColor: typeEntries.map((e) => TYPE_COLOR[e[0]] || "#94a3b8"),
        }],
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
    const data = window.TC_DEMENTIA_DATA;
    if (!data) {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：找不到內嵌資料 data/tc-dementia.js</div>`;
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
        if (meta.tcDementia) {
          els.metaUpdated.textContent = `資料筆數：${meta.tcDementia.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;
        }
      })
      .catch(() => {});
  }

  init();
})();
