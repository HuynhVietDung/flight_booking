## Agents & Processing Flow

### `BaseAgent` (`src/agents/base_agent.py`)
- Two LLMs: `llm` (tool-enabled, user-facing) and `processed_llm` (low temperature for JSON parsing).
- `tools`: binds all tools from `src/tools/flight_tools.py`.
- `compile_graph(file_path)`: compiles `StateGraph` with SQLite checkpointer (`data/langgraph_checkpoints.db`).
- `run(user_input, thread_id, user_id, ...)`: invokes the graph; returns `AgentResponse` (intent, confidence, language, booking_info, response).
- `stream(...)`: streams with `stream_mode="custom"` emitting `question_chunk`/`completion_chunk`.

### `FlightAgent` (`src/agents/enhanced_agent.py`)
Nodes:
- `save_conversation`: extracts last `HumanMessage`/`AIMessage` pair and persists via `conversation_service` (SQLite `conversations.db`).
- `classify_intent`: classifies intent with confidence, reasoning, language (JSON output → `IntentClassification`).
- `collect_booking_info`:
  - Uses `settings.booking.required_fields` by intent.
  - LLM extracts missing fields from reasoning, updates `booking_info`.
  - If still missing → streams a natural multilingual question (`QuestionTemplates`), sets `current_step=collecting_info` and provides an `action` hint.
  - If complete → streams completion message and sets `current_step=info_complete`.
- `process_booking`:
  - Builds system prompt from current intent and `booking_info`.
  - Calls LLM with bound tools; executes tool calls and appends outputs.
- `summarize_conversation`: when enough messages (>=5), generates a short summary and saves to `conversation_summaries`.

Routing:
- `route_based_on_intent`: picks `collect_info` vs `process_booking` by confidence and missing fields.
- `route_after_collect_info`: if `collecting_info` → `END` (await user); if `info_complete` → `process_booking`.

### State
- `FlightBookingState`: `messages`, `intent_classification`, `booking_info`, `conversation_history`, `current_step`, `data`, `action`, `thread_id`, `user_id`.

### Prompts & Streaming
- Uses `ChatPromptTemplate`, `MessagesPlaceholder`, `JsonOutputParser`.
- Streaming splits strings via `chunk_text()` and `get_stream_writer()` to emit `question_chunk`/`completion_chunk` events.
