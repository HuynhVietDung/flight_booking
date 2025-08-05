"""
Configuration settings for the Flight Booking Agent
"""

import os
from typing import Dict, Any, List
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv


# Load environment variables from .env file
def load_environment():
    """Load environment variables from .env file."""
    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent
    env_file = project_root / ".env"
    
    # Load .env file if it exists
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Loaded environment from {env_file}")
    else:
        print(f"⚠️  No .env file found at {env_file}")
        print("   Using system environment variables only")


# Load environment variables
load_environment()


@dataclass
class LLMConfig:
    """LLM configuration settings."""
    model: str = "gpt-4.1-mini"
    temperature: float = 0.0
    max_tokens: int = 1000
    api_key: str = None
    base_url: str = "https://api.openai.com/v1"


@dataclass
class AgentConfig:
    """Agent configuration settings."""
    name: str = "Flight Booking Agent"
    version: str = "1.0.0"
    intent_confidence_threshold: float = 0.6
    default_passengers: int = 1
    default_class_type: str = "economy"


@dataclass
class BookingConfig:
    """Booking configuration settings."""
    class_types: List[str] = None
    required_fields: Dict[str, List[str]] = None
    field_names: Dict[str, str] = None
    
    def __post_init__(self):
        if self.class_types is None:
            self.class_types = ["economy", "business", "first"]
        
        if self.required_fields is None:
            self.required_fields = {
                "book_flight": ["departure_city", "arrival_city", "round_trip", "date", "passengers", "class_type", "passenger_name", "email"],
                "search_flights": ["departure_city", "arrival_city", "round_trip", "date"],
                "check_weather": ["city"],
                "flight_status": ["flight_number"]
            }
        
        if self.field_names is None:
            self.field_names = {
                "departure_city": "departure city",
                "arrival_city": "destination city",
                "round_trip": "round trip (yes/no)",
                "date": "travel date",
                "return_date": "return date (required if round_trip is true)",
                "passenger_name": "passenger name",
                "email": "email address",
                "passengers": "number of passengers",
                "class_type": "class type (economy, business, or first)",
                "flight_number": "flight number"
            }


@dataclass
class MockDataConfig:
    """Mock data configuration settings."""
    airlines: List[str] = None
    cities: List[str] = None
    
    def __post_init__(self):
        if self.airlines is None:
            self.airlines = ["MockAir", "SkyWay", "GlobalFly"]
        
        if self.cities is None:
            self.cities = ["New York", "London", "Paris", "Tokyo", "Sydney", "Seoul", "Berlin", "Rome"]


class Settings:
    """Main settings class that combines all configurations (Singleton)."""
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.llm = LLMConfig(
                model=os.getenv("LLM_MODEL", "gpt-4.1-mini"),
                temperature=float(os.getenv("LLM_TEMPERATURE", "0")),
                max_tokens=int(os.getenv("LLM_MAX_TOKENS", "1000")),
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            )
            self.agent = AgentConfig(
                intent_confidence_threshold=float(os.getenv("INTENT_CONFIDENCE_THRESHOLD", "0.6")),
                default_passengers=int(os.getenv("DEFAULT_PASSENGERS", "1")),
                default_class_type=os.getenv("DEFAULT_CLASS_TYPE", "economy")
            )
            self.booking = BookingConfig()
            self.mock_data = MockDataConfig()
            # Project paths
            self.project_root = Path(__file__).parent.parent.parent
            self.src_path = self.project_root / "src"
            self.data_path = self.project_root / "data"
            self.logs_path = self.project_root / "logs"
            self.env_file = self.project_root / ".env"
            # Create necessary directories
            self.data_path.mkdir(exist_ok=True)
            self.logs_path.mkdir(exist_ok=True)
            self._initialized = True

    def validate(self) -> bool:
        """Validate the configuration."""
        errors = []
        
        if not self.llm.api_key:
            errors.append("OPENAI_API_KEY is required (set in .env file or environment)")
        
        if not (0 <= self.llm.temperature <= 2):
            errors.append("LLM_TEMPERATURE must be between 0 and 2")
        
        if not (0 <= self.agent.intent_confidence_threshold <= 1):
            errors.append("INTENT_CONFIDENCE_THRESHOLD must be between 0 and 1")
        
        if errors:
            print("❌ Configuration validation failed:")
            for error in errors:
                print(f"   - {error}")
            return False
        
        print("✅ Configuration validated successfully")
        return True


# Global settings instance
settings = Settings() 