## Utilities, Data Models, and Auxiliary Services

### `src/utils/models.py`
- Pydantic schemas: `IntentClassification`, `BookingInformation`, `Order`, `Cart`, `PaymentStatus`, `OrderStatus`, ...
- `FlightBookingState` for LangGraph state.
- `QuestionTemplates`: multilingual question/completion templates (`en`, `vi`).

### `src/utils/cart_service.py`
- Manages `Cart` per `user_id`, creates `Order` from `booking_data`, adds to cart, processes batch checkout.
- Integrates `payment_service` for transactions and payment status updates.

### `src/utils/payment_service.py`
- Enums: `PaymentMethod`, `PaymentStatus` (service-specific).
- `PaymentTransaction` (Pydantic) + `PaymentService`: mock payment processing; create, process, receipt, refund, get transaction(s).

### `src/utils/database.py` and `src/utils/conversation_service.py`
- `DatabaseManager`: SQLite CRUD (conversations, entries, summaries), stats, cleanup.
- `ConversationService`: thin domain wrapper over `db_manager`.
