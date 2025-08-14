## Flight Booking Agent Docs

This documentation covers the architecture, components, how to run, and how to extend the LangGraph/LangChain-based flight booking assistant.

- Purpose: Tebby helps users search and book flights, check weather and flight status, manage cart and mock payments.
- Core tech: LangGraph, LangChain, Pydantic, SQLite, OpenAI Chat API.

### Index
- Overview: see `overview.md`
- Setup & Configuration: see `setup_and_config.md`
- Reference: see `reference.md`
- How-To & Operations: see `howto.md`

### Project Structure
```text
flight_booking/
  ├─ src/
  │  ├─ agents/             # BaseAgent, FlightAgent (enhanced)
  │  ├─ config/             # Settings + .env loader
  │  ├─ tools/              # flight_tools (@tool collection)
  │  └─ utils/              # models, cart_service, payment_service, database, conversation_service
  ├─ data/                  # SQLite DBs: conversations.db, langgraph_checkpoints.db
  ├─ main.py                # Console app
  ├─ manage_conversation_db.py / view_*.py / inspect_db.py  # CLI/admin scripts
  └─ README.md              # Project readme
```

### Quick Start
1) Install dependencies
```bash
pip install -r requirements.txt
```
2) First run to generate `.env` template, then add your API key
```bash
python main.py
# then edit .env and add OPENAI_API_KEY
```
3) Run the app
```bash
python main.py
```

### Quick Links
- Architecture: see `legacy/architecture.md`
- API reference details: see `legacy/api_reference.md`
- Extending: see `legacy/extending.md`
