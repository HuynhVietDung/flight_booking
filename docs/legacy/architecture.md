## Architecture

- Core: LangGraph `StateGraph` with main nodes: `save_conversation`, `classify_intent`, `collect_info`, `process_booking`, `summarize_conversation`.
- LLM: `ChatOpenAI` (configured via `.env`).
- Tools: `@tool` functions in `src/tools/flight_tools.py` for flight search/booking, cart, payment, weather, flight status, refunds, etc.
- State: `FlightBookingState` (TypedDict) holds `messages`, `intent_classification`, `booking_info`, `current_step`, `thread_id`, `user_id`, ...
- Persistence:
  - LangGraph checkpoint: `data/langgraph_checkpoints.db`
  - Conversations and summaries: `data/conversations.db` driven by `src/utils/database.py`

### Flow
```
START
 ├─ save_conversation ──> summarize_conversation ──> END
 └─ classify_intent ──(route)──> collect_info ──(route)──> process_booking ──> END
```

### Responsibilities by module
- `src/agents/base_agent.py`: init LLM, bind tools, compile graph with checkpointer, expose `run()`/`stream()`.
- `src/agents/enhanced_agent.py` (`FlightAgent`): node logic, prompts, parsers, routing.
- `src/config/settings.py`: singleton `settings` combining `LLMConfig`, `AgentConfig`, `BookingConfig`, `MockDataConfig`; loads `.env`; validates; creates `data/`, `logs/`.
- `src/utils/models.py`: schemas for intents, booking info, order/cart/payment, `QuestionTemplates`.
- `src/utils/database.py`: SQLite manager (conversations, entries, summaries), indices, stats, cleanup.
- `src/utils/conversation_service.py`: thin domain service wrapping `db_manager`.
- `src/tools/flight_tools.py`: tools for booking, cart, payments, weather, status.

### Routing rules
- Low confidence → `process_booking` to ask clarifying questions.
- For `book_flight`/`search_flights`, if required fields are missing → go to `collect_info` (multilingual streaming question).
- If enough info or a simple request → `process_booking`.
