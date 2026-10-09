/**
 * Ca Mau Fertilizer Classification - Modern Web Dashboard Application
 * Manages real-time data polling, ApexCharts rendering, video controls,
 * and order management with sleek reactive updates.
 */

// Global Chart Instances
let throughputChart = null;
let distributionChart = null;
let isOrderAlertTriggered = false;
let currentLineOrientation = "horizontal";
let currentLineCoord = 310;

// Initialize on DOM Ready
document.addEventListener("DOMContentLoaded", () => {
  lucide.createIcons();
  initClock();
  initApexCharts();
  fetchOrders();
  fetchSampleVideos();
  
  // Start Real-time Data Polling
  setInterval(pollSystemStatus, 800);
  setInterval(pollChartData, 1500);
});

// ================= CLOCK =================
function initClock() {
  const clockEl = document.getElementById("headerClock");
  const update = () => {
    const now = new Date();
    clockEl.innerText = now.toLocaleTimeString("vi-VN", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  };
  update();
  setInterval(update, 1000);
}

// ================= APEX CHARTS =================
function initApexCharts() {
  // 1. Spline Area Chart: Conveyor Speed (Bags/Min)
  const throughputOptions = {
    series: [{ name: "Tốc độ (Bao/phút)", data: [0, 0, 0, 0, 0] }],
    chart: {
      type: "area",
      height: 170,
      sparkline: { enabled: false },
      toolbar: { show: false },
      animations: {
        enabled: true,
        easing: "linear",
        dynamicAnimation: { speed: 1000 },
      },
      background: "transparent",
    },
    colors: ["#10b981"],
    stroke: { curve: "smooth", width: 2.5 },
    fill: {
      type: "gradient",
      gradient: {
        shadeIntensity: 1,
        opacityFrom: 0.45,
        opacityTo: 0.05,
        stops: [0, 90, 100],
      },
    },
    dataLabels: { enabled: false },
    grid: {
      borderColor: "rgba(51, 65, 85, 0.4)",
      strokeDashArray: 3,
      padding: { top: 0, right: 10, bottom: 0, left: 10 },
    },
    xaxis: {
      categories: ["--", "--", "--", "--", "--"],
      labels: {
        style: { colors: "#64748b", fontSize: "10px", fontFamily: "JetBrains Mono" },
      },
      axisBorder: { show: false },
      axisTicks: { show: false },
    },
    yaxis: {
      labels: {
        style: { colors: "#64748b", fontSize: "10px", fontFamily: "JetBrains Mono" },
        formatter: (val) => Math.round(val),
      },
    },
    tooltip: {
      theme: "dark",
      y: { formatter: (val) => `${val} bao/phút` },
    },
  };

  throughputChart = new ApexCharts(
    document.querySelector("#throughputChart"),
    throughputOptions
  );
  throughputChart.render();

  // 2. Donut Chart: Product Breakdown
  const distributionOptions = {
    series: [1, 1, 1],
    labels: ["Urea Bio xanh", "NPK 22-5-6", "Urea hạt đục"],
    chart: {
      type: "donut",
      height: 170,
      background: "transparent",
      animations: { enabled: true },
    },
    colors: ["#10b981", "#f59e0b", "#a855f7"],
    legend: {
      position: "right",
      fontSize: "11px",
      labels: { colors: "#94a3b8" },
      markers: { width: 8, height: 8, radius: 4 },
    },
    stroke: { width: 1, colors: ["#0f172a"] },
    dataLabels: { enabled: false },
    plotOptions: {
      pie: {
        donut: {
          size: "70%",
          labels: {
            show: true,
            total: {
              show: true,
              label: "Tổng cộng",
              color: "#94a3b8",
              fontSize: "11px",
              formatter: function (w) {
                return w.globals.seriesTotals.reduce((a, b) => a + b, 0);
              },
            },
          },
        },
      },
    },
    tooltip: { theme: "dark" },
  };

  distributionChart = new ApexCharts(
    document.querySelector("#distributionChart"),
    distributionOptions
  );
  distributionChart.render();
}

// ================= DATA POLLING =================
async function pollSystemStatus() {
  try {
    const res = await fetch("/api/status");
    if (!res.ok) return;
    const data = await res.json();

    // 1. Total Counted & Speed
    document.getElementById("metricTotal").innerText = data.total_counted;
    document.getElementById("metricSpeed").innerText = `${data.speed_bags_per_min} bao/phút`;
    document.getElementById("chartSpeedBadge").innerText = `${data.speed_bags_per_min} bao/phút`;

    // 2. Counts for 3 Products
    const counts = data.counts || {};
    const bio = counts["Urea_Bio_xanh"] || 0;
    const npk = counts["NPK_22-5-6"] || 0;
    const duc = counts["Urea_hat_duc"] || 0;

    document.getElementById("metricBio").innerText = bio;
    document.getElementById("metricNPK").innerText = npk;
    document.getElementById("metricDuc").innerText = duc;

    // 3. Header & Badges
    document.getElementById("streamFpsBadge").innerText = `FPS: ${data.fps}`;
    document.getElementById("currentSourceBadge").innerText = data.video_source;

    // 4. Line Config Badge
    const lineConfig = data.line_config || {};
    currentLineOrientation = lineConfig.orientation || "horizontal";
    currentLineCoord = lineConfig.coord || 310;
    const oriText = currentLineOrientation === "horizontal" ? "Ngang" : "Dọc";
    document.getElementById("activeLineBadge").innerText = `${oriText} (${currentLineCoord}px)`;

    // 5. Active Target Order Updates
    const order = data.active_order || {};
    const targets = order.targets || {};
    const tBio = targets["Urea_Bio_xanh"] || targets["Urea Bio xanh"] || 0;
    const tNPK = targets["NPK_22-5-6"] || 0;
    const tDuc = targets["Urea_hat_duc"] || targets["Urea hạt đục"] || 0;

    document.getElementById("targetBioText").innerText = tBio > 0 ? `/ ${tBio} bao` : "/ -- bao";
    document.getElementById("targetNPKText").innerText = tNPK > 0 ? `/ ${tNPK} bao` : "/ -- bao";
    document.getElementById("targetDucText").innerText = tDuc > 0 ? `/ ${tDuc} bao` : "/ -- bao";

    document.getElementById("progBio").style.width = tBio > 0 ? `${Math.min(100, (bio / tBio) * 100)}%` : "0%";
    document.getElementById("progNPK").style.width = tNPK > 0 ? `${Math.min(100, (npk / tNPK) * 100)}%` : "0%";
    document.getElementById("progDuc").style.width = tDuc > 0 ? `${Math.min(100, (duc / tDuc) * 100)}%` : "0%";

    // Large Order Progress
    const pct = order.progress_percentage || 0;
    document.getElementById("activeCustomerName").innerText = order.customer || "Chưa gán đơn hàng mục tiêu";
    document.getElementById("orderPercentText").innerText = `${pct}%`;
    document.getElementById("orderTotalProgressBar").style.width = `${pct}%`;

    const statusBadge = document.getElementById("orderStatusBadge");
    if (order.is_completed) {
      statusBadge.innerText = "HOÀN THÀNH";
      statusBadge.className = "px-2.5 py-0.5 text-[11px] font-semibold rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 glow-green";
      if (!isOrderAlertTriggered) {
        isOrderAlertTriggered = true;
        playOrderCompletedChime();
        showToast("Hoàn Thành Đơn Hàng", `Đơn hàng của "${order.customer}" đã đếm đủ số lượng yêu cầu!`, "success");
      }
    } else if (order.customer && order.customer !== "Chưa chọn đơn hàng") {
      statusBadge.innerText = "ĐANG ĐẾM";
      statusBadge.className = "px-2.5 py-0.5 text-[11px] font-semibold rounded-full bg-cyan-500/20 text-cyan-400 border border-cyan-500/40";
      isOrderAlertTriggered = false;
    } else {
      statusBadge.innerText = "Chưa chọn đơn";
      statusBadge.className = "px-2.5 py-0.5 text-[11px] font-semibold rounded-full bg-slate-800 text-slate-400 border border-slate-700";
    }

    // 6. Pause UI Updates
    const pauseOverlay = document.getElementById("pausedOverlay");
    const pauseBtnText = document.getElementById("btnPauseText");
    const pauseBtnIcon = document.getElementById("btnPauseIcon");

    if (data.is_paused) {
      pauseOverlay.classList.remove("hidden");
      pauseOverlay.classList.add("flex");
      pauseBtnText.innerText = "Tiếp tục";
      pauseBtnIcon.setAttribute("data-lucide", "play");
    } else {
      pauseOverlay.classList.add("hidden");
      pauseOverlay.classList.remove("flex");
      pauseBtnText.innerText = "Tạm dừng";
      pauseBtnIcon.setAttribute("data-lucide", "pause");
    }
    lucide.createIcons();

  } catch (err) {
    console.warn("Polling error:", err);
  }
}

async function pollChartData() {
  try {
    const res = await fetch("/api/chart_data");
    if (!res.ok) return;
    const data = await res.json();

    // Update Throughput Chart
    if (throughputChart && data.categories && data.categories.length > 0) {
      throughputChart.updateOptions({
        xaxis: { categories: data.categories },
      });
      throughputChart.updateSeries([{ data: data.speed_series }]);
    }

    // Update Donut Distribution Chart
    if (distributionChart && data.distribution) {
      const series = data.distribution.series;
      const total = series.reduce((a, b) => a + b, 0);
      if (total > 0) {
        distributionChart.updateSeries(series);
      }
    }
  } catch (err) {
    console.warn("Chart poll error:", err);
  }
}

// ================= VIDEO CONTROLS =================
async function togglePauseVideo() {
  try {
    await fetch("/api/video/control", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "toggle_pause" }),
    });
  } catch (err) {
    showToast("Lỗi", "Không thể điều khiển luồng video", "error");
  }
}

