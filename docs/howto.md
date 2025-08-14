## Hướng dẫn & Vận hành

Tài liệu này hướng dẫn run graph.


### Chạy ứng dụng
```bash
pip install -r requirements.txt
python main.py
```
Lệnh trong ứng dụng: `quit`, `help`, `tools`, `config`, `history`, `summary`, `stream`.

### Chạy với LangGraph Studio (Recommendation)
Đã cài qua requirements. Từ thư mục gốc dự án:
```bash
langgraph dev
```
- Studio sẽ tự đọc `langgraph.json` (đã khai báo graph `flight_booking_agent`).
- Biến môi trường `LANGCHAIN_API_KEY` được nạp từ `.env` (trường `env` trong `langgraph.json`).
- Mở URL Studio hiển thị trong terminal để gửi message, xem state, checkpoint, và luồng node.


### Ví dụ Python
```python
from src import FlightAgent
agent = FlightAgent()
resp = agent.run("Tìm vé từ Hà Nội đi Tokyo 12/10", thread_id="demo", user_id="u1")
print(resp.intent, resp.confidence)
print(resp.response)
```
Streaming:
```python
for chunk in agent.stream("Đặt vé khứ hồi Paris-Tokyo 15/03", thread_id="demo", user_id="u1"):
    if chunk.get("type") == "question_chunk":
        print(chunk["content"], end="")
    elif chunk.get("type") == "completion_chunk":
        print(chunk["content"], end="")
```

### Công cụ CLI
```bash
python manage_conversation_db.py stats
python manage_conversation_db.py list --limit 10
python manage_conversation_db.py show --thread <id>
python manage_conversation_db.py export --thread <id> --output out.json
python view_conversations.py --list
python view_summaries.py
python inspect_db.py detailed
```

### Troubleshooting nhanh
- Thiếu `.env`/`OPENAI_API_KEY`: chạy `python main.py` để sinh template rồi thêm key
- Validation fail: kiểm tra nhiệt độ (0..2), threshold (0..1)
- Không thấy hội thoại: dùng script `view_conversations.py` hoặc `manage_conversation_db.py list`
- Streaming/route không như mong đợi: xem prompt/`QuestionTemplates`

### Mở rộng
- Thêm tool mới với `@tool` và đưa vào `flight_tools`
- Sửa prompt/routing trong `enhanced_agent.py`; cập nhật `settings.booking.required_fields`
- Thêm ngôn ngữ trong `QuestionTemplates`
- Tích hợp API thực thay cho mock trong `flight_tools.py`

