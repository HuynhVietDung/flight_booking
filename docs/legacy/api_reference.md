## Tham chiếu API (public trong `src/`)

### Import nhanh
```python
from src import FlightAgent, BaseAgent, settings, AgentResponse, FlightBookingState, flight_tools
```

### `FlightAgent`
- `run(user_input: str, thread_id: str=None, user_id: str=None, **kwargs) -> AgentResponse`
- `stream(...) -> Iterator[dict]` với sự kiện `question_chunk`/`completion_chunk`.

### `AgentResponse`
- Trường: `success`, `intent`, `confidence`, `response`, `language`, `booking_info`, `error`.

### `settings`
- `settings.validate()` kiểm tra cấu hình.
- `settings.print_config()` (được gọi trong `main.py`).
- `settings.create_env_template()` (được gọi khi chưa có `.env`).

### Tools
- Tham khảo file `docs/tools.md` để xem chữ ký hàm và mô tả chi tiết.

### Models chính
- `BookingInformation`, `Order`, `Cart`, `PaymentTransaction`, enums `OrderStatus`, `PaymentStatus`, `PaymentMethod`.

### State
- `FlightBookingState`: dùng trong LangGraph để chuyển dữ liệu giữa các node.
