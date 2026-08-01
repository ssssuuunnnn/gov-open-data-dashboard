/* 新北市銀髮俱樂部 dashboard */
(function () {
  const state = { all: [], fields: [], filtered: [] };

  const els = {
    district: document.getElementById("f-district"),
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    statTotal: document.getElementById("stat-total"),
    statDistricts: document.getElementById("stat-districts"),
    statPhone: document.getElementById("stat-phone"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  let districtChart;

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 25,
    columns: [
      { key: "id", label: "序號" },
      { key: "name", label: "名稱" },
      { key: "district", label: "行政區" },
      { key: "address", label: "地址", render: (r) => addressLink(r) },
      { key: "phone", label: "電話", render: (r) => phoneLink(r) },
    ],
  });

  function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  // 市話（localPhone）／手機（mobilePhone）為原始兩欄，皆有時並列顯示，各自轉 tel: 連結；
  // 僅其一有值時單獨顯示，兩者皆空則顯示空白。
  function phoneLink(r) {
    const parts = [];
    if (r.localPhone) {
      const digits = r.localPhone.replace(/[^\d+]/g, "");
      parts.push(digits ? `<a href="tel:${digits}">${escapeHtml(r.localPhone)}</a>` : escapeHtml(r.localPhone));
    }
    if (r.mobilePhone) {
      const digits = r.mobilePhone.replace(/[^\d+]/g, "");
      parts.push(digits ? `<a href="tel:${digits}">${escapeHtml(r.mobilePhone)}</a>` : escapeHtml(r.mobilePhone));
    }
    return parts.join("　");
  }

  // 原始地址欄位不含「新北市」＋行政區字首，僅顯示文字原文照登，但查詢 Google Maps 時
  // 需自行補上「新北市」＋該筆行政區前綴，才能正確定位地點。
  function addressLink(r) {
    if (!r.address) return "";
    const query = `新北市${r.district || ""}${r.address}`;
    const href = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(query)}`;
    return `<a href="${href}" target="_blank" rel="noopener">${escapeHtml(r.address)}</a>`;
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
        const hay = `${r.name} ${r.address}`.toLowerCase();
        if (!hay.includes(keyword)) return false;
      }
      return true;
    });
    renderAll();
  }

  function renderStats() {
    const rows = state.filtered;
    const districtCounts = {};
    let withPhone = 0;
    rows.forEach((r) => {
      districtCounts[r.district] = (districtCounts[r.district] || 0) + 1;
      if (r.localPhone || r.mobilePhone) withPhone += 1;
    });
    els.statTotal.textContent = rows.length.toLocaleString();
    els.statDistricts.textContent = Object.keys(districtCounts).filter(Boolean).length;
    els.statPhone.textContent = withPhone.toLocaleString();
  }

  function renderCharts() {
    const districtCounts = {};
    state.filtered.forEach((r) => {
      districtCounts[r.district] = (districtCounts[r.district] || 0) + 1;
    });
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
    const data = window.NTPC_SILVER_HAIR_CLUB_DATA;
    if (!data) {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：找不到內嵌資料 data/ntpc-silver-hair-club.js</div>`;
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
        if (meta.ntpcSilverHairClub) {
          els.metaUpdated.textContent = `資料筆數：${meta.ntpcSilverHairClub.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;
        }
      })
      .catch(() => {});
  }

  init();
})();
