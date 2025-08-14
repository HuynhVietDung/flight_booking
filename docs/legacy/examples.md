## Examples

### Python usage
```python
from src import FlightAgent

agent = FlightAgent()
resp = agent.run("I want to find a flight from Hanoi to Tokyo on 10/12", thread_id="demo", user_id="u1")
print(resp.intent, resp.confidence)
print(resp.response)
```

### Streaming
```python
for chunk in agent.stream("Round-trip Paris to Tokyo on 03/15", thread_id="demo", user_id="u1"):
    if chunk.get("type") == "question_chunk":
        print(chunk["content"], end="")
    elif chunk.get("type") == "completion_chunk":
        print(chunk["content"], end="")
```

### Sample (mock) booking flow
1) Search flights via `search_flights`
2) User picks a `flight_number`
3) Call `book_flight(...)` to create an order and add it to cart
4) Use `show_payment_methods` and `get_payment_summary(order_id, method)`
5) `confirm_payment(order_id, method, confirm=True)` to process mock payment and get a receipt
