/* 新竹市老人福利機構一覽表 dashboard */
(function () {
  const state = { all: [], fields: [], filtered: [] };

  const els = {
    district: document.getElementById("f-district"),
    target: document.getElementById("f-target"),
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    statTotal: document.getElementById("stat-total"),
    statDistricts: document.getElementById("stat-districts"),
    statCapacity: document.getElementById("stat-capacity"),
    statTop: document.getElementById("stat-top"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  const map = L.map("map", { preferCanvas: true }).setView([24.80, 120.95], 13);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);
  const clusterGroup = L.markerClusterGroup({ chunkedLoading: true, disableClusteringAtZoom: 16 });
  map.addLayer(clusterGroup);

  let districtChart, attrChart;

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 25,
    columns: [
      { key: "id", label: "編號" },
      { key: "attr", label: "屬性" },
      { key: "name", label: "機構名稱" },
      { key: "owner", label: "負責人" },
      { key: "district", label: "行政區" },
      { key: "address", label: "地址" },
      { key: "phone", label: "電話" },
      { key: "target", label: "收容對象" },
      { key: "capacity", label: "核定收容人數" },
      { key: "approvedDate", label: "立案日期" },
    ],
    onRowClick: (row) => {
      if (row.lat && row.lng) {
        map.setView([row.lat, row.lng], 16);
      }
    },
  });

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
    const target = els.target.value;
    const keyword = els.keyword.value.trim().toLowerCase();
    state.filtered = state.all.filter((r) => {
      if (district && r.district !== district) return false;
      if (target && r.target !== target) return false;
      if (keyword) {
        const hay = `${r.name} ${r.owner} ${r.address}`.toLowerCase();
        if (!hay.includes(keyword)) return false;
      }
      return true;
    });
    renderAll();
  }

  function renderStats() {
    const rows = state.filtered;
    const districtCounts = {};
    let capacitySum = 0;
    rows.forEach((r) => {
      districtCounts[r.district] = (districtCounts[r.district] || 0) + 1;
      capacitySum += Number(r.capacity) || 0;
    });
    els.statTotal.textContent = rows.length.toLocaleString();
    els.statDistricts.textContent = Object.keys(districtCounts).filter(Boolean).length;
    els.statCapacity.textContent = capacitySum.toLocaleString();
    const top = Object.entries(districtCounts).filter(([k]) => k).sort((a, b) => b[1] - a[1])[0];
    els.statTop.textContent = top ? `${top[0]}（${top[1]}）` : "-";
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
        `<strong>${escapeHtml(r.name)}</strong><br/>${escapeHtml(r.address)}<br/>電話：${escapeHtml(r.phone || "-")}<br/>收容對象：${escapeHtml(r.target || "-")}<br/>核定收容人數：${escapeHtml(r.capacity ?? "-")}`
      );
      markers.push(marker);
    });
    clusterGroup.addLayers(markers);
  }

  function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
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

    const attrCounts = {};
    state.filtered.forEach((r) => {
      const label = r.attr || "未標示";
      attrCounts[label] = (attrCounts[label] || 0) + 1;
    });
    const attrEntries = Object.entries(attrCounts).sort((a, b) => b[1] - a[1]);

    if (attrChart) attrChart.destroy();
    attrChart = new Chart(document.getElementById("chart-attr"), {
      type: "doughnut",
      data: {
        labels: attrEntries.map((e) => e[0]),
        datasets: [{ data: attrEntries.map((e) => e[1]), backgroundColor: ["#1f6f5c", "#e07a2c", "#2563eb", "#a855f7"] }],
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
  els.target.addEventListener("change", applyFilters);
  els.keyword.addEventListener("input", debounce(applyFilters, 250));
  els.reset.addEventListener("click", () => {
    els.district.value = "";
    els.target.value = "";
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
    const data = window.HCCG_ELDER_DATA;
    if (!data) {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：找不到內嵌資料 data/hccg-elder.js</div>`;
      return;
    }
    state.fields = data.fields;
    state.all = data.rows.map(rowToObj);

    const districts = Array.from(new Set(state.all.map((r) => r.district))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateSelect(els.district, districts);

    const targets = Array.from(new Set(state.all.map((r) => r.target))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateSelect(els.target, targets);

    els.metaUpdated.textContent = `資料筆數：${data.rows.length.toLocaleString()}`;
    applyFilters();

    // meta.json 僅用於補上資料整理時間，非核心資料，失敗也不影響上方篩選/圖表/表格運作。
    fetch("../data/meta.json")
      .then((r) => r.json())
      .then((meta) => {
        if (meta.hccgElder) {
          els.metaUpdated.textContent = `資料筆數：${meta.hccgElder.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;
        }
      })
      .catch(() => {});
  }

  init();
})();
