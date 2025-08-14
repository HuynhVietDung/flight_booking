## Ví dụ sử dụng

### Gọi trực tiếp từ Python
```python
from src import FlightAgent

agent = FlightAgent()
resp = agent.run("Mình muốn tìm vé từ Hà Nội đi Tokyo ngày 12/10", thread_id="demo", user_id="u1")
print(resp.intent, resp.confidence)
print(resp.response)
```

### Streaming câu hỏi/gợi ý
```python
for chunk in agent.stream("Tôi muốn đặt vé khứ hồi từ Paris đi Tokyo 15/03", thread_id="demo", user_id="u1"):
    if chunk.get("type") == "question_chunk":
        print(chunk["content"], end="")
    elif chunk.get("type") == "completion_chunk":
        print(chunk["content"], end="")
```

### Quy trình đặt vé mẫu (mock)
1) Tìm chuyến bay bằng `search_flights`
2) Người dùng chọn `flight_number`
3) Gọi `book_flight(...)` để sinh đơn + thêm vào giỏ
4) Dùng `show_payment_methods` và `get_payment_summary(order_id, method)`
5) `confirm_payment(order_id, method, confirm=True)` để thanh toán (mock) và nhận receipt
