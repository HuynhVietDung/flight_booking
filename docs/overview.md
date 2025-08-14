## Tổng quan hệ thống

### Giới thiệu
Tebby là trợ lý đặt vé máy bay (demo) xây dựng trên LangGraph/LangChain. Mục tiêu là mô phỏng một quy trình
tư vấn và hỗ trợ đặt vé end-to-end: nhận hiểu ý định, thu thập thông tin còn thiếu, tìm chuyến bay,
đặt vé (mock), quản lý giỏ hàng và thanh toán (mock), đồng thời lưu vết hội thoại/summarize để tra cứu.

### Chức năng chính
- Phân loại ý định (intent) kèm confidence, reasoning, và nhận diện ngôn ngữ
- Thu thập/chốt thông tin đặt vé (hỏi bổ sung đa ngôn ngữ, streaming câu hỏi/gợi ý)
- Tìm chuyến bay (mock), hiển thị giá theo hạng vé và số hành khách
- Đặt vé (mock), tạo Order và thêm vào Cart
- Quản lý giỏ hàng & thanh toán (mock): phương thức thanh toán, tính phí xử lý, xác nhận thanh toán, biên lai
- Tiện ích: tra cứu thời tiết, trạng thái chuyến bay, thông tin/huỷ đặt chỗ (mock)
- Ghi và tóm tắt hội thoại vào SQLite; checkpoint tiến trình bằng LangGraph checkpointer
- Cấu hình qua .env; CLI hỗ trợ xem/tra cứu/xuất hội thoại
- Thiết kế module hoá, dễ mở rộng (tool mới, prompt, routing, thêm ngôn ngữ, tích hợp API thật)


Tài liệu này gộp các nội dung: kiến trúc, agent/luồng xử lý và bộ công cụ (tools).

### Kiến trúc hệ thống

- Core: LangGraph `StateGraph` với các node: `save_conversation`, `classify_intent`, `collect_info`, `process_booking`, `summarize_conversation`.
- LLM: `ChatOpenAI` (cấu hình qua `.env`).
- Tools: tập hợp `@tool` trong `src/tools/flight_tools.py`.
- State: `FlightBookingState` lưu trữ messages, intent, booking_info, current_step, thread_id, user_id.
- Persistence: checkpoint LangGraph `data/langgraph_checkpoints.db`, hội thoại `data/conversations.db`.

Sơ đồ luồng:
```
START
 ├─ save_conversation ──> summarize_conversation ──> END
 └─ classify_intent ──(route)──> collect_info ──(route)──> process_booking ──> END
```

### Agent và luồng xử lý

- BaseAgent: khởi tạo LLM, bind tools, compile graph với checkpointer; `run()` trả `AgentResponse`, `stream()` phát sự kiện `question_chunk`/`completion_chunk`.
- FlightAgent: các node logic
  - save_conversation: lưu lượt hội thoại gần nhất
  - classify_intent: phân loại intent (JSON: intent, confidence, reasoning, language)
  - collect_booking_info: trích xuất/hoàn thiện field còn thiếu, hỏi người dùng (đa ngôn ngữ), cập nhật `booking_info`
  - process_booking: tạo system prompt theo intent, gọi tools khi cần
  - summarize_conversation: tóm tắt khi đủ số lượng tin nhắn
- Routing: thiếu field → collect_info; đủ/đơn giản → process_booking; confidence thấp → process_booking để hỏi rõ.

### Bộ công cụ (Tools)

- search_flights: tìm chuyến bay (mock), tính giá theo `passengers` và `class_type`.
- book_flight: tạo booking (mock), sinh order + add vào cart, hướng dẫn thanh toán.
- get_weather, get_flight_status: tiện ích tra cứu (mock).
- get_booking_info, cancel_booking: thao tác với booking (mock).
- Cart & Payment: `get_cart_summary`, `remove_order_from_cart`, `checkout_cart`, `get_payment_methods`, `show_payment_methods`, `get_payment_summary`, `confirm_payment`, `get_payment_receipt`, `get_user_payment_history`, `refund_payment`, `get_pending_payments`, `cancel_pending_payment`.

Tham khảo chi tiết hàm tại mã nguồn `src/tools/flight_tools.py`.
