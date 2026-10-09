# Ca-Mau-Fertilizer-Classification
[Project Overview Website](https://lpsangg.github.io/lpsang/template/project/project-ferterlizer-classification.html)

Hệ thống thị giác máy tính nhận diện, phân loại và đếm tự động bao bì Phân bón Cà Mau theo thời gian thực sử dụng **YOLOv8** và **ByteTrack**, tích hợp giao diện hiện đại **Modern Industrial Web Dashboard (FastAPI + PyWebView)** và phiên bản **PyQt5 Desktop**, lưu trữ cơ sở dữ liệu **SQLite**.

---

## 🌟 Tính năng nổi bật

### 1. Modern Web & Desktop Dashboard (Công nghệ mới nhất)
- **Giao diện Cyber Industrial Dark Mode:** Thiết kế đẳng cấp trung tâm điều hành nhà máy thông minh, kính mờ (Glassmorphism), mượt mà 60-120 FPS.
- **Biểu đồ thời gian thực (ApexCharts):** Theo dõi tốc độ băng tải (Bao / Phút) và phân bố tỷ lệ từng dòng sản phẩm với hiệu ứng gradient sóng thời gian thực.
- **Tùy biến Vạch đếm ảo:** Hỗ trợ linh hoạt cả **Băng chuyền Dọc (vạch ngang)** lẫn **Băng chuyền Ngang (vạch dọc)** với thanh trượt tinh chỉnh tọa độ trực tiếp.
- **Đa nền tảng (Desktop & Web/LAN):** Chạy như phần mềm Desktop độc lập (nhờ Microsoft Edge WebView2) hoặc mở từ máy tính bảng/điện thoại của quản đốc trong mạng nội bộ nhà máy.
- **Chuông âm thanh thông minh (Web Audio API):** Tự động phát âm báo chúc mừng khi đơn hàng đạt đủ số lượng mục tiêu.

### 2. Kiến trúc & Xử lý AI lõi
- **Kiến trúc phân tầng chuẩn (Layered Architecture):** Tách bạch giữa Backend (FastAPI), Giao diện (Web/PyWebView/Qt), AI Engine (YOLOv8 + ByteTrack) và CSDL (SQLite).
- **Bộ theo dõi ByteTrack hiện đại:** Gắn chặt Track ID với Class Name, khắc phục hoàn toàn hiện tượng nhảy nhãn của thuật toán SORT cũ.
- **Cơ sở dữ liệu SQLite (Zero-Config):** Cài là chạy ngay, không cần cấu hình MySQL/XAMPP. Mật khẩu băm an toàn với SHA-256 kèm Salt.
- **Xuất báo cáo Excel 1-click:** Tự động kết xuất số liệu đếm và tốc độ băng chuyền ra file `.xlsx`.

---

## 🚀 Hướng dẫn cài đặt & Khởi chạy

### 1. Cài đặt môi trường
Khuyến nghị sử dụng Python 3.8 đến 3.12:
```bash
pip install -r requirements.txt
```

### 2. Khởi chạy ứng dụng

#### 🌟 Cách 1: Giao diện Modern Web-based Dashboard (Khuyên dùng)
- **Khởi chạy nhanh trên Windows:** Nhấp đúp chuột vào file **`run_web.bat`**
- **Hoặc chạy bằng dòng lệnh:**
```bash
python run_web_app.py             # Mở cửa sổ Desktop App (PyWebView)
python run_web_app.py --browser   # Mở trực tiếp trên Trình duyệt web
python run_web_app.py --server    # Chạy làm máy chủ nội bộ cho máy tính bảng/LAN
```

#### 📦 Cách 2: Giao diện PyQt5 truyền thống (Desktop cũ)
- **Khởi chạy nhanh:** Nhấp đúp chuột vào file **`run.bat`**
- **Dòng lệnh:** `python run_app.py`

---

## 📂 Cấu trúc dự án
```text
Ca-Mau-Fertilizer-Classification/
├── run_web.bat                # Khởi chạy Modern Web Dashboard (1-click)
├── run_web_app.py             # Launcher Desktop App (FastAPI + PyWebView)
├── run.bat                    # Khởi chạy giao diện PyQt5 cũ (1-click)
├── run_app.py                 # Launcher giao diện PyQt5 cũ
├── requirements.txt           # Danh mục thư viện phụ thuộc
├── data/                      # Cơ sở dữ liệu SQLite (fertilizer.db)
├── exports/                   # Thư mục lưu các file báo cáo Excel xuất ra
├── models/                    # Trọng số mô hình YOLOv8n (model_n.pt)
├── assets/
│   ├── videos/demo.mp4        # Video mẫu băng tải phân bón thực tế
│   └── images/ & icons/       # Logo thương hiệu PVCFC, CTUET
├── docs/                      # Tài liệu kiến trúc kỹ thuật
└── src/
    ├── web/                   # Module Modern Web-based Dashboard
    │   ├── app.py             # FastAPI App Server
    │   ├── api.py             # REST API routes (Stats, Orders, Video, Export)
    │   ├── video_stream.py    # Bộ xử lý stream video & AI ByteTrack
    │   └── static/            # Frontend SPA (HTML5, Tailwind CSS, ApexCharts, JS)
    ├── config.py              # Cấu hình tập trung đường dẫn tuyệt đối
    ├── core/                  # DatabaseManager (SQLite) & Security (SHA-256)
    ├── ai/                    # FertilizerTracker (YOLOv8 + ByteTrack)
    ├── workers/               # VideoWorker đa luồng (QThread)
    ├── ui/                    # Các controller giao diện PyQt5 cũ
    └── utils/                 # Tệp nhãn class.txt và thuật toán SORT cũ đối chiếu
```

## 📖 Tài liệu kỹ thuật
- [Tài liệu tổng quan hệ thống (As-Is Architecture & Phân tích chuyên sâu)](docs/TONG_QUAN_DU_AN.md)