async function resetCounters() {
  if (!confirm("Bạn có chắc chắn muốn đặt lại toàn bộ số đếm về 0?")) return;
  try {
    await fetch("/api/video/control", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "reset" }),
    });
    isOrderAlertTriggered = false;
    showToast("Thành công", "Đã đặt lại số đếm về 0", "success");
  } catch (err) {
    showToast("Lỗi", "Không thể đặt lại số đếm", "error");
  }
}

async function selectSource(sourcePath) {
  try {
    await fetch("/api/video/control", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "change_source", source: sourcePath }),
    });
    closeModal("sourceModal");
    showToast("Đổi nguồn", `Đã chuyển sang: ${sourcePath}`, "success");
  } catch (err) {
    showToast("Lỗi", "Không thể chuyển nguồn video", "error");
  }
}

function selectCustomSource() {
  const val = document.getElementById("inputCustomSource").value.trim();
  if (!val) {
    showToast("Cảnh báo", "Vui lòng nhập đường dẫn file video hoặc RTSP", "warning");
    return;
  }
  selectSource(val);
}

// ================= LINE CONFIGURATION =================
function setLineOrientation(ori) {
  currentLineOrientation = ori;
  const btnH = document.getElementById("btnLineHoriz");
  const btnV = document.getElementById("btnLineVert");
  if (ori === "horizontal") {
    btnH.className = "px-3 py-2 rounded-lg border border-emerald-500 bg-emerald-500/10 text-emerald-400 font-semibold flex items-center justify-center gap-1.5";
    btnV.className = "px-3 py-2 rounded-lg border border-slate-700 bg-slate-950 text-slate-400 font-semibold flex items-center justify-center gap-1.5";
  } else {
    btnV.className = "px-3 py-2 rounded-lg border border-emerald-500 bg-emerald-500/10 text-emerald-400 font-semibold flex items-center justify-center gap-1.5";
    btnH.className = "px-3 py-2 rounded-lg border border-slate-700 bg-slate-950 text-slate-400 font-semibold flex items-center justify-center gap-1.5";
  }
}

