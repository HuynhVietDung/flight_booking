"""
Data models for the Flight Booking Agent
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from typing_extensions import TypedDict, Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class IntentClassification(BaseModel):
    """Model for intent classification output."""
    intent: str = Field(description="The classified intent")
    confidence: float = Field(description="Confidence score between 0 and 1")
    reasoning: str = Field(description="Brief reasoning for the classification")


class BookingInformation(BaseModel):
    """Model for booking information extraction."""
    departure_city: Optional[str] = Field(description="Departure city", default=None)
    arrival_city: Optional[str] = Field(description="Arrival city", default=None)
    date: Optional[str] = Field(description="Travel date", default=None)
    passenger_name: Optional[str] = Field(description="Passenger name", default=None)
    email: Optional[str] = Field(description="Email address", default=None)
    passengers: Optional[int] = Field(description="Number of passengers", default=1)
    class_type: Optional[str] = Field(description="Class type (economy, business, first)", default="economy")


class FlightBookingState(TypedDict):
    """State schema for the flight booking agent."""
    messages: Annotated[list[AnyMessage], add_messages]
    intent: str
    intent_confidence: float
    booking_info: dict
    conversation_history: list[dict]
    final_response: str
    current_step: str


class FlightData(BaseModel):
    """Model for flight data."""
    flight_number: str
    departure: str
    arrival: str
    departure_time: str
    arrival_time: str
    price: float
    airline: str
    available_seats: int
    class_type: str = "economy"


class BookingData(BaseModel):
    """Model for booking data."""
    flight_number: str
    passenger_name: str
    email: str
    passengers: int = 1
    class_type: str = "economy"
    total_price: float
    booking_reference: str
    status: str = "confirmed"


class WeatherData(BaseModel):
    """Model for weather data."""
    city: str
    temperature: int
    condition: str
    humidity: str


class AgentResponse(BaseModel):
    """Model for agent response."""
    success: bool
    intent: str
    confidence: float
    response: str
    booking_info: Dict[str, Any] = {}
    error: Optional[str] = None


class ConversationTurn(BaseModel):
    """Model for a conversation turn."""
    user_input: str
    agent_response: str
    intent: str
    confidence: float
    timestamp: str
    booking_info: Dict[str, Any] = {}


class ConversationHistory(BaseModel):
    """Model for conversation history."""
    user_id: str
    turns: List[ConversationTurn] = []
    current_booking_info: Dict[str, Any] = {}
    
    def add_turn(self, turn: ConversationTurn):
        """Add a new turn to the conversation."""
        self.turns.append(turn)
    
    def get_last_turn(self) -> Optional[ConversationTurn]:
        """Get the last conversation turn."""
        return self.turns[-1] if self.turns else None
    
    def get_turn_count(self) -> int:
        """Get the number of turns in the conversation."""
        return len(self.turns) 