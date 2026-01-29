# Module Quản lý Tài sản - Odoo 16

## Tổng quan
Module quản lý tài sản chuyên nghiệp với các tính năng:
- ✅ Quản lý thông tin tài sản toàn diện
- ✅ Khấu hao tự động (3 phương pháp)
- ✅ Dashboard phân tích và thống kê
- ✅ Mã QR code cho mỗi tài sản
- ✅ Quản lý bảo trì và sửa chữa
- ✅ Chuyển giao tài sản
- ✅ Kiểm kê định kỳ

## Tính năng nổi bật

### 1. Khấu hao Tự động (3 phương pháp)

#### Phương pháp Đường thẳng (Straight-line)
```
Khấu hao hàng năm = (Giá trị ban đầu - Giá trị thanh lý) / Số năm sử dụng
```
- Khấu hao đều qua các năm
- Phù hợp với tài sản có giá trị giảm đều

#### Phương pháp Số dư Giảm dần (Declining Balance)
```
Khấu hao hàng năm = Giá trị còn lại * (2 / Số năm)
```
- Khấu hao nhiều ở những năm đầu
- Phù hợp với công nghệ, thiết bị điện tử

#### Phương pháp Tổng số Năm (Sum of Years' Digits)
```
Tỷ lệ năm thứ n = (Năm còn lại) / Tổng số năm
Khấu hao năm n = (Giá trị - Thanh lý) * Tỷ lệ năm n
```
- Khấu hao giảm dần theo cấp số cộng
- Cân bằng giữa 2 phương pháp trên

### 2. Dashboard Tổng quan

**KPI Cards:**
- Tổng số tài sản
- Tổng giá trị
- Giá trị còn lại
- Tỷ lệ khấu hao trung bình

**Biểu đồ:**
- Biểu đồ đường: Khấu hao 12 tháng
- Biểu đồ tròn: Phân bố theo loại tài sản

**Cảnh báo:**
- Tài sản cần bảo trì sắp tới
- Tài sản hỏng
- Tài sản sắp hết khấu hao

**Phân tích:**
- Top 10 tài sản giá trị cao
- Thống kê theo trạng thái
- Chi phí bảo trì

### 3. Mã QR Code

Mỗi tài sản tự động tạo QR code chứa:
- Link trực tiếp đến form tài sản
- Thông tin cơ bản
- Dễ dàng in và dán lên tài sản

**Sử dụng:**
- Quét QR bằng điện thoại → Xem thông tin ngay
- In tem QR → Dán lên tài sản
- Kiểm kê nhanh bằng quét QR

### 4. Báo cáo PDF

#### Báo cáo QR Code
- In tem QR code với thông tin tài sản
- Dán lên thiết bị để tra cứu nhanh

#### Báo cáo Khấu hao Chi tiết
- Thông tin tài sản đầy đủ
- Phương pháp tính và kết quả
- Lịch sử khấu hao 12 tháng
- Biểu đồ tiến độ

## Cài đặt

### 1. Cài đặt thư viện Python

```bash
pip install qrcode pillow
```

### 2. Cài đặt Module trong Odoo

1. Copy folder `quan_ly_tai_san` vào `addons/`
2. Restart Odoo server
3. Vào Apps → Update Apps List
4. Tìm "Quản lý Tài sản"
5. Click Install

### 3. Cấu hình

Module tự động cấu hình, không cần thiết lập thêm.

## Sử dụng

### 1. Tạo Tài sản mới

**Menu:** Quản lý Tài sản → Tài sản → Create

**Thông tin cơ bản:**
- Mã tài sản (tự động)
- Tên tài sản
- Loại (Máy tính, Thiết bị, Xe cộ, Bàn ghế...)
- Phòng ban
- Người sử dụng (tùy chọn)

**Thông tin mua sắm:**
- Ngày mua
- Giá trị
- Nhà cung cấp
- Hóa đơn

**Khấu hao:**
- Giá trị thanh lý dự kiến
- Ngày bắt đầu sử dụng
- Phương pháp khấu hao (3 lựa chọn)
- Thời gian khấu hao (năm)

→ Hệ thống tự động tính:
- Tỷ lệ khấu hao năm
- Khấu hao hàng năm
- Khấu hao hàng tháng
- Tổng đã khấu hao
- Giá trị còn lại
- Tỷ lệ hoàn thành (%)

### 2. Xem Dashboard

**Menu:** Quản lý Tài sản → Dashboard

Xem tổng quan:
- KPI tổng hợp
- Biểu đồ khấu hao
- Phân bố tài sản
- Cảnh báo bảo trì
- Top tài sản giá trị cao

Click vào các card để xem chi tiết.

### 3. Quản lý Bảo trì

**Menu:** Quản lý Tài sản → Bảo trì

**Tạo lịch bảo trì:**
1. Click Create
2. Chọn tài sản
3. Nhập ngày bảo trì
4. Mô tả công việc
5. Chi phí (nếu có)
6. Chu kỳ bảo trì tiếp theo

