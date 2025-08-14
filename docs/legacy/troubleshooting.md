## Troubleshooting

- Missing `.env` or `OPENAI_API_KEY`
  - Run `python main.py` once to generate a `.env` template, then add your API key.

- `Configuration validation failed`
  - Check ranges: `LLM_TEMPERATURE` (0..2), `INTENT_CONFIDENCE_THRESHOLD` (0..1), and API key.

- Tools not running or empty outputs
  - Validate inputs and required fields. For `book_flight`, you need `flight_number`, `passenger_name`, `email`, ...

- No conversation history visible
  - Inspect `data/conversations.db`. Use `python manage_conversation_db.py list` or `view_conversations.py`.

- Checkpoints not updating
  - Verify write permissions to `data/langgraph_checkpoints.db` and correct `thread_id` in `run()`/`stream()`.

- Language quality (EN/VN) not ideal
  - Update `QuestionTemplates` or prompts in `enhanced_agent.py`.
