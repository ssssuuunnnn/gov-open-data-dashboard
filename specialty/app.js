/* 臺北市長照專業服務特約單位 dashboard */
(function () {
  const state = { all: [], fields: [], filtered: [], capabilityLabels: {} };

  const els = {
    district: document.getElementById("f-district"),
    capability: document.getElementById("f-capability"),
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    statTotal: document.getElementById("stat-total"),
    statDistricts: document.getElementById("stat-districts"),
    statAvgCap: document.getElementById("stat-avgcap"),
    statTop: document.getElementById("stat-top"),
    metaUpdated: document.getElementById("meta-updated"),
    capabilityLegend: document.getElementById("capability-legend"),
  };

  const CAP_KEYS = ["ca07", "ca08", "cb01", "cb02", "cb03", "cb04", "cc01", "cd02"];
  const TAIPEI_DISTRICTS = [
    "中正區", "大同區", "中山區", "松山區", "大安區", "萬華區",
    "信義區", "士林區", "北投區", "內湖區", "南港區", "文山區",
  ];

  let capabilityChart, districtChart;

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 25,
    columns: [
      { key: "id", label: "序號" },
      { key: "name", label: "機構名稱" },
      { key: "district", label: "服務區域" },
      { key: "address", label: "機構(服務)地址" },
      { key: "phone", label: "聯絡電話" },
      { key: "contact", label: "聯絡窗口" },
      {
        key: "capabilities",
        label: "提供之專業服務",
        render: (r) =>
          CAP_KEYS.filter((k) => r[k])
            .map((k) => `<span class="badge cap" title="${state.capabilityLabels[k] || ""}">${k.toUpperCase()}</span>`)
            .join(" ") || "-",
      },
    ],
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

  function buildCapabilityCheckboxes() {
    els.capability.innerHTML = "";
    CAP_KEYS.forEach((k) => {
      const label = document.createElement("label");
      const input = document.createElement("input");
      input.type = "checkbox";
      input.value = k;
      label.title = state.capabilityLabels[k] || "";
      label.appendChild(input);
      label.appendChild(document.createTextNode(` ${k.toUpperCase()}`));
      els.capability.appendChild(label);
      input.addEventListener("change", applyFilters);
    });
  }

  function buildCapabilityLegend() {
    els.capabilityLegend.innerHTML = "";
    CAP_KEYS.forEach((k) => {
      const li = document.createElement("li");
      li.textContent = state.capabilityLabels[k] || k.toUpperCase();
      els.capabilityLegend.appendChild(li);
    });
  }

  function selectedCapabilities() {
    return Array.from(els.capability.querySelectorAll("input:checked")).map((i) => i.value);
  }

  function districtMatches(row, district) {
    if (!district) return true;
    if (row.district === "全區") return true;
    return row.district.split("、").includes(district);
  }

  function applyFilters() {
    const district = els.district.value;
    const caps = selectedCapabilities();
    const keyword = els.keyword.value.trim().toLowerCase();
    state.filtered = state.all.filter((r) => {
      if (!districtMatches(r, district)) return false;
      if (caps.length && !caps.every((k) => r[k])) return false;
      if (keyword) {
        const hay = `${r.name} ${r.address} ${r.contact}`.toLowerCase();
        if (!hay.includes(keyword)) return false;
      }
      return true;
    });
    renderAll();
  }

  function renderStats() {
    const rows = state.filtered;
    els.statTotal.textContent = rows.length.toLocaleString();

    const districtSet = new Set();
    rows.forEach((r) => {
      if (r.district === "全區") {
        TAIPEI_DISTRICTS.forEach((d) => districtSet.add(d));
      } else {
        r.district.split("、").filter(Boolean).forEach((d) => districtSet.add(d));
      }
    });
    els.statDistricts.textContent = districtSet.size;

    let totalCaps = 0;
    const capCounts = {};
    CAP_KEYS.forEach((k) => (capCounts[k] = 0));
    rows.forEach((r) => {
      CAP_KEYS.forEach((k) => {
        if (r[k]) {
          totalCaps += 1;
          capCounts[k] += 1;
        }
      });
    });
    els.statAvgCap.textContent = rows.length ? (totalCaps / rows.length).toFixed(1) : "-";
    const topCap = Object.entries(capCounts).sort((a, b) => b[1] - a[1])[0];
    els.statTop.textContent = topCap && topCap[1] > 0
      ? `${topCap[0].toUpperCase()}（${topCap[1]}家）`
      : "-";
  }

  function renderCharts() {
    const capCounts = {};
    CAP_KEYS.forEach((k) => (capCounts[k] = 0));
    state.filtered.forEach((r) => CAP_KEYS.forEach((k) => { if (r[k]) capCounts[k] += 1; }));
    const capEntries = CAP_KEYS.map((k) => [k.toUpperCase(), capCounts[k]]);

    if (capabilityChart) capabilityChart.destroy();
    capabilityChart = new Chart(document.getElementById("chart-capability"), {
      type: "bar",
      data: {
        labels: capEntries.map((e) => e[0]),
        datasets: [{ data: capEntries.map((e) => e[1]), backgroundColor: "#1f6f5c" }],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
      },
    });

    const districtCounts = {};
    TAIPEI_DISTRICTS.forEach((d) => (districtCounts[d] = 0));
    state.filtered.forEach((r) => {
      if (r.district === "全區") {
        TAIPEI_DISTRICTS.forEach((d) => (districtCounts[d] += 1));
      } else {
        r.district.split("、").filter(Boolean).forEach((d) => {
          if (districtCounts[d] !== undefined) districtCounts[d] += 1;
        });
      }
    });
    const districtEntries = Object.entries(districtCounts).sort((a, b) => b[1] - a[1]);

    if (districtChart) districtChart.destroy();
    districtChart = new Chart(document.getElementById("chart-district"), {
      type: "bar",
      data: {
        labels: districtEntries.map((e) => e[0]),
        datasets: [{ data: districtEntries.map((e) => e[1]), backgroundColor: "#e07a2c" }],
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

  els.district.addEventListener("change", applyFilters);
  els.keyword.addEventListener("input", debounce(applyFilters, 250));
  els.reset.addEventListener("click", () => {
    els.district.value = "";
    els.keyword.value = "";
    els.capability.querySelectorAll("input:checked").forEach((i) => (i.checked = false));
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
    const data = window.SPECIALTY_DATA;
    if (!data) {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：找不到內嵌資料 data/specialty.js</div>`;
      return;
    }
    state.fields = data.fields;
    state.capabilityLabels = data.capabilityLabels || {};
    state.all = data.rows.map(rowToObj);

    const districts = Array.from(
      new Set(state.all.flatMap((r) => (r.district === "全區" ? TAIPEI_DISTRICTS : r.district.split("、").filter(Boolean))))
    ).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateSelect(els.district, districts);
    buildCapabilityCheckboxes();
    buildCapabilityLegend();

    els.metaUpdated.textContent = `資料筆數：${data.rows.length.toLocaleString()}`;
    applyFilters();

    // meta.json 僅用於補上資料整理時間，非核心資料，失敗也不影響上方篩選/圖表/表格運作。
    fetch("../data/meta.json")
      .then((r) => r.json())
      .then((meta) => {
        if (meta.specialty) {
          els.metaUpdated.textContent = `資料筆數：${meta.specialty.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;
        }
      })
      .catch(() => {});
  }

  init();
})();
