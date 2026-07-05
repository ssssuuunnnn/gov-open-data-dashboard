/* 共用：分頁表格元件 */
function createPagedTable({ container, columns, pageSize = 20, onRowClick = null }) {
  let data = [];
  let sortKey = null;
  let sortDir = 1;
  let page = 1;

  const wrap = document.createElement("div");
  wrap.className = "table-wrap";
  const table = document.createElement("table");
  table.className = "data-table";
  const thead = document.createElement("thead");
  const trHead = document.createElement("tr");
  columns.forEach((col) => {
    const th = document.createElement("th");
    th.textContent = col.label;
    th.addEventListener("click", () => {
      if (sortKey === col.key) {
        sortDir *= -1;
      } else {
        sortKey = col.key;
        sortDir = 1;
      }
      page = 1;
      render();
    });
    trHead.appendChild(th);
  });
  thead.appendChild(trHead);
  const tbody = document.createElement("tbody");
  table.appendChild(thead);
  table.appendChild(tbody);
  wrap.appendChild(table);

  const pagination = document.createElement("div");
  pagination.className = "pagination";

  container.appendChild(wrap);
  container.appendChild(pagination);

  function setData(rows) {
    data = rows;
    page = 1;
    render();
  }

  function sortedData() {
    if (!sortKey) return data;
    const copy = [...data];
    copy.sort((a, b) => {
      const va = a[sortKey];
      const vb = b[sortKey];
      if (typeof va === "number" && typeof vb === "number") return (va - vb) * sortDir;
      return String(va ?? "").localeCompare(String(vb ?? ""), "zh-Hant") * sortDir;
    });
    return copy;
  }

  function render() {
    const rows = sortedData();
    const totalPages = Math.max(1, Math.ceil(rows.length / pageSize));
    if (page > totalPages) page = totalPages;
    const start = (page - 1) * pageSize;
    const pageRows = rows.slice(start, start + pageSize);

    tbody.innerHTML = "";
    if (pageRows.length === 0) {
      const tr = document.createElement("tr");
      const td = document.createElement("td");
      td.colSpan = columns.length;
      td.textContent = "查無符合條件的資料";
      td.style.textAlign = "center";
      td.style.color = "#94a3b8";
      td.style.padding = "24px";
      tr.appendChild(td);
      tbody.appendChild(tr);
    } else {
      pageRows.forEach((row) => {
        const tr = document.createElement("tr");
        columns.forEach((col) => {
          const td = document.createElement("td");
          if (col.render) {
            td.innerHTML = col.render(row);
          } else {
            td.textContent = row[col.key] ?? "";
          }
          tr.appendChild(td);
        });
        if (onRowClick) {
          tr.style.cursor = "pointer";
          tr.addEventListener("click", () => onRowClick(row));
        }
        tbody.appendChild(tr);
      });
    }

    pagination.innerHTML = "";
    const info = document.createElement("span");
    info.textContent = `共 ${rows.length.toLocaleString()} 筆，第 ${page} / ${totalPages} 頁`;
    pagination.appendChild(info);

    const mkBtn = (label, target, disabled) => {
      const b = document.createElement("button");
      b.textContent = label;
      b.disabled = !!disabled;
      b.addEventListener("click", () => { page = target; render(); });
      return b;
    };
    pagination.appendChild(mkBtn("« 上一頁", page - 1, page <= 1));
    pagination.appendChild(mkBtn("下一頁 »", page + 1, page >= totalPages));
  }

  return { setData, render };
}
