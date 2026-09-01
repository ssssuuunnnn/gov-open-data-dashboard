/* 新北市長者健康檢查醫療院所 dashboard */
(function () {
  const state = { all: [], fields: [], filtered: [] };

  const els = {
    district: document.getElementById("f-district"),
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    statTotal: document.getElementById("stat-total"),
    statDistricts: document.getElementById("stat-districts"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  let districtChart;

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 25,
    columns: [
      { key: "id", label: "序號" },
      { key: "name", label: "機構名稱" },
      { key: "district", label: "行政區" },
      { key: "address", label: "地址", render: (r) => addressLink(r.address) },
      { key: "phone", label: "電話", render: (r) => phoneLink(r.phone) },
      { key: "google_rating", label: "Google Map 星等", render: (r) => (r.google_rating ? `⭐ ${r.google_rating}` : "-") },
      { key: "google_review_count", label: "Google Map 評論數", render: (r) => googleReviewCell(r) },
    ],
  });

  // Google Map 評論數欄位：有 google_place_id 時做成可點擊連結直接連到該機構的 Google 地圖評論頁，
  // 沒有 place_id（尚未執行一次性抓取或查無對照資料）則只顯示數字或「-」，不猜測連結。
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

  // 電話欄位轉成 tel: 連結，顯示文字保留原始格式，去除裝飾字元作為連結號碼。
  function phoneLink(phone) {
    if (!phone) return "";
    const digits = phone.replace(/[^\d+]/g, "");
    if (!digits) return escapeHtml(phone);
    return `<a href="tel:${digits}">${escapeHtml(phone)}</a>`;
  }

  // 地址欄位轉成 Google Maps 搜尋連結（無經緯度座標，故用地址文字查詢）。
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
        const hay = `${r.name} ${r.address}`.toLowerCase();
        if (!hay.includes(keyword)) return false;
      }
      return true;
    });
    syncUrl();
    renderAll();
  }

  // 將目前的行政區篩選同步到網址查詢字串（?district=OO區），供分享／SEO 深連結使用；
  // 用 replaceState 而非 pushState，避免每次篩選都新增一筆瀏覽器歷史紀錄。
  function syncUrl() {
    const url = new URL(window.location.href);
    if (els.district.value) {
      url.searchParams.set("district", els.district.value);
    } else {
      url.searchParams.delete("district");
    }
    window.history.replaceState(null, "", url.pathname + url.search);
  }

  function renderStats() {
    const rows = state.filtered;
    const districtCounts = {};
    rows.forEach((r) => {
      districtCounts[r.district] = (districtCounts[r.district] || 0) + 1;
    });
    els.statTotal.textContent = rows.length.toLocaleString();
    els.statDistricts.textContent = Object.keys(districtCounts).filter(Boolean).length;
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
    const data = window.NTPC_ELDER_CHECKUP_DATA;
    if (!data) {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：找不到內嵌資料 data/ntpc-elder-checkup.js</div>`;
      return;
    }
    state.fields = data.fields;
    state.all = data.rows.map(rowToObj);

    const districts = Array.from(new Set(state.all.map((r) => r.district))).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-Hant"));
    populateSelect(els.district, districts);

    // 深連結：頁面載入時讀取網址列 ?district= 參數預選行政區篩選，方便分享／收藏特定行政區的查詢結果
    // （例如 ?district=板橋區），若參數值不在既有行政區清單中則忽略，不影響正常瀏覽。
    const params = new URLSearchParams(window.location.search);
    const districtParam = params.get("district");
    if (districtParam && districts.includes(districtParam)) {
      els.district.value = districtParam;
    }

    els.metaUpdated.textContent = `資料筆數：${data.rows.length.toLocaleString()}`;
    applyFilters();

    // meta.json 僅用於補上資料整理時間，非核心資料，失敗也不影響上方篩選/圖表/表格運作。
    fetch("../data/meta.json")
      .then((r) => r.json())
      .then((meta) => {
        if (meta.ntpcElderCheckup) {
          els.metaUpdated.textContent = `資料筆數：${meta.ntpcElderCheckup.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;
        }
      })
      .catch(() => {});
  }

  init();
})();
