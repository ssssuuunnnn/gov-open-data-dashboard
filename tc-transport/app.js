/* 臺中市失能者交通接送服務 dashboard */
(function () {
  const state = { all: [], fields: [], filtered: [], allServiceAreas: [] };

  const els = {
    district: document.getElementById("f-district"),
    serviceArea: document.getElementById("f-service-area"),
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    statTotal: document.getElementById("stat-total"),
    statOrgDistricts: document.getElementById("stat-org-districts"),
    statServiceDistricts: document.getElementById("stat-service-districts"),
    statAllArea: document.getElementById("stat-all-area"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  const map = L.map("map", { preferCanvas: true }).setView([24.17, 120.72], 10);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);
  const clusterGroup = L.markerClusterGroup({ chunkedLoading: true, disableClusteringAtZoom: 16 });
  map.addLayer(clusterGroup);

  let serviceAreaChart, orgDistrictChart;

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 25,
    columns: [
      { key: "name", label: "辦理單位" },
      { key: "phone", label: "連絡電話", render: (r) => phoneLink(r.phone) },
      { key: "address", label: "地址", render: (r) => addressLink(r.address) },
      { key: "district", label: "所在行政區" },
      { key: "serviceAreas", label: "服務區域", render: (r) => escapeHtml((r.serviceAreas || []).join("、")) },
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

  // 電話欄位格式不一，混雜市話/手機並偶夾帶「分機」文字（如「(04)23950256分機15」），
  // 轉成 tel: 連結時去除裝飾字元，分機以 ;ext= 表示，顯示文字保留原始格式。
  function phoneLink(phone) {
    if (!phone) return "";
    const m = phone.match(/^(.*?)(?:分機|#)(\d+)\s*$/);
    const main = m ? m[1] : phone;
    const ext = m ? m[2] : "";
    const digits = main.replace(/[^\d+]/g, "");
    if (!digits) return escapeHtml(phone);
    const href = ext ? `tel:${digits};ext=${ext}` : `tel:${digits}`;
    return `<a href="${href}">${escapeHtml(phone)}</a>`;
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

  function populateServiceAreaCheckboxes(values) {
    els.serviceArea.innerHTML = "";
    values.forEach((v) => {
      const label = document.createElement("label");
      const input = document.createElement("input");
      input.type = "checkbox";
      input.value = v;
      input.addEventListener("change", applyFilters);
      label.appendChild(input);
      label.appendChild(document.createTextNode(" " + v));
      els.serviceArea.appendChild(label);
    });
  }

  function checkedServiceAreas() {
    return Array.from(els.serviceArea.querySelectorAll("input:checked")).map((cb) => cb.value);
  }

  function applyFilters() {
    const district = els.district.value;
    const keyword = els.keyword.value.trim().toLowerCase();
    const checkedAreas = checkedServiceAreas();
    state.filtered = state.all.filter((r) => {
      if (district && r.district !== district) return false;
      if (checkedAreas.length > 0) {
        const areas = r.serviceAreas || [];
        const matches = areas.includes("全區") || checkedAreas.some((a) => areas.includes(a));
        if (!matches) return false;
      }
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
    const orgDistrictSet = new Set();
    const serviceDistrictSet = new Set();
    let allAreaCount = 0;
    rows.forEach((r) => {
      if (r.district) orgDistrictSet.add(r.district);
      const areas = r.serviceAreas || [];
      if (areas.includes("全區")) {
        allAreaCount++;
        state.allServiceAreas.forEach((a) => serviceDistrictSet.add(a));
      } else {
        areas.forEach((a) => serviceDistrictSet.add(a));
      }
    });
    els.statTotal.textContent = rows.length.toLocaleString();
    els.statOrgDistricts.textContent = orgDistrictSet.size;
    els.statServiceDistricts.textContent = serviceDistrictSet.size;
    els.statAllArea.textContent = allAreaCount.toLocaleString();
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
        fillColor: "#1f6f5c",
        fillOpacity: 0.9,
      });
      marker.bindPopup(
        `<strong>${escapeHtml(r.name)}</strong><br/>${escapeHtml(r.address)}<br/>電話：${escapeHtml(r.phone || "-")}<br/>服務區域：${escapeHtml((r.serviceAreas || []).join("、") || "-")}`
      );
      markers.push(marker);
    });
    clusterGroup.addLayers(markers);
  }

  function renderCharts() {
    const serviceAreaCounts = {};
    state.filtered.forEach((r) => {
      const areas = r.serviceAreas || [];
      const expanded = areas.includes("全區") ? state.allServiceAreas : areas;
      expanded.forEach((a) => (serviceAreaCounts[a] = (serviceAreaCounts[a] || 0) + 1));
    });
    const serviceAreaEntries = Object.entries(serviceAreaCounts).sort((a, b) => b[1] - a[1]);

    if (serviceAreaChart) serviceAreaChart.destroy();
    serviceAreaChart = new Chart(document.getElementById("chart-service-area"), {
      type: "bar",
      data: {
        labels: serviceAreaEntries.map((e) => e[0]),
        datasets: [{ data: serviceAreaEntries.map((e) => e[1]), backgroundColor: "#1f6f5c" }],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
      },
    });

    const orgDistrictCounts = {};
    state.filtered.forEach((r) => {
      const label = r.district || "未標示";
      orgDistrictCounts[label] = (orgDistrictCounts[label] || 0) + 1;
    });
    const orgDistrictEntries = Object.entries(orgDistrictCounts).sort((a, b) => b[1] - a[1]);

    if (orgDistrictChart) orgDistrictChart.destroy();
    orgDistrictChart = new Chart(document.getElementById("chart-org-district"), {
      type: "doughnut",
      data: {
        labels: orgDistrictEntries.map((e) => e[0]),
        datasets: [{
          data: orgDistrictEntries.map((e) => e[1]),
          backgroundColor: ["#1f6f5c", "#e07a2c", "#2563eb", "#a855f7", "#dc2626", "#0891b2", "#65a30d", "#d97706"],
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
  els.keyword.addEventListener("input", debounce(applyFilters, 250));
  els.reset.addEventListener("click", () => {
    els.district.value = "";
    els.keyword.value = "";
    els.serviceArea.querySelectorAll("input:checked").forEach((cb) => (cb.checked = false));
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
    const data = window.TC_TRANSPORT_DATA;
    if (!data) {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：找不到內嵌資料 data/tc-transport.js</div>`;
      return;
    }
    state.fields = data.fields;
    state.all = data.rows.map(rowToObj);

    const districts = Array.from(new Set(state.all.map((r) => r.district))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateSelect(els.district, districts);

    const areaSet = new Set();
    state.all.forEach((r) => (r.serviceAreas || []).forEach((a) => { if (a !== "全區") areaSet.add(a); }));
    state.allServiceAreas = Array.from(areaSet).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateServiceAreaCheckboxes(state.allServiceAreas);

    els.metaUpdated.textContent = `資料筆數：${data.rows.length.toLocaleString()}`;
    applyFilters();

    // meta.json 僅用於補上資料整理時間，非核心資料，失敗也不影響上方篩選/圖表/表格運作。
    fetch("../data/meta.json")
      .then((r) => r.json())
      .then((meta) => {
        if (meta.tcTransport) {
          els.metaUpdated.textContent = `資料筆數：${meta.tcTransport.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;
        }
      })
      .catch(() => {});
  }

  init();
})();
