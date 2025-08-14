## Tham chiếu

Tài liệu này gộp API public, models và utils.

### API public
```python
from src import FlightAgent, BaseAgent, settings, AgentResponse, FlightBookingState, flight_tools
```
- `FlightAgent.run(user_input, thread_id=None, user_id=None, **kwargs) -> AgentResponse`
- `FlightAgent.stream(...) -> Iterator[dict]` với `question_chunk`/`completion_chunk`
- `settings.validate()`, `settings.print_config()`, `settings.create_env_template()`

### Models & State
- Intent/Booking: `IntentClassification`, `BookingInformation`, `FlightBookingState`
- Đặt vé và giỏ hàng: `BookingData`, `Order`, `Cart`, `OrderStatus`, `PaymentStatus`
- Thanh toán: `PaymentMethod`, `PaymentTransaction` (trong `payment_service`)
- `QuestionTemplates`: câu hỏi/hoàn tất theo ngôn ngữ

### Utils/Services
- `cart_service`: tạo order từ booking, giỏ hàng, checkout, cập nhật trạng thái
- `payment_service`: tạo/ xử lý giao dịch, sinh receipt, lịch sử, refund
- `database.db_manager` và `conversation_service`: CRUD hội thoại, summary, thống kê, cleanup
