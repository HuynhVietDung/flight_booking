## Setup & Configuration

### .env and Settings
- Settings (singleton) loads `.env` at project root; creates `data/` and `logs/` if missing.
- Variables:
  - LLM: `LLM_MODEL`, `LLM_TEMPERATURE`, `LLM_MAX_TOKENS`, `OPENAI_API_KEY`, `OPENAI_BASE_URL`
  - Agent: `INTENT_CONFIDENCE_THRESHOLD`, `DEFAULT_PASSENGERS`, `DEFAULT_CLASS_TYPE`
  - BookingConfig: required fields per intent; human-friendly labels
  - MockDataConfig: airlines, cities (mock)

Sample `.env`:
```bash
LLM_MODEL=gpt-4.1-mini
LLM_TEMPERATURE=0
LLM_MAX_TOKENS=1000
INTENT_CONFIDENCE_THRESHOLD=0.6
DEFAULT_PASSENGERS=1
DEFAULT_CLASS_TYPE=economy
OPENAI_API_KEY=your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
```

Validation: `settings.validate()` checks API key and value ranges.

### Databases
- LangGraph checkpoint: `data/langgraph_checkpoints.db` (via `SqliteSaver`).
- Conversation DB: `data/conversations.db` managed by `DatabaseManager`/`ConversationService`.
  - Tables: `conversations`, `conversation_entries`, `conversation_summaries`.
  - Ops: create/delete, add entry, summarize, stats, cleanup.

### Enable LangGraph Studio
From project root (reads `langgraph.json` automatically):
```bash
langgraph dev
```
- Studio reads `.env` via `langgraph.json` `env` field and exposes the `flight_booking_agent` graph.

### Enable LangSmith (Tracing)
```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=your-langsmith-api-key
export LANGCHAIN_PROJECT=flight-booking-agent  # optional
# export LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```
Place them in `.env` to keep tracing on for both `python main.py` and `langgraph dev`.
