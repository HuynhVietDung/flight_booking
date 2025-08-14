## Reference

### Public API
```python
from src import FlightAgent, BaseAgent, settings, AgentResponse, FlightBookingState, flight_tools
```
- `FlightAgent.run(user_input, thread_id=None, user_id=None, **kwargs) -> AgentResponse`
- `FlightAgent.stream(...) -> Iterator[dict]` with `question_chunk`/`completion_chunk`
- `settings.validate()`, `settings.print_config()`, `settings.create_env_template()`

### Models & State
- Intent/Booking: `IntentClassification`, `BookingInformation`, `FlightBookingState`
- Booking/Cart: `BookingData`, `Order`, `Cart`, `OrderStatus`, `PaymentStatus`
- Payment: `PaymentMethod`, `PaymentTransaction` (in `payment_service`)
- `QuestionTemplates` for multilingual prompts/completion

### Utils/Services
- `cart_service`: create orders from bookings, cart ops, checkout, status updates
- `payment_service`: create/process transactions, receipts, history, refunds
- `database.db_manager` & `conversation_service`: CRUD conversations, summaries, stats, cleanup
