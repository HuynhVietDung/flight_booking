## System Overview

### Introduction
Tebby is a demo flight-booking assistant built with LangGraph/LangChain. It simulates an end-to-end travel assistant: intent understanding, information collection, flight search, mock booking, cart and mock payment handling, and conversation storage/summarization.

### Key Features
- Intent classification with confidence, reasoning, and language detection
- Collect/confirm booking info (multilingual prompts, streaming questions/hints)
- Flight search (mock) with pricing by class and passenger count
- Booking (mock), create Order and add to Cart
- Cart & payment (mock): methods, processing fee, payment confirmation, receipt
- Utilities: weather, flight status, booking info/cancellation (mock)
- Persist conversations and summaries in SQLite; checkpoint state with LangGraph
- .env-driven configuration; CLI to inspect/search/export conversations
- Modular, extensible design (new tools, prompts, routing, languages, real APIs)

### Architecture
- Core: LangGraph `StateGraph` with nodes: `save_conversation`, `classify_intent`, `collect_info`, `process_booking`, `summarize_conversation`.
- LLM: `ChatOpenAI` (configured via `.env`).
- Tools: `@tool` functions in `src/tools/flight_tools.py`.
- State: `FlightBookingState` stores messages, intent, booking_info, current_step, thread_id, user_id.
- Persistence: LangGraph checkpoint `data/langgraph_checkpoints.db`, conversation DB `data/conversations.db`.

Flow:
```
START
 ├─ save_conversation ──> summarize_conversation ──> END
 └─ classify_intent ──(route)──> collect_info ──(route)──> process_booking ──> END
```

### Agents & Flow
- BaseAgent: init LLM, bind tools, compile graph with checkpointer; `run()` returns `AgentResponse`, `stream()` emits `question_chunk`/`completion_chunk`.
- FlightAgent nodes
  - save_conversation: persist the latest user/assistant pair
  - classify_intent: JSON result (intent, confidence, reasoning, language)
  - collect_booking_info: extract/complete missing fields, ask user (multilingual), update `booking_info`
  - process_booking: build system prompt by intent, call tools when needed
  - summarize_conversation: summarize when message count is sufficient
- Routing: missing fields → collect_info; simple/complete → process_booking; low confidence → process_booking for clarification.

### Tools (high-level)
- search_flights: mock flight search with class/passenger pricing
- book_flight: mock booking; creates order and adds to cart; guides to payment
- get_weather, get_flight_status: mock utilities
- get_booking_info, cancel_booking: mock booking operations
- Cart & Payment tools: `get_cart_summary`, `remove_order_from_cart`, `checkout_cart`, `get_payment_methods`, `show_payment_methods`, `get_payment_summary`, `confirm_payment`, `get_payment_receipt`, `get_user_payment_history`, `refund_payment`, `get_pending_payments`, `cancel_pending_payment`

See `src/tools/flight_tools.py` for signatures.
