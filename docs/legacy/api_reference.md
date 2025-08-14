## API Reference (legacy)

Most public APIs are summarized in `docs/reference.md`. This legacy file kept for completeness.

### Quick imports
```python
from src import FlightAgent, BaseAgent, settings, AgentResponse, FlightBookingState, flight_tools
```

### Key methods
- `FlightAgent.run(...) -> AgentResponse`
- `FlightAgent.stream(...) -> Iterator[dict]`
- `settings.validate()`, `settings.print_config()`, `settings.create_env_template()`

See also: tools signatures in `src/tools/flight_tools.py`.
