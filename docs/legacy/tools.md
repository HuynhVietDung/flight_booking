## Bộ công cụ (Tools)

File: `src/tools/flight_tools.py`

Các tool sử dụng decorator `@tool`, được bind vào LLM để gọi theo nhu cầu trong `process_booking`.

### Danh sách tool chính
- `search_flights(departure_city, arrival_city, date, passengers=1, class_type="economy")`
  - Tìm chuyến bay (mock). Nếu route chưa có sẵn, sinh ngẫu nhiên dữ liệu hợp lý.
  - Output là chuỗi mô tả danh sách chuyến bay và giá tính theo `passengers` và `class_type`.

- `book_flight(flight_number, passenger_name, email, passengers=1, class_type="economy", user_id=None)`
  - Tạo booking (mock), sinh `booking_ref`, tính giá, và đồng thời tạo `Order` + add vào `Cart` của user.
  - Không auto thanh toán. Hướng dẫn người dùng xem phương thức thanh toán và thực hiện.

- `get_weather(city)`
  - Trả về thông tin thời tiết (mock) theo thành phố.

- `get_flight_status(flight_number)`
  - Mô phỏng trạng thái chuyến bay + cửa ra (gate).

- `get_booking_info(booking_reference)` / `cancel_booking(booking_reference, email)`
  - Tra cứu thông tin booking hoặc huỷ booking (mock).

- `get_cart_summary(user_id)` / `remove_order_from_cart(user_id, order_id)` / `checkout_cart(user_id)`
  - Quản lý giỏ hàng và thanh toán hàng loạt.

- `get_payment_methods()` / `show_payment_methods()`
  - Liệt kê phương thức thanh toán, phí xử lý, thời gian xử lý.

- `get_payment_summary(order_id, payment_method)` / `confirm_payment(order_id, payment_method, confirm)`
  - Xem chi tiết số tiền cần trả, phí xử lý; xác nhận và tiến hành thanh toán (mock), sinh receipt.

- `get_payment_receipt(transaction_id)` / `get_user_payment_history(user_id)` / `refund_payment(transaction_id, reason)`
  - Xem hoá đơn, lịch sử thanh toán, hoàn tiền.

- `get_pending_payments(user_id)` / `cancel_pending_payment(order_id)`
  - Liệt kê các đơn chưa thanh toán và huỷ thanh toán đang chờ.

### Lưu ý
- Tất cả dữ liệu là mock, phục vụ demo. Trong production cần kết nối API thực (GDS, PSP,...).
- Tích hợp với `cart_service` và `payment_service` qua các model trong `utils/models.py`.
