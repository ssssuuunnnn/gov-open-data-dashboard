/* 嘉義市長照交通接送服務 dashboard */
(function () {
  const state = { all: [], fields: [], filtered: [] };

  const els = {
    district: document.getElementById("f-district"),
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    statTotal: document.getElementById("stat-total"),
    statDistricts: document.getElementById("stat-districts"),
    statSaturday: document.getElementById("stat-saturday"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  const map = L.map("map", { preferCanvas: true }).setView([23.478, 120.449], 13);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);
  // 資料筆數少（僅4筆），不需 markercluster 分群，直接用 layerGroup 管理標記。
  const markerLayer = L.layerGroup().addTo(map);

  let districtChart, saturdayChart;

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 25,
    columns: [
      { key: "category", label: "類別" },
      { key: "name", label: "名稱" },
      { key: "phone", label: "電話", render: (r) => phoneLink(r.phone) },
      { key: "contact", label: "聯絡人" },
      { key: "address", label: "地址", render: (r) => addressLink(r.address) },
      { key: "officeHours", label: "辦公室服務時間" },
      { key: "driverHours", label: "司機服務時間" },
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

  function phoneLink(phone) {
    if (!phone) return "";
    const digits = phone.replace(/[^\d+]/g, "");
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
    const keyword = els.keyword.value.trim().toLowerCase();
    state.filtered = state.all.filter((r) => {
      if (district && r.district !== district) return false;
      if (keyword) {
        const hay = `${r.name} ${r.address} ${r.phone} ${r.contact}`.toLowerCase();
        if (!hay.includes(keyword)) return false;
      }
      return true;
    });
    renderAll();
  }

  function renderStats() {
    const rows = state.filtered;
    const districts = new Set();
    let saturdayCount = 0;
    rows.forEach((r) => {
      if (r.district) districts.add(r.district);
      if (r.driverHours && r.driverHours.includes("週六")) saturdayCount += 1;
    });
    els.statTotal.textContent = rows.length.toLocaleString();
    els.statDistricts.textContent = districts.size;
    els.statSaturday.textContent = saturdayCount.toLocaleString();
  }

  function renderMap() {
    markerLayer.clearLayers();
    state.filtered.forEach((r) => {
      if (!r.lat || !r.lng) return;
      const marker = L.circleMarker([r.lat, r.lng], {
        radius: 8,
        color: "#fff",
        weight: 1,
        fillColor: "#1f6f5c",
        fillOpacity: 0.9,
      });
      marker.bindPopup(
        `<strong>${escapeHtml(r.name)}</strong><br/>${escapeHtml(r.address)}<br/>電話：${escapeHtml(r.phone || "-")}<br/>聯絡人：${escapeHtml(r.contact || "-")}`
      );
      marker.addTo(markerLayer);
    });
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
      type: "doughnut",
      data: {
        labels: districtEntries.map((e) => e[0]),
        datasets: [{ data: districtEntries.map((e) => e[1]), backgroundColor: ["#1f6f5c", "#e07a2c", "#3b6fa0"] }],
      },
      options: { responsive: true, maintainAspectRatio: false },
    });

    let saturdayCount = 0;
    let otherCount = 0;
    state.filtered.forEach((r) => {
      if (r.driverHours && r.driverHours.includes("週六")) saturdayCount += 1;
      else otherCount += 1;
    });

    if (saturdayChart) saturdayChart.destroy();
    saturdayChart = new Chart(document.getElementById("chart-saturday"), {
      type: "doughnut",
      data: {
        labels: ["含週六服務", "僅週一至週五"],
        datasets: [{ data: [saturdayCount, otherCount], backgroundColor: ["#1f6f5c", "#e07a2c"] }],
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
    const data = window.CHIAYI_TRANSPORT_DATA;
    if (!data) {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：找不到內嵌資料 data/chiayi-transport.js</div>`;
      return;
    }
    state.fields = data.fields;
    state.all = data.rows.map(rowToObj);

    const districts = Array.from(new Set(state.all.map((r) => r.district))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateSelect(els.district, districts);

    els.metaUpdated.textContent = `資料筆數：${data.rows.length.toLocaleString()}`;
    applyFilters();

    // meta.json 僅用於補上資料整理時間，非核心資料，失敗也不影響上方篩選/圖表/表格運作。
    fetch("../data/meta.json")
      .then((r) => r.json())
      .then((meta) => {
        if (meta.chiayiTransport) {
          els.metaUpdated.textContent = `資料筆數：${meta.chiayiTransport.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;
        }
      })
      .catch(() => {});
  }

  init();
})();
