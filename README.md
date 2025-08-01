# Flight Booking Agent with LangGraph

A sophisticated flight booking agent built using LangGraph with three main nodes for intent classification, information collection, and LLM processing.

## 🏗️ Architecture

The agent consists of three main nodes:

1. **Intent Classification Node** - Determines user intent with confidence scoring
2. **Collect Info Node** - Intelligently extracts and requests missing booking information
3. **LLM Processing Node** - Handles the main booking logic with tool calling

## 📁 Project Structure

```
flight_booking/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py          # Base agent class
│   │   └── enhanced_agent.py      # Enhanced flight booking agent
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py            # Configuration management
│   ├── tools/
│   │   ├── __init__.py
│   │   └── flight_tools.py        # Flight booking tools
│   ├── utils/
│   │   ├── __init__.py
│   │   └── models.py              # Data models
│   ├── examples/
│   │   ├── __init__.py
│   │   └── demo.py                # Demo scripts
│   └── __init__.py                # Main package
├── main.py                        # Main entry point
├── setup.py                       # Setup script
├── requirements.txt               # Python dependencies
├── .env                           # Environment variables (auto-created)
├── .gitignore                     # Git ignore
└── README.md                      # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up Environment Variables

The application will automatically create a `.env` template file on first run. You need to edit it and add your OpenAI API key:

```bash
# Run the application (it will create .env template)
python main.py

# Edit the .env file and add your API key
# OPENAI_API_KEY=your-openai-api-key-here
```

Or manually create a `.env` file:

```bash
# Create .env file
cat > .env << EOF
# Flight Booking Agent Environment Configuration

# LLM Configuration
LLM_MODEL=gpt-4.1-mini
LLM_TEMPERATURE=0
LLM_MAX_TOKENS=1000

# Intent Classification
INTENT_CONFIDENCE_THRESHOLD=0.6

# Booking Configuration
DEFAULT_PASSENGERS=1
DEFAULT_CLASS_TYPE=economy

# OpenAI Configuration (required)
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
EOF
```

### 3. Run the Application

```bash
# Run main application
python main.py

# Or run demo
python src/examples/demo.py
```

## 🎯 Features

### Enhanced Agent (`src/agents/enhanced_agent.py`)
- **Confidence-based intent classification** with reasoning
- **Intelligent information extraction** from user messages
- **Structured output parsing** using Pydantic models
- **Enhanced tool integration** with better error handling
- **Context-aware responses** based on current state
- **Conversation memory** and state management
- **Modular architecture** with base classes

### Configuration Management (`src/config/settings.py`)
- **Environment-based configuration** with `.env` file support
- **Automatic .env template creation**
- **Validation and error handling**
- **Structured settings classes**
- **Easy customization**

### Tools (`src/tools/flight_tools.py`)
- **Mock flight search and booking**
- **Weather information**
- **Flight status checking**
- **Booking management**
- **Extensible tool system**

## 🛠️ Available Tools

The agent includes several mock tools for demonstration:

- **`search_flights`** - Search for available flights
- **`book_flight`** - Book a specific flight
- **`get_weather`** - Get weather information for a city
- **`get_flight_status`** - Check flight status
- **`get_booking_info`** - Get booking information
- **`cancel_booking`** - Cancel a flight booking

## 📊 State Management

The agent uses a structured state with the following components:

```python
class FlightBookingState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]  # Conversation history
    intent: str                                          # Classified intent
    intent_confidence: float                             # Confidence score
    booking_info: dict                                   # Collected booking information
    conversation_history: list[dict]                     # Additional conversation data
    final_response: str                                  # Final agent response
    current_step: str                                    # Current processing step
```

## 🔄 Graph Flow

```
START → Intent Classification → Route Based on Intent
                                    ↓
                            ┌─────────────────┐
                            │ Collect Info    │ (if missing info)
                            └─────────────────┘
                                    ↓
                            ┌─────────────────┐
                            │ LLM Processing  │ (with tools)
                            └─────────────────┘
                                    ↓
                                   END
```

## 🎮 Usage Examples

### Basic Usage

```python
from src.agents import EnhancedFlightAgent

# Create agent
agent = EnhancedFlightAgent()

# Run agent
response = agent.run("I want to book a flight from New York to London")
print(response.response)
```

### Advanced Usage

```python
from src.agents import EnhancedFlightAgent
from src.config import settings

# Validate configuration
if settings.validate():
    agent = EnhancedFlightAgent()
    
    # Process multiple requests
    requests = [
        "Book me a flight from Paris to Tokyo on March 15th",
        "What's the weather like in London?",
        "Search for flights from Tokyo to Seoul"
    ]
    
    for request in requests:
        response = agent.run(request)
        print(f"Intent: {response.intent} (confidence: {response.confidence:.2f})")
        print(f"Response: {response.response}")
```

## 🧪 Testing

The demo script includes several test scenarios:

1. **Basic Conversation** - Complete booking process
2. **Different Intents** - Various user intents
3. **Error Handling** - Edge cases and error scenarios
4. **Interactive Demo** - Real-time conversation

## ⚙️ Configuration

The agent can be configured using environment variables in the `.env` file:

```bash
# LLM Configuration
LLM_MODEL=gpt-4.1-mini
LLM_TEMPERATURE=0
LLM_MAX_TOKENS=1000

# Intent Classification
INTENT_CONFIDENCE_THRESHOLD=0.6

# Booking Configuration
DEFAULT_PASSENGERS=1
DEFAULT_CLASS_TYPE=economy

# OpenAI Configuration (required)
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
```

## 🔧 Customization

### Adding New Tools

```python
from langchain_core.tools import tool

@tool
def your_custom_tool(param1: str, param2: int) -> str:
    """Description of what your tool does."""
    # Your tool implementation
    return "Tool result"
```

### Creating Custom Agents

```python
from src.agents.base_agent import BaseFlightAgent

class CustomAgent(BaseFlightAgent):
    def create_graph(self) -> StateGraph:
        # Your custom graph implementation
        pass
```

### Extending Configuration

```python
from src.config.settings import Settings

class CustomSettings(Settings):
    def __init__(self):
        super().__init__()
        # Add custom configuration
        self.custom_setting = "value"
```

## 🚨 Important Notes

- **Environment Variables**: The application automatically creates a `.env` template file on first run
- **API Key**: You need a valid OpenAI API key in the `.env` file to run the agent
- **Mock Tools**: All tools in this demo are mock implementations for demonstration purposes
- **Rate Limits**: Be aware of OpenAI API rate limits when testing
- **Error Handling**: The agent includes comprehensive error handling
- **Modular Design**: Easy to extend and customize

## 📈 Future Enhancements

Potential improvements for production use:

- **Real API Integration** - Connect to actual flight booking APIs
- **Database Integration** - Store booking information and user preferences
- **Authentication** - User authentication and session management
- **Payment Processing** - Integrate payment gateways
- **Email Notifications** - Send booking confirmations
- **Multi-language Support** - Internationalization
- **Advanced Error Handling** - Comprehensive error management
- **Logging and Monitoring** - Production-grade observability
- **Unit Tests** - Comprehensive test coverage
- **Docker Support** - Containerized deployment

## 🤝 Contributing

Feel free to contribute by:

1. Adding new tools and capabilities
2. Improving intent classification accuracy
3. Enhancing error handling
4. Adding new test scenarios
5. Improving documentation
6. Adding unit tests
7. Optimizing performance

## 📄 License

This project is for educational and demonstration purposes. 