## Tiện ích, mô hình dữ liệu và dịch vụ phụ trợ

### `src/utils/models.py`
- Khai báo schema Pydantic cho: `IntentClassification`, `BookingInformation`, `Order`, `Cart`, `PaymentStatus`, `OrderStatus`, ...
- `FlightBookingState`: schema state của LangGraph.
- `QuestionTemplates`: singleton sinh câu hỏi/ thông báo hoàn tất theo ngôn ngữ (`en`, `vi`).

### `src/utils/cart_service.py`
- Quản lý `Cart` theo `user_id`, tạo `Order` từ `booking_data`, thêm vào giỏ, xử lý checkout hàng loạt.
- Tích hợp `payment_service` để tạo transaction và cập nhật trạng thái thanh toán.

### `src/utils/payment_service.py`
- Enum `PaymentMethod`, `PaymentStatus` (riêng của payment service).
- `PaymentTransaction` (Pydantic) + `PaymentService` giả lập xử lý thanh toán: tạo transaction, process, sinh receipt, refund, truy vấn transaction.

### `src/utils/database.py` và `src/utils/conversation_service.py`
- `DatabaseManager`: thao tác SQLite (tạo bảng, CRUD hội thoại, entries, summaries, thống kê, cleanup).
- `ConversationService`: lớp mỏng theo domain, dùng `db_manager` phía dưới.
