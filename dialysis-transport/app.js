/* 洗腎（透析）接送資源清單 dashboard（人工蒐集資料，非政府開放資料） */
(function () {
  const state = { all: [], fields: [], filtered: [] };

  const els = {
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    statTotal: document.getElementById("stat-total"),
    statArea: document.getElementById("stat-area"),
    statUrl: document.getElementById("stat-url"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 1000,
    columns: [
      {
        key: "name",
        label: "名稱",
        render: (r) => (r.url ? `<a href="${r.url}" target="_blank" rel="noopener">${r.name}</a>` : r.name),
      },
      {
        key: "phone",
        label: "聯絡電話",
        render: (r) => {
          const phone = (r.phone || "").trim();
          if (!phone) return "—";
          const telHref = phone.replace(/[^0-9+#]/g, "");
          return `<a href="tel:${telHref}">${phone}</a>`;
        },
      },
      { key: "serviceArea", label: "服務地區", render: (r) => r.serviceArea || "—" },
    ],
  });

  function rowToObj(row) {
    const o = {};
    state.fields.forEach((f, i) => (o[f] = row[i]));
    return o;
  }

  function applyFilters() {
    const keyword = els.keyword.value.trim().toLowerCase();
    state.filtered = state.all.filter((r) => {
      if (keyword) {
        const hay = `${r.name} ${r.serviceArea || ""}`.toLowerCase();
        if (!hay.includes(keyword)) return false;
      }
      return true;
    });
    renderAll();
  }

  function renderStats() {
    const rows = state.filtered;
    const areaCount = rows.filter((r) => r.serviceArea).length;
    const urlCount = rows.filter((r) => r.url).length;
    els.statTotal.textContent = rows.length.toLocaleString();
    els.statArea.textContent = areaCount.toLocaleString();
    els.statUrl.textContent = urlCount.toLocaleString();
  }

  function renderAll() {
    renderStats();
    table.setData(state.filtered);
  }

  els.keyword.addEventListener("input", debounce(applyFilters, 250));
  els.reset.addEventListener("click", () => {
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
    const data = window.DIALYSIS_TRANSPORT_DATA;
    if (!data) {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：找不到內嵌資料 data/dialysis-transport.js</div>`;
      return;
    }
    state.fields = data.fields;
    state.all = data.rows.map(rowToObj);

    els.metaUpdated.textContent = `資料筆數：${data.rows.length.toLocaleString()}`;
    applyFilters();

    // meta.json 僅用於補上資料整理時間，非核心資料，失敗也不影響上方篩選/表格運作。
    fetch("../data/meta.json")
      .then((r) => r.json())
      .then((meta) => {
        if (meta.dialysisTransport) {
          els.metaUpdated.textContent = `資料筆數：${meta.dialysisTransport.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;
        }
      })
      .catch(() => {});
  }

  init();
})();
