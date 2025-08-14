## Mở rộng và tuỳ biến

### Thêm tool mới
```python
from langchain_core.tools import tool

@tool
def your_custom_tool(arg1: str) -> str:
    """Mô tả chức năng ngắn gọn"""
    return "Kết quả"
```
- Import tool mới vào `src/tools/__init__.py` (nếu có) và thêm vào danh sách `flight_tools`.
- Tool sẽ tự động được bind nhờ `BaseAgent`.

### Thay đổi prompt / logic routing
- Chỉnh trong `src/agents/enhanced_agent.py` các phần: `system_prompts`, `classify_intent` prompt, `collect_booking_info` extraction prompt.
- Điều chỉnh `settings.booking.required_fields` để bổ sung field bắt buộc cho intent.

### Thêm ngôn ngữ hỏi đáp
- Cập nhật `QuestionTemplates` trong `src/utils/models.py` với key ngôn ngữ mới.

### Kết nối API thực tế
- Thay thế mock logic trong `flight_tools.py` bằng gọi API thật (GDS, thời tiết, PSP,...).
- Chuẩn hoá dữ liệu trả về, xử lý lỗi và timeout, thêm tests.

### Lưu trữ/quan sát
- Bổ sung logging/telemetry, thêm chỉ số trong `database.py`/`conversation_service.py` hoặc một storage khác.
