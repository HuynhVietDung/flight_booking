## Extending & Customization

### Add a new tool
```python
from langchain_core.tools import tool

@tool
def your_custom_tool(arg1: str) -> str:
    """Short description"""
    return "Result"
```
- Import it into `src/tools/__init__.py` (if present) and add to `flight_tools`.
- Tools are automatically bound via `BaseAgent`.

### Change prompts / routing
- Edit `src/agents/enhanced_agent.py`: `system_prompts`, `classify_intent` prompt, `collect_booking_info` extraction prompt.
- Adjust `settings.booking.required_fields` to add required fields per intent.

### Add languages
- Update `QuestionTemplates` in `src/utils/models.py` with the new language key.

### Integrate real APIs
- Replace mock logic in `flight_tools.py` with actual integrations (GDS, weather, PSP, etc.).
- Normalize results, handle errors/timeouts, add tests.

### Storage/Observability
- Add logging/telemetry, metrics in `database.py`/`conversation_service.py` or external storage as needed.