function updateLineSlider(val) {
  currentLineCoord = parseInt(val);
  document.getElementById("lineCoordDisplay").innerText = `${val} px`;
}

async function applyLineConfig() {
  try {
    await fetch("/api/video/control", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action: "set_line",
        orientation: currentLineOrientation,
        coord: currentLineCoord,
      }),
    });
    closeModal("lineModal");
    showToast("Thành công", `Đã cập nhật vạch đếm (${currentLineOrientation}, ${currentLineCoord}px)`, "success");
  } catch (err) {
    showToast("Lỗi", "Không thể cập nhật vạch đếm", "error");
  }
}

// ================= ORDER MANAGEMENT =================
async function fetchOrders() {
  try {
    const res = await fetch("/api/orders");
    if (!res.ok) return;
    const orders = await res.json();

    const tbody = document.getElementById("orderTableBody");
    if (!orders || orders.length === 0) {
      tbody.innerHTML = `<tr><td colspan="3" class="py-4 text-center text-slate-500">Chưa có đơn hàng nào trong CSDL SQLite.</td></tr>`;
      return;
    }

    tbody.innerHTML = orders.map((o) => {
      const itemsStr = (o.items || [])
        .map((it) => `${it.product_name}: ${it.quantity_ordered}`)
        .join(" | ");

      return `
        <tr class="hover:bg-slate-800/40 transition">
          <td class="py-2.5 text-slate-200 font-semibold">
            ${o.customer_name}
          </td>
          <td class="py-2.5 text-slate-400 text-[11px] truncate max-w-[180px]">
            ${itemsStr || "Không có mặt hàng"}
          </td>
          <td class="py-2.5 text-right space-x-1">
            <button onclick="selectActiveOrder(${o.id})" class="px-2 py-1 bg-emerald-600/20 hover:bg-emerald-600/40 border border-emerald-500/40 text-emerald-400 rounded text-[10px] font-semibold transition">
              Chọn đếm
            </button>
            <button onclick="deleteOrder(${o.id})" class="px-2 py-1 bg-rose-600/20 hover:bg-rose-600/40 border border-rose-500/40 text-rose-400 rounded text-[10px] font-semibold transition">
              Xóa
            </button>
          </td>
        </tr>
      `;
    }).join("");

    lucide.createIcons();
  } catch (err) {
    console.error("Order fetch error:", err);
  }
}

