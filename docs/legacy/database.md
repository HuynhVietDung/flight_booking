## Cơ sở dữ liệu và lưu trữ

Có hai cơ sở dữ liệu SQLite độc lập:

1) Checkpoint của LangGraph: `data/langgraph_checkpoints.db`
   - Dùng trong `BaseAgent.compile_graph()` thông qua `SqliteSaver` để checkpoint state theo `thread_id`.
   - Dùng các script `inspect_db.py` để xem nhanh cấu trúc và các checkpoint.

2) CSDL hội thoại: `data/conversations.db`
   - Quản lý qua `src/utils/database.py` (`DatabaseManager`) và `src/utils/conversation_service.py`.
   - Bảng chính:
     - `conversations(thread_id UNIQUE, user_id, created_at, updated_at)`
     - `conversation_entries(thread_id, user_input, assistant_response, session_id, metadata JSON, timestamp)`
     - `conversation_summaries(thread_id UNIQUE, user_id, summary_text, key_points JSON, intent_summary, booking_info JSON)`
   - API chính:
     - Tạo/ghi/xoá hội thoại, thêm entry
     - Lấy danh sách, tóm tắt, thống kê, cleanup theo thời gian

### Công cụ xem và quản trị
- `view_conversations.py`: liệt kê hoặc xem chi tiết hội thoại.
- `view_summaries.py`: xem các bản tóm tắt hội thoại.
- `manage_conversation_db.py`: lệnh `stats`, `list`, `show`, `delete`, `cleanup`, `export`, `search`.
- `inspect_db.py`: kiểm tra database checkpoint LangGraph: bảng, mẫu dữ liệu, tìm kiếm theo nội dung.
