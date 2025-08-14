## CLI Utilities & Scripts

### `main.py`
- Console app: checks `.env`, validates config, initializes `FlightAgent`, interactive loop.
- Built-in commands: `quit`, `help`, `tools`, `config`, `history`, `summary`, `stream`.
- Generates a random `thread_id` and sample `user_id`.

### `manage_conversation_db.py`
Commands:
- `stats`: DB statistics
- `list [--user USER] [--limit N]`: list conversations
- `show --thread THREAD_ID`: show conversation details
- `delete --thread THREAD_ID`: delete conversation (with confirmation)
- `cleanup [--days N]`: cleanup old conversations
- `export --thread THREAD_ID [--output FILE]`: export JSON
- `search --query TEXT [--user USER]`: search by content

### `view_conversations.py`
- `--thread THREAD_ID`: view details
- `--list`: compact listing
- No flags: print full logs for all threads

### `view_summaries.py`
- No flags: list summaries
- Pass `THREAD_ID` to view a specific summary

### `inspect_db.py`
LangGraph checkpoint DB utilities:
```bash
python inspect_db.py basic
python inspect_db.py detailed
python inspect_db.py threads
python inspect_db.py search "keyword"
```
