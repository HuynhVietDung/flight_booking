## Configuration & Environment Variables

Source: `src/config/settings.py`

- `Settings` is a singleton that loads `.env` from the project root, creates `data/` and `logs/` if needed.
- Groups:
  - `LLMConfig`: `LLM_MODEL`, `LLM_TEMPERATURE`, `LLM_MAX_TOKENS`, `OPENAI_API_KEY`, `OPENAI_BASE_URL`
  - `AgentConfig`: `INTENT_CONFIDENCE_THRESHOLD`, `DEFAULT_PASSENGERS`, `DEFAULT_CLASS_TYPE`
  - `BookingConfig`: required fields per intent, friendly field names
  - `MockDataConfig`: airlines, cities (mock)

### Sample .env
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

### Validation
- `settings.validate()` checks API key and value ranges (temperature 0..2, threshold 0..1).