async function submitNewOrder() {
  const customerName = document.getElementById("inputCustName").value.trim();
  const qBio = parseInt(document.getElementById("inputQtyBio").value) || 0;
  const qNPK = parseInt(document.getElementById("inputQtyNPK").value) || 0;
  const qDuc = parseInt(document.getElementById("inputQtyDuc").value) || 0;

  if (!customerName) {
    showToast("Cảnh báo", "Vui lòng nhập tên khách hàng", "warning");
    return;
  }

  const items = {
    "Urea_Bio_xanh": qBio,
    "NPK_22-5-6": qNPK,
    "Urea_hat_duc": qDuc,
  };

  try {
    const res = await fetch("/api/orders", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ customer_name: customerName, items }),
    });

    if (res.ok) {
      closeModal("orderModal");
      document.getElementById("inputCustName").value = "";
      fetchOrders();
      showToast("Thành công", `Đã lưu đơn hàng của "${customerName}" vào SQLite!`, "success");
    } else {
      showToast("Lỗi", "Không thể lưu đơn hàng", "error");
    }
  } catch (err) {
    showToast("Lỗi", "Lỗi kết nối cơ sở dữ liệu", "error");
  }
}

async function selectActiveOrder(orderId) {
  try {
    const res = await fetch("/api/orders/select", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ order_id: orderId }),
    });
    if (res.ok) {
      isOrderAlertTriggered = false;
      showToast("Kích hoạt mục tiêu", "Đã gán đơn hàng vào luồng giám sát AI!", "success");
    }
  } catch (err) {
    showToast("Lỗi", "Không thể gán đơn hàng", "error");
  }
}

