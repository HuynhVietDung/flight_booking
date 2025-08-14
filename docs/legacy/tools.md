## Tools

File: `src/tools/flight_tools.py`

Tools use the `@tool` decorator and are bound to the LLM (used in `process_booking`).

### Main tools
- `search_flights(departure_city, arrival_city, date, passengers=1, class_type="economy")`
  - Mock flight search; generates plausible flights if the route is not pre-seeded.
  - Returns a formatted string with flight list and price per class/passengers.

- `book_flight(flight_number, passenger_name, email, passengers=1, class_type="economy", user_id=None)`
  - Mock booking; creates `Order` and adds to user's `Cart`.
  - Does not auto-pay; returns guidance for payment tools.

- `get_weather(city)`: mock weather info.
- `get_flight_status(flight_number)`: mock status + gate.
- `get_booking_info(booking_reference)` / `cancel_booking(booking_reference, email)`: mock booking lookup/cancel.

- `get_cart_summary(user_id)` / `remove_order_from_cart(user_id, order_id)` / `checkout_cart(user_id)`: cart and batch payment operations.

- `get_payment_methods()` / `show_payment_methods()`: list methods, fees, processing time.

- `get_payment_summary(order_id, payment_method)` / `confirm_payment(order_id, payment_method, confirm)`: calculate totals+fees and process payment (mock) with receipt.

- `get_payment_receipt(transaction_id)` / `get_user_payment_history(user_id)` / `refund_payment(transaction_id, reason)`: receipts, history, refund.

- `get_pending_payments(user_id)` / `cancel_pending_payment(order_id)`: list/cancel pending payments.

Notes:
- All data is mock for demo; replace with real APIs in production.
- Integrates with `cart_service` and `payment_service` models in `utils/models.py`.
