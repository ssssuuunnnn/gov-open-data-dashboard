/**
 * 共用 Google Analytics（gtag.js）篩選功能事件追蹤。
 *
 * 透過事件代理（event delegation）監聽頁面上所有篩選相關容器（`.filters`、`.category-tabs`）內的
 * 使用者操作，不需要修改各頁面 app.js 既有的篩選邏輯，即可統一送出 GA 事件，記錄下拉選單、複選框、
 * 關鍵字輸入、重設按鈕、分類頁籤等篩選操作。
 *
 * 事件名稱固定為 "filter_use"，並附帶：
 *   - filter_name：篩選項目名稱（依 <label> 文字、按鈕文字或元素 id 推斷）
 *   - filter_value：使用者選擇/輸入的值
 *   - page_path：目前頁面路徑（區分不同資料集頁面）
 */
(function () {
  function send(filterName, filterValue) {
    if (typeof gtag !== "function") return;
    gtag("event", "filter_use", {
      event_category: "filter",
      event_label: filterName + (filterValue ? "：" + filterValue : ""),
      filter_name: filterName,
      filter_value: filterValue,
      page_path: location.pathname,
    });
  }

  function labelFor(el) {
    var field = el.closest(".field");
    if (field) {
      var label = field.querySelector("label");
      if (label && label.textContent.trim()) return label.textContent.trim();
    }
    if (el.tagName === "BUTTON") {
      return (el.textContent || "").trim() || el.id || "按鈕";
    }
    if (el.matches('[role="tab"]')) {
      return "分類頁籤";
    }
    return el.id || el.name || el.tagName.toLowerCase();
  }

  function valueFor(el) {
    if (el.tagName === "SELECT") {
      var opt = el.options[el.selectedIndex];
      return opt ? opt.textContent.trim() : el.value;
    }
    if (el.type === "checkbox") {
      return (el.checked ? "勾選" : "取消勾選") + (el.value ? "：" + el.value : "");
    }
    if (el.tagName === "INPUT") {
      return el.value;
    }
    if (el.tagName === "BUTTON") {
      return el.dataset.category || el.textContent.trim();
    }
    return "";
  }

  function handleChange(e) {
    var el = e.target.closest("select, input[type=checkbox], input[type=text], input[type=search]");
    if (!el) return;
    send(labelFor(el), valueFor(el));
  }

  function handleClick(e) {
    var el = e.target.closest('button, [role="tab"]');
    if (!el) return;
    send(labelFor(el), valueFor(el));
  }

  document.addEventListener("DOMContentLoaded", function () {
    var containers = document.querySelectorAll(".filters, .category-tabs");
    containers.forEach(function (container) {
      container.addEventListener("change", handleChange);
      container.addEventListener("click", handleClick);
    });
  });
})();
