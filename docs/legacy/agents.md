## Agent và luồng xử lý

### `BaseAgent` (`src/agents/base_agent.py`)
- Khởi tạo 2 LLM: `llm` (dùng tool, sinh output người dùng thấy) và `processed_llm` (nhiệt độ thấp để parse JSON).
- `tools`: bind toàn bộ tool từ `src/tools/flight_tools.py`.
- `compile_graph(file_path)`: biên dịch `StateGraph` với checkpointer SQLite (`data/langgraph_checkpoints.db`).
- `run(user_input, thread_id, user_id, ...)`: invoke graph, trả `AgentResponse` (intent, confidence, language, booking_info, response).
- `stream(...)`: stream với `stream_mode="custom"` để phát mảnh câu hỏi/trả lời.

### `FlightAgent` (`src/agents/enhanced_agent.py`)
Node chính:
- `save_conversation`: trích `HumanMessage` + `AIMessage` cuối cùng rồi ghi vào `conversation_service` (SQLite `conversations.db`).
- `classify_intent`: prompt phân loại intent + confidence + reasoning + language (JSONOutputParser → `IntentClassification`).
- `collect_booking_info`:
  - Dựa trên `required_fields` theo intent từ `settings.booking`.
  - Dùng LLM để trích xuất fields còn thiếu từ reasoning, cập nhật `booking_info`.
  - Nếu còn thiếu → stream câu hỏi tự nhiên theo ngôn ngữ (`QuestionTemplates`), trả `current_step=collecting_info` và `action` gợi ý UI.
  - Nếu đủ → stream thông báo hoàn tất và đặt `current_step=info_complete`.
- `process_booking`:
  - Tạo system prompt theo intent và `booking_info` hiện tại.
  - Gọi LLM có bind tools. Nếu có `tool_calls` → thực thi tool và ghép kết quả vào câu trả lời.
- `summarize_conversation`: khi đủ số message (>=5), sinh tóm tắt ngắn bằng LLM và lưu `conversation_summaries`.

Routing:
- `route_based_on_intent`: quyết định `collect_info` vs `process_booking` dựa vào confidence và thiếu field.
- `route_after_collect_info`: nếu vẫn đang `collecting_info` → `END` (đợi người dùng trả lời); nếu `info_complete` → `process_booking`.

### State
- Kiểu `FlightBookingState` gồm: `messages`, `intent_classification`, `booking_info`, `conversation_history`, `current_step`, `data`, `action`, `thread_id`, `user_id`.

### Prompt và streaming
- Sử dụng `ChatPromptTemplate`, `MessagesPlaceholder`, `JsonOutputParser`.
- Streaming chia nhỏ chuỗi qua `chunk_text()` và `get_stream_writer()` để gửi sự kiện `question_chunk`/`completion_chunk`.
