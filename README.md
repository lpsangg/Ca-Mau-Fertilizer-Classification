# Ca-Mau-Fertilizer-Classification
[Project Overview Website](https://lpsangg.github.io/lpsang/template/project/project-ferterlizer-classification.html)

Hệ thống thị giác máy tính nhận diện, phân loại và đếm tự động bao bì Phân bón Cà Mau theo thời gian thực sử dụng **YOLOv8** và **ByteTrack**, kết hợp giao diện máy tính **PyQt5** và cơ sở dữ liệu **SQLite**.

---

## 🌟 Tính năng nổi bật (Phiên bản mới)
- **Kiến trúc phân tầng chuẩn (Layered Architecture):** Tách bạch rõ ràng giữa Giao diện (UI), Đa luồng (Workers), Trí tuệ nhân tạo (AI Engine) và Cơ sở dữ liệu (Core).
- **Bộ theo dõi ByteTrack hiện đại:** Đồng bộ chính xác 100% giữa mã định danh (Track ID) và loại sản phẩm (Class Name), khắc phục hoàn toàn hiện tượng gán nhầm nhãn.
- **Đếm vector có hướng (Directional Line Crossing):** Đếm chính xác bao phân khi di chuyển qua vạch ảo, chống đếm sót khi frame nhảy cóc.
- **Đa luồng không nghẽn giao diện (QThread):** Xử lý luồng video và mô hình AI trên luồng riêng, giao diện luôn đạt 60 FPS mượt mà.
- **Cơ sở dữ liệu SQLite (Zero-Config):** Cài là chạy ngay, không cần cài đặt hay cấu hình máy chủ MySQL.
- **Bảo mật mật khẩu:** Băm mật khẩu người dùng bằng thuật toán SHA-256 kèm Salt ngẫu nhiên.
- **Đồng bộ Đơn hàng & Bộ đếm:** Cho phép chọn đơn hàng từ giỏ, đặt mục tiêu số lượng và tự động bật thông báo khi băng chuyền đếm đủ hàng.
- **Xuất báo cáo Excel:** Tự động tổng hợp số liệu và xuất ra file `.xlsx` theo thời gian thực.

---

## 🚀 Hướng dẫn cài đặt & Khởi chạy

### 1. Cài đặt môi trường
Khuyến nghị sử dụng Python 3.8 đến 3.12:
```bash
pip install -r requirements.txt
```

### 2. Khởi chạy ứng dụng
- **Cách 1 (Windows - Nhanh nhất):** Nhấp đúp chuột vào file `run.bat`
- **Cách 2 (Dòng lệnh):** Chạy trực tiếp tại thư mục gốc:
```bash
python run_app.py
```

### 3. Tài khoản đăng nhập mặc định
Hệ thống đã tự động khởi tạo sẵn các tài khoản sau trong CSDL SQLite:
- **Tài khoản Quản trị viên (Admin):**
  - Tên đăng nhập: `admin`
  - Mật khẩu: `123456`
- **Tài khoản Người vận hành (Operator / Tương thích phiên bản cũ):**
  - Tên đăng nhập: `phanloaisp`
  - Mật khẩu: `123`
*(Bạn cũng có thể tự tạo tài khoản mới ngay trên màn hình Đăng ký của ứng dụng).*

---

## 📂 Cấu trúc dự án
```text
Ca-Mau-Fertilizer-Classification/
├── run.bat                    # Script khởi chạy nhanh trên Windows (1-click)
├── run_app.py                 # Điểm khởi chạy chính của ứng dụng
├── requirements.txt           # Danh mục thư viện phụ thuộc
├── data/                      # Lưu trữ cơ sở dữ liệu SQLite (fertilizer.db)
├── exports/                   # Thư mục lưu các file báo cáo Excel xuất ra
├── models/                    # Trọng số mô hình YOLOv8n (model_n.pt)
├── docs/                      # Tài liệu kỹ thuật chi tiết
│   └── TONG_QUAN_DU_AN.md     # Tài liệu kiến trúc và phân tích chuyên sâu
└── src/
    ├── config.py              # Cấu hình tập trung đường dẫn tuyệt đối
    ├── core/                  # DatabaseManager (SQLite) & Security (SHA-256)
    ├── ai/                    # FertilizerTracker (YOLOv8 + ByteTrack)
    ├── workers/               # VideoWorker (QThread chạy video ngầm)
    ├── ui/                    # Các controller màn hình (Splash, Login, Order, Video)
    └── utils/                 # Tệp nhãn class.txt và mã nguồn SORT cũ (đối chiếu)
```

## 📖 Tài liệu kỹ thuật
- [Tài liệu tổng quan hệ thống (As-Is Architecture & Phân tích chuyên sâu)](docs/TONG_QUAN_DU_AN.md)
