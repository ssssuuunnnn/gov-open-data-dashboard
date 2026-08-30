/* 高雄市醫療院所資料 dashboard */
(function () {
  const state = { all: [], fields: [], filtered: [], specialtyGroups: {}, specialtyKeys: [] };

  const els = {
    district: document.getElementById("f-district"),
    specialtyGroups: document.getElementById("f-specialty-groups"),
    keyword: document.getElementById("f-keyword"),
    reset: document.getElementById("f-reset"),
    statTotal: document.getElementById("stat-total"),
    statDistricts: document.getElementById("stat-districts"),
    statAvgSpec: document.getElementById("stat-avgspec"),
    statTop: document.getElementById("stat-top"),
    metaUpdated: document.getElementById("meta-updated"),
  };

  let districtChart, specialtyChart;

  const table = createPagedTable({
    container: document.getElementById("table-container"),
    pageSize: 25,
    columns: [
      { key: "seq", label: "序號" },
      { key: "name", label: "機構名稱" },
      { key: "code", label: "機構代碼" },
      { key: "address", label: "地址", render: (r) => addressLink(r.address) },
      { key: "district", label: "行政區" },
      { key: "phone", label: "電話", render: (r) => phoneLink(r.phone) },
      {
        key: "specialties",
        label: "提供之科別",
        render: (r) =>
          Object.entries(state.specialtyGroups)
            .map(([group, keys]) => {
              const provided = keys.filter((k) => r[k]);
              if (!provided.length) return "";
              return `<div><strong>${escapeHtml(group)}：</strong>${provided
                .map((k) => `<span class="badge cap">${escapeHtml(k)}</span>`)
                .join(" ")}</div>`;
            })
            .join("") || "-",
      },
    ],
  });

  function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  // 電話欄位格式不一（空格或橫線分隔），轉成 tel: 連結時去除裝飾字元，顯示文字保留原始格式。
  function phoneLink(phone) {
    if (!phone) return "";
    const digits = phone.replace(/[^\d+]/g, "");
    if (!digits) return escapeHtml(phone);
    return `<a href="tel:${digits}">${escapeHtml(phone)}</a>`;
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

  // 39 個科別欄位分三組（西醫科別/牙科/中醫科別）各自渲染成一個可捲動的 checkbox 區塊。
  function buildSpecialtyCheckboxes() {
    els.specialtyGroups.innerHTML = "";
    Object.entries(state.specialtyGroups).forEach(([group, keys]) => {
      const fieldset = document.createElement("fieldset");
      fieldset.style.border = "1px solid var(--color-border)";
      fieldset.style.borderRadius = "var(--radius)";
      fieldset.style.margin = "8px 0";
      fieldset.style.padding = "6px 10px";
      const legend = document.createElement("legend");
      legend.textContent = `${group}（${keys.length}）`;
      legend.style.fontSize = ".82rem";
      legend.style.padding = "0 4px";
      fieldset.appendChild(legend);
      const wrap = document.createElement("div");
      wrap.className = "checkbox-group scroll";
      keys.forEach((k) => {
        const label = document.createElement("label");
        const input = document.createElement("input");
        input.type = "checkbox";
        input.value = k;
        label.appendChild(input);
        label.appendChild(document.createTextNode(` ${k}`));
        wrap.appendChild(label);
        input.addEventListener("change", applyFilters);
      });
      fieldset.appendChild(wrap);
      els.specialtyGroups.appendChild(fieldset);
    });
  }

  function selectedSpecialties() {
    return Array.from(els.specialtyGroups.querySelectorAll("input:checked")).map((i) => i.value);
  }

  function applyFilters() {
    const district = els.district.value;
    const specs = selectedSpecialties();
    const keyword = els.keyword.value.trim().toLowerCase();
    state.filtered = state.all.filter((r) => {
      if (district && r.district !== district) return false;
      if (specs.length && !specs.every((k) => r[k])) return false;
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
    els.statTotal.textContent = rows.length.toLocaleString();
    els.statDistricts.textContent = new Set(rows.map((r) => r.district).filter(Boolean)).size;

    const specCounts = {};
    state.specialtyKeys.forEach((k) => (specCounts[k] = 0));
    let totalSpecs = 0;
    rows.forEach((r) => {
      state.specialtyKeys.forEach((k) => {
        if (r[k]) {
          totalSpecs += 1;
          specCounts[k] += 1;
        }
      });
    });
    els.statAvgSpec.textContent = rows.length ? (totalSpecs / rows.length).toFixed(1) : "-";
    const top = Object.entries(specCounts).sort((a, b) => b[1] - a[1])[0];
    els.statTop.textContent = top && top[1] > 0 ? `${top[0]}（${top[1]}家）` : "-";
  }

  function renderCharts() {
    const districtCounts = {};
    state.filtered.forEach((r) => {
      if (!r.district) return;
      districtCounts[r.district] = (districtCounts[r.district] || 0) + 1;
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

    const specCounts = {};
    state.specialtyKeys.forEach((k) => (specCounts[k] = 0));
    state.filtered.forEach((r) => state.specialtyKeys.forEach((k) => { if (r[k]) specCounts[k] += 1; }));
    const specEntries = Object.entries(specCounts).sort((a, b) => b[1] - a[1]).slice(0, 15);

    if (specialtyChart) specialtyChart.destroy();
    specialtyChart = new Chart(document.getElementById("chart-specialty"), {
      type: "bar",
      data: {
        labels: specEntries.map((e) => e[0]),
        datasets: [{ data: specEntries.map((e) => e[1]), backgroundColor: "#e07a2c" }],
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
    els.specialtyGroups.querySelectorAll("input:checked").forEach((i) => (i.checked = false));
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
    const data = window.KCG_HOSPITALS_DATA;
    if (!data) {
      document.getElementById("table-container").innerHTML = `<div class="loading">資料載入失敗：找不到內嵌資料 data/kcg-hospitals.js</div>`;
      return;
    }
    state.fields = data.fields;
    state.specialtyGroups = data.specialtyGroups || {};
    state.specialtyKeys = Object.values(state.specialtyGroups).flat();
    state.all = data.rows.map(rowToObj);

    const districts = Array.from(new Set(state.all.map((r) => r.district).filter(Boolean))).sort((a, b) =>
      a.localeCompare(b, "zh-Hant")
    );
    populateSelect(els.district, districts);
    buildSpecialtyCheckboxes();

    els.metaUpdated.textContent = `資料筆數：${data.rows.length.toLocaleString()}`;
    applyFilters();

    // meta.json 僅用於補上資料整理時間，非核心資料，失敗也不影響上方篩選/圖表/表格運作。
    fetch("../data/meta.json")
      .then((r) => r.json())
      .then((meta) => {
        if (meta.kcgHospitals) {
          els.metaUpdated.textContent = `資料筆數：${meta.kcgHospitals.count.toLocaleString()}　資料整理時間：${new Date(meta.generatedAt).toLocaleString("zh-Hant-TW")}`;
        }
      })
      .catch(() => {});
  }

  init();
})();
