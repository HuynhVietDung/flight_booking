## Kiến trúc hệ thống

- **Core**: LangGraph `StateGraph` với các node chính: `save_conversation`, `classify_intent`, `collect_info`, `process_booking`, `summarize_conversation`.
- **LLM**: `ChatOpenAI` (model, temperature, max_tokens cấu hình qua `.env`).
- **Tools**: Tập hợp các `@tool` trong `src/tools/flight_tools.py` để tìm chuyến bay, đặt vé, giỏ hàng, thanh toán, thời tiết, tra cứu tình trạng chuyến bay, hoàn tiền,...
- **State**: Kiểu `FlightBookingState` (Pydantic/TypedDict) lưu `messages`, `intent_classification`, `booking_info`, `current_step`, `thread_id`, `user_id`,...
- **Persistence**:
  - Checkpoint LangGraph: `data/langgraph_checkpoints.db`
  - Lưu hội thoại/summarize SQLite: `data/conversations.db` qua `src/utils/database.py`

### Sơ đồ luồng
```
START
 ├─ save_conversation ──> summarize_conversation ──> END
 └─ classify_intent ──(route)──> collect_info ──(route)──> process_booking ──> END
```

### Trách nhiệm từng lớp/chức năng
- `src/agents/base_agent.py`: Khởi tạo LLM, bind tools, biên dịch graph với checkpointer, expose `run()` và `stream()`.
- `src/agents/enhanced_agent.py` (`FlightAgent`): Định nghĩa node logic chi tiết, prompt, parser, routing.
- `src/config/settings.py`: Singleton `settings` gom `LLMConfig`, `AgentConfig`, `BookingConfig`, `MockDataConfig`, load `.env`, validate, tạo thư mục `data/`, `logs/`.
- `src/utils/models.py`: Toàn bộ schema: intent, booking info, order/cart/payment enums & models, `QuestionTemplates` đa ngôn ngữ.
- `src/utils/database.py`: SQLite manager (conversations, entries, summaries) + index, thống kê, cleanup.
- `src/utils/conversation_service.py`: Service mỏng wrap `db_manager` theo domain conversation.
- `src/tools/flight_tools.py`: Các tool thao tác booking, cart, payment, weather, status.

### Quy tắc routing chính
- Confidence thấp → `process_booking` để LLM hỏi rõ.
- `book_flight`/`search_flights` thiếu trường bắt buộc → `collect_info` hỏi bổ sung (streaming câu hỏi theo ngôn ngữ phát hiện).
- Đủ thông tin → `process_booking` thực thi và có thể gọi tool.
