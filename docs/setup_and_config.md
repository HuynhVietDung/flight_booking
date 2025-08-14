## Cài đặt & Cấu hình

Tài liệu này gộp cấu hình `.env` và cơ sở dữ liệu.

### Cấu hình (.env) và Settings
- Settings (singleton) nạp `.env` ở project root; tạo `data/`, `logs/` nếu chưa có.
- Nhóm biến:
  - LLM: `LLM_MODEL`, `LLM_TEMPERATURE`, `LLM_MAX_TOKENS`, `OPENAI_API_KEY`, `OPENAI_BASE_URL`
  - Agent: `INTENT_CONFIDENCE_THRESHOLD`, `DEFAULT_PASSENGERS`, `DEFAULT_CLASS_TYPE`
  - BookingConfig: yêu cầu field theo intent; tên field thân thiện
  - MockDataConfig: airlines, cities (mock)

Mẫu `.env`:
```bash
LLM_MODEL=gpt-4.1-mini
LLM_TEMPERATURE=0
LLM_MAX_TOKENS=1000
INTENT_CONFIDENCE_THRESHOLD=0.6
DEFAULT_PASSENGERS=1
DEFAULT_CLASS_TYPE=economy
OPENAI_API_KEY=your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
```

Validate cấu hình: `settings.validate()` kiểm tra API key, dải nhiệt độ và threshold.

### Cơ sở dữ liệu
- Checkpoint LangGraph: `data/langgraph_checkpoints.db` (dùng trong compile graph qua `SqliteSaver`).
- Hội thoại: `data/conversations.db` quản lý bởi `DatabaseManager`/`ConversationService`.
  - Bảng: `conversations`, `conversation_entries`, `conversation_summaries`.
  - Hỗ trợ: tạo/xoá, thêm entry, tóm tắt, thống kê, cleanup.

Công cụ quản trị:
- `manage_conversation_db.py`: stats, list, show, delete, cleanup, export, search
- `view_conversations.py`, `view_summaries.py`: xem hội thoại/tóm tắt
- `inspect_db.py`: kiểm tra checkpoint của LangGraph

### Bật LangSmith (Tracing)
Thiết lập biến môi trường để bật tracing LangChain/LangGraph:
```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=your-langsmith-api-key
# Tuỳ chọn
export LANGCHAIN_PROJECT=flight-booking-agent
# export LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```
Có thể đặt các biến này trong `.env` để luôn bật khi chạy `python main.py` hoặc `langgraph dev`.

