# Đặc tả Ứng dụng Giám sát Hệ thống

## Mô tả Giao diện Người dùng (UI)

Ứng dụng được thiết kế với bố cục hai cột đơn giản và hiện đại:

### Thanh điều hướng bên trái (Sidebar)

**Trên cùng:** LOGO của ứng dụng

**Khu vực Menu:** Danh sách các chức năng chính, được sắp xếp theo chiều dọc. Mỗi mục là một nút bấm để chuyển đổi nội dung hiển thị ở khung bên phải.

- 📊 Dashboard (Bảng điều khiển)
- ⚙️ Thông tin Phần cứng
- 📦 Ứng dụng
- 🛡️ Bảo mật
- 🌐 Mạng
- 🛠️ Sửa chữa & Khôi phục
- ℹ️ Thông tin

### Khung nội dung chính (Main Content Area)

Đây là khu vực hiển thị chi tiết nội dung tương ứng với mục menu được chọn ở thanh bên trái. Mỗi menu sẽ có một giao diện riêng biệt.

---

## Mô tả Chi tiết các Tính năng và Giao diện tương ứng

### 1. 📊 Dashboard

**Mục đích:** Cung cấp cái nhìn tổng quan, thời gian thực về hiệu suất của hệ thống.

**Giao diện:**

- **CPU:** Một biểu đồ tròn (gauge chart) hoặc biểu đồ đường (line chart) hiển thị % tải hiện tại. Kèm theo thông tin về nhiệt độ (nếu có thể).
- **RAM:** Một biểu đồ tròn hiển thị % RAM đã sử dụng. Kèm theo văn bản chi tiết (ví dụ: 8.1/16 GB).
- **GPU:** Một biểu đồ tròn hiển thị % tải hiện tại và nhiệt độ.
- **Ổ cứng:** Danh sách các ổ đĩa, mỗi ổ có một thanh tiến trình (progress bar) hiển thị % dung lượng đã sử dụng.
- **Mạng:** Hai đồng hồ hoặc biểu đồ hiển thị tốc độ Tải xuống (Download) và Tải lên (Upload) theo thời gian thực (đơn vị Mbps hoặc MB/s).

### 2. ⚙️ Thông tin Phần cứng

**Mục đích:** Liệt kê toàn bộ thông tin chi tiết về các linh kiện phần cứng của máy.

**Giao diện:** Một danh sách các mục, mỗi mục gồm "Thuộc tính" và "Giá trị".

- **Hệ thống:** Loại máy (Desktop/Laptop), Tên máy, Nhà sản xuất.
- **Hệ điều hành:** Tên (ví dụ: Windows 11 Pro), Phiên bản, Build.
- **CPU:** Tên đầy đủ (ví dụ: Intel Core i7-10700K), Số lõi, Số luồng, Tốc độ xung nhịp.
- **RAM:** Tổng dung lượng, Loại (DDR4), Tốc độ, Số khe cắm đã dùng.
- **GPU:** Tên đầy đủ (ví dụ: NVIDIA GeForce RTX 3080), Dung lượng VRAM.
- **Ổ cứng:** Danh sách các ổ đĩa với Tên Model, Loại (SSD/HDD), Dung lượng.
- **Card mạng:** Tên các card mạng (Ethernet, Wi-Fi).
- **Màn hình:** Tên màn hình, Độ phân giải, Tần số quét.

### 3. 📦 Ứng dụng

**Mục đích:** Quản lý các phần mềm đã cài đặt và các ứng dụng khởi động cùng hệ thống.

**Giao diện:** Được chia làm hai tab hoặc hai khu vực riêng biệt.

**Ứng dụng đã cài đặt:**
- Một bảng (table) liệt kê tất cả phần mềm. Các cột bao gồm: Tên ứng dụng, Nhà phát hành, Ngày cài đặt, Kích thước.
- Ở cuối mỗi hàng sẽ có một nút "Gỡ cài đặt".

**Khởi động cùng hệ thống (Startup Apps):**
- Một danh sách các ứng dụng được cấu hình để tự động chạy khi bật máy.
- Mỗi ứng dụng có một công tắc Bật/Tắt (Enable/Disable) bên cạnh.

### 4. 🛡️ Bảo mật

**Mục đích:** Kiểm tra nhanh các cài đặt bảo mật cơ bản của Windows.

**Giao diện:** Một danh sách trạng thái.

- **Tường lửa (Firewall):** Trạng thái Bật hoặc Tắt. Có nút để mở cài đặt tường lửa của Windows.
- **Windows Update:** Trạng thái cập nhật (ví dụ: Đã cập nhật hoặc Có bản cập nhật mới). Nút để chạy Windows Update.
- **Antivirus:** Tên phần mềm Antivirus đang hoạt động, trạng thái định nghĩa virus (Cập nhật hoặc Lỗi thời).

### 5. 🌐 Mạng

**Mục đích:** Hiển thị thông tin cấu hình mạng và các kết nối đang hoạt động.

**Giao diện:** Chia làm hai phần.

