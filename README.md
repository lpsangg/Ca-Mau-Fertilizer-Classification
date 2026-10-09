# Ca-Mau-Fertilizer-Classification
[Project Overview Website](https://lpsangg.github.io/lpsang/template/project/project-ferterlizer-classification.html)

Hệ thống thị giác máy tính nhận diện, phân loại và đếm tự động bao bì Phân bón Cà Mau theo thời gian thực sử dụng **YOLOv8** và **ByteTrack**, kết hợp giao diện hiện đại **Modern Web Dashboard (FastAPI + Tailwind CSS + ApexCharts)** và cơ sở dữ liệu **SQLite**.

---

## 🌟 Tính năng nổi bật

### 1. Giao diện Web Hiện đại (Modern Web Dashboard)
- **Giao diện Cyber Industrial Dark Mode:** Thiết kế chuẩn trung tâm điều hành nhà máy thông minh, kính mờ (Glassmorphism), mượt mà 60-120 FPS.
- **Biểu đồ thời gian thực (ApexCharts):** Theo dõi tốc độ băng tải (Bao / Phút) và phân bố tỷ lệ từng dòng sản phẩm với hiệu ứng sóng gradient thời gian thực.
- **Tùy biến Vạch đếm ảo:** Hỗ trợ linh hoạt cả **Băng chuyền Dọc (vạch ngang)** lẫn **Băng chuyền Ngang (vạch dọc)** với thanh trượt tinh chỉnh tọa độ trực tiếp.
- **Đa nền tảng (Web & LAN):** Mở trên bất kỳ trình duyệt nào (Chrome, Edge, Cốc Cốc) hoặc truy cập từ máy tính bảng, điện thoại của quản đốc trong mạng nội bộ nhà máy.
- **Chuông âm thanh thông minh (Web Audio API):** Tự động phát âm báo chúc mừng khi đơn hàng đạt đủ số lượng mục tiêu.

### 2. Kiến trúc & Xử lý AI lõi
- **Kiến trúc phân tầng chuẩn (Layered Architecture):** Tách bạch giữa Backend (FastAPI), Giao diện (Web Frontend), AI Engine (YOLOv8 + ByteTrack) và CSDL (SQLite).
- **Bộ theo dõi ByteTrack hiện đại:** Gắn chặt Track ID với Class Name, khắc phục hoàn toàn hiện tượng gán nhầm nhãn của thuật toán cũ.
- **Cơ sở dữ liệu SQLite (Zero-Config):** Cài là chạy ngay, không cần cấu hình máy chủ MySQL/XAMPP. Mật khẩu băm an toàn với SHA-256 kèm Salt.
- **Xuất báo cáo Excel 1-click:** Tự động kết xuất số liệu đếm và tốc độ băng chuyền ra file `.xlsx` theo thời gian thực.

---

## 🚀 Hướng dẫn cài đặt & Khởi chạy

### 1. Cài đặt môi trường
Khuyến nghị sử dụng Python 3.8 đến 3.12:
```bash
pip install -r requirements.txt
```

### 2. Khởi chạy ứng dụng
- **Cách 1 (Windows - Nhanh nhất):** Nhấp đúp chuột vào file **`run.bat`**
- **Cách 2 (Dòng lệnh):**
```bash
python main.py              # Khởi động server & tự động mở trình duyệt web
python main.py --no-browser # Khởi động chế độ server chạy ngầm
python main.py --server     # Mở mạng LAN (0.0.0.0) cho điện thoại / máy tính bảng
```

---

## 📂 Cấu trúc dự án
```text
Ca-Mau-Fertilizer-Classification/
├── main.py                    # Điểm khởi chạy chính (FastAPI Server + Web Dashboard)
├── run.bat                    # Script khởi chạy nhanh 1-click trên Windows
├── requirements.txt           # Danh mục thư viện phụ thuộc (Web & AI)
├── data/                      # Cơ sở dữ liệu SQLite (fertilizer.db)
├── exports/                   # Thư mục lưu các file báo cáo Excel xuất ra
├── models/                    # Trọng số mô hình YOLOv8n (model_n.pt)
├── assets/
│   ├── videos/demo.mp4        # Video mẫu băng tải phân bón thực tế
│   └── images/                # Logo thương hiệu PVCFC, CTUET
├── docs/                      # Tài liệu kỹ thuật chi tiết
│   └── TONG_QUAN_DU_AN.md     # Tài liệu kiến trúc và phân tích chuyên sâu
└── src/
    ├── config.py              # Cấu hình tập trung đường dẫn tuyệt đối
    ├── core/                  # DatabaseManager (SQLite) & Security (SHA-256)
    ├── ai/                    # FertilizerTracker (YOLOv8 + ByteTrack)
    ├── utils/                 # Tệp nhãn class.txt
    └── web/                   # Module Giao diện Web & REST API
        ├── app.py             # Máy chủ FastAPI Server
        ├── api.py             # REST API routes (Stats, Orders, Video, Export)
        ├── video_stream.py    # Bộ xử lý đa luồng video & AI ByteTrack
        └── static/            # Frontend SPA (HTML5, Tailwind CSS, ApexCharts, JS)
```

## 📖 Tài liệu kỹ thuật
- [Tài liệu tổng quan hệ thống (As-Is Architecture & Phân tích chuyên sâu)](docs/TONG_QUAN_DU_AN.md)
