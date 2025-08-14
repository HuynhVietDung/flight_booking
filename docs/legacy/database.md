## Databases & Persistence

Two SQLite databases:

1) LangGraph checkpoint: `data/langgraph_checkpoints.db`
   - Used by `BaseAgent.compile_graph()` through `SqliteSaver` for per-thread state checkpoints.
   - Inspect with `inspect_db.py` (tables, samples, search).

2) Conversation database: `data/conversations.db`
   - Managed via `src/utils/database.py` (`DatabaseManager`) and `src/utils/conversation_service.py`.
   - Tables:
     - `conversations(thread_id UNIQUE, user_id, created_at, updated_at)`
     - `conversation_entries(thread_id, user_input, assistant_response, session_id, metadata JSON, timestamp)`
     - `conversation_summaries(thread_id UNIQUE, user_id, summary_text, key_points JSON, intent_summary, booking_info JSON)`
   - Capabilities: create/write/delete conversations, add entries, list, summaries, stats, cleanup.

### Admin/Viewing Tools
- `view_conversations.py`: list or inspect conversations.
- `view_summaries.py`: list summaries.
- `manage_conversation_db.py`: `stats`, `list`, `show`, `delete`, `cleanup`, `export`, `search`.
- `inspect_db.py`: inspect LangGraph checkpoint DB (tables, sample data, content search).
