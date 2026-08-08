/* 看護／照服機構名錄 dashboard（人工蒐集資料，非政府開放資料） */
(function () {
  const state = { all: [], fields: [], filtered: [] };

  const els = {
    region: document.getElementById("f-region"),
    pay: document.getElementById("f-pay"),
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    statTotal: document.getElementById("stat-total"),
    statPay: document.getElementById("stat-pay"),
    statRegion: document.getElementById("stat-region"),
    statUid: document.getElementById("stat-uid"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 1000,
    columns: [
      {
        key: "name",
        label: "機構名稱",
        render: (r) => (r.url ? `<a href="${r.url}" target="_blank" rel="noopener">${r.name}</a>` : r.name),
      },
      { key: "regions", label: "服務地區", render: (r) => (r.regions && r.regions.length ? r.regions.join("、") : "—") },
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
      {
        key: "payUrl",
        label: "收費頁面",
        render: (r) => (r.payUrl ? `<a href="${r.payUrl}" target="_blank" rel="noopener">查看收費</a>` : "—"),
      },
      { key: "uid", label: "統一編號", render: (r) => r.uid || "—" },
      { key: "google_rating", label: "Google Map 星等", render: (r) => (r.google_rating ? `⭐ ${r.google_rating}` : "—") },
      { key: "google_review_count", label: "Google Map 評論數", render: (r) => googleReviewCell(r) },
    ],
  });

  // Google Map 評論數欄位：有 google_place_id 時做成可點擊連結直接連到該機構的 Google 地圖評論頁，
  // 沒有 place_id（一次性抓取時查無對照資料或已排除誤配對）則只顯示數字或「—」，不猜測連結。
  function googleReviewCell(r) {
    if (!r.google_review_count) return "—";
    const label = `${Number(r.google_review_count).toLocaleString()} 則`;
    if (!r.google_place_id) return label;
    const href = `https://search.google.com/local/reviews?placeid=${encodeURIComponent(r.google_place_id)}`;
    return `<a href="${href}" target="_blank" rel="noopener">${label}</a>`;
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
    const region = els.region.value;
    const payOnly = els.pay.checked;
    const keyword = els.keyword.value.trim().toLowerCase();
    state.filtered = state.all.filter((r) => {
      if (region && !(r.regions || []).includes(region)) return false;
      if (payOnly && !r.payUrl) return false;
      if (keyword && !r.name.toLowerCase().includes(keyword)) return false;
      return true;
    });
    renderAll();
  }

  function renderStats() {
    const rows = state.filtered;
    const payCount = rows.filter((r) => r.payUrl).length;
    const regionCount = rows.filter((r) => r.regions && r.regions.length).length;
    const uidCount = rows.filter((r) => r.uid).length;
    els.statTotal.textContent = rows.length.toLocaleString();
    els.statPay.textContent = payCount.toLocaleString();
    els.statRegion.textContent = regionCount.toLocaleString();
    els.statUid.textContent = uidCount.toLocaleString();
  }

  function renderAll() {
    renderStats();
    table.setData(state.filtered);
  }

  els.region.addEventListener("change", applyFilters);
  els.pay.addEventListener("change", applyFilters);
  els.keyword.addEventListener("input", debounce(applyFilters, 250));
  els.reset.addEventListener("click", () => {
    els.region.value = "";
    els.pay.checked = false;
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
    const data = window.CAREGIVER_DATA;
    if (!data) {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：找不到內嵌資料 data/caregiver.js</div>`;
      return;
    }
    state.fields = data.fields;
    state.all = data.rows.map(rowToObj);

    const regions = Array.from(new Set(state.all.flatMap((r) => r.regions || []))).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateSelect(els.region, regions);

    els.metaUpdated.textContent = `資料筆數：${data.rows.length.toLocaleString()}`;
    applyFilters();

    // meta.json 僅用於補上資料整理時間，非核心資料，失敗也不影響上方篩選/表格運作。
    fetch("../data/meta.json")
      .then((r) => r.json())
      .then((meta) => {
        if (meta.caregiver) {
          els.metaUpdated.textContent = `資料筆數：${meta.caregiver.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;
        }
      })
      .catch(() => {});
  }

  init();
})();
