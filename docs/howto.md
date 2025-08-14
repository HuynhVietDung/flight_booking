## How-To & Operations

### Run the App
```bash
pip install -r requirements.txt
python main.py
```
In-app commands: `quit`, `help`, `tools`, `config`, `history`, `summary`, `stream`.

### CLI Utilities
```bash
python manage_conversation_db.py stats
python manage_conversation_db.py list --limit 10
python manage_conversation_db.py show --thread <id>
python manage_conversation_db.py export --thread <id> --output out.json
python view_conversations.py --list
python view_summaries.py
python inspect_db.py detailed
```

### Python Examples
```python
from src import FlightAgent
agent = FlightAgent()
resp = agent.run("Find flights from Hanoi to Tokyo on 10/12", thread_id="demo", user_id="u1")
print(resp.intent, resp.confidence)
print(resp.response)
```
Streaming:
```python
for chunk in agent.stream("Round-trip Paris-Tokyo on 03/15", thread_id="demo", user_id="u1"):
    if chunk.get("type") == "question_chunk":
        print(chunk["content"], end="")
    elif chunk.get("type") == "completion_chunk":
        print(chunk["content"], end="")
```

### Troubleshooting (quick)
- Missing `.env`/`OPENAI_API_KEY`: run `python main.py` to generate a template and add your key
- Validation failed: check temperature (0..2), threshold (0..1)
- No conversations: use `view_conversations.py` or `manage_conversation_db.py list`
- Streaming/routing unexpected: review prompts/`QuestionTemplates`

### Extending
- Add a new `@tool` and include it in `flight_tools`
- Adjust prompts/routing in `enhanced_agent.py`; update `settings.booking.required_fields`
- Add languages in `QuestionTemplates`
- Integrate real APIs in `flight_tools.py` instead of mocks

### LangGraph Studio
From project root:
```bash
langgraph dev
```
Studio auto-detects `langgraph.json` and `.env`, and exposes the `flight_booking_agent` graph.
