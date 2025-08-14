## Công cụ dòng lệnh (CLI) và kịch bản hỗ trợ

### `main.py`
- Ứng dụng console chính: kiểm tra `.env`, validate config, khởi tạo `FlightAgent`, vòng lặp nhập/xuất.
- Lệnh nội bộ: `quit`, `help`, `tools`, `config`, `history`, `summary`, `stream`.
- Tạo `thread_id` ngẫu nhiên cho phiên, `user_id` mẫu.

### `manage_conversation_db.py`
- Lệnh:
  - `stats`: thống kê DB
  - `list [--user USER] [--limit N]`: liệt kê hội thoại
  - `show --thread THREAD_ID`: xem chi tiết hội thoại
  - `delete --thread THREAD_ID`: xoá hội thoại (có xác nhận)
  - `cleanup [--days N]`: dọn hội thoại cũ
  - `export --thread THREAD_ID [--output FILE]`: xuất JSON
  - `search --query TEXT [--user USER]`: tìm theo nội dung

Ví dụ:
```bash
python manage_conversation_db.py stats
python manage_conversation_db.py list --limit 10
python manage_conversation_db.py show --thread <id>
python manage_conversation_db.py export --thread <id> --output out.json
```

### `view_conversations.py`
- `--thread THREAD_ID`: xem chi tiết
- `--list`: liệt kê rút gọn
- Không tham số: in toàn bộ log các hội thoại

### `view_summaries.py`
- Không tham số: liệt kê summaries
- Truyền `THREAD_ID` để xem summary chi tiết

### `inspect_db.py`
- Kiểm tra DB checkpoint LangGraph:
```bash
python inspect_db.py basic
python inspect_db.py detailed
python inspect_db.py threads
python inspect_db.py search "keyword"
```
