## Lỗi thường gặp và cách khắc phục

- Không có `.env` hoặc thiếu `OPENAI_API_KEY`
  - Chạy `python main.py` lần đầu để sinh mẫu `.env` hoặc tự tạo và thêm API key.

- `Configuration validation failed`
  - Kiểm tra dải `LLM_TEMPERATURE` (0..2), `INTENT_CONFIDENCE_THRESHOLD` (0..1), và API key.

- Tool không chạy hoặc kết quả rỗng
  - Kiểm tra tham số đầu vào (đủ trường required chưa). Với `book_flight` cần `flight_number`, `passenger_name`, `email`...

- Không thấy lịch sử hội thoại
  - Xem `data/conversations.db`. Dùng `python manage_conversation_db.py list` hoặc `view_conversations.py`.

- Checkpoint không được cập nhật
  - Kiểm tra quyền ghi vào `data/langgraph_checkpoints.db` và `thread_id` khi gọi `run()`/`stream()`.

- Tiếng Việt/tiếng Anh hiển thị chưa tự nhiên
  - Cập nhật `QuestionTemplates` hoặc prompt trong `enhanced_agent.py`.
