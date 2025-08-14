## Bộ tài liệu dự án Flight Booking Agent

Tài liệu này mô tả đầy đủ kiến trúc, thành phần, cách chạy và mở rộng hệ thống đặt vé máy bay sử dụng LangGraph/LangChain.

- **Mục tiêu**: Xây dựng trợ lý Tebby hỗ trợ tìm kiếm, đặt vé, theo dõi thời tiết, trạng thái chuyến bay, quản lý giỏ hàng và thanh toán mô phỏng.
- **Công nghệ chính**: LangGraph, LangChain, Pydantic, SQLite, OpenAI Chat API.

### Mục lục
- Tổng quan: xem `overview.md`
- Cài đặt & Cấu hình: xem `setup_and_config.md`
- Tham chiếu: xem `reference.md`
- Hướng dẫn & Vận hành: xem `howto.md`
- Tổng quan nhanh và cách chạy: xem phần bên dưới

### Cấu trúc dự án
```text
flight_booking/
  ├─ src/
  │  ├─ agents/             # BaseAgent, FlightAgent (enhanced)
  │  ├─ config/             # Settings + .env loader
  │  ├─ tools/              # flight_tools (tập hợp @tool)
  │  └─ utils/              # models, cart_service, payment_service, database, conversation_service
  ├─ data/                  # DB SQLite: conversations.db, langgraph_checkpoints.db
  ├─ main.py                # Ứng dụng tương tác dạng console
  ├─ manage_conversation_db.py / view_*.py / inspect_db.py  # CLI quản trị & kiểm tra
  └─ README.md              # Giới thiệu (tiếng Anh)
```

### Cài đặt nhanh
1) Cài dependencies
```bash
pip install -r requirements.txt
```
2) Khởi chạy lần đầu để sinh `.env` mẫu, rồi nhập API key
```bash
python main.py
# sau đó sửa .env và thêm OPENAI_API_KEY
```
3) Chạy ứng dụng
```bash
python main.py
```

### Liên kết nhanh
- Kiến trúc tổng thể: xem `architecture.md`
- Tham chiếu API trong mã nguồn: xem `api_reference.md`
- Mở rộng thêm tool/agent: xem `extending.md`
