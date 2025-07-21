# InfoPCTools

**InfoPCTools** là một ứng dụng Python giúp kiểm tra, thu thập, tổng hợp và xuất báo cáo thông tin phần cứng, phần mềm của máy tính, dành cho người dùng cá nhân, kỹ thuật viên, phòng IT hoặc các tổ chức cần quản lý thiết bị.

---

## Tính năng nổi bật

- **Thu thập thông tin phần cứng:**
  - CPU: model, số nhân, tốc độ xung nhịp, trạng thái sử dụng hiện tại.
  - RAM: tổng dung lượng, dung lượng đã sử dụng, số khe cắm, loại RAM.
  - Ổ cứng: danh sách ổ cứng, loại (HDD/SSD), dung lượng, dung lượng còn trống.
  - Card đồ họa: tên, bộ nhớ, driver.
  - Mainboard: mã sản phẩm, nhà sản xuất, phiên bản BIOS.
  - Thiết bị ngoại vi: bàn phím, chuột, màn hình, máy in.

- **Thu thập thông tin phần mềm:**
  - Hệ điều hành: tên, phiên bản, trạng thái kích hoạt, thời gian khởi động.
  - Danh sách phần mềm đã cài đặt: tên, phiên bản, ngày cài đặt.
  - Thông tin bản cập nhật hệ thống.
  - Dịch vụ đang chạy.

- **Thông tin mạng:**
  - Địa chỉ IP, MAC, DNS.
  - Tốc độ kết nối, trạng thái mạng hiện tại.
  - Liệt kê các adapter mạng.

- **Kiểm tra bảo mật:**
  - Trạng thái tường lửa, phần mềm diệt virus.
  - Liệt kê các cổng đang mở.
  - Thông tin user đang đăng nhập.

- **Xuất báo cáo:**
  - Lưu thông tin thu thập dưới dạng file txt, html hoặc pdf.
  - Hỗ trợ chia sẻ thông tin qua email hoặc mạng nội bộ.

- **Giao diện:**
  - Giao diện dòng lệnh (CLI) đơn giản, dễ sử dụng.
  - Có thể mở rộng giao diện đồ họa (GUI) nếu cần.

---

## Yêu cầu hệ thống

- **Python** >= 3.6
- Hệ điều hành: Windows, Linux, macOS
- Các thư viện phụ thuộc (cài qua pip):  
  - `psutil` (thông tin hệ thống)
  - `platform` (thông tin OS)
  - `socket` (thông tin mạng)
  - `tabulate` (hiển thị bảng)
  - `reportlab` (xuất PDF)
  - `colorama` (màu sắc CLI)
  - Có thể bổ sung các thư viện khác theo nhu cầu.

---

## Cài đặt

1. **Clone repo:**
   ```bash
   git clone https://github.com/khoaiprovip123/InfoPCTools.git
   cd InfoPCTools
   ```

2. **Cài đặt các thư viện phụ thuộc:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Chạy ứng dụng:**
   ```bash
   python main.py
   ```

---

## Sử dụng

- Chạy ứng dụng và làm theo hướng dẫn trên màn hình.
- Các chức năng chính:
  - Xem thông tin tổng quan hệ thống.
  - Xuất báo cáo chi tiết.
  - Kiểm tra bảo mật cơ bản.
  - Lưu thông tin ra file để chia sẻ hoặc lưu trữ.

---

## Mở rộng & đóng góp

- Khuyến khích đóng góp thêm tính năng mới, tối ưu hoặc sửa lỗi.
- Tạo Pull Request hoặc Issue nếu bạn muốn góp ý hoặc báo lỗi.
- Hướng dẫn đóng góp chi tiết trong file `CONTRIBUTING.md` (nếu có).

---

## License

Phần mềm được phát hành theo giấy phép MIT.

---

**Liên hệ & hỗ trợ:**
- Tác giả: [khoaiprovip123](https://github.com/khoaiprovip123)
- Email: (Thêm email nếu muốn)