async function deleteOrder(orderId) {
  if (!confirm("Bạn có chắc chắn muốn xóa đơn hàng này?")) return;
  try {
    const res = await fetch(`/api/orders/${orderId}`, { method: "DELETE" });
    if (res.ok) {
      fetchOrders();
      showToast("Đã xóa", "Đã xóa đơn hàng khỏi CSDL", "success");
    }
  } catch (err) {
    showToast("Lỗi", "Không thể xóa đơn hàng", "error");
  }
}

// ================= SAMPLE VIDEOS =================
async function fetchSampleVideos() {
  try {
    const res = await fetch("/api/sample_videos");
    if (!res.ok) return;
    const files = await res.json();
    const container = document.getElementById("sampleVideoList");

    if (!files || files.length === 0) {
      container.innerHTML = `<span class="text-slate-500 text-[11px]">Không tìm thấy video mẫu trong assets/videos</span>`;
      return;
    }

    container.innerHTML = files.map((f) => `
      <button onclick="selectSource('${f.path.replace(/\\/g, '/')}')" class="w-full text-left px-3 py-2 bg-slate-950 hover:bg-slate-800 border border-slate-700/80 rounded-lg flex items-center justify-between transition">
        <span class="font-medium text-slate-200 text-xs truncate max-w-[260px]">${f.name}</span>
        <span class="text-[10px] text-slate-400 font-mono">${f.size_mb} MB</span>
      </button>
    `).join("");
  } catch (err) {
    console.warn("Fetch sample video err:", err);
  }
}

// ================= EXPORT EXCEL =================
function exportExcelReport() {
  showToast("Xuất Excel", "Đang kết xuất báo cáo thống kê ra file .xlsx...", "info");
  window.open("/api/export_excel", "_blank");
}

// ================= AUDIO CHIME =================
function playOrderCompletedChime() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const notes = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6
    notes.forEach((freq, index) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(freq, ctx.currentTime + index * 0.12);
      gain.gain.setValueAtTime(0.15, ctx.currentTime + index * 0.12);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + index * 0.12 + 0.4);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(ctx.currentTime + index * 0.12);
      osc.stop(ctx.currentTime + index * 0.12 + 0.45);
    });
  } catch (e) {
    console.log("Audio API not available or blocked");
  }
}

// ================= MODAL & TOAST HELPERS =================
function openModal(id) {
  const m = document.getElementById(id);
  if (m) m.classList.remove("hidden");
}

function closeModal(id) {
  const m = document.getElementById(id);
  if (m) m.classList.add("hidden");
}

function showToast(title, message, type = "info") {
  const container = document.getElementById("toastContainer");
  const toast = document.createElement("div");

  let borderCol = "border-cyan-500/50 bg-slate-900/90 text-cyan-300";
  let icon = "info";
  if (type === "success") {
    borderCol = "border-emerald-500/50 bg-slate-900/90 text-emerald-300";
    icon = "check-circle";
  } else if (type === "warning") {
    borderCol = "border-amber-500/50 bg-slate-900/90 text-amber-300";
    icon = "alert-triangle";
  } else if (type === "error") {
    borderCol = "border-rose-500/50 bg-slate-900/90 text-rose-300";
    icon = "alert-octagon";
  }

  toast.className = `glass-panel px-4 py-3 border ${borderCol} rounded-xl shadow-2xl flex items-start gap-3 w-80 transform transition-all duration-300 translate-y-2 opacity-0 text-xs`;
  toast.innerHTML = `
    <i data-lucide="${icon}" class="w-4 h-4 mt-0.5 flex-shrink-0"></i>
    <div class="flex-1">
      <div class="font-bold text-slate-100">${title}</div>
      <div class="text-slate-400 mt-0.5 leading-relaxed">${message}</div>
    </div>
  `;

  container.appendChild(toast);
  lucide.createIcons();

  setTimeout(() => {
    toast.classList.remove("translate-y-2", "opacity-0");
  }, 10);

  setTimeout(() => {
    toast.classList.add("opacity-0", "translate-y-2");
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}