**Trạng thái:**
- Chờ thực hiện
- Đang thực hiện
- Hoàn thành

### 4. In QR Code

**Cách 1: Từ form tài sản**
- Mở tài sản → Print → In mã QR Tài sản

**Cách 2: Từ list view**
- Chọn nhiều tài sản → Print → In mã QR Tài sản

→ Tạo PDF với QR code, in và dán lên tài sản.

### 5. Xem Báo cáo Khấu hao

**Menu:** Quản lý Tài sản → Báo cáo Khấu hao

**Views:**
- **Tree:** Danh sách lịch sử khấu hao
- **Pivot:** Phân tích theo nhiều chiều
- **Graph:** Biểu đồ trực quan

**Xuất báo cáo PDF:**
- Mở tài sản → Print → Báo cáo Khấu hao Chi tiết

### 6. Chuyển giao Tài sản

**Menu:** Quản lý Tài sản → Chuyển giao

1. Click Create
2. Chọn tài sản
3. Phòng ban/Người từ → Phòng ban/Người đến
4. Lý do chuyển giao
5. Submit

→ Hệ thống tự động cập nhật vị trí tài sản.

### 7. Kiểm kê Định kỳ

**Menu:** Quản lý Tài sản → Kiểm kê

1. Click Create
2. Nhập thông tin đợt kiểm kê
3. Thêm chi tiết kiểm kê (tài sản + trạng thái)
4. Xác nhận

## Cấu trúc Module

```
quan_ly_tai_san/
├── models/
│   ├── tai_san.py                 # Model chính
│   ├── khau_hao_tai_san.py       # Lịch sử khấu hao
│   ├── dashboard_tai_san.py       # Dashboard
│   ├── bao_tri_tai_san.py        # Bảo trì
│   ├── chuyen_giao_tai_san.py    # Chuyển giao
│   ├── kiem_ke_tai_san.py        # Kiểm kê
│   └── ...
├── views/
│   ├── tai_san_views.xml
│   ├── dashboard_views.xml
│   ├── report_templates.xml       # PDF reports
│   └── ...
├── static/
│   ├── src/
│   │   ├── js/
│   │   │   └── dashboard.js       # Dashboard JS
│   │   ├── css/
│   │   │   └── dashboard.css      # Dashboard CSS
│   │   └── xml/
│   │       └── dashboard_templates.xml  # QWeb templates
├── security/
│   └── ir.model.access.csv
├── data/
│   └── tai_san_sequence.xml
├── __init__.py
├── __manifest__.py
└── README.md (this file)
```

## API / RPC Methods

### Dashboard Data
```python
self.env['dashboard.tai_san'].get_dashboard_data()
```
Trả về: Dict với tất cả dữ liệu dashboard

### Tài sản theo Phòng ban
```python
self.env['dashboard.tai_san'].get_tai_san_theo_phong_ban()
```

### Xuất Báo cáo Khấu hao
```python
self.env['dashboard.tai_san'].export_bao_cao_khau_hao(year=2024)
```

## Lưu ý Kỹ thuật

### Khấu hao
- Computed fields: `@api.depends(['gia_tri', 'thoi_gian_khau_hao', ...])`
- Tính toán lại khi thay đổi giá trị/thời gian
- Không lưu trong DB, tính realtime

### QR Code
- Tạo tự động khi lưu record
- Format: PNG base64
- URL: `/web#id={id}&model=tai_san&view_type=form`

### Dashboard
- TransientModel (không lưu DB)
- Dữ liệu tính realtime từ tài sản
- Sử dụng Chart.js cho biểu đồ

### Performance
- Index trên `ma_tai_san`, `phong_ban_id`
- Computed fields có `store=False`
- Dashboard cache trong session

## Tương thích

- **Odoo Version:** 16.0
- **Python:** 3.10+
- **Database:** PostgreSQL 12+
- **Dependencies:**
  - base
  - mail
  - web
  - quan_ly_nhan_su

## Giấy phép

LGPL-3 License

## Tác giả

**Nhóm 4 - TTDN-16-05-N4**
- GitHub: https://github.com/Nemmer772004/TTDN-16-05-N4
- Kế thừa từ: Nhóm 8 (TTDN-15-05-N8)

## Changelog

### Version 2.0 (2024)
- ✅ Thêm 3 phương pháp khấu hao
- ✅ Dashboard tổng quan
- ✅ QR code tự động
- ✅ Báo cáo PDF chuyên nghiệp
- ✅ Cải tiến giao diện
- ✅ Tối ưu performance

### Version 1.0 (2023)
- Phiên bản đầu tiên từ Nhóm 8
- Các tính năng cơ bản

## Hỗ trợ

Nếu gặp vấn đề, vui lòng tạo Issue trên GitHub hoặc liên hệ nhóm phát triển.