**Cấu hình mạng:**
- Hiển thị thông tin của card mạng đang hoạt động: Địa chỉ IP, Subnet Mask, Default Gateway, DNS Servers.
- Cho biết IP là động (DHCP) hay tĩnh (Static).

**Ứng dụng đang truy cập mạng:**
- Một bảng liệt kê các tiến trình (processes) đang sử dụng mạng, địa chỉ IP kết nối đến, và cổng (port).

### 6. 🛠️ Sửa chữa & Khôi phục

**Mục đích:** Cung cấp các công cụ nhanh để chẩn đoán, sửa lỗi và sao lưu hệ thống.

**Giao diện:** Một loạt các nút bấm, mỗi nút thực hiện một chức năng cụ thể.

- **Kiểm tra tệp hệ thống:** Nút "Quét và sửa lỗi hệ thống" (chạy lệnh sfc /scannow).
- **Sửa lỗi máy in:** Nút "Gỡ rối dịch vụ in" (xóa hàng đợi in, khởi động lại spooler).
- **Gỡ cài đặt máy in:** Nút để mở trình quản lý thiết bị và máy in.
- **Tạo điểm khôi phục:** Nút "Tạo điểm khôi phục hệ thống".
- **Sao lưu Drivers:** Nút "Sao lưu toàn bộ trình điều khiển (drivers)".

### 7. ℹ️ Thông tin

**Mục đích:** Hiển thị thông tin về chính ứng dụng.

**Giao diện:** Văn bản đơn giản.

- Tên ứng dụng, phiên bản.
- Thông tin về tác giả/nhà phát triển.
- Liên kết đến trang chủ hoặc kho mã nguồn (GitHub).

---

## Danh sách Công việc (Task List) cho việc Phát triển bằng Python

Đây là các công việc được chia nhỏ để xây dựng dự án.

| # | Task (Công việc) | Mô tả Giao diện cần Xây dựng | Thư viện Python gợi ý |
|---|---|---|---|
| 1 | Xây dựng Giao diện Chính | Tạo cửa sổ chính, thanh điều hướng bên trái (với logo và các nút menu), và khung nội dung trống bên phải. | tkinter, PyQt5, PySide6 |
| 2 | Lập trình Module Dashboard | Trong khung nội dung, tạo các biểu đồ tròn, biểu đồ đường và nhãn văn bản. Lập trình logic để lấy và cập nhật dữ liệu CPU, RAM, GPU, Disk, Network theo thời gian thực. | psutil, matplotlib (để vẽ biểu đồ), py-cpuinfo |
| 3 | Lập trình Module Thông tin Phần cứng | Tạo một khung có thể cuộn (scrollable frame). Lập trình logic để lấy thông tin tĩnh về hệ điều hành, CPU, RAM, GPU, ổ cứng... và hiển thị dưới dạng danh sách "Key: Value". | wmi, platform, psutil |
| 4 | Lập trình Module Ứng dụng | Tạo giao diện với hai tab. Tab 1: Tạo một bảng (TreeView) để hiển thị danh sách ứng dụng. Tab 2: Tạo một danh sách với các nút gạt (checkbox/toggle). Lập trình logic để đọc registry, thực thi lệnh gỡ cài đặt và quản lý startup apps. | winreg, subprocess |
| 5 | Lập trình Module Bảo mật | Tạo giao diện hiển thị văn bản và các nút bấm. Lập trình logic để kiểm tra trạng thái tường lửa, Windows Defender/Antivirus thông qua các lệnh command-line hoặc API của Windows. | subprocess, os |
| 6 | Lập trình Module Mạng | Tạo giao diện với hai phần. Phần 1: Hiển thị văn bản tĩnh. Phần 2: Tạo một bảng (TreeView) để cập nhật liên tục. Lập trình logic lấy cấu hình IP và quét các kết nối mạng đang hoạt động. | psutil, socket |
| 7 | Lập trình Module Sửa chữa & Khôi phục | Tạo giao diện gồm các nút bấm. Gán mỗi nút với một hàm Python để thực thi các lệnh hệ thống tương ứng (ví dụ: sfc /scannow, net stop spooler). | subprocess, os |
| 8 | Lập trình Module Thông tin | Tạo một trang văn bản đơn giản hiển thị thông tin về ứng dụng. | tkinter.Label, PyQt.QLabel |
| 9 | Hoàn thiện và Đóng gói | Tinh chỉnh giao diện, xử lý lỗi, tối ưu hiệu năng và đóng gói dự án thành một file thực thi (.exe). | PyInstaller, cx_Freeze |

---

## Ghi chú Phát triển

**[Chưa xác minh]** Đây là đặc tả dự án dựa trên tài liệu được cung cấp, không có thông tin xác thực về tính khả thi hoặc hiệu quả của các thư viện được đề xuất.

**[Suy luận]** Dự án này có vẻ phù hợp cho việc phát triển ứng dụng giám sát hệ thống Windows sử dụng Python, nhưng cần kiểm tra khả năng tương thích và quyền truy cập hệ thống cần thiết.